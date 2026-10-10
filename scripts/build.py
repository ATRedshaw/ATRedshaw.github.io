from datetime import date
from html.parser import HTMLParser
import math
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"


class ReadingTime(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.words = 0
        self.images = 0
        self.in_hidden_content = False
        self.feed(html)
        # Allow 240 words per minute and 10 seconds to view each image.
        seconds = self.words / 240 * 60 + self.images * 10
        self.minutes = max(1, math.ceil(seconds / 60))

    def handle_starttag(self, tag, attributes):
        if tag in ("script", "style"):
            self.in_hidden_content = True
        elif tag == "img" and not self.in_hidden_content:
            self.images += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_hidden_content = False

    def handle_data(self, data):
        if not self.in_hidden_content:
            self.words += len(re.findall(r"\b\w+(?:['’]\w+)*\b", data))


class ContentLoader(yaml.SafeLoader):
    pass


# Keep dates as text so validation can report their source file and field.
ContentLoader.add_constructor("tag:yaml.org,2002:timestamp", lambda loader, node: loader.construct_scalar(node))


def load_data(filename):
    path = ROOT / "data" / filename
    return parse_yaml(path.read_text(encoding="utf-8"), f"data/{filename}")


def parse_yaml(text, source):
    try:
        data = yaml.load(text, Loader=ContentLoader)
    except yaml.YAMLError as error:
        raise ValueError(f"{source}: invalid YAML: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"{source}: expected a YAML mapping of field names to values")
    return data


def require_text(data, field, source):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: {field} must be a non-empty string")


def validate_entry(entry, section):
    source = entry["source"]
    fields = ("title", "slug", "excerpt", "image", "topic") if section == "blog" else (
        "title", "slug", "description", "thumbnail", "markdown", "legacy_slug"
    )
    for field in fields:
        require_text(entry, field, source)
    if section == "blog":
        for field in ("topic", "series"):
            if field in entry:
                require_text(entry, field, source)
                entry[field] = entry[field].strip()
        if "series_order" in entry:
            order = entry["series_order"]
            if "series" not in entry or type(order) is not int or order < 1:
                raise ValueError(f"{source}: series_order must be a positive integer with a series name")
    tags = entry.get("tags")
    if not isinstance(tags, list) or not tags or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
        raise ValueError(f"{source}: tags must be a non-empty list of strings, such as [Python, Analytics]")
    for field in ("date", "updated"):
        if field not in entry and (field != "date" or section != "blog"):
            continue
        value = entry.get(field)
        if isinstance(value, date):
            value = value.isoformat()
        try:
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"{source}: {field} must be a valid date in YYYY-MM-DD format") from None
        entry[field] = value
    if "updated" in entry and "date" in entry and entry["updated"] < entry["date"]:
        raise ValueError(f"{source}: updated cannot be earlier than date")
    if "featured" in entry and not isinstance(entry["featured"], bool):
        raise ValueError(f"{source}: featured must be true or false")
    links = entry.get("links", [])
    if not isinstance(links, list):
        raise ValueError(f"{source}: links must be a list")
    for index, link in enumerate(links, start=1):
        if not isinstance(link, dict):
            raise ValueError(f"{source}: link {index} must contain url, icon and label")
        for field in ("url", "icon", "label"):
            require_text(link, field, f"{source}, link {index}")


def validate_site(site):
    source = "data/site.yaml"
    for field in ("name", "handle", "person_id", "title", "description", "tagline", "headshot", "headshot_alt", "about"):
        require_text(site, field, source)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", site["person_id"]):
        raise ValueError(f"{source}: person_id must use lowercase words separated by hyphens")
    if not isinstance(site.get("social"), dict):
        raise ValueError(f"{source}: social must contain profile links")
    for field in ("github", "linkedin"):
        require_text(site["social"], field, f"{source}, social")


def load_entries(filename, key, section):
    entries = load_data(filename).get(key)
    if not isinstance(entries, list):
        raise ValueError(f"data/{filename}: {key} must be a list")
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"data/{filename}, entry {index}: expected a YAML mapping")
        entry["source"] = f"data/{filename}, entry {index}"
    return prepare_entries(entries, section)


def load_posts():
    entries = []
    for path in sorted((ROOT / "content/blog").glob("*.md")):
        source = path.relative_to(ROOT).as_posix()
        parts = path.read_text(encoding="utf-8").split("\n---\n", 1)
        if not parts[0].startswith("---\n") or len(parts) != 2:
            raise ValueError(f"{source}: expected YAML front matter between --- lines")
        entry = parse_yaml(parts[0][4:], source)
        entry["source"] = source
        entry["markdown"] = source
        entry["markdown_text"] = parts[1].lstrip("\n")
        entries.append(entry)
    return prepare_entries(entries, "blog")


def prepare_entries(entries, section):
    slugs = {}
    legacy_slugs = set()
    for entry in entries:
        validate_entry(entry, section)
        source = entry["source"]
        slug = entry["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"{source}: slug must use lowercase words separated by hyphens")
        if slug in slugs:
            raise ValueError(f"{source}: duplicate slug '{slug}', also used by {slugs[slug]}")
        slugs[slug] = source
        if section == "projects":
            legacy_slug = entry["legacy_slug"]
            if legacy_slug in legacy_slugs:
                raise ValueError(f"{source}: duplicate legacy_slug '{legacy_slug}'")
            legacy_slugs.add(legacy_slug)
        entry["url"] = f"/{section}/{slug}/"
        if "markdown_text" not in entry:
            try:
                entry["markdown_text"] = (ROOT / entry["markdown"]).read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError(f"{source}: Markdown file not found: {entry['markdown']}") from None
        if not entry["markdown_text"].strip():
            raise ValueError(f"{source}: Markdown body must not be empty")
    return entries


def group_posts(posts, field):
    groups = {}
    for post in posts:
        name = post.get(field)
        if not name:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if not slug:
            raise ValueError(f"{post['source']}: {field} needs letters or numbers for its URL")
        if slug in groups and groups[slug]["name"] != name:
            raise ValueError(
                f"{post['source']}: {field} '{name}' shares a URL with '{groups[slug]['name']}'; "
                "use one consistent name"
            )
        url = f"/journal/{'topics' if field == 'topic' else 'series'}/{slug}/"
        group = groups.setdefault(slug, {"name": name, "url": url, "posts": []})
        group["posts"].append(post)
        post[f"{field}_url"] = url
    for group in groups.values():
        group["topics"] = sorted({post["topic"] for post in group["posts"]})
        if field != "series":
            continue
        orders = {}
        for post in group["posts"]:
            if "series_order" in post:
                order = post["series_order"]
                if order in orders:
                    raise ValueError(
                        f"{post['source']}: duplicate series_order {order} in '{group['name']}', "
                        f"also used by {orders[order]}"
                    )
                orders[order] = post["source"]
        group["posts"].sort(key=lambda post: (post.get("series_order", math.inf), post["date"], post["slug"]))
        for index, post in enumerate(group["posts"]):
            post["series_position"] = index + 1
            post["series_count"] = len(group["posts"])
            for direction, neighbour in (("previous", index - 1), ("next", index + 1)):
                post[f"series_{direction}"] = None
                if 0 <= neighbour < len(group["posts"]):
                    related = group["posts"][neighbour]
                    post[f"series_{direction}"] = {"title": related["title"], "url": related["url"]}
    return sorted(groups.values(), key=lambda group: group["name"].casefold())


def render_markdown(text, legacy_urls, domain):
    html = markdown.markdown(
        text,
        extensions=["extra", "toc", "pymdownx.arithmatex"],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
    )

    def rewrite_url(match):
        attribute, url = match.groups()
        parts = urlsplit(url)
        if parts.netloc and parts.netloc != domain:
            return match.group(0)
        path = parts.path.lstrip("/")
        if path.startswith("assets/"):
            url = parts._replace(scheme="", netloc="", path="/" + path).geturl()
        elif path == "blog.html":
            url = parts._replace(scheme="", netloc="", path="/journal.html").geturl()
        elif path in ("post.html", "projects.html"):
            parameter = "id" if path == "post.html" else "project"
            identifier = parse_qs(parts.query).get(parameter, [""])[0]
            if identifier in legacy_urls:
                url = legacy_urls[identifier] + ("#" + parts.fragment if parts.fragment else "")
        return f'{attribute}="{url}"'

    html = re.sub(r'\b(href|src)="([^"]+)"', rewrite_url, html)
    return html.replace("<table>", '<div class="prose-table-scroll"><table>').replace(
        "</table>", "</table></div>"
    )


def build():
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["short_date"] = lambda value: (
        date.fromisoformat(value).strftime("%b %d, %Y").replace(" 0", " ")
    )
    environment.filters["long_date"] = lambda value: (
        date.fromisoformat(value).strftime("%B %d, %Y").replace(" 0", " ")
    )
    site = load_data("site.yaml")
    validate_site(site)
    domain = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    base_url = "https://" + domain
    projects = load_entries("projects.yaml", "projects", "projects")
    posts = load_posts()
    posts.sort(key=lambda post: post["date"], reverse=True)
    topics = group_posts(posts, "topic")
    series = group_posts(posts, "series")
    legacy_urls = {post["slug"]: post["url"] for post in posts}
    legacy_urls.update({project["legacy_slug"]: project["url"] for project in projects})
    for entry in projects + posts:
        entry["html"] = render_markdown(entry["markdown_text"], legacy_urls, domain)
        entry["reading_time"] = f"{ReadingTime(entry['html']).minutes} min"
    context = {
        "site": site,
        "skills": load_data("skills.yaml")["categories"],
        "experience": load_data("experience.yaml")["entries"],
        "year": date.today().year,
        "projects": projects,
        "posts": posts,
        "topics": topics,
        "series": series,
    }
    person = {
        "@type": "Person",
        "@id": base_url + "/#" + site["person_id"],
        "name": site["name"],
        "alternateName": site["handle"],
        "url": base_url + "/",
        "image": base_url + "/" + site["headshot"],
        "description": site["tagline"],
        "sameAs": list(site["social"].values()),
    }
    sitemap_urls = []
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(exist_ok=True)
    for directory in ("assets", "css", "js", ".well-known"):
        shutil.copytree(
            ROOT / directory, OUTPUT / directory,
            ignore=shutil.ignore_patterns(".DS_Store", "*.py", "__pycache__", "tailwind.css"),
        )
    shutil.copy2(ROOT / "CNAME", OUTPUT / "CNAME")

    def write_page(
        filename, template, title, active, description,
        image=None, structured_data=None, noindex=False, **page_context,
    ):
        path = "/" if filename == "index.html" else "/" + filename.removesuffix("index.html")
        canonical = base_url + path
        image = image or site["headshot"]
        html = environment.get_template(template).render(
            **context, title=title, active=active, description=description,
            canonical=canonical, image_url=base_url + "/" + image.lstrip("/"),
            image_alt=title, structured_data=structured_data, noindex=noindex,
            **page_context,
        )
        destination = OUTPUT / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding="utf-8")
        if not noindex:
            sitemap_urls.append(canonical)

    profile = {
        "@context": "https://schema.org", "@type": "ProfilePage",
        "url": base_url + "/", "mainEntity": person,
    }
    write_page(
        "index.html", "home.html", f"{site['name']} | {site['title']}", "home",
        site["description"], structured_data=profile,
    )
    for filename, template, title, active, description, noindex in (
        (
            'experience.html', 'experience.html', f"Experience & Skills | {site['name']}", 'experience',
            f"{site['name']}'s experience in data science, machine learning and data engineering, alongside technical skills, education and certifications.",
            False,
        ),
        (
            'projects.html', 'projects.html', f"Data Science & Machine Learning Projects | {site['name']}", 'projects',
            f"Explore {site['name']}'s projects in football analytics, FPL forecasting, applied machine learning and software engineering, with demos and case studies.",
            False,
        ),
        (
            'blog.html', 'legacy-blog.html', f"Journal | {site['name']}", 'journal',
            f"Visit {site['name']}'s journal at its new address.",
            True,
        ),
        (
            'post.html', 'legacy-post.html', f"Journal | {site['name']}", 'journal',
            f"Find {site['name']}'s articles at their new addresses.",
            True,
        ),
        (
            '404.html', '404.html', f"Page Not Found | {site['name']}", '',
            f"This page could not be found. Explore {site['name']}'s projects or return to the homepage.",
            True,
        ),
    ):
        write_page(filename, template, title, active, description, noindex=noindex)
    write_page(
        "journal.html", "journal.html", f"Journal | {site['name']}", "journal",
        f"Articles by {site['name']} on sports analytics, projects, technology and more. Browse by topic or follow a series.",
        archive_kind="all", archive_name="Journal", archive_posts=posts,
        selected_topic=None, archive_series=series,
    )
    for field, groups in (("topic", topics), ("series", series)):
        for group in groups:
            name = group["name"]
            if field == "topic":
                selected_topic = name
                archive_series = [item for item in series if name in item["topics"]]
                title = f"{name} | Journal | {site['name']}"
                description = f"Browse {name} articles by {site['name']}."
            else:
                selected_topic = group["topics"][0] if len(group["topics"]) == 1 else None
                archive_series = []
                title = f"{name} series | Journal | {site['name']}"
                description = f"Read the {name} series by {site['name']}."
            write_page(
                group["url"].lstrip("/") + "index.html", "journal.html", title, "journal", description,
                archive_kind=field, archive_name=name, archive_posts=group["posts"],
                selected_topic=selected_topic, archive_series=archive_series,
            )
    for section, entries in (("projects", projects), ("blog", posts)):
        for entry in entries:
            image = entry.get("image", entry.get("thumbnail", site["headshot"]))
            article = {
                "@context": "https://schema.org",
                "@type": "BlogPosting" if section == "blog" else "Article",
                "headline": entry["title"],
                "description": entry["excerpt"] if section == "blog" else entry["description"],
                "url": base_url + entry["url"],
                "mainEntityOfPage": base_url + entry["url"],
                "image": base_url + "/" + image.lstrip("/"),
                "author": {key: person[key] for key in ("@type", "@id", "name", "url")},
            }
            if "date" in entry:
                article["datePublished"] = entry["date"]
            if "updated" in entry:
                article["dateModified"] = entry["updated"]
            write_page(
                f"{section}/{entry['slug']}/index.html", "detail.html",
                f"{entry['title']} | {context['site']['name']}", 'journal' if section == 'blog' else section,
                article["description"], image=image, structured_data=article,
                entry=entry, section=section,
            )
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ElementTree.register_namespace("", namespace)
    sitemap = ElementTree.Element(f"{{{namespace}}}urlset")
    for url in sitemap_urls:
        node = ElementTree.SubElement(sitemap, f"{{{namespace}}}url")
        ElementTree.SubElement(node, f"{{{namespace}}}loc").text = url
    ElementTree.indent(sitemap)
    ElementTree.ElementTree(sitemap).write(OUTPUT / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (OUTPUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8"
    )
    (OUTPUT / ".nojekyll").touch()
    print(f"Built {len(projects)} projects and {len(posts)} articles in {OUTPUT}")


if __name__ == "__main__":
    try:
        build()
    except (ValueError, FileNotFoundError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
