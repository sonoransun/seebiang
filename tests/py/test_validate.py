import json
import tempfile
from pathlib import Path

from seebiang.validate import validate_all, validate_file
from seebiang.io import data_root


def test_toy_fixture_passes():
    issues = validate_all()
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], "\n".join(i.format() for i in issues)


def test_bad_stroke_count_is_caught(tmp_path: Path):
    original = json.loads((data_root() / "characters" / "toy-trio.json").read_text())
    bad = {**original, "id": "bad-count", "strokeCount": 99}
    path = tmp_path / "bad-count.json"
    path.write_text(json.dumps(bad))
    issues = validate_file(path)
    msgs = [i.message for i in issues]
    assert any("strokeCount=99" in m for m in msgs), msgs


def test_missing_required_field_is_caught(tmp_path: Path):
    original = json.loads((data_root() / "characters" / "toy-trio.json").read_text())
    bad = {k: v for k, v in original.items() if k != "strokes"}
    bad["id"] = "no-strokes"
    path = tmp_path / "no-strokes.json"
    path.write_text(json.dumps(bad))
    issues = validate_file(path)
    assert any("schema" in i.message for i in issues)
