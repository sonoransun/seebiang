"""SVG builder and CairoSVG-based rasterisation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape as xml_escape

from .io import Character, Stroke
from .animate import progresses_at_time, frame_count, total_duration_ms


STROKE_COLOR = "#111111"
STROKE_WIDTH = 60
BACKGROUND = "#ffffff"


@lru_cache(maxsize=4096)
def _path_length(d: str) -> float:
    # svgpathtools is the workhorse for parsing and measuring SVG path data.
    from svgpathtools import parse_path

    return parse_path(d).length()


def _stroke_element(stroke: Stroke, progress: float) -> str:
    if progress <= 0.0:
        return ""
    d_attr = xml_escape(stroke.path)
    base = (
        f'<path d="{d_attr}" fill="none" stroke="{STROKE_COLOR}" '
        f'stroke-width="{STROKE_WIDTH}" stroke-linecap="round" stroke-linejoin="round"'
    )
    if progress >= 1.0:
        return base + " />"
    length = _path_length(stroke.path)
    offset = length * (1.0 - progress)
    return base + f' stroke-dasharray="{length:.3f}" stroke-dashoffset="{offset:.3f}" />'


def build_svg(character: Character, progresses: Sequence[float] | None = None) -> str:
    """Render the glyph at the given per-stroke progresses as an SVG string.

    If progresses is None, emit the final (fully-drawn) glyph.
    """
    if progresses is None:
        progresses = [1.0] * len(character.strokes)
    w, h = character.canvas.width, character.canvas.height
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
    ]
    for stroke, p in zip(character.strokes, progresses):
        elt = _stroke_element(stroke, p)
        if elt:
            parts.append(elt)
    parts.append("</svg>")
    return "\n".join(parts)


def render_png(character: Character, size: int = 2048, out_path: Path | None = None) -> Path:
    """Rasterise the final (fully-drawn) glyph to a high-resolution PNG."""
    import cairosvg

    svg = build_svg(character)
    out = out_path or (_default_outdir() / "png" / f"{character.id}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=size,
        output_height=size,
        write_to=str(out),
    )
    _write_attribution_sidecar(character, out)
    return out


def render_frames(
    character: Character,
    fps: int = 30,
    size: int = 1024,
    tail_ms: int = 600,
):
    """Generator of PIL.Image frames for the stroke-order animation."""
    import io as _io
    import cairosvg
    from PIL import Image

    total = total_duration_ms(character.strokes) + tail_ms
    n = frame_count(fps, character.strokes, tail_ms=tail_ms)
    for i in range(n):
        t_ms = (i / max(n - 1, 1)) * total
        progresses = progresses_at_time(t_ms, character.strokes)
        svg = build_svg(character, progresses)
        png_bytes = cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            output_width=size,
            output_height=size,
        )
        yield Image.open(_io.BytesIO(png_bytes)).convert("RGBA")


def _default_outdir() -> Path:
    from .io import data_root

    return data_root().parent / "outputs"


def _write_attribution_sidecar(character: Character, primary: Path) -> None:
    sidecar = primary.with_suffix(primary.suffix + ".attribution.txt")
    src = character.source
    lines = [
        f"id: {character.id}",
        f"variant: {character.variant_name}",
        f"source.kind: {src.kind}",
        f"license: {src.license}",
    ]
    if src.url:
        lines.append(f"source.url: {src.url}")
    if src.author:
        lines.append(f"author: {src.author}")
    if src.attribution:
        lines.append(f"attribution: {src.attribution}")
    sidecar.write_text("\n".join(lines) + "\n", encoding="utf-8")
