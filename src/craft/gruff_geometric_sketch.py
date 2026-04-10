from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class PaperSpec:
    width: float = 20.0
    height: float = 14.0
    spacing: float = 1.0


@dataclass(frozen=True)
class CompassSpec:
    radius: float = 4.0


@dataclass(frozen=True)
class Render360Spec:
    max_radius: float = 8.0
    cluster_radius: float = 2.5
    angle_step_deg: int = 15


@dataclass(frozen=True)
class CompassXSpec:
    y_top: float = 6.0
    y_bottom: float = 2.0
    x_anchor: float = 0.0
    diagonal_length: float = 8.0
    arc_radius: float = 3.0


@dataclass(frozen=True)
class ShiftCycleSpec:
    cycles: int = 5
    shift_x: float = 2.1
    shift_y: float = 0.28
    cluster_spread: float = 1.8
    cluster_point_radius: float = 0.45
    cluster_points: int = 18


def gruff_sketch(
    paper: PaperSpec = PaperSpec(),
    compass: CompassSpec = CompassSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Render a Gruff geometric sketch with midpoint-cut X/Y axes.

    Scope:
    - paper with grid points
    - compass circle centered at paper midpoint
    - bold dark X and Y axes cutting through full paper midpoint partition
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0

    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)

    # Paper boundary
    boundary = plt.Rectangle((x0, y0), paper.width, paper.height, fill=False, edgecolor="black", linewidth=2.0)
    ax.add_patch(boundary)

    # Grid points
    ax.scatter(gx.ravel(), gy.ravel(), s=12, c="#777777", alpha=0.7, linewidths=0)

    # Midpoint partition axes (bold + dark)
    ax.plot([x0, x1], [0.0, 0.0], color="#0a0a0a", linewidth=3.2, solid_capstyle="round")
    ax.plot([0.0, 0.0], [y0, y1], color="#0a0a0a", linewidth=3.2, solid_capstyle="round")

    # Compass: center point + radius circle
    circle = plt.Circle((0.0, 0.0), compass.radius, fill=False, edgecolor="#1b1b1b", linewidth=2.6)
    ax.add_patch(circle)
    ax.scatter([0.0], [0.0], s=42, c="#121212", zorder=5)

    ax.set_xlim(x0 - 0.6, x1 + 0.6)
    ax.set_ylim(y0 - 0.6, y1 + 0.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Gruff Geometric Sketch", fontsize=14, pad=10)

    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=180, bbox_inches="tight")

    return fig, ax


def demo(output_path: str = "out/gruff_sketch.png") -> str:
    fig, _ax = gruff_sketch(output_path=output_path)
    plt.close(fig)
    return output_path


def gruff_wide_360_render(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Map the full 360-degree scope of the central point cluster.

    Produces a wide 2-panel render:
    - Left: cartesian wide map with radial sweep lines and central cluster highlight.
    - Right: polar scope map (0..360) of cluster points by angle and distance.
    """
    fig, (ax_map, ax_polar) = plt.subplots(
        1,
        2,
        figsize=(16, 7),
        subplot_kw={"projection": None},
    )

    # Convert second axis to polar while preserving wide layout
    ax_polar.remove()
    ax_polar = fig.add_subplot(1, 2, 2, projection="polar")

    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0

    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)
    pts_x = gx.ravel()
    pts_y = gy.ravel()

    radii = np.hypot(pts_x, pts_y)
    cluster_mask = radii <= scope.cluster_radius

    # Left panel: wide cartesian map
    boundary = plt.Rectangle((x0, y0), paper.width, paper.height, fill=False, edgecolor="black", linewidth=2.0)
    ax_map.add_patch(boundary)
    ax_map.scatter(pts_x[~cluster_mask], pts_y[~cluster_mask], s=10, c="#8a8a8a", alpha=0.55, linewidths=0)
    ax_map.scatter(pts_x[cluster_mask], pts_y[cluster_mask], s=18, c="#101010", alpha=0.95, linewidths=0)

    # Midpoint partition axes (bold + dark)
    ax_map.plot([x0, x1], [0.0, 0.0], color="#050505", linewidth=3.4, solid_capstyle="round")
    ax_map.plot([0.0, 0.0], [y0, y1], color="#050505", linewidth=3.4, solid_capstyle="round")

    # 360 radial sweep lines from center
    for deg in range(0, 360, max(1, scope.angle_step_deg)):
        rad = np.deg2rad(deg)
        xe = scope.max_radius * np.cos(rad)
        ye = scope.max_radius * np.sin(rad)
        ax_map.plot([0.0, xe], [0.0, ye], color="#1f1f1f", alpha=0.22, linewidth=1.1)

    # Scope rings
    for rr, lw, alpha in [(scope.cluster_radius, 2.2, 0.9), (scope.max_radius, 1.8, 0.8)]:
        ring = plt.Circle((0.0, 0.0), rr, fill=False, edgecolor="#121212", linewidth=lw, alpha=alpha)
        ax_map.add_patch(ring)

    ax_map.set_xlim(x0 - 0.6, x1 + 0.6)
    ax_map.set_ylim(y0 - 0.6, y1 + 0.6)
    ax_map.set_aspect("equal", adjustable="box")
    ax_map.set_facecolor("white")
    ax_map.set_xticks([])
    ax_map.set_yticks([])
    ax_map.set_title("Wide Cartesian Scope", fontsize=13, pad=10)

    # Right panel: polar 360 map of cluster points
    cluster_x = pts_x[cluster_mask]
    cluster_y = pts_y[cluster_mask]
    theta = np.arctan2(cluster_y, cluster_x)
    theta = np.mod(theta, 2.0 * np.pi)
    cluster_r = np.hypot(cluster_x, cluster_y)

    ax_polar.scatter(theta, cluster_r, s=24, c="#111111", alpha=0.92)
    ax_polar.set_theta_zero_location("E")
    ax_polar.set_theta_direction(-1)
    ax_polar.set_thetagrids(np.arange(0, 360, max(1, scope.angle_step_deg)))
    ax_polar.set_rmax(scope.max_radius)
    ax_polar.grid(True, alpha=0.35)
    ax_polar.set_title("360 Polar Scope of Central Cluster", va="bottom", fontsize=13)

    fig.suptitle("Gruff 360 Cluster Map", fontsize=15, y=0.98)
    fig.tight_layout()

    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=180, bbox_inches="tight")

    return fig, (ax_map, ax_polar)


def demo_360(output_path: str = "out/gruff_360_wide.png") -> str:
    fig, _axes = gruff_wide_360_render(output_path=output_path)
    plt.close(fig)
    return output_path


def _diagonal_through(
    center: tuple[float, float], theta_deg: float, length: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    t = math.radians(theta_deg)
    dx, dy = math.cos(t), math.sin(t)
    return (center[0] - length * dx, center[1] - length * dy), (center[0] + length * dx, center[1] + length * dy)


def _line_intersection(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> tuple[float, float] | None:
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return px, py


def gruff_compass_x_contrast_render(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    cx: CompassXSpec = CompassXSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Overlay Compass-X integration attributes against the central point map.

    Left panel: baseline central map (grayscale).
    Right panel: enriched map with rails, grounding segment AB, center O, diagonals / and \\,
    compass arc, and property pins.
    """
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 7))

    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0
    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)
    pts_x = gx.ravel()
    pts_y = gy.ravel()
    radii = np.hypot(pts_x, pts_y)
    cluster_mask = radii <= scope.cluster_radius

    # Baseline panel
    base_boundary = plt.Rectangle((x0, y0), paper.width, paper.height, fill=False, edgecolor="black", linewidth=2.0)
    ax_left.add_patch(base_boundary)
    ax_left.scatter(pts_x[~cluster_mask], pts_y[~cluster_mask], s=10, c="#8a8a8a", alpha=0.55, linewidths=0)
    ax_left.scatter(pts_x[cluster_mask], pts_y[cluster_mask], s=18, c="#101010", alpha=0.95, linewidths=0)
    ax_left.plot([x0, x1], [0.0, 0.0], color="#050505", linewidth=3.4, solid_capstyle="round")
    ax_left.plot([0.0, 0.0], [y0, y1], color="#050505", linewidth=3.4, solid_capstyle="round")
    ax_left.add_patch(plt.Circle((0.0, 0.0), scope.cluster_radius, fill=False, edgecolor="#121212", linewidth=2.2))

    # Enriched panel
    rich_boundary = plt.Rectangle((x0, y0), paper.width, paper.height, fill=False, edgecolor="#111111", linewidth=2.0)
    ax_right.add_patch(rich_boundary)
    ax_right.scatter(pts_x[~cluster_mask], pts_y[~cluster_mask], s=9, c="#98a2b3", alpha=0.35, linewidths=0)
    ax_right.scatter(pts_x[cluster_mask], pts_y[cluster_mask], s=20, c="#0f172a", alpha=0.9, linewidths=0)

    # Midpoint axes retained
    ax_right.plot([x0, x1], [0.0, 0.0], color="#0b0f19", linewidth=3.6, solid_capstyle="round", label="midpoint X axis")
    ax_right.plot([0.0, 0.0], [y0, y1], color="#0b0f19", linewidth=3.6, solid_capstyle="round", label="midpoint Y axis")

    # Compass-X objects from integration doc
    y_top = cx.y_top
    y_bottom = cx.y_bottom
    a = (cx.x_anchor, y_top)
    b = (cx.x_anchor, y_bottom)
    o = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    slash = _diagonal_through(o, 45.0, cx.diagonal_length)
    backslash = _diagonal_through(o, 135.0, cx.diagonal_length)
    x_center = _line_intersection(slash[0], slash[1], backslash[0], backslash[1])

    # Rails
    ax_right.plot([x0, x1], [y_top, y_top], color="#16a34a", linewidth=2.4, label="rail top")
    ax_right.plot([x0, x1], [y_bottom, y_bottom], color="#16a34a", linewidth=2.4, label="rail bottom")
    # Grounding AB
    ax_right.plot([a[0], b[0]], [a[1], b[1]], color="#2563eb", linewidth=3.0, label="grounding AB")
    # Horizontal through O
    ax_right.plot([x0, x1], [o[1], o[1]], color="#06b6d4", linewidth=1.8, alpha=0.9, label="horizontal through O")
    # Integration X
    ax_right.plot([slash[0][0], slash[1][0]], [slash[0][1], slash[1][1]], color="#f97316", linewidth=2.8, label="/")
    ax_right.plot(
        [backslash[0][0], backslash[1][0]],
        [backslash[0][1], backslash[1][1]],
        color="#ef4444",
        linewidth=2.8,
        label="\\",
    )
    # Compass arc locus
    arc = np.linspace(0.0, math.pi, 96)
    ax_right.plot(
        o[0] + cx.arc_radius * np.cos(arc),
        o[1] + cx.arc_radius * np.sin(arc),
        color="#a855f7",
        linewidth=2.2,
        alpha=0.9,
        label="compass arc",
    )

    # Pins with properties/attributes
    ax_right.scatter(
        [a[0], b[0], o[0]], [a[1], b[1], o[1]], s=[80, 80, 95], c=["#1d4ed8", "#1d4ed8", "#b91c1c"], zorder=6
    )
    ax_right.annotate("A\n(anchor)", a, xytext=(8, 8), textcoords="offset points", fontsize=9, color="#1e3a8a")
    ax_right.annotate("B\n(anchor)", b, xytext=(8, -20), textcoords="offset points", fontsize=9, color="#1e3a8a")
    ax_right.annotate(
        "O\n(integration center)", o, xytext=(10, 10), textcoords="offset points", fontsize=9, color="#7f1d1d"
    )
    if x_center is not None:
        ax_right.scatter([x_center[0]], [x_center[1]], s=70, c="#111827", marker="x", linewidths=2.0, zorder=7)

    # Styling for both panels
    for ax in (ax_left, ax_right):
        ax.set_xlim(x0 - 0.6, x1 + 0.6)
        ax.set_ylim(y0 - 0.6, y1 + 0.6)
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor("white")
        ax.set_xticks([])
        ax.set_yticks([])

    ax_left.set_title("Current Central Point Map (Baseline)", fontsize=12)
    ax_right.set_title("Compass-X Integrated Map (Attributed)", fontsize=12)
    ax_right.legend(loc="upper right", fontsize=8, framealpha=0.95)
    fig.suptitle("Gruff Contrast: Baseline vs Compass-X Integration", fontsize=15, y=0.98)
    fig.tight_layout()

    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=180, bbox_inches="tight")

    return fig, (ax_left, ax_right)


def demo_compass_x(output_path: str = "out/gruff_compass_x_contrast.png") -> str:
    fig, _axes = gruff_compass_x_contrast_render(output_path=output_path)
    plt.close(fig)
    return output_path


def gruff_shift_cycles_render(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    cx: CompassXSpec = CompassXSpec(),
    cycle: ShiftCycleSpec = ShiftCycleSpec(),
    output_path: str | None = None,
    animation_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Run repeated integration-X cycles and render 2D+3D panes.

    Each cycle creates:
    - one integration X centered at O
    - three nearby clusters
    After 5 cycles, markings populate the graph sheet and are mirrored in a 3D pane.
    """
    fig = plt.figure(figsize=(17, 8))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")

    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0
    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)

    # Base paper and midpoint partitions
    boundary = plt.Rectangle((x0, y0), paper.width, paper.height, fill=False, edgecolor="#111111", linewidth=2.0)
    ax2d.add_patch(boundary)
    ax2d.scatter(gx.ravel(), gy.ravel(), s=8, c="#9ca3af", alpha=0.33, linewidths=0)
    ax2d.plot([x0, x1], [0.0, 0.0], color="#030712", linewidth=3.3, solid_capstyle="round")
    ax2d.plot([0.0, 0.0], [y0, y1], color="#030712", linewidth=3.3, solid_capstyle="round")
    ax2d.add_patch(plt.Circle((0.0, 0.0), scope.cluster_radius, fill=False, edgecolor="#111827", linewidth=2.0))

    cmap = plt.get_cmap("tab10")
    reveal_artists_2d: list[list[Any]] = []
    reveal_artists_3d: list[list[Any]] = []

    for i in range(cycle.cycles):
        color = cmap(i % 10)
        sx = cx.x_anchor + (i - (cycle.cycles - 1) / 2.0) * cycle.shift_x
        sy = (i - (cycle.cycles - 1) / 2.0) * cycle.shift_y

        y_top = cx.y_top + sy
        y_bottom = cx.y_bottom + sy
        a = (sx, y_top)
        b = (sx, y_bottom)
        o = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        slash = _diagonal_through(o, 45.0, cx.diagonal_length)
        backslash = _diagonal_through(o, 135.0, cx.diagonal_length)

        cycle_2d: list[object] = []
        cycle_3d: list[object] = []

        # Per-cycle rails and grounding
        cycle_2d.extend(
            [
                ax2d.plot([x0, x1], [y_top, y_top], color=color, linewidth=1.8, alpha=0.72)[0],
                ax2d.plot([x0, x1], [y_bottom, y_bottom], color=color, linewidth=1.8, alpha=0.72)[0],
                ax2d.plot([a[0], b[0]], [a[1], b[1]], color=color, linewidth=2.6, alpha=0.95)[0],
                ax2d.plot([slash[0][0], slash[1][0]], [slash[0][1], slash[1][1]], color=color, linewidth=2.4)[0],
                ax2d.plot(
                    [backslash[0][0], backslash[1][0]],
                    [backslash[0][1], backslash[1][1]],
                    color=color,
                    linewidth=2.4,
                )[0],
                ax2d.scatter([o[0]], [o[1]], s=70, c=[color], edgecolors="#111111", linewidths=0.8, zorder=6),
            ]
        )
        ax2d.annotate(f"C{i + 1}", o, xytext=(7, 6), textcoords="offset points", fontsize=8, color="#111827")

        # Three cluster centers around O
        cluster_angles = (0.0, 120.0, 240.0)
        z_level = float(i + 1)
        for j, deg in enumerate(cluster_angles, start=1):
            rad = math.radians(deg)
            cx0 = o[0] + cycle.cluster_spread * math.cos(rad)
            cy0 = o[1] + cycle.cluster_spread * math.sin(rad)

            t = np.linspace(0.0, 2.0 * math.pi, cycle.cluster_points, endpoint=False)
            px = cx0 + cycle.cluster_point_radius * np.cos(t)
            py = cy0 + cycle.cluster_point_radius * np.sin(t)
            cluster_scatter_2d = ax2d.scatter(px, py, s=14, c=[color], alpha=0.85, linewidths=0)
            cycle_2d.append(cluster_scatter_2d)
            ax2d.scatter([cx0], [cy0], s=36, c=[color], edgecolors="#0f172a", linewidths=0.7, zorder=6)

            # 3D pane points for this cluster and center
            pz = np.full_like(px, z_level)
            cluster_scatter_3d = ax3d.scatter(px, py, pz, s=12, c=[color], alpha=0.85, depthshade=True)
            center_scatter_3d = ax3d.scatter([cx0], [cy0], [z_level], s=36, c=[color], alpha=0.95, depthshade=True)
            cycle_3d.extend([cluster_scatter_3d, center_scatter_3d])

            # 2D pin label for properties
            ax2d.annotate(
                f"C{i + 1}.K{j}",
                (cx0, cy0),
                xytext=(5, -10),
                textcoords="offset points",
                fontsize=7,
                color="#1f2937",
            )

        # 3D X-lines and center pin
        xline1 = ax3d.plot(
            [slash[0][0], slash[1][0]],
            [slash[0][1], slash[1][1]],
            [z_level, z_level],
            color=color,
            linewidth=1.8,
            alpha=0.9,
        )[0]
        xline2 = ax3d.plot(
            [backslash[0][0], backslash[1][0]],
            [backslash[0][1], backslash[1][1]],
            [z_level, z_level],
            color=color,
            linewidth=1.8,
            alpha=0.9,
        )[0]
        opoint3d = ax3d.scatter([o[0]], [o[1]], [z_level], s=52, c=[color], edgecolors="#111111", linewidths=0.7)
        cycle_3d.extend([xline1, xline2, opoint3d])

        reveal_artists_2d.append(cycle_2d)
        reveal_artists_3d.append(cycle_3d)

    # 2D style
    ax2d.set_xlim(x0 - 0.6, x1 + 0.6)
    ax2d.set_ylim(y0 - 0.6, y1 + 0.6)
    ax2d.set_aspect("equal", adjustable="box")
    ax2d.set_facecolor("white")
    ax2d.set_xticks([])
    ax2d.set_yticks([])
    ax2d.set_title("Graph Sheet Pane: 5 Shift Cycles", fontsize=12)

    # 3D style
    ax3d.set_xlim(x0, x1)
    ax3d.set_ylim(y0, y1)
    ax3d.set_zlim(0.5, cycle.cycles + 0.8)
    ax3d.set_xlabel("x")
    ax3d.set_ylabel("y")
    ax3d.set_zlabel("cycle")
    ax3d.set_title("3D Pane: Integration X + 3 Clusters per Cycle", fontsize=12)
    ax3d.view_init(elev=24, azim=28)

    fig.suptitle("Gruff Shift Cycles: Marked Grid and 3D Reference", fontsize=15, y=0.98)
    fig.tight_layout()

    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=190, bbox_inches="tight")

    if animation_path:
        # Start hidden, reveal cycle-by-cycle with 3D camera spin.
        flat_artists = [artist for group in reveal_artists_2d for artist in group]
        flat_artists.extend(artist for group in reveal_artists_3d for artist in group)
        for artist in flat_artists:
            artist.set_visible(False)

        frames_per_cycle = 10
        total_frames = max(1, cycle.cycles * frames_per_cycle)

        def update(frame: int):
            shown = min(cycle.cycles - 1, frame // frames_per_cycle)
            for idx in range(cycle.cycles):
                visible = idx <= shown
                for a in reveal_artists_2d[idx]:
                    a.set_visible(visible)
                for a in reveal_artists_3d[idx]:
                    a.set_visible(visible)
            ax3d.view_init(elev=24, azim=28 + frame * 3)
            return []

        anim = FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False)
        target = Path(animation_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        anim.save(target, writer="pillow", dpi=120)

    return fig, (ax2d, ax3d)


def demo_shift_cycles(
    output_path: str = "out/gruff_shift_cycles.png",
    animation_path: str = "out/gruff_shift_cycles.gif",
) -> tuple[str, str]:
    fig, _axes = gruff_shift_cycles_render(output_path=output_path, animation_path=animation_path)
    plt.close(fig)
    return output_path, animation_path
