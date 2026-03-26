"""Tests for scripts/update_readme.py"""
import pytest
import tempfile
import os
from datetime import date

from scripts.update_readme import last_completed_quarter, update_readme


# --- last_completed_quarter ---

@pytest.mark.parametrize("input_date,expected", [
    # Q4 of previous year
    (date(2026, 1, 1),  (4, 2025)),
    (date(2026, 3, 31), (4, 2025)),
    # Q1
    (date(2026, 4, 1),  (1, 2026)),
    (date(2026, 6, 30), (1, 2026)),
    # Q2
    (date(2026, 7, 1),  (2, 2026)),
    (date(2026, 9, 30), (2, 2026)),
    # Q3
    (date(2026, 10, 1),  (3, 2026)),
    (date(2026, 12, 31), (3, 2026)),
])
def test_last_completed_quarter(input_date, expected):
    assert last_completed_quarter(input_date) == expected


# --- update_readme ---

TEMPLATE = "The tile aggregates start in Q1 2019 and go through the most recently completed quarter **(Q4 2025)**."


def make_temp_readme(content):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_update_readme_changes_quarter(monkeypatch):
    path = make_temp_readme(TEMPLATE)
    try:
        monkeypatch.setattr("scripts.update_readme.last_completed_quarter",
                            lambda: (1, 2026))
        result = update_readme(path)
        assert result is True
        assert "**(Q1 2026)**" in open(path).read()
    finally:
        os.unlink(path)


def test_update_readme_already_current(monkeypatch):
    content = TEMPLATE.replace("Q4 2025", "Q1 2026")
    path = make_temp_readme(content)
    try:
        monkeypatch.setattr("scripts.update_readme.last_completed_quarter",
                            lambda: (1, 2026))
        result = update_readme(path)
        assert result is False
        assert "**(Q1 2026)**" in open(path).read()
    finally:
        os.unlink(path)


def test_update_readme_no_pattern():
    path = make_temp_readme("No quarter pattern here.")
    try:
        result = update_readme(path)
        assert result is False
    finally:
        os.unlink(path)


def test_update_readme_does_not_touch_other_quarters():
    content = (
        "Added in Q4 2022 dataset.\n"
        "Beginning in Q3 2023 dataset.\n"
        "Goes through **(Q4 2025)**.\n"
    )
    path = make_temp_readme(content)
    try:
        result = update_readme(path)
        updated = open(path).read()
        assert "Q4 2022" in updated
        assert "Q3 2023" in updated
    finally:
        os.unlink(path)
