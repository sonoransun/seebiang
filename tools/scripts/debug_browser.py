"""One-shot browser smoke test: open the preview, dump console errors and DOM."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
WEB = REPO / "web"


def main() -> int:
    subprocess.check_call(["npm", "run", "build", "--silent"], cwd=WEB)
    proc = subprocess.Popen(
        ["npm", "run", "preview", "--silent", "--", "--port", "4173", "--strictPort"],
        cwd=WEB,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 20
    import urllib.request

    while time.time() < deadline:
        try:
            urllib.request.urlopen("http://localhost:4173/", timeout=1).read()
            break
        except Exception:
            time.sleep(0.3)
    else:
        proc.kill()
        print("preview never up", file=sys.stderr)
        return 1

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 640, "height": 900}, reduced_motion="reduce")
            page = ctx.new_page()
            page.on("console", lambda msg: print(f"[console.{msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: print(f"[pageerror] {err}"))
            page.goto("http://localhost:4173/#/variant/toy-trio", wait_until="networkidle")
            page.wait_for_timeout(500)
            html = page.evaluate("() => document.getElementById('app').outerHTML.slice(0, 2000)")
            print("--- app DOM (first 2000 chars) ---")
            print(html)
            svg_count = page.evaluate("() => document.querySelectorAll('svg').length")
            path_count = page.evaluate("() => document.querySelectorAll('svg path').length")
            print(f"svg count: {svg_count}")
            print(f"path count: {path_count}")
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
