# Data Scientist Portfolio Template

A clean, minimalist, and responsive portfolio website designed for Data Scientists and Engineers. Built with pure HTML, CSS (Tailwind), and vanilla JavaScript. No build steps required.

## Features

- **YAML-driven Content**: Update your site info, skills, projects, and blog posts by simply editing `.yaml` files.
- **Markdown Support**: Write detailed project descriptions and blog posts in Markdown, rendered dynamically with syntax highlighting.
- **Filtering**: Tag-based filtering for Projects and Blog posts.
- **Responsive Design**: Fully responsive layout using Tailwind CSS.
- **Zero Build Step**: Just host the static files. Works perfectly with GitHub Pages.

## Directory Structure

- `data/`: Contains YAML files for all dynamic content structure.
- `content/`: Contains Markdown files for full text content.
- `assets/`: Store your images and resume here.
- `js/`: Application logic.
- `css/`: Custom styles overriding or extending Tailwind.

## How to Customize

### 1. Personal Information
Edit `data/site.yaml` to update your name, title, bio, and social links.

### 2. Adding Projects
1. Add a new entry to `data/projects.yaml`.
2. Create a Markdown file in `content/projects/YOUR-PROJECT.md`.
3. Link the markdown file in the YAML entry.

### 3. Adding Blog Posts
1. Add a new entry to `data/blog.yaml`.
2. Create a Markdown file in `content/blog/YOUR-POST.md`.
3. Link the markdown file in the YAML entry.

### 4. Updating Skills & Experience
Edit `data/skills.yaml` and `data/experience.yaml`.

## Deployment

### GitHub Pages
1. Push this repository to GitHub.
2. Go to **Settings** > **Pages**.
3. Select `main` branch as the source.
4. Your site is live!

## Images
Please place your headshot in `assets/images/headshot.jpg` or update the path in `data/site.yaml`.
