"""Extract 1024-unit SVG outlines for a set of CJK codepoints from Noto Serif CJK.

Writes one SVG per codepoint into data/reference/noto/. These outlines are the
reference imagery for the digitiser: a human uses them to cut the glyph into
ordered strokes. The outlines are *not* per-stroke data.

Usage:
    python -m tools.scripts.extract_noto_outline \\
        --font /path/to/NotoSerifCJKsc-Regular.otf \\
        --codepoint U+30EDE U+30EDD U+4E09

The font is not vendored; pass the path explicitly or set NOTO_FONT env var.
Noto CJK: https://github.com/notofonts/noto-cjk
Licence: SIL OFL 1.1.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def parse_codepoint(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("u+"):
        return int(s[2:], 16)
    if s.startswith("0x"):
        return int(s, 16)
    return int(s)


def extract(font_path: Path, codepoint: int, out_path: Path, canvas: int = 1024) -> None:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen

    font = TTFont(str(font_path))
    cmap = font.getBestCmap()
    glyph_name = cmap.get(codepoint)
    if glyph_name is None:
        raise SystemExit(f"codepoint U+{codepoint:04X} not present in {font_path}")
    glyph_set = font.getGlyphSet()
    glyph = glyph_set[glyph_name]

    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_d = pen.getCommands()

    units_per_em = font["head"].unitsPerEm
    ascender = font["OS/2"].sTypoAscender
    scale = canvas / units_per_em
    # Flip Y (SVG Y grows down; font Y grows up) and shift the glyph down by the ascender.
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas} {canvas}" '
        f'width="{canvas}" height="{canvas}">\n'
        f'  <g transform="translate(0 {ascender * scale:.3f}) scale({scale:.6f} -{scale:.6f})">\n'
        f'    <path d="{path_d}" fill="#111" stroke="none"/>\n'
        '  </g>\n'
        '</svg>\n'
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    print(f"wrote {out_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--font",
        default=os.environ.get("NOTO_FONT"),
        help="Path to Noto Serif CJK font (.otf/.ttc). Env: NOTO_FONT.",
    )
    parser.add_argument(
        "--codepoint",
        nargs="+",
        required=True,
        help="One or more codepoints (e.g. U+30EDE, U+30EDD, U+4E09)",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Destination directory (default: data/reference/noto/)",
    )
    parser.add_argument("--canvas", type=int, default=1024)
    args = parser.parse_args(argv)

    if not args.font:
        sys.exit(
            "Provide --font or set NOTO_FONT. Download Noto Serif CJK from\n"
            "  https://github.com/notofonts/noto-cjk\n"
            "and choose a weight (e.g. NotoSerifCJKsc-Regular.otf)."
        )
    font_path = Path(args.font).expanduser()
    if not font_path.is_file():
        sys.exit(f"font not found: {font_path}")

    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        from seebiang.io import data_root

        out_dir = data_root() / "reference" / "noto"

    for cp_str in args.codepoint:
        cp = parse_codepoint(cp_str)
        out_path = out_dir / f"U+{cp:04X}.svg"
        extract(font_path, cp, out_path, canvas=args.canvas)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
