"""Smoke tests — keep imports aligned with package __init__ (matplotlib + numpy)."""

from __future__ import annotations


def test_import_craft() -> None:
    import craft

    assert craft.__doc__
    assert "PaperSpec" in craft.__all__
