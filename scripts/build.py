from datetime import date
import math
from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"


def load_data(filename):
    return yaml.safe_load((ROOT / "data" / filename).read_text(encoding="utf-8"))


def load_entries(filename, key, section):
    entries = load_data(filename)[key]
    slugs = set()
    for entry in entries:
        slug = entry["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"Invalid or duplicate slug in {filename}: {slug}")
        slugs.add(slug)
        entry["url"] = f"/{section}/{slug}/"
        entry["markdown_text"] = (ROOT / entry["markdown"]).read_text(encoding="utf-8")
        entry["reading_time"] = f"{max(1, math.floor(len(entry['markdown_text']) / 1000 + 0.5))} min"
    return entries


def render_markdown(text, legacy_urls):
    html = markdown.markdown(
        text,
        extensions=["extra", "toc", "pymdownx.arithmatex"],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
    )

    def rewrite_url(match):
        attribute, url = match.groups()
        parts = urlsplit(url)
        if parts.netloc and parts.netloc != "atredshaw.com":
            return match.group(0)
        path = parts.path.lstrip("/")
        if path.startswith("assets/"):
            url = "/" + path
        elif path in ("post.html", "projects.html"):
            parameter = "id" if path == "post.html" else "project"
            identifier = parse_qs(parts.query).get(parameter, [""])[0]
            url = legacy_urls.get(identifier, url)
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
    environment.filters["short_date"] = lambda value: date.fromisoformat(value).strftime("%b %d, %Y").replace(" 0", " ")
    environment.filters["long_date"] = lambda value: date.fromisoformat(value).strftime("%B %d, %Y").replace(" 0", " ")
    projects = load_entries("projects.yaml", "projects", "projects")
    posts = load_entries("blog.yaml", "posts", "blog")
    posts.sort(key=lambda post: post["date"], reverse=True)
    legacy_urls = {Path(post["markdown"]).stem: post["url"] for post in posts}
    legacy_urls.update({project["legacy_slug"]: project["url"] for project in projects})
    for entry in projects + posts:
        entry["html"] = render_markdown(entry["markdown_text"], legacy_urls)
    context = {
        "site": load_data("site.yaml"),
        "skills": load_data("skills.yaml")["categories"],
        "experience": load_data("experience.yaml")["entries"],
        "year": date.today().year,
        "projects": projects,
        "posts": posts,
    }
    site = context["site"]
    base_url = "https://" + (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    person = {
        "@type": "Person",
        "@id": base_url + "/#alex-redshaw",
        "name": site["name"],
        "alternateName": "ATRedshaw",
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
            ignore=shutil.ignore_patterns(".DS_Store", "*.py", "__pycache__"),
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
        ("experience.html", "experience.html", "Experience & Skills | Alex Redshaw", "experience", "Alex Redshaw's experience in data science, machine learning and data engineering, alongside technical skills, education and certifications.", False),
        ("projects.html", "projects.html", "Data Science & Machine Learning Projects | Alex Redshaw", "projects", "Explore Alex Redshaw's projects in football analytics, FPL forecasting, applied machine learning and software engineering, with demos and case studies.", False),
        ("blog.html", "blog.html", "Journal | Alex Redshaw", "blog", "Articles by Alex Redshaw on sports analytics, Fantasy Premier League optimisation, probabilistic modelling and practical data science.", False),
        ("post.html", "legacy-post.html", "Journal | Alex Redshaw", "blog", "Find Alex Redshaw's articles at their new addresses.", True),
        ("404.html", "404.html", "Page Not Found | Alex Redshaw", "", "This page could not be found. Explore Alex Redshaw's projects or return to the homepage.", True),
    ):
        write_page(filename, template, title, active, description, noindex=noindex)
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
                f"{entry['title']} | {context['site']['name']}", section,
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
    build()
