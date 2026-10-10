# Alex Redshaw's portfolio

Personal portfolio at [atredshaw.com](https://atredshaw.com/). Python renders YAML and Markdown into complete HTML pages; Tailwind compiles the existing theme into static CSS. JavaScript enhances navigation, tag filters, maths, code highlighting and image enlargement. Core content and links work without it.

This repository originally used `cotes2020/chirpy-starter`. It is now a standalone implementation with no Chirpy runtime dependency.

## Build and preview

Requires Python 3.10+ and Node.js 20+. GitHub Actions builds with Python 3.13 and Node.js 24. The compiled Tailwind 4 styles target modern browsers (Safari 16.4+, Chrome 111+, Firefox 128+).

In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm ci --ignore-scripts
npm run build
python -m unittest discover -s tests -v
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`; the remaining commands are the same.

Open `http://127.0.0.1:8000/`. Serve `dist/`, not the repository root. Rebuild after editing content, templates, scripts or styles. `npm run build` recreates `dist/`, compiles the stylesheet and checks local links, assets, metadata, sitemap coverage and deployment files. Generated files are not committed.

## Editing content

| Location | Purpose |
| --- | --- |
| `data/site.yaml` | Name, professional descriptor, introduction, biography, headshot and profile links |
| `data/experience.yaml`, `data/skills.yaml` | Experience, qualifications and skills |
| `data/projects.yaml` | Project summaries, stable slugs, thumbnails, demo/code links and homepage selection |
| `data/blog.yaml` | Article titles, stable slugs, dates, excerpts and social preview images |
| `content/projects/`, `content/blog/` | Full Markdown write-ups; begin section headings at `##`, since the template supplies the page title |
| `templates/` | Shared layout and page templates |
| `css/custom.css`, `tailwind.config.js` | Custom styles and the existing theme |
| `js/main.js` | Optional browser interactions |
| `CNAME` | Custom domain; also supplies the hostname for canonicals, structured data and sitemap URLs |

To add a project, add its YAML entry and Markdown file. Set a unique lowercase hyphenated `slug`, such as `xlthm`; the page is generated at `/projects/xlthm/`. Set `featured: true` to include it among the homepage selections. Keep the selection small.

Existing projects retain `legacy_slug`, the old title-derived `?project=` identifier. Preserve those values when changing titles. For a new project, `legacy_slug` can match its `slug`.

To add an article, add its YAML entry and Markdown file, with a unique `slug`, an ISO publication date (`YYYY-MM-DD`), excerpt, tags and a local `image` path for link previews. Its page is generated at `/blog/<slug>/`. An optional `updated` date is used in article structured data; change it only for a real substantive update. Keep publication dates accurate.

Keep published slugs stable. Existing `post.html?id=<slug>` and `projects.html?project=<legacy_slug>` links route to the generated documents using a small browser redirect. Without JavaScript, the old pages provide normal links to the write-ups. These compatibility redirects are not HTTP 301 redirects; a hosting layer with redirect support would be needed for those.

Use root-relative local links and images in Markdown, such as `/assets/images/projects/xlthm/pipeline.png`. Existing `assets/...` references and recognised old article/project links are normalised during the build. Tables, fenced code and `$...$` / `$$...$$` maths are supported; without JavaScript, maths remains readable as TeX.

Jinja escapes YAML text; Markdown is trusted, repository-authored content and may contain HTML. Assets, CSS, JavaScript, `CNAME`, `.nojekyll`, crawler files and `.well-known/assetlinks.json` are included in the deployment. Source YAML, Markdown, build scripts, tests and `local-docs/` are excluded. Python files and `.DS_Store` files inside assets are excluded too.

## Publishing

`.github/workflows/pages.yml` builds and checks pull requests targeting `main`. Pushes to `main` also deploy the verified `dist/` artifact to GitHub Pages. A manual workflow run on another branch builds without deploying it. Hidden deployment files are included so `.well-known/assetlinks.json` survives packaging.

For the first deployment:

1. Push this branch and open a pull request to `main`; review the build and regression checks.
2. Coordinate switching **Settings → Pages → Build and deployment → Source** to **GitHub Actions** with merging the pull request. The new source layout requires the build workflow; publishing the raw branch will not produce the site.
3. Keep the custom domain set to `atredshaw.com` and HTTPS enabled. Merge once checks pass, then watch the build and deploy jobs finish.
4. Check the homepage, a project and an article directly, plus `/sitemap.xml`, `/robots.txt` and `/.well-known/assetlinks.json`. Test an old shared link too. Confirm `www` and the GitHub hostname resolve or redirect to the intended domain.

The workflow has been prepared for GitHub Pages; local checks do not verify account settings, DNS or the first hosted deployment. [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## After deployment

1. Verify a Search Console Domain property for `atredshaw.com`, then submit `https://atredshaw.com/sitemap.xml`.
2. Inspect the homepage, `/projects/xlthm/` and a blog article. Check Google's rendered text and selected canonical, then request indexing for the key pages after the migration. Validate the profile/article markup with Google's Rich Results Test.
3. Align GitHub and LinkedIn with the same name, headshot and professional descriptor. Link both to the homepage, and feature the selected case studies. Add a short author link from public project READMEs and project apps where useful.
4. Share useful write-ups with relevant communities, keep demos and results current, and seek relevant independent references to the work.
5. Review name-search impressions, clicks and average position monthly. Search Console covers this domain, so separately sample which first-page results identify you across the website, LinkedIn and GitHub.

Titles, descriptions, canonical URLs, person/author structured data and social previews are rendered into each page. The sitemap includes the 15 current indexable pages; the compatibility post shell and 404 page are excluded and marked `noindex`. No modification dates are invented for the sitemap. These changes improve access and identity signals, but cannot guarantee indexing, rich results or first place for a name search.
