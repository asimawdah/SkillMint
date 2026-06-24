from __future__ import annotations

import json

from skillmint.detectors import detect


def detection_ids(root):
    return {item.id for item in detect(root)}


def test_detects_node_project_from_lockfile_without_package_json(tmp_path):
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")

    ids = detection_ids(tmp_path)

    assert "node" in ids


def test_invalid_package_json_does_not_crash_detection(tmp_path):
    (tmp_path / "package.json").write_text("{ invalid json", encoding="utf-8")

    ids = detection_ids(tmp_path)

    assert ids == set()


def test_detects_react_from_package_dependencies(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^19.0.0"}}),
        encoding="utf-8",
    )

    ids = detection_ids(tmp_path)

    assert "node" in ids
    assert "react" in ids
