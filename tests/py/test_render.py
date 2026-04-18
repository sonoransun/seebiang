from pathlib import Path

from seebiang.io import load_character
from seebiang.render import build_svg, render_png, render_frames


def test_build_svg_includes_every_stroke():
    character = load_character("toy-trio")
    svg = build_svg(character)
    assert svg.startswith("<?xml")
    assert svg.count("<path") == len(character.strokes)


def test_build_svg_respects_progress():
    character = load_character("toy-trio")
    svg_empty = build_svg(character, progresses=[0, 0, 0])
    assert svg_empty.count("<path") == 0

    svg_mid = build_svg(character, progresses=[1, 0.5, 0])
    assert svg_mid.count("<path") == 2
    assert "stroke-dashoffset" in svg_mid


def test_render_png_writes_file(tmp_path: Path):
    character = load_character("toy-trio")
    out = render_png(character, size=128, out_path=tmp_path / "t.png")
    assert out.is_file()
    assert out.stat().st_size > 0
    sidecar = tmp_path / "t.png.attribution.txt"
    assert sidecar.is_file()


def test_render_frames_yields_expected_count():
    character = load_character("toy-trio")
    frames = list(render_frames(character, fps=10, size=64, tail_ms=0))
    assert len(frames) >= 10
    assert frames[0].size == (64, 64)
