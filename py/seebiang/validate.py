"""Validate character JSON files against the schema and internal invariants."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .io import data_root, load_character, iter_characters


@dataclass
class ValidationIssue:
    character_id: str
    severity: str  # "error" | "warning"
    message: str

    def format(self) -> str:
        return f"[{self.severity}] {self.character_id}: {self.message}"


def _load_schema() -> dict:
    with (data_root() / "schema" / "character.schema.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_file(path: Path, schema: dict | None = None) -> list[ValidationIssue]:
    from jsonschema import Draft202012Validator

    issues: list[ValidationIssue] = []
    schema = schema or _load_schema()
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    cid = raw.get("id", path.stem)

    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        issues.append(ValidationIssue(cid, "error", f"schema: {loc}: {err.message}"))
    if issues:
        return issues

    character = load_character(path)
    if character.stroke_count != len(character.strokes):
        issues.append(
            ValidationIssue(
                cid,
                "error",
                f"strokeCount={character.stroke_count} but strokes list has {len(character.strokes)} entries",
            )
        )
    seen_indices = set()
    for stroke in character.strokes:
        if stroke.index in seen_indices:
            issues.append(ValidationIssue(cid, "error", f"duplicate stroke index {stroke.index}"))
        seen_indices.add(stroke.index)
    expected = set(range(len(character.strokes)))
    if seen_indices != expected:
        issues.append(
            ValidationIssue(
                cid,
                "error",
                f"stroke indices must be 0..{len(character.strokes) - 1}, got {sorted(seen_indices)}",
            )
        )

    try:
        from svgpathtools import parse_path

        for stroke in character.strokes:
            try:
                parse_path(stroke.path)
            except Exception as e:  # pragma: no cover
                issues.append(
                    ValidationIssue(cid, "error", f"stroke {stroke.index}: path parse failed ({e})")
                )
    except ImportError:
        issues.append(
            ValidationIssue(cid, "warning", "svgpathtools not installed; skipping path parse check")
        )

    return issues


def validate_all() -> list[ValidationIssue]:
    schema = _load_schema()
    out: list[ValidationIssue] = []
    for path in sorted((data_root() / "characters").glob("*.json")):
        if path.name == "index.json":
            continue
        out.extend(validate_file(path, schema))
    return out


def format_issues(issues: Iterable[ValidationIssue]) -> str:
    return "\n".join(issue.format() for issue in issues)
