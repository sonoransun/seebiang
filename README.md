# See Biáng!

<img src="Biáng-v1.svg" alt="BiangBiang" width="512">
<br />

Static and animated stroke-by-stroke visualisations of the Biáng character —
an unusually complex Chinese character famous for the Shaanxi noodle dish it
names — in every variant form catalogued on
<https://en.wikipedia.org/wiki/Biangbiang_noodles>.

## About the character

**Biáng** is the onomatopoeic name of a wheat-noodle dish from Shaanxi
province in northwest China — *biángbiáng miàn* (Biáng-Biáng noodles), a
specialty most closely associated with Xi'an. The syllable imitates the
*biáng, biáng* sound of the long, hand-pulled dough being slapped
rhythmically against the counter as it is stretched.

The character written for *biáng* is one of the most visually intricate
in any living writing system. The traditional form has around **58
strokes**; the simplified form retains around **42**. It does not appear
in the classical dictionaries — it is a comparatively modern coinage
thought to have been invented to match the spoken name of the dish, and
for most of its existence it was not available in digital type at all.
Local restaurants painted it on signboards; in print it was often
replaced with phonetic substitutes or left as a blank space with a
footnote. A number of folk verses exist to help people memorise the
stroke order, each enumerating the radicals and components from top to
bottom and inside to outside.

Unicode finally encoded the character in **Unicode 13.0 (2020)**:

| Form | Codepoint | Strokes (approx.) |
|---|---|---|
| Traditional | **U+30EDE** 𰻞 | 58 |
| Simplified | **U+30EDD** 𰻝 | 42 |

Both codepoints live in the Tertiary Ideographic Plane (CJK Unified
Ideographs Extension G) and have glyphs in recent releases of Noto Sans
CJK, Noto Serif CJK, and Source Han Sans.

Beyond the two Unicode-encoded forms, the Wikipedia article catalogues
a further **~20 regional, historical, and folk variants** that differ
in structure, stroke count (ranging ~56–70), and in which radicals they
assemble. This project aims to cover every one of those variants.

## What this software does

See Biáng! turns each variant of the character into a set of rendered
artefacts from a single hand-digitised stroke-data source:

| Format | Where | Use |
|---|---|---|
| **Static SVG** | inline in the web viewer, emitted from the JSON | lossless vector display at any size |
| **High-resolution PNG** | `outputs/png/<id>.png` | rasterised to any pixel size via CairoSVG — good for print, slides, embedding in READMEs |
| **Animated GIF** | `outputs/gif/<id>.gif` | stroke-by-stroke reveal at a configurable frame rate; universally supported |
| **Animated PNG (APNG)** | `outputs/apng/<id>.png` | same animation, alpha-preserving, higher fidelity than GIF where supported |
| **Interactive SVG in the browser** | `web/` viewer | play / pause / reset controls, keyboard shortcuts, honours `prefers-reduced-motion` |
| **Contact-sheet gallery** | `outputs/index.html` | one page showing every variant's static + animated render and attribution |

### How the animation works

Each variant is stored as an ordered list of strokes on a 1024×1024
canvas (matching the Make Me A Hanzi convention). Every stroke has an
SVG path and an optional duration. Both renderers animate by setting
`stroke-dasharray`/`stroke-dashoffset` on each path — so a stroke is
"drawn" along its centreline over time — and a cross-pipeline parity
test pixel-compares the final frame between the browser and the Python
renderer to keep them identical.

### How variants are covered

- **The two Unicode forms (U+30EDE, U+30EDD)** are digitised from Noto
  Serif CJK glyph outlines. An included extractor
  (`tools/scripts/extract_noto_outline.py`) renders any codepoint from
  any Noto CJK OTF to a 1024-unit SVG for tracing.
- **The non-Unicode variants** are digitised from Wikimedia Commons
  SVGs. Each reference file carries a sibling `.attribution.yaml` with
  `source_url`, `author`, `licence`, and retrieval date; the derived
  character JSON inherits the provenance.

A browser-based stroke tracer at `tools/digitize/` loads a reference as
faint background and lets a human drag strokes in canonical order,
exporting schema-compliant JSON with one click. Stroke order is
cross-checked against Wiktionary / Unihan for the Unicode forms and
against the Wikipedia caption for the non-Unicode ones.

## What's in the repo today

- **Shared JSON data format** — `data/schema/character.schema.json`,
  validated by both pipelines. A 3-stroke fixture (`toy-trio.json`, the
  numeral 三) exercises the pipeline end-to-end.
- **Python export pipeline** (`py/seebiang/`) — `seebiang validate |
  ls | render png|gif|apng|all | review`. CairoSVG + Pillow + imageio.
- **Web viewer** (`web/`) — Vite + vanilla TypeScript. Gallery +
  per-variant detail with RAF-driven animation.
- **Stroke tracer** (`tools/digitize/`) — standalone Vite app for
  hand-digitisation.
- **Noto outline extractor** — pulls any codepoint's filled outline
  from a Noto CJK OTF for use as tracer reference imagery.
- **14 tests** including a headless-Chromium parity test that
  pixel-compares the web and Python renderers on the toy fixture.

## Quick start

```sh
# Python pipeline
python3 -m venv .venv
.venv/bin/pip install -e py/
.venv/bin/seebiang validate
.venv/bin/seebiang render all --size 1024 --fps 30
open outputs/index.html

# Web viewer
cd web
npm install
npm run sync-data && npm run dev    # http://localhost:5173/

# Stroke tracer
cd tools/digitize
npm install
npm run dev                         # http://localhost:5174/
```

## Adding a new variant

1. Obtain a reference image:
   - **Unicode forms**: download Noto Serif CJK from
     <https://github.com/notofonts/noto-cjk>, then
     ```sh
     python3 tools/scripts/extract_noto_outline.py \
       --font path/to/NotoSerifCJKsc-Regular.otf \
       --codepoint U+30EDE U+30EDD
     ```
   - **Non-Unicode variants**: save the SVG from Wikimedia Commons into
     `data/reference/wikimedia/` with a sibling `.attribution.yaml`
     recording `source_url`, `author`, `license`, `retrieved_on`.
2. Launch the tracer (`cd tools/digitize && npm run dev`). Paste the
   reference path into the input box, load it, then drag strokes in
   canonical order. Cross-check ordering against Wiktionary / Unihan.
3. Click **Export JSON**. Paste the result into
   `data/characters/<id>.json`. Fill in `source`, `variantName`,
   `description`.
4. Add an entry to `data/characters/index.json` and a row to
   `ATTRIBUTIONS.md`.
5. Run `.venv/bin/seebiang validate` to check the schema, stroke count,
   and path parsing.

## Licensing

- **Code** (everything outside `data/`): MIT (`LICENSE-CODE`).
- **Data** (`data/`): each file declares its own `source.license`.
  Files derived from Wikimedia Commons are CC-BY-SA-4.0; Noto-derived
  outline data is OFL-1.1; hand-crafted fixtures are CC0-1.0
  (`LICENSE-DATA`).

See `ATTRIBUTIONS.md` for per-file provenance.
