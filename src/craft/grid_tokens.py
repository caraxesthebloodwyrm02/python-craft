"""GRID design-system tokens — Python mirror of ``docs/design-system/colors_and_type.css``.

The CSS file is the canonical source. This module exposes the same palette,
type scale, spacing, radius, and motion values as immutable dataclasses so
Python renders (matplotlib figures in ``src/craft/*_render.py`` etc.) can
consume the GRID brand without drifting from the web design system.

Parity with the CSS is enforced by ``tests/test_grid_tokens.py`` — if the CSS
gains a token or changes a hex, the test fails loudly.

Public surface
--------------
- ``Palette``            dataclass holding all color tokens (dark-theme values)
- ``PALETTE``            canonical dark-theme instance
- ``PALETTE_LIGHT``      light-theme override instance
- ``TypeScale``          fonts, sizes, weights, tracking
- ``Space``              4-px-base spacing stops
- ``Radius``             corner-radius stops
- ``Motion``             durations + bezier easings
- ``TYPE`` / ``SPACE`` / ``RADIUS`` / ``MOTION`` canonical instances
- ``rgba(hex_str, alpha)`` ``'#RRGGBB' + float → (r, g, b, a)`` in [0, 1]
- ``apply_matplotlib_style(dark=True)`` set rcParams to GRID house style
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass


# ─── color ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Palette:
    """GRID color tokens. Values match ``colors_and_type.css`` verbatim.

    Dark theme is the default (the app runs dark-first). For the light-theme
    override values, use ``PALETTE_LIGHT``.
    """

    # Graphite ramp (neutrals)
    graphite_50: str = "#FAFAFC"
    graphite_100: str = "#F5F5F8"
    graphite_200: str = "#E0E0E8"
    graphite_300: str = "#BABAC8"
    graphite_400: str = "#8A8A9E"
    graphite_500: str = "#5A5A6E"
    graphite_600: str = "#3A3A4A"
    graphite_700: str = "#2A2A36"
    graphite_800: str = "#1F1F28"
    graphite_900: str = "#14141A"
    graphite_950: str = "#0A0A0F"

    # Amber / orange (primary)
    amber_300: str = "#FCD34D"
    amber_400: str = "#FBBF24"
    amber_500: str = "#F59E0B"  # primary
    amber_600: str = "#D97706"  # hover / press
    amber_700: str = "#EA580C"  # deep edge, outdoor rust

    # Ember (deep saturated orange-red, sparingly)
    ember_600: str = "#C2410C"
    ember_700: str = "#9A3412"

    # Cyan (secondary accent — data-viz glints only)
    cyan_300: str = "#66E8FF"
    cyan_500: str = "#00D9FF"
    cyan_700: str = "#0099B3"

    # Semantic
    success: str = "#059669"
    warning: str = "#D97706"
    error: str = "#DC2626"
    info: str = "#0891B2"

    # Surfaces (dark-first)
    bg_0: str = "#0A0A0F"
    bg_1: str = "#14141A"
    bg_2: str = "#1F1F28"
    bg_3: str = "#2A2A36"
    surface_card: str = "#17171F"
    surface_raised: str = "#1E1E28"
    surface_glass_rgba: tuple[float, float, float, float] = (30 / 255, 30 / 255, 40 / 255, 0.55)

    # Foreground / text
    fg_1: str = "#F5F5F8"
    fg_2: str = "#BABAC8"
    fg_3: str = "#8A8A9E"
    fg_4: str = "#5A5A6E"
    fg_inverse: str = "#14141A"

    # Borders (alpha on white over dark bg)
    border_1_rgba: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.08)
    border_2_rgba: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.12)
    border_3_rgba: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.18)
    border_amber_rgba: tuple[float, float, float, float] = (245 / 255, 158 / 255, 11 / 255, 0.35)

    # Primary / accent tokens
    primary: str = "#F59E0B"
    primary_hover: str = "#FBBF24"
    primary_press: str = "#D97706"
    primary_soft_rgba: tuple[float, float, float, float] = (245 / 255, 158 / 255, 11 / 255, 0.14)
    primary_border_rgba: tuple[float, float, float, float] = (245 / 255, 158 / 255, 11 / 255, 0.35)
    primary_fg: str = "#1A0F00"
    accent: str = "#00D9FF"
    accent_soft_rgba: tuple[float, float, float, float] = (0.0, 217 / 255, 1.0, 0.12)

    # Glows
    glow_amber_rgba: tuple[float, float, float, float] = (245 / 255, 158 / 255, 11 / 255, 0.28)
    glow_amber_strong_rgba: tuple[float, float, float, float] = (245 / 255, 158 / 255, 11 / 255, 0.45)
    glow_cyan_rgba: tuple[float, float, float, float] = (0.0, 217 / 255, 1.0, 0.25)


PALETTE: Palette = Palette()


# Light-theme override surface/fg values (from [data-theme="light"] in the CSS).
# Colors not listed here are inherited from the dark Palette unchanged.
PALETTE_LIGHT: Palette = Palette(
    bg_0="#FAFAFC",
    bg_1="#FFFFFF",
    bg_2="#F5F5F8",
    bg_3="#E0E0E8",
    surface_card="#FFFFFF",
    surface_raised="#FFFFFF",
    surface_glass_rgba=(1.0, 1.0, 1.0, 0.72),
    fg_1="#14141A",
    fg_2="#3A3A4A",
    fg_3="#5A5A6E",
    fg_4="#8A8A9E",
    fg_inverse="#FFFFFF",
    border_1_rgba=(10 / 255, 10 / 255, 15 / 255, 0.06),
    border_2_rgba=(10 / 255, 10 / 255, 15 / 255, 0.10),
    border_3_rgba=(10 / 255, 10 / 255, 15 / 255, 0.16),
)


# ─── type ───────────────────────────────────────────────────────────────────────

_SANS_FALLBACKS: tuple[str, ...] = ("DejaVu Sans", "sans-serif")
_MONO_FALLBACKS: tuple[str, ...] = ("Fira Code", "DejaVu Sans Mono", "monospace")


@dataclass(frozen=True, slots=True)
class TypeScale:
    """Typography tokens. Sizes are in rem (16-px root) to match the CSS."""

    font_display: tuple[str, ...] = field(default=("Space Grotesk",) + _SANS_FALLBACKS)
    font_body: tuple[str, ...] = field(default=("Manrope",) + _SANS_FALLBACKS)
    font_mono: tuple[str, ...] = field(default=("JetBrains Mono",) + _MONO_FALLBACKS)

    fs_xs: float = 0.75
    fs_sm: float = 0.8125
    fs_base: float = 0.9375
    fs_md: float = 1.0
    fs_lg: float = 1.125
    fs_xl: float = 1.375
    fs_2xl: float = 1.75
    fs_3xl: float = 2.25
    fs_4xl: float = 3.0
    fs_5xl: float = 4.0

    lh_tight: float = 1.1
    lh_snug: float = 1.25
    lh_normal: float = 1.5
    lh_relaxed: float = 1.7

    fw_regular: int = 400
    fw_medium: int = 500
    fw_semibold: int = 600
    fw_bold: int = 700

    tracking_tight: float = -0.02
    tracking_snug: float = -0.01
    tracking_normal: float = 0.0
    tracking_wide: float = 0.06
    tracking_widest: float = 0.15


TYPE: TypeScale = TypeScale()


# ─── spacing ────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Space:
    """4-px base grid. Pixel values."""

    s0: int = 0
    s1: int = 4
    s2: int = 8
    s3: int = 12
    s4: int = 16
    s5: int = 20
    s6: int = 24
    s8: int = 32
    s10: int = 40
    s12: int = 48
    s16: int = 64
    s20: int = 80
    s24: int = 96


SPACE: Space = Space()


# ─── radius ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Radius:
    """Corner-radius stops. Pixel values except ``full`` which is conventionally 9999."""

    sm: int = 6
    md: int = 10
    lg: int = 14
    xl: int = 20
    xl_2: int = 28
    full: int = 9999


RADIUS: Radius = Radius()


# ─── motion ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Motion:
    """Animation durations (ms) and cubic-bezier easings as 4-tuples."""

    dur_fast: int = 120
    dur_normal: int = 200
    dur_slow: int = 350
    dur_organic: int = 600

    ease_std: tuple[float, float, float, float] = (0.4, 0.0, 0.2, 1.0)
    ease_decel: tuple[float, float, float, float] = (0.0, 0.0, 0.2, 1.0)
    ease_accel: tuple[float, float, float, float] = (0.4, 0.0, 1.0, 1.0)
    ease_organic: tuple[float, float, float, float] = (0.34, 1.56, 0.64, 1.0)


MOTION: Motion = Motion()


# ─── helpers ────────────────────────────────────────────────────────────────────

def rgba(hex_str: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """Convert ``'#RRGGBB'`` to a matplotlib-friendly RGBA float tuple in [0, 1].

    >>> rgba("#F59E0B", 0.5)  # doctest: +ELLIPSIS
    (0.96..., 0.61..., 0.04..., 0.5)
    """
    if not isinstance(hex_str, str) or not hex_str.startswith("#") or len(hex_str) != 7:
        raise ValueError(f"expected '#RRGGBB', got {hex_str!r}")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")
    r = int(hex_str[1:3], 16) / 255.0
    g = int(hex_str[3:5], 16) / 255.0
    b = int(hex_str[5:7], 16) / 255.0
    return (r, g, b, float(alpha))


# Canonical data-viz color order, per README §Data viz:
# amber primary first, cyan secondary, ember for rare contrast, amber_300 for
# tonal variation within family, graphite_400 for muted reference series.
DATA_VIZ_CYCLE: tuple[str, ...] = (
    PALETTE.amber_500,
    PALETTE.cyan_500,
    PALETTE.ember_600,
    PALETTE.amber_300,
    PALETTE.graphite_400,
    PALETTE.ember_700,
)


def apply_matplotlib_style(dark: bool = True) -> None:
    """Set matplotlib ``rcParams`` to the GRID house style.

    matplotlib is imported lazily so this module is cheap to import in
    environments where matplotlib isn't installed.

    Parameters
    ----------
    dark
        If True (default), use the dark-first surfaces (``bg_1 = #14141A``,
        ``fg_1 = #F5F5F8``). If False, use the light-theme overrides.
    """
    import matplotlib as mpl
    from cycler import cycler

    p = PALETTE if dark else PALETTE_LIGHT
    # border_3 on dark bg reads as graphite_500-ish; use fg_3 for axis edges so
    # the line stays visible in both themes without relying on the rgba border.
    edge = p.fg_3
    grid = p.fg_4 if dark else p.graphite_300

    mpl.rcParams.update({
        # Figure / axes surface
        "figure.facecolor": p.bg_1,
        "figure.edgecolor": p.bg_1,
        "axes.facecolor": p.bg_1,
        "savefig.facecolor": p.bg_1,
        "savefig.edgecolor": p.bg_1,

        # Text / labels
        "text.color": p.fg_1,
        "axes.labelcolor": p.fg_2,
        "axes.titlecolor": p.fg_1,
        "xtick.color": p.fg_2,
        "ytick.color": p.fg_2,

        # Edges, spines, grid
        "axes.edgecolor": edge,
        "axes.linewidth": 1.0,
        "grid.color": grid,
        "grid.alpha": 0.35,
        "grid.linewidth": 0.5,

        # Fonts (falls back cleanly if Space Grotesk / Manrope aren't installed)
        "font.family": "sans-serif",
        "font.sans-serif": list(TYPE.font_body),
        "font.monospace": list(TYPE.font_mono),

        # Color cycle
        "axes.prop_cycle": cycler(color=list(DATA_VIZ_CYCLE)),

        # Legend blends into surface_card
        "legend.facecolor": p.surface_card,
        "legend.edgecolor": edge,
        "legend.labelcolor": p.fg_1,
    })
