"""Generate outputs/index.html — a contact sheet listing every rendered variant."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Iterable

from .io import Character, iter_characters


def write_index(out_dir: Path, characters: Iterable[Character] | None = None) -> Path:
    chars = list(characters if characters is not None else iter_characters())
    out_path = out_dir / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cards: list[str] = []
    for c in chars:
        png = out_dir / "png" / f"{c.id}.png"
        gif = out_dir / "gif" / f"{c.id}.gif"
        apng = out_dir / "apng" / f"{c.id}.png"
        pieces: list[str] = []
        if png.is_file():
            pieces.append(f'<img src="png/{c.id}.png" alt="{html.escape(c.variant_name)} (static)" loading="lazy" />')
        if gif.is_file():
            pieces.append(f'<img src="gif/{c.id}.gif" alt="{html.escape(c.variant_name)} (animated)" loading="lazy" />')
        if not pieces:
            pieces.append('<p class="missing">No render yet. Run <code>seebiang render all</code>.</p>')
        apng_note = f' · <a href="apng/{c.id}.png">APNG</a>' if apng.is_file() else ""

        src = c.source
        attribution = html.escape(src.attribution or src.author or src.kind)
        cards.append(
            f'''<article class="card">
              <header>
                <h2>{html.escape(c.variant_name)}</h2>
                <p class="meta">
                  <code>{html.escape(c.id)}</code> ·
                  {html.escape(c.codepoint or "(no codepoint)")} ·
                  {c.stroke_count} strokes
                </p>
              </header>
              <div class="previews">{"".join(pieces)}</div>
              <footer>
                <p class="attribution">
                  Source: {html.escape(src.kind)} · Licence: {html.escape(src.license)}{apng_note}
                  <br/><small>{attribution}</small>
                </p>
              </footer>
            </article>'''
        )

    style = """
    body { font-family: system-ui, sans-serif; background: #fafaf7; color: #161614; margin: 0; padding: 2rem; }
    h1 { margin: 0 0 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.25rem; }
    .card { background: #fff; border: 1px solid #d8d6cf; border-radius: 10px; padding: 1rem; }
    .card h2 { margin: 0 0 0.25rem; font-size: 1.1rem; }
    .meta { color: #65635c; margin: 0 0 0.75rem; font-size: 0.9rem; }
    .previews { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .previews img { width: calc(50% - 0.25rem); height: auto; background: #fff; border: 1px solid #e6e4dd; border-radius: 6px; }
    .attribution { color: #65635c; font-size: 0.85rem; margin: 0.75rem 0 0; }
    .missing { color: #b0302e; }
    """
    body = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>See Biáng! — render review</title>'
        f'<style>{style}</style></head><body>'
        f'<h1>See Biáng! — {len(chars)} variant{"" if len(chars) == 1 else "s"}</h1>'
        '<div class="grid">'
        + "".join(cards)
        + "</div></body></html>"
    )
    out_path.write_text(body, encoding="utf-8")
    return out_path
