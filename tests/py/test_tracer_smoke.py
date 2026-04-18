"""Smoke-test the digitizer Vite app: build, preview, verify DOM + no JS errors."""

from __future__ import annotations

import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TRACER = REPO / "tools" / "digitize"


pytestmark = pytest.mark.skipif(
    shutil.which("npm") is None, reason="npm not available"
)


def _preview_up(port: int) -> subprocess.Popen:
    subprocess.check_call(["npm", "run", "build", "--silent"], cwd=TRACER)
    proc = subprocess.Popen(
        ["npm", "run", "preview", "--silent", "--", "--port", str(port), "--strictPort"],
        cwd=TRACER,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/", timeout=1).read()
            return proc
        except Exception:
            time.sleep(0.3)
    proc.kill()
    raise RuntimeError("preview server never came up")


def test_tracer_loads_without_errors():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")
    proc = _preview_up(4174)
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as e:
                pytest.skip(f"chromium unavailable: {e}")
            ctx = browser.new_context(viewport={"width": 1200, "height": 800})
            page = ctx.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto("http://localhost:4174/", wait_until="networkidle")
            page.wait_for_selector("#canvas", state="attached")
            page.wait_for_selector("#stroke-list", state="attached")
            assert errors == [], f"page errors: {errors}"

            # Simulate a pointer drag to check that the tracer adds a stroke.
            box = page.locator("#canvas").bounding_box()
            assert box is not None
            start_x = box["x"] + box["width"] * 0.3
            start_y = box["y"] + box["height"] * 0.4
            end_x = box["x"] + box["width"] * 0.7
            end_y = box["y"] + box["height"] * 0.4
            page.mouse.move(start_x, start_y)
            page.mouse.down()
            steps = 10
            for i in range(1, steps + 1):
                page.mouse.move(
                    start_x + (end_x - start_x) * i / steps,
                    start_y + (end_y - start_y) * i / steps,
                )
            page.mouse.up()
            page.wait_for_timeout(100)
            count = page.evaluate(
                "() => document.querySelectorAll('#stroke-list li').length"
            )
            assert count == 1, f"expected 1 stroke committed, got {count}"
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
