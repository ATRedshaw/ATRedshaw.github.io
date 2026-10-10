from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import build
from scripts.check_site import Page, check_site


class BuildTests(unittest.TestCase):
    def test_articles_are_discovered_from_front_matter_with_stable_slugs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "content/blog"
            folder.mkdir(parents=True)
            path = folder / "new-article.md"
            path.write_text(
                '---\ntitle: A new title\nslug: stable-address\ndate: 2026-10-10\n'
                'tags: [Python]\nexcerpt: A summary.\nimage: /assets/preview.png\n---\n\n## Article\nBody.',
                encoding="utf-8",
            )
            with patch.object(build, "ROOT", root):
                posts = build.load_posts()
            self.assertEqual(len(posts), 1)
            self.assertEqual(posts[0]["url"], "/blog/stable-address/")
            self.assertEqual(posts[0]["date"], "2026-10-10")
            self.assertEqual(posts[0]["markdown_text"], "## Article\nBody.")

    def test_article_without_front_matter_identifies_its_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "content/blog"
            folder.mkdir(parents=True)
            (folder / "unfinished.md").write_text("## An unfinished article", encoding="utf-8")
            with patch.object(build, "ROOT", root), self.assertRaisesRegex(ValueError, "content/blog/unfinished.md: expected YAML front matter"):
                build.load_posts()

    def test_generated_site_links_metadata_and_public_files(self):
        check_site()

    def test_identity_and_experience_are_in_the_initial_html(self):
        home_html = (build.OUTPUT / "index.html").read_text(encoding="utf-8")
        home = unescape(home_html)
        experience = unescape((build.OUTPUT / "experience.html").read_text(encoding="utf-8"))
        site = build.load_data("site.yaml")
        for paragraph in site["about"].split("\n\n"):
            self.assertIn(paragraph, home)
        for entry in build.load_data("experience.yaml")["entries"]:
            self.assertIn(entry["description"], experience)
        profile = Page(home_html).structured_data[0]["mainEntity"]
        self.assertEqual(profile["name"], site["name"])
        self.assertEqual(profile["sameAs"], list(site["social"].values()))

    def test_identity_changes_flow_into_profile_links_and_page_metadata(self):
        load_data = build.load_data
        site = load_data("site.yaml")
        site.update(name="Sample Person", handle="SampleHandle", person_id="stable-person")
        site["social"] = {"github": "https://github.com/sample", "linkedin": "https://www.linkedin.com/in/sample/"}
        with TemporaryDirectory() as directory:
            output = Path(directory)
            with patch.object(build, "OUTPUT", output), patch.object(
                build, "load_data", side_effect=lambda filename: site if filename == "site.yaml" else load_data(filename)
            ):
                build.build()
            home = (output / "index.html").read_text(encoding="utf-8")
            profile = Page(home).structured_data[0]["mainEntity"]
            self.assertEqual(profile["alternateName"], "SampleHandle")
            self.assertTrue(profile["@id"].endswith("/#stable-person"))
            for url in site["social"].values():
                self.assertGreaterEqual(home.count(f'href="{url}"'), 2)
            for filename in ("experience.html", "projects.html", "blog.html", "post.html", "404.html"):
                page = Page((output / filename).read_text(encoding="utf-8"))
                self.assertIn("Sample Person", page.title)
                self.assertIn("Sample Person", page.meta["description"])

    def test_legacy_markdown_links_use_the_configured_domain(self):
        html = build.render_markdown(
            "[Internal](https://portfolio.example/post.html?id=old) "
            "[External](https://atredshaw.com/post.html?id=old)",
            {"old": "/blog/new/"}, "portfolio.example",
        )
        self.assertIn('href="/blog/new/"', html)
        self.assertIn('href="https://atredshaw.com/post.html?id=old"', html)

    def test_every_writeup_has_a_linked_static_page_and_author(self):
        for section, entries in (("projects", build.load_data("projects.yaml")["projects"]), ("blog", build.load_posts())):
            listing = (build.OUTPUT / f"{section}.html").read_text(encoding="utf-8")
            for entry in entries:
                with self.subTest(slug=entry["slug"]):
                    url = f"/{section}/{entry['slug']}/"
                    self.assertIn(f'href="{url}"', listing)
                    page = (build.OUTPUT / section / entry["slug"] / "index.html").read_text(encoding="utf-8")
                    self.assertIn('data-article-body', page)
                    self.assertIn('rel="author"', page)
                    self.assertNotIn('fetch(', page)
                    self.assertEqual(Page(page).structured_data[0]["author"]["name"], "Alex Redshaw")

    def test_markdown_keeps_math_code_tables_and_normalises_local_urls(self):
        text = r"""Inline $x_i$ and a display equation:

$$
p(x|y) = \frac{x_i}{y}
$$

```python
price = "$x_i$"
```

| Model | Score |
| --- | --- |
| Baseline | 0.5 |

![Chart](assets/images/chart.png)
[Old article](https://atredshaw.com/post.html?id=old#results)
[External article](https://example.com/post.html?id=old)
"""
        html = build.render_markdown(text, {"old": "/blog/new/"}, "atredshaw.com")
        self.assertIn(r'\(x_i\)', html)
        self.assertIn(r'\frac{x_i}{y}', html)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn('&quot;$x_i$&quot;', html)
        self.assertIn('<div class="prose-table-scroll"><table>', html)
        self.assertIn('src="/assets/images/chart.png"', html)
        self.assertIn('href="/blog/new/#results"', html)
        self.assertIn('href="https://example.com/post.html?id=old"', html)

    def test_duplicate_or_unsafe_slugs_fail_the_build(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "article.md").write_text("A write-up.", encoding="utf-8")
            for slugs in (("same", "same"), ("../outside",)):
                entries = [{"slug": slug, "markdown": "article.md"} for slug in slugs]
                with self.subTest(slugs=slugs), patch.object(build, "ROOT", root), patch.object(build, "load_data", return_value={"posts": entries}):
                    with self.assertRaises(ValueError):
                        build.load_entries("blog.yaml", "posts", "blog")

    def test_missing_writeup_fails_the_build(self):
        with TemporaryDirectory() as directory:
            entries = [{"slug": "missing", "markdown": "missing.md"}]
            with patch.object(build, "ROOT", Path(directory)), patch.object(build, "load_data", return_value={"posts": entries}):
                with self.assertRaises(FileNotFoundError):
                    build.load_entries("blog.yaml", "posts", "blog")

    def test_extra_title_in_content_fails_validation(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "index.html").write_text(
                '<title>Page</title><meta name="description" content="Description">'
                '<h1>Heading</h1><title>Accidental raw HTML in a write-up</title>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Expected one title"):
                check_site(output)


if __name__ == "__main__":
    unittest.main()
