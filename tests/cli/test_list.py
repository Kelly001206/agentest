import json

from agentest.cli import main


def test_list_all(capsys):
    assert main(["list"]) == 0
    assert "110 test(s)" in capsys.readouterr().out


def test_list_class_t3(capsys):
    assert main(["list", "--class", "T3", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 14 and all(r["class_id"] == "T3" for r in rows)


def test_list_bad_class():
    assert main(["list", "--class", "T9"]) == 2


def test_framework_mapping_covers_all_classes():
    from pathlib import Path

    text = (Path(__file__).resolve().parents[2] / "docs" / "FRAMEWORK-MAPPING.md").read_text()
    for c in ("T1", "T2", "T3", "T4", "T5", "T6", "T7"):
        assert f"| {c} " in text
