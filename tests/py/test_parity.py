"""Cross-pipeline visual parity test.

Loads the toy fixture in the web app via a preview server + headless Chromium,
screenshots the final SVG frame, and compares it pixel-for-pixel to the Python
renderer's output using pixelmatch.

Skipped if Playwright's browser binaries or the Node toolchain are missing.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WEB = REPO / "web"
VIEWPORT = 512  # must match the pixel size requested from Python


pytestmark = pytest.mark.skipif(
    shutil.which("npm") is None, reason="npm not available"
)


def _python_png(character_id: str, size: int) -> bytes:
    from seebiang.io import load_character
    from seebiang.render import build_svg
    import cairosvg

    character = load_character(character_id)
    svg = build_svg(character)
    return cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=size,
        output_height=size,
    )


def _start_preview() -> subprocess.Popen:
    # Rebuild + preview ensures the served data matches data/characters/.
    subprocess.check_call(["npm", "run", "build", "--silent"], cwd=WEB)
    proc = subprocess.Popen(
        ["npm", "run", "preview", "--silent", "--", "--port", "4173", "--strictPort"],
        cwd=WEB,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # Wait for server readiness
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            import urllib.request

            urllib.request.urlopen("http://localhost:4173/", timeout=1).read()
            return proc
        except Exception:
            time.sleep(0.3)
    proc.kill()
    raise RuntimeError("preview server never came up")


def _browser_screenshot(url: str, size: int) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:
            pytest.skip(f"chromium unavailable: {e}")
        context = browser.new_context(
            viewport={"width": size, "height": size},
            device_scale_factor=1,
            reduced_motion="reduce",  # force final-frame render
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        # Wait for the animator to install the final-frame SVG.
        page.wait_for_selector("svg path[data-stroke-index]")
        page.wait_for_timeout(400)
        elt = page.locator("section.stage svg")
        shot = elt.screenshot(omit_background=True)
        browser.close()
        return shot


def _compare(a: bytes, b: bytes, tolerance: float = 0.06) -> float:
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch

    img_a = Image.open(io.BytesIO(a)).convert("RGBA")
    img_b = Image.open(io.BytesIO(b)).convert("RGBA")
    if img_a.size != img_b.size:
        img_b = img_b.resize(img_a.size, Image.LANCZOS)
    diff = Image.new("RGBA", img_a.size)
    mismatched = pixelmatch(img_a, img_b, diff, threshold=0.2)
    ratio = mismatched / (img_a.size[0] * img_a.size[1])
    assert ratio < tolerance, f"pixel mismatch ratio {ratio:.4f} exceeds {tolerance}"
    return ratio


def test_toy_trio_parity_final_frame(tmp_path: Path):
    proc = _start_preview()
    try:
        shot = _browser_screenshot(
            "http://localhost:4173/#/variant/toy-trio", VIEWPORT
        )
        py = _python_png("toy-trio", VIEWPORT)
        (tmp_path / "web.png").write_bytes(shot)
        (tmp_path / "py.png").write_bytes(py)
        _compare(shot, py)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
