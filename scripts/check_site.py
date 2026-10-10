from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.title = ""
        self.title_count = 0
        self.headings = 0
        self.meta = {}
        self.canonicals = []
        self.references = []
        self.structured_data = []
        self.in_title = False
        self.in_json = False
        self.json_text = ""
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "title":
            self.in_title = True
            self.title_count += 1
        if tag == "h1":
            self.headings += 1
        if tag == "meta":
            key = attributes.get("name", attributes.get("property"))
            self.meta[key] = attributes.get("content", "")
            if key in ("og:image", "twitter:image"):
                self.references.append(attributes["content"])
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonicals.append(attributes["href"])
        if tag in ("a", "img", "link", "script"):
            for key in ("href", "src"):
                if attributes.get(key):
                    self.references.append(attributes[key])
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_json = True
            self.json_text = ""

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_json:
            self.json_text += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_json:
            self.structured_data.append(json.loads(self.json_text))
            self.in_json = False


def check_site(output=None):
    output = output or ROOT / "dist"
    domain = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    base_url = f"https://{domain}/"
    pages = {path: Page(path.read_text(encoding="utf-8")) for path in output.rglob("*.html")}
    if not pages:
        raise ValueError("No generated pages found. Run npm run build first.")

    titles = set()
    canonicals = set()
    for path, page in pages.items():
        if page.title_count != 1 or not page.title or page.headings != 1 or not page.meta.get("description"):
            raise ValueError(f"Expected one title, one main heading and a description: {path}")
        page_url = urljoin(base_url, path.relative_to(output).as_posix())
        for reference in page.references:
            parts = urlsplit(urljoin(page_url, reference))
            if parts.scheme not in ("http", "https") or parts.netloc != domain:
                continue
            target = output / unquote(parts.path).lstrip("/")
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                raise ValueError(f"Broken local link or asset in {path}: {reference}")
        if "noindex" not in page.meta.get("robots", ""):
            if len(page.canonicals) != 1 or page.canonicals[0] in canonicals or page.title in titles:
                raise ValueError(f"Missing or duplicate canonical/title: {path}")
            canonical = page.canonicals[0]
            canonical_path = output / urlsplit(canonical).path.lstrip("/")
            if canonical_path.is_dir():
                canonical_path /= "index.html"
            if not canonical.startswith(base_url) or canonical_path != path:
                raise ValueError(f"Canonical does not identify its own page: {path}")
            canonicals.add(canonical)
            titles.add(page.title)
        for item in page.structured_data:
            if item["@type"] in ("Article", "BlogPosting"):
                if item["url"] != page.canonicals[0] or item["author"]["url"] != base_url:
                    raise ValueError(f"Inconsistent article or author URL: {path}")

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap_urls = [node.text for node in ElementTree.parse(output / "sitemap.xml").iter(namespace + "loc")]
    if len(sitemap_urls) != len(canonicals) or set(sitemap_urls) != canonicals:
        raise ValueError("Sitemap must contain every indexable canonical exactly once.")
    for directory in ("data", "content", "local-docs", "templates", "scripts", "tests", ".git", ".venv", "node_modules"):
        if (output / directory).exists():
            raise ValueError(f"Source or private directory in deployment: {directory}")
    for filename in ("CNAME", ".nojekyll", ".well-known/assetlinks.json", "robots.txt"):
        if not (output / filename).is_file():
            raise ValueError(f"Missing deployment file: {filename}")
    print(f"Validated {len(pages)} HTML pages and {len(canonicals)} sitemap URLs.")


if __name__ == "__main__":
    check_site()
