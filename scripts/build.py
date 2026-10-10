from datetime import date
import math
from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlsplit

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
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(exist_ok=True)
    for directory in ("assets", "css", "js", ".well-known"):
        shutil.copytree(
            ROOT / directory, OUTPUT / directory,
            ignore=shutil.ignore_patterns(".DS_Store", "*.py", "__pycache__"),
        )
    shutil.copy2(ROOT / "CNAME", OUTPUT / "CNAME")

    def write_page(filename, template, title, active, **page_context):
        html = environment.get_template(template).render(
            **context, title=title, active=active, **page_context
        )
        destination = OUTPUT / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding="utf-8")

    for filename, template, title, active in (
        ("index.html", "home.html", "Alex Redshaw - Data Science & Machine Learning Professional", "home"),
        ("experience.html", "experience.html", "Experience - Alex Redshaw", "experience"),
        ("projects.html", "projects.html", "Projects - Alex Redshaw", "projects"),
        ("blog.html", "blog.html", "Journal | Alex Redshaw", "blog"),
        ("post.html", "legacy-post.html", "Journal | Alex Redshaw", "blog"),
        ("404.html", "404.html", "Page Not Found | Alex Redshaw", ""),
    ):
        write_page(filename, template, title, active)
    for section, entries in (("projects", projects), ("blog", posts)):
        for entry in entries:
            write_page(
                f"{section}/{entry['slug']}/index.html", "detail.html",
                f"{entry['title']} | {context['site']['name']}", section,
                entry=entry, section=section,
            )
    print(f"Built {len(projects)} projects and {len(posts)} articles in {OUTPUT}")


if __name__ == "__main__":
    build()
