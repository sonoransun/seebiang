"""Data loading and traversal."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


DEFAULT_STROKE_DURATION_MS = 500


def data_root() -> Path:
    """Locate the repository's data/ directory relative to this package."""
    here = Path(__file__).resolve()
    for ancestor in (here, *here.parents):
        candidate = ancestor / "data" / "characters"
        if candidate.is_dir():
            return ancestor / "data"
    raise FileNotFoundError("data/ directory not found relative to package")


@dataclass(frozen=True)
class Stroke:
    index: int
    path: str
    median: tuple[tuple[float, float], ...] = ()
    radical_hint: str | None = None
    duration_ms: int = DEFAULT_STROKE_DURATION_MS


@dataclass(frozen=True)
class Source:
    kind: str
    license: str
    url: str | None = None
    author: str | None = None
    attribution: str | None = None
    retrieved: str | None = None


@dataclass(frozen=True)
class Canvas:
    width: int
    height: int


@dataclass(frozen=True)
class Character:
    id: str
    variant_name: str
    source: Source
    canvas: Canvas
    stroke_count: int
    strokes: tuple[Stroke, ...]
    schema_version: int = 1
    codepoint: str | None = None
    description: str = ""
    raw: dict = field(default_factory=dict, repr=False, compare=False)


def _stroke_from_dict(d: dict) -> Stroke:
    return Stroke(
        index=d["index"],
        path=d["path"],
        median=tuple(tuple(p) for p in d.get("median", [])),
        radical_hint=d.get("radicalHint"),
        duration_ms=d.get("durationMs", DEFAULT_STROKE_DURATION_MS),
    )


def character_from_dict(d: dict) -> Character:
    return Character(
        id=d["id"],
        variant_name=d["variantName"],
        source=Source(**{k: v for k, v in d["source"].items()}),
        canvas=Canvas(width=d["canvas"]["width"], height=d["canvas"]["height"]),
        stroke_count=d["strokeCount"],
        strokes=tuple(_stroke_from_dict(s) for s in d["strokes"]),
        schema_version=d["schemaVersion"],
        codepoint=d.get("codepoint"),
        description=d.get("description", ""),
        raw=d,
    )


def load_character(path_or_id: str | Path) -> Character:
    """Load a character by absolute path, relative path, or id."""
    p = Path(path_or_id)
    if not p.is_file():
        p = data_root() / "characters" / f"{path_or_id}.json"
    with p.open("r", encoding="utf-8") as f:
        return character_from_dict(json.load(f))


def iter_characters(root: Path | None = None) -> Iterator[Character]:
    """Yield every character JSON under data/characters/."""
    base = (root or data_root()) / "characters"
    for path in sorted(base.glob("*.json")):
        if path.name == "index.json":
            continue
        yield load_character(path)
