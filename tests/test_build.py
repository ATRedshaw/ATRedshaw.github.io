from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import build
from scripts.check_site import Page, check_site


class BuildTests(unittest.TestCase):
    def test_reading_time_uses_words_and_rounds_up_to_at_least_one_minute(self):
        for words, minutes in ((0, 1), (1, 1), (240, 1), (241, 2), (480, 2)):
            with self.subTest(words=words):
                self.assertEqual(build.ReadingTime("word " * words).minutes, minutes)

    def test_reading_time_counts_rendered_text_without_urls_or_markup(self):
        text = (
            "word " * 234
            + "\n\n## Heading\n\n[Link](https://example.com/" + "long-path/" * 200 + ")\n\n"
            + "| First | Second |\n| --- | --- |\n| Third | Fourth |\n\n"
            + "<!-- " + "comment " * 240 + " -->\n"
            + "<script>" + "script " * 240 + "</script>\n"
            + "<style>" + "style " * 240 + "</style>\n"
        )
        html = build.render_markdown(text, {}, "atredshaw.com")
        self.assertEqual(build.ReadingTime(html).words, 240)
        self.assertEqual(build.ReadingTime(html).minutes, 1)
        html = build.render_markdown(text + "\n```text\ncode\n```", {}, "atredshaw.com")
        self.assertEqual(build.ReadingTime(html).minutes, 2)
        self.assertEqual(build.ReadingTime("<p>Don't stop &amp; re-read.</p>").words, 4)

    def test_reading_time_allows_ten_seconds_per_article_image(self):
        image = '<img src="/chart.png" alt="' + "description " * 240 + '" />'
        self.assertEqual(build.ReadingTime(image * 6).minutes, 1)
        self.assertEqual(build.ReadingTime(image * 7).minutes, 2)
        self.assertEqual(build.ReadingTime("word " * 240 + image).minutes, 2)

    def test_articles_are_discovered_from_front_matter_with_stable_slugs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "content/blog"
            folder.mkdir(parents=True)
            path = folder / "new-article.md"
            path.write_text(
                '---\ntitle: A new title\nslug: stable-address\ndate: 2026-10-10\n'
                'topic: Technology\ntags: [Python]\nexcerpt: A summary.\nimage: /assets/preview.png\n---\n\n## Article\nBody.',
                encoding="utf-8",
            )
            with patch.object(build, "ROOT", root):
                posts = build.load_posts()
            self.assertEqual(len(posts), 1)
            self.assertEqual(posts[0]["url"], "/journal/stable-address/")
            self.assertEqual(posts[0]["date"], "2026-10-10")
            self.assertEqual(posts[0]["markdown_text"], "## Article\nBody.")
            path.write_text(path.read_text(encoding="utf-8").replace("2026-10-10", "2026-02-30"), encoding="utf-8")
            with patch.object(build, "ROOT", root), self.assertRaisesRegex(ValueError, "content/blog/new-article.md: date must be a valid date"):
                build.load_posts()

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

    def test_old_blog_routes_redirect_to_journal_and_are_not_indexed(self):
        journal = (build.OUTPUT / "journal.html").read_text(encoding="utf-8")
        legacy = (build.OUTPUT / "blog.html").read_text(encoding="utf-8")
        sitemap = (build.OUTPUT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn('/journal.html', Page(journal).canonicals[0])
        self.assertIn('content="0;url=/journal.html"', legacy)
        self.assertEqual(Page(legacy).meta["og:url"], Page(journal).canonicals[0])
        self.assertIn("noindex", Page(legacy).meta["robots"])
        self.assertNotIn('/blog.html</loc>', sitemap)
        self.assertIn('/journal.html</loc>', sitemap)
        self.assertNotIn('/blog/', sitemap)
        for post in build.load_posts():
            self.assertTrue(post["url"].startswith("/journal/"))
            article = (build.OUTPUT / post["url"].strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="/journal.html"', article)
            self.assertIn(f'href="{post["url"]}"', journal)
            redirect = (build.OUTPUT / "blog" / post["slug"] / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'content="0;url={post["url"]}"', redirect)
            self.assertIn(f'href="{post["url"]}"', redirect)
            self.assertIn("noindex", Page(redirect).meta["robots"])
            self.assertEqual(Page(redirect).meta["og:url"], Page(article).canonicals[0])
            self.assertTrue(Page(article).canonicals[0].endswith(post["url"]))
            self.assertEqual(Page(article).structured_data[0]["mainEntityOfPage"], Page(article).canonicals[0])

    def test_generated_pages_do_not_link_to_old_blog_routes(self):
        for path in build.OUTPUT.rglob("*.html"):
            with self.subTest(path=path.relative_to(build.OUTPUT)):
                html = path.read_text(encoding="utf-8")
                self.assertNotIn('href="/blog/', html)
                self.assertNotIn('href="/blog.html', html)
                self.assertNotIn('href="https://atredshaw.com/blog/', html)
                self.assertNotIn('href="https://atredshaw.com/post.html', html)
                self.assertNotIn('href="https://atredshaw.github.io/post.html', html)

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
            self.assertIn('SP<span class="text-terracotta">.</span>', home)
            profile = Page(home).structured_data[0]["mainEntity"]
            self.assertEqual(profile["alternateName"], "SampleHandle")
            self.assertTrue(profile["@id"].endswith("/#stable-person"))
            for url in site["social"].values():
                self.assertGreaterEqual(home.count(f'href="{url}"'), 2)
            for filename in ("experience.html", "projects.html", "journal.html", "post.html", "404.html"):
                page = Page((output / filename).read_text(encoding="utf-8"))
                self.assertIn("Sample Person", page.title)
                self.assertIn("Sample Person", page.meta["description"])

    def test_legacy_markdown_links_use_the_configured_domain(self):
        html = build.render_markdown(
            "[Internal](https://portfolio.example/post.html?id=old) "
            "[External](https://atredshaw.com/post.html?id=old)",
            {"old": "/journal/new/"}, "portfolio.example",
        )
        self.assertIn('href="/journal/new/"', html)
        self.assertIn('href="https://atredshaw.com/post.html?id=old"', html)

    def test_every_writeup_has_a_linked_static_page_and_author(self):
        for section, entries in (("projects", build.load_data("projects.yaml")["projects"]), ("journal", build.load_posts())):
            listing = (build.OUTPUT / ("projects.html" if section == "projects" else "journal.html")).read_text(encoding="utf-8")
            for entry in entries:
                with self.subTest(slug=entry["slug"]):
                    url = f"/{section}/{entry['slug']}/"
                    self.assertIn(f'href="{url}"', listing)
                    page = (build.OUTPUT / section / entry["slug"] / "index.html").read_text(encoding="utf-8")
                    self.assertIn('data-article-body', page)
                    self.assertIn('rel="author"', page)
                    self.assertNotIn('fetch(', page)
                    self.assertEqual(Page(page).structured_data[0]["author"]["name"], build.load_data("site.yaml")["name"])

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
[Old article route](/blog/old/?view=full#results)
[Old absolute route](https://atredshaw.com/blog/old/#results)
[Old listing](https://atredshaw.com/blog.html#writing)
[External article](https://example.com/post.html?id=old)
[External blog](https://example.com/blog/old/)
"""
        html = build.render_markdown(text, {"old": "/journal/new/"}, "atredshaw.com")
        self.assertIn(r'\(x_i\)', html)
        self.assertIn(r'\frac{x_i}{y}', html)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn('&quot;$x_i$&quot;', html)
        self.assertIn('<div class="prose-table-scroll"><table>', html)
        self.assertIn('src="/assets/images/chart.png"', html)
        self.assertIn('href="/journal/new/#results"', html)
        self.assertIn('href="/journal.html#writing"', html)
        self.assertIn('href="/journal/old/?view=full#results"', html)
        self.assertIn('href="/journal/old/#results"', html)
        self.assertIn('href="https://example.com/post.html?id=old"', html)
        self.assertIn('href="https://example.com/blog/old/"', html)

    def test_duplicate_or_unsafe_slugs_fail_the_build(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "article.md").write_text("A write-up.", encoding="utf-8")
            for slugs in (("same", "same"), ("../outside",)):
                entries = [{"title": "Project", "slug": slug, "markdown": "article.md", "description": "Summary", "thumbnail": "/assets/image.png", "tags": ["Python"], "legacy_slug": f"legacy-{index}"} for index, slug in enumerate(slugs)]
                with self.subTest(slugs=slugs), patch.object(build, "ROOT", root), patch.object(build, "load_data", return_value={"projects": entries}):
                    with self.assertRaisesRegex(ValueError, "duplicate slug|slug must use lowercase"):
                        build.load_entries("projects.yaml", "projects", "projects")

    def test_missing_writeup_fails_the_build(self):
        with TemporaryDirectory() as directory:
            entries = [{"title": "Project", "slug": "missing", "markdown": "missing.md", "description": "Summary", "thumbnail": "/assets/image.png", "tags": ["Python"], "legacy_slug": "missing"}]
            with patch.object(build, "ROOT", Path(directory)), patch.object(build, "load_data", return_value={"projects": entries}):
                with self.assertRaisesRegex(ValueError, "data/projects.yaml, entry 1: Markdown file not found: missing.md"):
                    build.load_entries("projects.yaml", "projects", "projects")

    def test_invalid_article_metadata_reports_the_file_and_field(self):
        valid = {
            "source": "content/blog/example.md", "title": "Example", "slug": "example",
            "date": "2026-10-10", "topic": "Technology", "tags": ["Python"], "excerpt": "Summary",
            "image": "/assets/preview.png", "markdown_text": "## Body\nArticle.",
        }
        for field, value in (
            ("title", None), ("slug", 123), ("image", ""), ("excerpt", False),
            ("topic", None), ("series", ""), ("series_order", 0), ("series_order", True),
            ("date", "2026-02-30"), ("date", "10/10/2026"), ("date", None),
            ("tags", "Python"), ("tags", [123]), ("tags", []),
            ("updated", "2025-01-01"), ("featured", "yes"), ("markdown_text", ""),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(ValueError, "content/blog/example.md:") as error:
                    build.prepare_entries([{**valid, field: value}], "blog")
                self.assertIn("Markdown body" if field == "markdown_text" else field, str(error.exception))

    def test_topic_archives_and_series_order_come_from_article_metadata(self):
        entries = [
            {"title": "Second", "slug": "second", "source": "second.md", "date": "2025-01-01", "topic": "Theme Parks", "series": "Park Reviews", "series_order": 2, "url": "/journal/second/"},
            {"title": "First", "slug": "first", "source": "first.md", "date": "2026-01-01", "topic": "Theme Parks", "series": "Park Reviews", "series_order": 1, "url": "/journal/first/"},
            {"title": "Standalone", "slug": "standalone", "source": "standalone.md", "date": "2026-02-01", "topic": "Theme Parks", "url": "/journal/standalone/"},
        ]
        topics = build.group_posts(entries, "topic")
        series = build.group_posts(entries, "series")
        self.assertEqual(topics[0]["url"], "/journal/topics/theme-parks/")
        self.assertEqual(len(topics[0]["posts"]), 3)
        self.assertEqual(series[0]["url"], "/journal/series/park-reviews/")
        self.assertEqual([post["slug"] for post in series[0]["posts"]], ["first", "second"])
        self.assertEqual(entries[1]["series_next"]["url"], "/journal/second/")
        self.assertIsNone(entries[1]["series_previous"])
        self.assertEqual(entries[0]["series_previous"]["url"], "/journal/first/")
        self.assertNotIn("series_url", entries[2])

    def test_series_without_explicit_order_use_publication_order(self):
        entries = [
            {"title": "Newer", "slug": "newer", "source": "newer.md", "date": "2026-01-01", "topic": "Darts", "series": "Darts Analysis", "url": "/journal/newer/"},
            {"title": "Older", "slug": "older", "source": "older.md", "date": "2025-01-01", "topic": "Darts", "series": "Darts Analysis", "url": "/journal/older/"},
        ]
        group = build.group_posts(entries, "series")[0]
        self.assertEqual([post["slug"] for post in group["posts"]], ["older", "newer"])

    def test_conflicting_group_names_and_series_orders_report_the_source(self):
        entry = {"title": "First", "slug": "first", "source": "first.md", "date": "2026-01-01", "topic": "FPL", "series": "Example", "series_order": 1, "url": "/journal/first/"}
        with self.assertRaisesRegex(ValueError, "second.md: topic.*shares a URL"):
            build.group_posts([entry, {**entry, "source": "second.md", "topic": "fpl"}], "topic")
        with self.assertRaisesRegex(ValueError, "second.md: duplicate series_order"):
            build.group_posts([entry, {**entry, "source": "second.md"}], "series")

    def test_journal_group_pages_are_static_and_linked_from_articles(self):
        posts = build.load_posts()
        for field in ("topic", "series"):
            for group in build.group_posts(posts, field):
                path = build.OUTPUT / group["url"].strip("/") / "index.html"
                html = path.read_text(encoding="utf-8")
                for post in group["posts"]:
                    self.assertIn(f'href="{post["url"]}"', html)
                    article = (build.OUTPUT / post["url"].strip("/") / "index.html").read_text(encoding="utf-8")
                    self.assertIn(f'href="{group["url"]}"', article)
                if field == "series":
                    positions = [html.index(f'data-legacy-id="{post["slug"]}"') for post in group["posts"]]
                    self.assertEqual(positions, sorted(positions))

    def test_new_topics_and_optional_series_generate_without_a_separate_registry(self):
        posts = build.prepare_entries([
            {
                "source": "content/blog/park-review.md", "title": "A park review", "slug": "park-review",
                "date": "2026-10-10", "topic": "Theme Parks", "series": "Theme Park Reviews", "series_order": 1,
                "tags": ["Reviews"], "excerpt": "A day at the park.", "image": "/assets/web/icon-512.png",
                "markdown_text": "## My visit\nA review.",
            },
            {
                "source": "content/blog/park-notes.md", "title": "Some park notes", "slug": "park-notes",
                "date": "2026-10-09", "topic": "Theme Parks", "tags": ["Travel"], "excerpt": "Some notes.",
                "image": "/assets/web/icon-512.png", "markdown_text": "## Notes\nSome notes.",
            },
        ], "blog")
        with TemporaryDirectory() as directory:
            output = Path(directory)
            with patch.object(build, "OUTPUT", output), patch.object(build, "load_posts", return_value=posts):
                build.build()
            for route in ("journal/topics/theme-parks", "journal/series/theme-park-reviews"):
                self.assertTrue((output / route / "index.html").is_file())
                self.assertIn(f"/{route}/</loc>", (output / "sitemap.xml").read_text(encoding="utf-8"))
            standalone = (output / "journal/park-notes/index.html").read_text(encoding="utf-8")
            self.assertNotIn('aria-label="Series navigation"', standalone)

    def test_duplicate_article_slugs_identify_both_sources(self):
        entry = {
            "source": "content/blog/first.md", "title": "Example", "slug": "same",
            "date": "2026-10-10", "topic": "Technology", "tags": ["Python"], "excerpt": "Summary",
            "image": "/assets/preview.png", "markdown_text": "Article.",
        }
        with self.assertRaisesRegex(ValueError, "content/blog/second.md: duplicate slug 'same', also used by content/blog/first.md"):
            build.prepare_entries([entry, {**entry, "source": "content/blog/second.md"}], "blog")

    def test_invalid_yaml_reports_the_source(self):
        for text in ("title: [unfinished", "- a list", ""):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "content/blog/example.md:"):
                build.parse_yaml(text, "content/blog/example.md")

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
