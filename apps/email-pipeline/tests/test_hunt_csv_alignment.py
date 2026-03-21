"""Tests for hunt CSV id_lead alignment helpers."""

from __future__ import annotations

import csv
from pathlib import Path

from origenlab_email_pipeline.hunt_csv_alignment import (
    describe_hunt_misalignment,
    id_lead_set_from_hunt_csv,
)


def test_id_lead_set_from_hunt_csv(tmp_path: Path) -> None:
    p = tmp_path / "h.csv"
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id_lead", "x"])
        w.writeheader()
        w.writerow({"id_lead": "3", "x": "a"})
        w.writerow({"id_lead": "1", "x": "b"})
        w.writerow({"id_lead": "", "x": "c"})
    assert id_lead_set_from_hunt_csv(p) == {1, 3}


def test_describe_hunt_misalignment_none_when_equal(tmp_path: Path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    for p in (a, b):
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id_lead"])
            w.writeheader()
            w.writerow({"id_lead": "10"})
            w.writerow({"id_lead": "20"})
    assert describe_hunt_misalignment(a, b) is None


def test_describe_hunt_misalignment_message(tmp_path: Path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    with a.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id_lead"])
        w.writeheader()
        w.writerow({"id_lead": "1"})
    with b.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id_lead"])
        w.writeheader()
        w.writerow({"id_lead": "2"})
    msg = describe_hunt_misalignment(a, b)
    assert msg is not None
    assert "do not match" in msg
    assert "Only in current" in msg or "Only in merged" in msg
