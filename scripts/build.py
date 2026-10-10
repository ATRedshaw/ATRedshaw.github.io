from datetime import date
from pathlib import Path
import shutil

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"


def load_data(filename):
    return yaml.safe_load((ROOT / "data" / filename).read_text(encoding="utf-8"))


def build():
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    context = {
        "site": load_data("site.yaml"),
        "skills": load_data("skills.yaml")["categories"],
        "experience": load_data("experience.yaml")["entries"],
        "year": date.today().year,
    }
    OUTPUT.mkdir(exist_ok=True)
    for directory in ("assets", "css", "js", "data", "content", ".well-known"):
        shutil.copytree(ROOT / directory, OUTPUT / directory, dirs_exist_ok=True)
    shutil.copy2(ROOT / "CNAME", OUTPUT / "CNAME")
    for filename in ("projects.html", "blog.html", "post.html"):
        shutil.copy2(ROOT / filename, OUTPUT / filename)
    for filename, template, title, active in (
        ("index.html", "home.html", "Alex Redshaw - Data Science & Machine Learning Professional", "home"),
        ("experience.html", "experience.html", "Experience - Alex Redshaw", "experience"),
    ):
        html = environment.get_template(template).render(
            **context, title=title, active=active
        )
        (OUTPUT / filename).write_text(html, encoding="utf-8")
    print(f"Built site in {OUTPUT}")


if __name__ == "__main__":
    build()
