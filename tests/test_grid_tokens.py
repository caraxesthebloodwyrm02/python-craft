"""Parity + invariant tests for ``craft.grid_tokens``.

The CSS under ``docs/design-system/colors_and_type.css`` is the canonical
source; this test extracts each ``--token: value;`` pair and asserts the
Python module still matches. If the CSS is updated, this test fails loudly
so the Python mirror can be re-synced.
"""
from __future__ import annotations

import re
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from craft.grid_tokens import (
    DATA_VIZ_CYCLE,
    MOTION,
    PALETTE,
    PALETTE_LIGHT,
    RADIUS,
    SPACE,
    TYPE,
    apply_matplotlib_style,
    rgba,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = REPO_ROOT / "docs" / "design-system" / "colors_and_type.css"


# ─── CSS parity ────────────────────────────────────────────────────────────────

def _extract_block(css: str, selector: str) -> str:
    """Return the body of the first ``<selector> { ... }`` rule, matched brace-wise."""
    start = css.index(selector)
    brace = css.index("{", start)
    depth = 1
    i = brace + 1
    while i < len(css) and depth > 0:
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
        i += 1
    return css[brace + 1 : i - 1]


def _parse_css_hex_tokens(block: str) -> dict[str, str]:
    """Return ``{'--amber-500': '#F59E0B', ...}`` for every bare-hex token in *block*."""
    pairs: dict[str, str] = {}
    for name, value in re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", block):
        value = value.strip()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            pairs[name] = value.upper()
    return pairs


@pytest.fixture(scope="module")
def css_text() -> str:
    assert CSS_PATH.exists(), f"missing canonical CSS at {CSS_PATH}"
    return CSS_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def css_tokens(css_text) -> dict[str, str]:
    """Bare-hex tokens from the ``:root { ... }`` (dark) block only."""
    return _parse_css_hex_tokens(_extract_block(css_text, ":root"))


@pytest.fixture(scope="module")
def css_tokens_light(css_text) -> dict[str, str]:
    """Bare-hex tokens from the ``[data-theme="light"] { ... }`` override block."""
    return _parse_css_hex_tokens(_extract_block(css_text, '[data-theme="light"]'))


# Map CSS token names → attribute name on ``PALETTE``.
_CSS_TO_ATTR: dict[str, str] = {
    "--graphite-50":  "graphite_50",
    "--graphite-100": "graphite_100",
    "--graphite-200": "graphite_200",
    "--graphite-300": "graphite_300",
    "--graphite-400": "graphite_400",
    "--graphite-500": "graphite_500",
    "--graphite-600": "graphite_600",
    "--graphite-700": "graphite_700",
    "--graphite-800": "graphite_800",
    "--graphite-900": "graphite_900",
    "--graphite-950": "graphite_950",
    "--amber-300": "amber_300",
    "--amber-400": "amber_400",
    "--amber-500": "amber_500",
    "--amber-600": "amber_600",
    "--amber-700": "amber_700",
    "--ember-600": "ember_600",
    "--ember-700": "ember_700",
    "--cyan-300":  "cyan_300",
    "--cyan-500":  "cyan_500",
    "--cyan-700":  "cyan_700",
    "--success": "success",
    "--warning": "warning",
    "--error":   "error",
    "--info":    "info",
    "--surface-card":    "surface_card",
    "--surface-raised":  "surface_raised",
    "--fg-1": "fg_1",
    "--fg-2": "fg_2",
    "--fg-3": "fg_3",
    "--fg-4": "fg_4",
    "--fg-inverse": "fg_inverse",
    "--primary-fg": "primary_fg",
}


@pytest.mark.parametrize("css_name,attr", list(_CSS_TO_ATTR.items()))
def test_palette_hex_parity_with_css(css_tokens, css_name, attr):
    """Every bare-hex token in the CSS must match ``PALETTE.<attr>`` exactly."""
    assert css_name in css_tokens, f"CSS missing expected token {css_name}"
    want = css_tokens[css_name].upper()
    got = getattr(PALETTE, attr).upper()
    assert got == want, f"{attr}: python={got} css={want}"


def test_css_has_no_unmapped_bare_hex_tokens(css_tokens):
    """Guard: if the CSS adds a new bare-hex token, this test catches it.

    Fails loudly so the Python mirror can be extended. We only assert that
    every CSS token maps into our known set — we don't require the Python
    module to expose them yet, but the mismatch must be visible.
    """
    unmapped = sorted(set(css_tokens) - set(_CSS_TO_ATTR))
    assert not unmapped, (
        f"new bare-hex tokens in CSS not yet mirrored in grid_tokens.py: {unmapped}"
    )


# ─── dataclass invariants ──────────────────────────────────────────────────────

def test_palette_is_hashable():
    hash(PALETTE)  # must not raise
    hash(PALETTE_LIGHT)


def test_palette_is_frozen():
    with pytest.raises(FrozenInstanceError):
        PALETTE.amber_500 = "#000000"  # type: ignore[misc]


def test_light_palette_overrides_bg_and_fg():
    assert PALETTE_LIGHT.bg_1 == "#FFFFFF"
    assert PALETTE_LIGHT.fg_1 == "#14141A"
    # primary stays amber in both themes
    assert PALETTE_LIGHT.primary == PALETTE.primary == "#F59E0B"


_LIGHT_OVERRIDES: dict[str, str] = {
    "--bg-0": "bg_0",
    "--bg-1": "bg_1",
    "--bg-2": "bg_2",
    "--bg-3": "bg_3",
    "--surface-card": "surface_card",
    "--surface-raised": "surface_raised",
    "--fg-1": "fg_1",
    "--fg-2": "fg_2",
    "--fg-3": "fg_3",
    "--fg-4": "fg_4",
    "--fg-inverse": "fg_inverse",
}


@pytest.mark.parametrize("css_name,attr", list(_LIGHT_OVERRIDES.items()))
def test_light_palette_parity_with_css(css_tokens_light, css_name, attr):
    """The light-theme block's hex overrides must match ``PALETTE_LIGHT``."""
    assert css_name in css_tokens_light, f"CSS light block missing {css_name}"
    want = css_tokens_light[css_name].upper()
    got = getattr(PALETTE_LIGHT, attr).upper()
    assert got == want, f"PALETTE_LIGHT.{attr}: python={got} css={want}"


def test_type_scale_values():
    assert TYPE.fs_base == 0.9375
    assert TYPE.fw_bold == 700
    assert TYPE.tracking_widest == 0.15
    assert TYPE.font_display[0] == "Space Grotesk"
    assert TYPE.font_mono[0] == "JetBrains Mono"


def test_space_is_4px_grid():
    # Every canonical stop is a multiple of 4.
    for name in ("s0", "s1", "s2", "s3", "s4", "s5", "s6", "s8",
                 "s10", "s12", "s16", "s20", "s24"):
        value = getattr(SPACE, name)
        assert value % 4 == 0, f"SPACE.{name}={value} is not a 4-px multiple"


def test_radius_and_motion_values():
    assert RADIUS.lg == 14
    assert RADIUS.full == 9999
    assert MOTION.dur_fast == 120
    assert MOTION.ease_organic == (0.34, 1.56, 0.64, 1.0)


# ─── rgba() helper ─────────────────────────────────────────────────────────────

def test_rgba_converts_amber_500():
    r, g, b, a = rgba("#F59E0B", 0.5)
    assert r == pytest.approx(245 / 255, rel=1e-6)
    assert g == pytest.approx(158 / 255, rel=1e-6)
    assert b == pytest.approx(11 / 255, rel=1e-6)
    assert a == 0.5


def test_rgba_default_alpha_is_one():
    _, _, _, a = rgba("#000000")
    assert a == 1.0


@pytest.mark.parametrize("bad", ["F59E0B", "#abc", "#1234567", "", None])
def test_rgba_rejects_bad_hex(bad):
    with pytest.raises((ValueError, TypeError)):
        rgba(bad, 1.0)  # type: ignore[arg-type]


def test_rgba_rejects_bad_alpha():
    with pytest.raises(ValueError):
        rgba("#000000", 1.5)
    with pytest.raises(ValueError):
        rgba("#000000", -0.1)


# ─── apply_matplotlib_style smoke ──────────────────────────────────────────────

def test_apply_matplotlib_style_dark():
    mpl = pytest.importorskip("matplotlib")
    pytest.importorskip("cycler")

    apply_matplotlib_style(dark=True)

    assert mpl.rcParams["axes.facecolor"].lower() == PALETTE.bg_1.lower()
    colors = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    assert colors[0].lower() == PALETTE.amber_500.lower()
    assert colors[1].lower() == PALETTE.cyan_500.lower()
    assert list(c.lower() for c in colors) == list(c.lower() for c in DATA_VIZ_CYCLE)


def test_apply_matplotlib_style_light():
    mpl = pytest.importorskip("matplotlib")
    pytest.importorskip("cycler")

    apply_matplotlib_style(dark=False)
    assert mpl.rcParams["axes.facecolor"].lower() == PALETTE_LIGHT.bg_1.lower()
    assert mpl.rcParams["text.color"].lower() == PALETTE_LIGHT.fg_1.lower()
