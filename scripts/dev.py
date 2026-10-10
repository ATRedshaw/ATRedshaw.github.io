import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from livereload import Server
from livereload.handlers import LiveReloadHandler


ROOT = Path(__file__).resolve().parent.parent
NPM = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")


def rebuild():
    return subprocess.run([NPM, "run", "build"], cwd=ROOT).returncode == 0


def refresh():
    if rebuild():
        # Reload the whole page, including images with Windows file paths.
        LiveReloadHandler.reload_waiters(path="*")
    else:
        print("Build failed. Fix the error above and save again; the preview server is still running.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Build, serve and automatically refresh the portfolio.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if NPM is None:
        sys.exit("npm was not found. Install Node.js and run npm ci --ignore-scripts first.")
    if not rebuild():
        sys.exit(1)
    server = Server()
    server.setHeader("Cache-Control", "no-store")
    for path in (
        "content", "data", "templates", "css", "js", "assets", ".well-known",
        "scripts/build.py", "scripts/check_site.py", "tailwind.config.js", "CNAME",
    ):
        server.watch(str(ROOT / path), refresh)
    server.serve(root=str(ROOT / "dist"), host="127.0.0.1", port=args.port, live_css=False)


if __name__ == "__main__":
    main()
