"""Caraxes Fireworks — 5-layer composited GIF renderer.

Layers (bottom → top):
1. Sky gradient     — Draco Meteor base: deep blue zenith → warm horizon
2. Moonblast wash   — Sylveon's purplish lavender / baby-pink / magenta highlights
3. Volcano + eruption — dark silhouette with structured pyrotechnic bursts
4. Dragon flight    — detailed Caraxes silhouette tracing arc paths with fire trails
5. Glass refraction — full-frame generously subtle angular prismatic overlay

Output: GIF only, standalone in ``out/``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Spec dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FireworksSpec:
    width: float = 16.0
    height: float = 10.0
    resolution: int = 300
    total_frames: int = 60
    interval_ms: int = 80
    seed: int = 7


@dataclass(frozen=True)
class SkyGradientSpec:
    zenith_color: tuple[float, float, float] = (0.04, 0.06, 0.22)
    horizon_color: tuple[float, float, float] = (0.35, 0.18, 0.10)


@dataclass(frozen=True)
class MoonblastSpec:
    num_blobs: int = 18
    min_radius: float = 0.6
    max_radius: float = 2.2
    colors: tuple[str, ...] = ("#c084fc", "#f0abfc", "#f9a8d4", "#e879a8", "#d946ef")
    base_alpha: float = 0.10
    highlight_alpha: float = 0.18


@dataclass(frozen=True)
class VolcanoSpec:
    cone_base_y: float = -5.0
    cone_peak_x: float = -1.2
    cone_peak_y: float = -1.8
    cone_half_width: float = 3.8
    num_bursts: int = 45
    burst_colors: tuple[str, ...] = ("#ff6b35", "#e63946", "#fca311", "#f77f00", "#ffba08")


@dataclass(frozen=True)
class DragonSpec:
    """Detailed Caraxes silhouette parameters."""

    arc_center_x: float = 2.0
    arc_center_y: float = 2.0
    arc_radius: float = 3.5
    arc_start_deg: float = 200.0
    arc_end_deg: float = 340.0
    body_color: str = "#1a0a00"
    trail_colors: tuple[str, ...] = ("#ff6b35", "#fca311", "#e63946", "#ff006e")
    wing_span: float = 1.4
    body_length: float = 1.0


@dataclass(frozen=True)
class GlassSpec:
    num_facets: int = 14
    opacity: float = 0.20
    hue_shift_range: float = 0.08
    facet_colors: tuple[str, ...] = (
        "#a78bfa22",
        "#f0abfc1a",
        "#67e8f91a",
        "#fbbf2418",
        "#fb71851a",
    )


@dataclass(frozen=True)
class RidgeSpec:
    """Dark ridge silhouette foreground."""

    base_y: float = -5.0
    peak_y: float = -3.6
    num_points: int = 80


# ---------------------------------------------------------------------------
# Layer builders
# ---------------------------------------------------------------------------


def _build_sky_gradient(
    ax: plt.Axes,
    spec: FireworksSpec,
    sky: SkyGradientSpec,
) -> np.ndarray:
    """Vertical gradient from zenith (top) to horizon (bottom)."""
    res = spec.resolution
    gradient = np.zeros((res, res, 4), dtype=np.float64)
    for i in range(res):
        t = i / max(res - 1, 1)  # 0 = top (zenith), 1 = bottom (horizon)
        r = sky.zenith_color[0] * (1.0 - t) + sky.horizon_color[0] * t
        g = sky.zenith_color[1] * (1.0 - t) + sky.horizon_color[1] * t
        b = sky.zenith_color[2] * (1.0 - t) + sky.horizon_color[2] * t
        gradient[i, :, 0] = r
        gradient[i, :, 1] = g
        gradient[i, :, 2] = b
        gradient[i, :, 3] = 1.0
    x0 = -spec.width / 2.0
    y0 = -spec.height / 2.0
    ax.imshow(
        gradient,
        extent=[x0, x0 + spec.width, y0, y0 + spec.height],
        aspect="auto",
        zorder=0,
    )
    return gradient


def _draw_moonblast_wash(
    ax: plt.Axes,
    spec: FireworksSpec,
    moon: MoonblastSpec,
    rng: np.random.Generator,
) -> list[Any]:
    """Sparse purplish / pink highlight blobs — luminous wash not dense."""
    artists: list[Any] = []
    hw = spec.width / 2.0
    hh = spec.height / 2.0
    for _ in range(moon.num_blobs):
        cx = float(rng.uniform(-hw, hw))
        cy = float(rng.uniform(-hh * 0.2, hh))  # bias toward upper sky
        r = float(rng.uniform(moon.min_radius, moon.max_radius))
        color = moon.colors[int(rng.integers(0, len(moon.colors)))]
        alpha = float(rng.uniform(moon.base_alpha, moon.highlight_alpha))
        circle = plt.Circle((cx, cy), r, color=color, alpha=alpha, linewidth=0, zorder=1)
        ax.add_patch(circle)
        artists.append(circle)
    return artists


def _draw_volcano(
    ax: plt.Axes,
    spec: FireworksSpec,
    vol: VolcanoSpec,
    rng: np.random.Generator,
    frame: int = 0,
) -> tuple[list[Any], list[tuple[float, float, float, float, str]]]:
    """Dark cone silhouette + structured pyrotechnic particle bursts.

    Returns (static artists, burst params for animation re-use).
    """
    hw = spec.width / 2.0
    # Cone polygon
    cone_verts = [
        (vol.cone_peak_x - vol.cone_half_width, vol.cone_base_y),
        (vol.cone_peak_x, vol.cone_peak_y),
        (vol.cone_peak_x + vol.cone_half_width, vol.cone_base_y),
    ]
    cone = plt.Polygon(cone_verts, closed=True, facecolor="#0a0a0a", edgecolor="none", zorder=2)
    ax.add_patch(cone)

    # Burst particles
    burst_params: list[tuple[float, float, float, float, str]] = []
    burst_artists: list[Any] = []
    for _ in range(vol.num_bursts):
        angle = float(rng.uniform(60.0, 120.0))
        dist = float(rng.uniform(0.3, 3.0))
        rad = math.radians(angle)
        bx = vol.cone_peak_x + dist * math.cos(rad)
        by = vol.cone_peak_y + dist * math.sin(rad)
        size = float(rng.uniform(15.0, 80.0))
        color = vol.burst_colors[int(rng.integers(0, len(vol.burst_colors)))]
        burst_params.append((bx, by, size, float(rng.uniform(0.5, 1.0)), color))
        s = ax.scatter([bx], [by], s=size, c=color, alpha=0.85, linewidths=0, zorder=3)
        burst_artists.append(s)

    return [cone] + burst_artists, burst_params


def _make_dragon_silhouette_points(spec: DragonSpec, t: float) -> dict[str, np.ndarray]:
    """Generate dragon body, wing, and tail points for a position along the arc.

    ``t`` in [0, 1] is progress along the flight arc.
    """
    angle_deg = spec.arc_start_deg + t * (spec.arc_end_deg - spec.arc_start_deg)
    angle = math.radians(angle_deg)
    cx = spec.arc_center_x + spec.arc_radius * math.cos(angle)
    cy = spec.arc_center_y + spec.arc_radius * math.sin(angle)

    heading = angle + math.pi / 2.0  # perpendicular = body axis direction

    # Body: elongated diamond
    bl = spec.body_length
    body_xs = np.array(
        [
            cx + bl * math.cos(heading),
            cx + 0.25 * bl * math.cos(heading + math.pi / 2.0),
            cx - bl * math.cos(heading),
            cx + 0.25 * bl * math.cos(heading - math.pi / 2.0),
        ]
    )
    body_ys = np.array(
        [
            cy + bl * math.sin(heading),
            cy + 0.25 * bl * math.sin(heading + math.pi / 2.0),
            cy - bl * math.sin(heading),
            cy + 0.25 * bl * math.sin(heading - math.pi / 2.0),
        ]
    )

    # Wings: two triangular extensions
    ws = spec.wing_span
    wing_angle_offset = 0.45
    lwx = np.array(
        [
            cx,
            cx + ws * math.cos(heading + wing_angle_offset + math.pi / 2.0),
            cx + 0.4 * ws * math.cos(heading + wing_angle_offset + math.pi / 3.0),
        ]
    )
    lwy = np.array(
        [
            cy,
            cy + ws * math.sin(heading + wing_angle_offset + math.pi / 2.0),
            cy + 0.4 * ws * math.sin(heading + wing_angle_offset + math.pi / 3.0),
        ]
    )
    rwx = np.array(
        [
            cx,
            cx + ws * math.cos(heading - wing_angle_offset - math.pi / 2.0),
            cx + 0.4 * ws * math.cos(heading - wing_angle_offset - math.pi / 3.0),
        ]
    )
    rwy = np.array(
        [
            cy,
            cy + ws * math.sin(heading - wing_angle_offset - math.pi / 2.0),
            cy + 0.4 * ws * math.sin(heading - wing_angle_offset - math.pi / 3.0),
        ]
    )

    # Tail: trail behind body
    tail_len = bl * 1.6
    tail_xs = np.array(
        [
            cx - bl * math.cos(heading),
            cx - tail_len * math.cos(heading) + 0.15 * math.cos(heading + 0.5),
            cx - tail_len * 1.1 * math.cos(heading),
        ]
    )
    tail_ys = np.array(
        [
            cy - bl * math.sin(heading),
            cy - tail_len * math.sin(heading) + 0.15 * math.sin(heading + 0.5),
            cy - tail_len * 1.1 * math.sin(heading),
        ]
    )

    # Head: small triangle at front
    hl = bl * 0.5
    head_xs = np.array(
        [
            cx + bl * math.cos(heading),
            cx + (bl + hl) * math.cos(heading),
            cx + bl * math.cos(heading) + 0.12 * math.cos(heading + math.pi / 2.0),
        ]
    )
    head_ys = np.array(
        [
            cy + bl * math.sin(heading),
            cy + (bl + hl) * math.sin(heading),
            cy + bl * math.sin(heading) + 0.12 * math.sin(heading + math.pi / 2.0),
        ]
    )

    return {
        "center": np.array([cx, cy]),
        "body_x": body_xs,
        "body_y": body_ys,
        "lwing_x": lwx,
        "lwing_y": lwy,
        "rwing_x": rwx,
        "rwing_y": rwy,
        "tail_x": tail_xs,
        "tail_y": tail_ys,
        "head_x": head_xs,
        "head_y": head_ys,
    }


def _draw_dragon(
    ax: plt.Axes,
    dragon: DragonSpec,
    t: float,
    rng: np.random.Generator,
) -> list[Any]:
    """Draw detailed dragon silhouette with fire trail at position ``t``."""
    pts = _make_dragon_silhouette_points(dragon, t)
    artists: list[Any] = []

    # Fire trail — scatter along previous arc positions
    trail_steps = 12
    for i in range(trail_steps):
        t_trail = max(0.0, t - i * 0.015)
        angle_deg = dragon.arc_start_deg + t_trail * (dragon.arc_end_deg - dragon.arc_start_deg)
        angle = math.radians(angle_deg)
        tx = dragon.arc_center_x + dragon.arc_radius * math.cos(angle)
        ty = dragon.arc_center_y + dragon.arc_radius * math.sin(angle)
        alpha = max(0.05, 0.7 * (1.0 - i / trail_steps))
        size = max(5.0, 55.0 * (1.0 - i / trail_steps))
        color = dragon.trail_colors[i % len(dragon.trail_colors)]
        s = ax.scatter([tx], [ty], s=size, c=color, alpha=alpha, linewidths=0, zorder=4)
        artists.append(s)

    # Body
    body = plt.Polygon(
        np.column_stack([pts["body_x"], pts["body_y"]]),
        closed=True,
        facecolor=dragon.body_color,
        edgecolor="#2a0a00",
        linewidth=0.8,
        zorder=5,
    )
    ax.add_patch(body)
    artists.append(body)

    # Wings
    for wx, wy in [("lwing_x", "lwing_y"), ("rwing_x", "rwing_y")]:
        wing = plt.Polygon(
            np.column_stack([pts[wx], pts[wy]]),
            closed=True,
            facecolor="#1c0800",
            edgecolor="#3a1500",
            linewidth=0.6,
            alpha=0.92,
            zorder=5,
        )
        ax.add_patch(wing)
        artists.append(wing)

    # Tail
    tail = plt.Polygon(
        np.column_stack([pts["tail_x"], pts["tail_y"]]),
        closed=True,
        facecolor="#1a0800",
        edgecolor="none",
        alpha=0.85,
        zorder=5,
    )
    ax.add_patch(tail)
    artists.append(tail)

    # Head
    head = plt.Polygon(
        np.column_stack([pts["head_x"], pts["head_y"]]),
        closed=True,
        facecolor="#120600",
        edgecolor="#4a1a00",
        linewidth=0.5,
        zorder=5,
    )
    ax.add_patch(head)
    artists.append(head)

    # Ember breath — small scatter near head
    hx, hy = float(pts["head_x"][1]), float(pts["head_y"][1])
    for _ in range(5):
        ex = hx + float(rng.uniform(-0.25, 0.25))
        ey = hy + float(rng.uniform(-0.15, 0.25))
        ec = dragon.trail_colors[int(rng.integers(0, len(dragon.trail_colors)))]
        s = ax.scatter([ex], [ey], s=float(rng.uniform(8, 30)), c=ec, alpha=0.8, linewidths=0, zorder=6)
        artists.append(s)

    return artists


def _draw_ridge(
    ax: plt.Axes,
    spec: FireworksSpec,
    ridge: RidgeSpec,
    rng: np.random.Generator,
) -> list[Any]:
    """Dark ridge silhouette foreground."""
    hw = spec.width / 2.0
    xs = np.linspace(-hw, hw, ridge.num_points)
    ys = np.full_like(xs, ridge.peak_y)
    for i in range(len(xs)):
        ys[i] += float(rng.uniform(-0.3, 0.3))
        # Hills: two gentle humps
        ys[i] += 0.4 * math.exp(-((xs[i] + 3.0) ** 2) / 6.0)
        ys[i] += 0.55 * math.exp(-((xs[i] - 4.0) ** 2) / 8.0)

    verts = [(float(xs[0]), ridge.base_y)]
    for x, y in zip(xs, ys):
        verts.append((float(x), float(y)))
    verts.append((float(xs[-1]), ridge.base_y))

    poly = plt.Polygon(verts, closed=True, facecolor="#060606", edgecolor="none", zorder=7)
    ax.add_patch(poly)
    return [poly]


def _draw_glass_refraction(
    ax: plt.Axes,
    spec: FireworksSpec,
    glass: GlassSpec,
    rng: np.random.Generator,
) -> list[Any]:
    """Full-frame generously subtle angular prismatic overlay."""
    hw = spec.width / 2.0
    hh = spec.height / 2.0
    artists: list[Any] = []
    for _ in range(glass.num_facets):
        # Random convex quadrilateral
        cx = float(rng.uniform(-hw, hw))
        cy = float(rng.uniform(-hh, hh))
        angles = sorted(rng.uniform(0, 2 * math.pi, size=4))
        radii = rng.uniform(0.8, 3.5, size=4)
        verts = [
            (cx + float(radii[j]) * math.cos(float(angles[j])), cy + float(radii[j]) * math.sin(float(angles[j])))
            for j in range(4)
        ]
        color = glass.facet_colors[int(rng.integers(0, len(glass.facet_colors)))]
        facet = plt.Polygon(verts, closed=True, facecolor=color, edgecolor="none", alpha=glass.opacity, zorder=8)
        ax.add_patch(facet)
        artists.append(facet)
    return artists


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------


def fireworks_render(
    spec: FireworksSpec = FireworksSpec(),
    sky: SkyGradientSpec = SkyGradientSpec(),
    moon: MoonblastSpec = MoonblastSpec(),
    vol: VolcanoSpec = VolcanoSpec(),
    dragon: DragonSpec = DragonSpec(),
    glass: GlassSpec = GlassSpec(),
    ridge: RidgeSpec = RidgeSpec(),
    animation_path: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Render the 5-layer Caraxes Fireworks composition and save as GIF.

    Returns the figure and axes for further inspection or testing.
    """
    rng = np.random.default_rng(spec.seed)

    fig, ax = plt.subplots(figsize=(spec.width * 0.7, spec.height * 0.7))
    hw = spec.width / 2.0
    hh = spec.height / 2.0

    # Layer 1: Sky gradient
    _build_sky_gradient(ax, spec, sky)

    # Layer 2: Moonblast wash (static)
    _draw_moonblast_wash(ax, spec, moon, rng)

    # Frame setup
    ax.set_xlim(-hw, hw)
    ax.set_ylim(-hh, hh)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#0a0e18")
    ax.set_title("")
    fig.patch.set_facecolor("#0a0e18")
    fig.tight_layout(pad=0.2)

    if animation_path:

        def build_frame(frame: int) -> list[Any]:
            # Clear dynamic artists from previous frame
            while len(ax.patches) > 0 and hasattr(ax.patches[-1], "_fireworks_dynamic"):
                ax.patches[-1].remove()
            # Remove dynamic scatter collections
            to_remove = [c for c in ax.collections if hasattr(c, "_fireworks_dynamic")]
            for c in to_remove:
                c.remove()

            frame_rng = np.random.default_rng(spec.seed + frame * 31)
            t = frame / max(spec.total_frames - 1, 1)

            # Layer 3: Volcano + eruption (re-drawn with slight variation per frame)
            vol_artists, _ = _draw_volcano(ax, spec, vol, frame_rng, frame)
            for a in vol_artists:
                a._fireworks_dynamic = True  # type: ignore[attr-defined]

            # Layer 4: Dragon flight along arc
            dragon_artists = _draw_dragon(ax, dragon, t, frame_rng)
            for a in dragon_artists:
                a._fireworks_dynamic = True  # type: ignore[attr-defined]

            # Dark ridge foreground
            ridge_artists = _draw_ridge(ax, spec, ridge, frame_rng)
            for a in ridge_artists:
                a._fireworks_dynamic = True  # type: ignore[attr-defined]

            # Layer 5: Glass refraction (subtle shift per frame)
            glass_artists = _draw_glass_refraction(ax, spec, glass, frame_rng)
            for a in glass_artists:
                a._fireworks_dynamic = True  # type: ignore[attr-defined]

            return vol_artists + dragon_artists + ridge_artists + glass_artists

        # Pre-build first frame for static figure
        build_frame(0)

        def update(frame: int) -> list[Any]:
            return build_frame(frame)

        anim = FuncAnimation(fig, update, frames=spec.total_frames, interval=spec.interval_ms, blit=False)
        target = Path(animation_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        anim.save(target, writer="pillow", dpi=130)
    else:
        # Static frame at t=0.5 (mid-flight)
        static_rng = np.random.default_rng(spec.seed + 15 * 31)
        _draw_volcano(ax, spec, vol, static_rng, 0)
        _draw_dragon(ax, dragon, 0.5, static_rng)
        _draw_ridge(ax, spec, ridge, static_rng)
        _draw_glass_refraction(ax, spec, glass, static_rng)

    return fig, ax


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------


def demo_fireworks(
    animation_path: str = "out/caraxes_fireworks.gif",
) -> str:
    """Generate the Caraxes Fireworks GIF and return output path."""
    fig, _ax = fireworks_render(animation_path=animation_path)
    plt.close(fig)
    return animation_path


if __name__ == "__main__":
    out = demo_fireworks()
    print(f"Rendered: {out}")
