"""
routine_field_render.py — Structured Routine Constraint Profile
Renders the constraint profile across 5 panels using the classic GRUFF workflow sequence.

Panel mapping (mirrors existing render functions):
  1. render_governance()      → gruff_sketch style
  2. render_attention_field() → gruff_wide_360_render style
  3. render_gate_contrast()   → gruff_compass_x_contrast_render style
  4. render_phase_cycles()    → gruff_shift_cycles_render style
  5. render_unified_360()     → gruff_wide_360_render style (final summary)

Modern methods deferred: animation, GIF output, signal-chain standalone pattern.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .gruff_geometric_sketch import (
    CompassXSpec,
    PaperSpec,
    Render360Spec,
    ShiftCycleSpec,
    _diagonal_through,
    _line_intersection,
)


# ── Domain specs ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GovernanceSpec:
    """Governance hierarchy anchor positions."""
    principles_y: float = 5.5
    mission_y: float = 2.0
    vision_radius: float = 4.0
    hard_stop_y: float = 6.3


@dataclass(frozen=True)
class AttentionSpec:
    """Attention field foreground / background radii."""
    foreground_radius: float = 2.5
    background_radius: float = 6.5


@dataclass(frozen=True)
class GateSpec:
    """Gate pivot positions for anomaly / conflict / corruption."""
    anomaly_x: float = -5.5
    conflict_x: float = 0.0
    corruption_x: float = 5.5
    pivot_y: float = 0.0
    escalation_y: float = 6.0
    diag_len: float = 1.2
    arc_radius: float = 1.0


# ── Palette ───────────────────────────────────────────────────────────────────

_GOV = {
    "principles": "#1e3a5f",
    "mission":    "#2d6a4f",
    "vision":     "#6a4c93",
    "hard_stop":  "#9b2226",
    "invalid":    "#e76f51",
}
_PHASE_COLORS = ["#264653", "#2a9d8f", "#e9c46a", "#e76f51"]
_PHASE_LABELS = ["A\nField\nIntake", "B\nGate\nMapping", "C\nResearch\nBin", "D\nAuto\nSeed"]

# ── Internal helpers ──────────────────────────────────────────────────────────

def _paper_base(ax: plt.Axes, paper: PaperSpec) -> tuple[float, float, float, float]:
    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0
    ax.add_patch(
        plt.Rectangle((x0, y0), paper.width, paper.height,
                       fill=False, edgecolor="#111111", linewidth=2.0)
    )
    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)
    ax.scatter(gx.ravel(), gy.ravel(), s=8, c="#c8c8c8", alpha=0.40, linewidths=0)
    ax.plot([x0, x1], [0.0, 0.0], color="#0a0a0a", linewidth=3.2, solid_capstyle="round")
    ax.plot([0.0, 0.0], [y0, y1], color="#0a0a0a", linewidth=3.2, solid_capstyle="round")
    return x0, x1, y0, y1


def _style(ax: plt.Axes, x0: float, x1: float, y0: float, y1: float,
           title: str, margin: float = 0.6) -> None:
    ax.set_xlim(x0 - margin, x1 + margin)
    ax.set_ylim(y0 - margin, y1 + margin)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=11, pad=8)


def _ix(ax: plt.Axes, center: tuple[float, float], diag: float,
        color: str, alpha: float = 0.90) -> None:
    """Draw integration-X at center."""
    s = _diagonal_through(center, 45.0, diag)
    bs = _diagonal_through(center, 135.0, diag)
    ax.plot([s[0][0], s[1][0]], [s[0][1], s[1][1]], color=color, linewidth=2.6, alpha=alpha)
    ax.plot([bs[0][0], bs[1][0]], [bs[0][1], bs[1][1]], color=color, linewidth=2.6, alpha=alpha)
    xi = _line_intersection(s[0], s[1], bs[0], bs[1])
    if xi:
        ax.scatter([xi[0]], [xi[1]], s=60, c=[color], zorder=7,
                   edgecolors="#ffffff", linewidths=0.8)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 1 — Governance  (mirrors gruff_sketch)
# ══════════════════════════════════════════════════════════════════════════════

def render_governance(
    paper: PaperSpec = PaperSpec(),
    gov: GovernanceSpec = GovernanceSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Governance: Principles / Mission / Vision as compass-on-grid.

    Y-axis  = Principles (vertical authority).
    X-axis  = Mission (horizontal execution scope).
    Circle  = Vision lens (selection · ordering · noise filter · attribution).
    Rail A  = hard-stop safety boundaries.
    Strip   = invalidation zone at bottom.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    x0, x1, y0, y1 = _paper_base(ax, paper)

    # Vision compass circle
    ax.add_patch(
        plt.Circle((0.0, 0.0), gov.vision_radius,
                   fill=False, edgecolor=_GOV["vision"], linewidth=2.8)
    )
    ax.scatter([0.0], [0.0], s=52, c=_GOV["vision"], zorder=5)
    ax.annotate("Vision\nselect · order · filter · attribute",
                (0.0, 0.0), xytext=(8, -22),
                textcoords="offset points", fontsize=8, color=_GOV["vision"])

    # Grounding AB: Principles → Mission
    a = (0.0, gov.principles_y)
    b = (0.0, gov.mission_y)
    ax.plot([a[0], b[0]], [a[1], b[1]],
            color=_GOV["principles"], linewidth=3.4, solid_capstyle="round")
    ax.scatter([a[0]], [a[1]], s=90, c=_GOV["principles"], zorder=6)
    ax.scatter([b[0]], [b[1]], s=72, c=_GOV["mission"], zorder=6)
    ax.annotate("A — Principles\n(governs, first)", a, xytext=(10, 4),
                textcoords="offset points", fontsize=9, color=_GOV["principles"])
    ax.annotate("B — Mission\n(scoped by)", b, xytext=(10, -20),
                textcoords="offset points", fontsize=9, color=_GOV["mission"])

    # Hard-stop rails
    for i, label in enumerate(["identity", "belongings", "security"]):
        yv = gov.hard_stop_y - i * 0.65
        ax.plot([x0, x1], [yv, yv],
                color=_GOV["hard_stop"], linewidth=1.6, linestyle="--", alpha=0.90 - i * 0.12)
        ax.text(x1 - 0.2, yv + 0.12, f"\u26d4 {label}",
                fontsize=7, color=_GOV["hard_stop"], ha="right")

    # Invalidation zone
    ax.axhspan(y0, y0 + 1.1, color=_GOV["invalid"], alpha=0.07)
    ax.text(x0 + 0.3, y0 + 0.35,
            "false grounding  ·  misattribution  ·  trace loss  ·  safety drift",
            fontsize=6.5, color=_GOV["invalid"])

    _style(ax, x0, x1, y0, y1, "Panel 1 — Governance: Principles · Mission · Vision")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# Panel 2 — Attention Field  (mirrors gruff_wide_360_render)
# ══════════════════════════════════════════════════════════════════════════════

def render_attention_field(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    att: AttentionSpec = AttentionSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Attention field: foreground (gate-sensitive) vs background (static/inert).

    Inner cluster = foreground; outer scatter = background.
    Relevance threshold ring labels the boundary that earns foreground status.
    Recall arrows point from background into foreground on recurrence / pattern match.
    Polar panel shows the 360 foreground signal scope.
    Trace integrity reference rail at bottom.
    """
    fig, (ax_map, _ph) = plt.subplots(1, 2, figsize=(16, 7))
    _ph.remove()
    ax_polar = fig.add_subplot(1, 2, 2, projection="polar")

    x0, x1, y0, y1 = _paper_base(ax_map, paper)

    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)
    pts_x, pts_y = gx.ravel(), gy.ravel()
    radii = np.hypot(pts_x, pts_y)

    fg_mask = radii <= att.foreground_radius
    bg_mask = (radii > att.foreground_radius) & (radii <= att.background_radius)

    # Scatter layers
    ax_map.scatter(pts_x[~fg_mask & ~bg_mask], pts_y[~fg_mask & ~bg_mask],
                   s=6, c="#d4d4d4", alpha=0.30, linewidths=0)
    ax_map.scatter(pts_x[bg_mask], pts_y[bg_mask],
                   s=10, c="#6b7280", alpha=0.55, linewidths=0, label="background (static/inert)")
    ax_map.scatter(pts_x[fg_mask], pts_y[fg_mask],
                   s=24, c="#1e3a5f", alpha=0.95, linewidths=0, label="foreground (gate/integration)")

    # 360 radial sweep
    for deg in range(0, 360, scope.angle_step_deg):
        rad = np.deg2rad(deg)
        ax_map.plot([0.0, scope.max_radius * np.cos(rad)],
                    [0.0, scope.max_radius * np.sin(rad)],
                    color="#1f1f1f", alpha=0.16, linewidth=0.9)

    # Rings
    ax_map.add_patch(
        plt.Circle((0.0, 0.0), att.foreground_radius,
                   fill=False, edgecolor="#121212", linewidth=2.4, alpha=0.90)
    )
    ax_map.add_patch(
        plt.Circle((0.0, 0.0), att.background_radius,
                   fill=False, edgecolor="#555555", linewidth=1.6, alpha=0.65)
    )
    # Static overload fill
    ax_map.add_patch(
        plt.Circle((0.0, 0.0), att.background_radius,
                   color="#e76f51", alpha=0.05)
    )
    ax_map.text(-att.background_radius + 0.4, 0.3,
                "\u26a0 static overload zone", fontsize=7, color="#e76f51")

    # Relevance threshold label on foreground ring
    ax_map.annotate("relevance\nthreshold", (att.foreground_radius * 0.71, att.foreground_radius * 0.71),
                    xytext=(6, 6), textcoords="offset points", fontsize=7.5, color="#111827")

    # Recall arrows (background → foreground) at cardinal points
    for deg in (0, 90, 180, 270):
        rad = np.deg2rad(deg)
        bx = (att.foreground_radius + 1.2) * np.cos(rad)
        by = (att.foreground_radius + 1.2) * np.sin(rad)
        fx = att.foreground_radius * 0.85 * np.cos(rad)
        fy = att.foreground_radius * 0.85 * np.sin(rad)
        ax_map.annotate("", xy=(fx, fy), xytext=(bx, by),
                        arrowprops=dict(arrowstyle="->", color="#6a4c93", lw=1.4))
    ax_map.text(0.3, -(att.foreground_radius + 1.6),
                "recall on recurrence / relevance", fontsize=7, color="#6a4c93", ha="center")

    # Trace integrity rail
    ax_map.plot([x0, x1], [y0 + 0.9, y0 + 0.9],
                color="#2d6a4f", linewidth=1.8, linestyle="-.", alpha=0.80)
    ax_map.text(x0 + 0.3, y0 + 1.05, "trace integrity \u2192", fontsize=7, color="#2d6a4f")

    ax_map.legend(loc="upper right", fontsize=7.5, framealpha=0.92)
    _style(ax_map, x0, x1, y0, y1, "Cartesian Attention Field")

    # Polar: foreground scope
    fg_x, fg_y = pts_x[fg_mask], pts_y[fg_mask]
    theta = np.mod(np.arctan2(fg_y, fg_x), 2.0 * np.pi)
    fg_r = np.hypot(fg_x, fg_y)
    ax_polar.scatter(theta, fg_r, s=30, c="#1e3a5f", alpha=0.90)
    ax_polar.set_theta_zero_location("N")
    ax_polar.set_theta_direction(-1)
    ax_polar.set_thetagrids(np.arange(0, 360, scope.angle_step_deg))
    ax_polar.set_rmax(att.foreground_radius + 0.6)
    ax_polar.grid(True, alpha=0.32)
    ax_polar.set_title("360 Polar — Foreground Signal Scope", va="bottom", fontsize=11)

    fig.suptitle("Panel 2 — Attention Field: Foreground / Background / Recurrence / Trace Integrity",
                 fontsize=13, y=0.98)
    fig.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    return fig, (ax_map, ax_polar)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Gate Contrast  (mirrors gruff_compass_x_contrast_render)
# ══════════════════════════════════════════════════════════════════════════════

def render_gate_contrast(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    gate: GateSpec = GateSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Gate contrast: ungated baseline vs gate map active.

    Left  = baseline free-scatter, no rails (pre-gate state).
    Right = gate map active: integration-X at anomaly/conflict/corruption pivots,
            hard-stop rails, research & insights bin zone,
            compass arc at conflict pivot (soft integration signal).
    """
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 7))

    xs_arr = np.arange(-paper.width / 2.0, paper.width / 2.0 + paper.spacing, paper.spacing)
    ys_arr = np.arange(-paper.height / 2.0, paper.height / 2.0 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs_arr, ys_arr)
    pts_x, pts_y = gx.ravel(), gy.ravel()
    radii = np.hypot(pts_x, pts_y)
    cl_mask = radii <= scope.cluster_radius

    for ax in (ax_left, ax_right):
        x0, x1, y0, y1 = _paper_base(ax, paper)

    # Left: baseline
    ax_left.scatter(pts_x[~cl_mask], pts_y[~cl_mask], s=8, c="#a3a3a3", alpha=0.45, linewidths=0)
    ax_left.scatter(pts_x[cl_mask], pts_y[cl_mask], s=16, c="#2d2d2d", alpha=0.85, linewidths=0)
    ax_left.add_patch(plt.Circle((0.0, 0.0), scope.cluster_radius,
                                  fill=False, edgecolor="#333333", linewidth=2.0))
    ax_left.text(-paper.width / 2.0 + 0.4, paper.height / 2.0 - 0.7,
                 "Ungated — free scatter, no rails", fontsize=8, color="#6b7280")

    # Right: gate map active
    ax_right.scatter(pts_x[~cl_mask], pts_y[~cl_mask], s=7, c="#98a2b3", alpha=0.30, linewidths=0)
    ax_right.scatter(pts_x[cl_mask], pts_y[cl_mask], s=18, c="#0f172a", alpha=0.88, linewidths=0)

    x0r = -paper.width / 2.0
    x1r = paper.width / 2.0

    # Hard-stop rails
    for i, label in enumerate(["identity", "belongings", "security"]):
        yv = gate.escalation_y - i * 0.65
        ax_right.plot([x0r, x1r], [yv, yv],
                      color=_GOV["hard_stop"], linewidth=1.6, linestyle="--",
                      alpha=0.90 - i * 0.12)
        ax_right.text(x1r - 0.2, yv + 0.12, f"\u26d4 {label}",
                      fontsize=7, color=_GOV["hard_stop"], ha="right")

    # Escalation rail
    ax_right.plot([x0r, x1r], [gate.escalation_y + 0.45, gate.escalation_y + 0.45],
                  color="#7f1d1d", linewidth=2.4, alpha=0.90, label="escalation rail")

    # Integration-X pivots
    pivot_defs = [
        (gate.anomaly_x,    gate.pivot_y, "#264653", "anomaly\n\u2192 constrain scope"),
        (gate.conflict_x,   gate.pivot_y, "#2a9d8f", "conflict\n\u2192 research pin"),
        (gate.corruption_x, gate.pivot_y, "#e76f51", "corruption\n\u2192 generate+flag"),
    ]
    for px, py, color, label in pivot_defs:
        _ix(ax_right, (px, py), gate.diag_len, color)
        ax_right.annotate(label, (px, py), xytext=(0, -32),
                          textcoords="offset points", fontsize=7.5,
                          color=color, ha="center")

    # Compass arc at conflict (soft integration signal)
    arc_t = np.linspace(0.0, math.pi, 80)
    ax_right.plot(gate.conflict_x + gate.arc_radius * np.cos(arc_t),
                  gate.pivot_y + gate.arc_radius * np.sin(arc_t),
                  color="#a855f7", linewidth=2.0, alpha=0.85, label="integration arc")

    # Research & insights bin (bottom-right zone)
    y0r = -paper.height / 2.0
    ax_right.add_patch(
        plt.Rectangle((x1r - 3.4, y0r + 0.4), 3.1, 2.4,
                       facecolor="#e9c46a", edgecolor="#b5830a",
                       linewidth=1.4, alpha=0.22)
    )
    ax_right.text(x1r - 3.2, y0r + 0.65, "research &\ninsights bin",
                  fontsize=7.5, color="#92610a")

    ax_right.legend(loc="upper left", fontsize=7, framealpha=0.92)

    for ax, title in [
        (ax_left,  "Baseline — Ungated Field"),
        (ax_right, "Gate Map Active — Integration-X + Rails + Research Bin"),
    ]:
        x0, x1, y0, y1 = (-paper.width/2, paper.width/2, -paper.height/2, paper.height/2)
        _style(ax, x0, x1, y0, y1, title)

    fig.suptitle("Panel 3 — Gate Contrast: Ungated vs Gate Map Active",
                 fontsize=13, y=0.98)
    fig.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    return fig, (ax_left, ax_right)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Phase + Softness Cycles  (mirrors gruff_shift_cycles_render)
# ══════════════════════════════════════════════════════════════════════════════

def render_phase_cycles(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    cx: CompassXSpec = CompassXSpec(),
    cycle: ShiftCycleSpec = ShiftCycleSpec(cycles=4),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Phase shift cycles A→D with softness 50/50 → adaptive weighting.

    Mirrors gruff_shift_cycles_render() for 4 phase cycles.
    Each cycle = one phase (A/B/C/D) with:
      - Integration-X at O (phase decision point)
      - Two interleaved tracks: intuition lane (dashed) + grounding lane (solid),
        starting 50/50 wide and converging by cycle D (adaptive pulse)
      - Three scenario clusters (failure episode / decision pattern / struggle cluster)
    3D pane: Z-axis = learning iteration depth; scenario clusters per phase.
    Learning loop feedback arc: D → A at bottom.
    Animation deferred.
    """
    fig = plt.figure(figsize=(17, 8))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")

    x0, x1 = -paper.width / 2.0, paper.width / 2.0
    y0, y1 = -paper.height / 2.0, paper.height / 2.0
    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)

    # Paper base
    ax2d.add_patch(plt.Rectangle((x0, y0), paper.width, paper.height,
                                  fill=False, edgecolor="#111111", linewidth=2.0))
    ax2d.scatter(gx.ravel(), gy.ravel(), s=7, c="#b8bfc9", alpha=0.28, linewidths=0)
    ax2d.plot([x0, x1], [0.0, 0.0], color="#030712", linewidth=3.0, solid_capstyle="round")
    ax2d.plot([0.0, 0.0], [y0, y1], color="#030712", linewidth=3.0, solid_capstyle="round")
    ax2d.add_patch(plt.Circle((0.0, 0.0), scope.cluster_radius,
                               fill=False, edgecolor="#111827", linewidth=1.8))

    o_positions: list[tuple[float, float]] = []

    for i in range(cycle.cycles):
        color = _PHASE_COLORS[i]
        # Converging softness: spread starts wide (cycle 0) and narrows (cycle 3)
        softness_spread = 1.6 - i * 0.35
        sx = cx.x_anchor + (i - (cycle.cycles - 1) / 2.0) * cycle.shift_x
        sy = (i - (cycle.cycles - 1) / 2.0) * cycle.shift_y
        y_top = cx.y_top + sy
        y_bottom = cx.y_bottom + sy
        a = (sx, y_top)
        b = (sx, y_bottom)
        o = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        o_positions.append(o)
        slash = _diagonal_through(o, 45.0, cx.diagonal_length)
        backslash = _diagonal_through(o, 135.0, cx.diagonal_length)

        # Rails + grounding
        ax2d.plot([x0, x1], [y_top, y_top], color=color, linewidth=1.6, alpha=0.62)
        ax2d.plot([x0, x1], [y_bottom, y_bottom], color=color, linewidth=1.6, alpha=0.62)
        ax2d.plot([a[0], b[0]], [a[1], b[1]], color=color, linewidth=2.8, alpha=0.92)

        # Integration-X
        ax2d.plot([slash[0][0], slash[1][0]], [slash[0][1], slash[1][1]],
                  color=color, linewidth=2.2)
        ax2d.plot([backslash[0][0], backslash[1][0]], [backslash[0][1], backslash[1][1]],
                  color=color, linewidth=2.2)
        ax2d.scatter([o[0]], [o[1]], s=72, c=[color],
                     edgecolors="#111111", linewidths=0.8, zorder=6)
        ax2d.annotate(_PHASE_LABELS[i], o, xytext=(7, 6),
                      textcoords="offset points", fontsize=8, color="#111827")

        # Softness tracks: intuition (dashed, wider) + grounding (solid, narrower) at 50/50 → converge
        for sign, lw, ls, label in [
            (+1, 1.8, "--", "intuition"),
            (-1, 2.0, "-",  "grounding"),
        ]:
            track_y = o[1] + sign * softness_spread
            ax2d.plot([o[0] - 1.2, o[0] + 1.2], [track_y, track_y],
                      color=color, linewidth=lw, linestyle=ls, alpha=0.75)

        # Scenario clusters (failure / decision / struggle)
        z_level = float(i + 1)
        for j, (deg, scenario_label) in enumerate(
            zip((0.0, 120.0, 240.0),
                ("failure\nepisode", "decision\npattern", "struggle\ncluster"))
        ):
            rad = math.radians(deg)
            cx0_pt = o[0] + cycle.cluster_spread * math.cos(rad)
            cy0_pt = o[1] + cycle.cluster_spread * math.sin(rad)
            t = np.linspace(0.0, 2.0 * math.pi, cycle.cluster_points, endpoint=False)
            px = cx0_pt + cycle.cluster_point_radius * np.cos(t)
            py = cy0_pt + cycle.cluster_point_radius * np.sin(t)
            ax2d.scatter(px, py, s=12, c=[color], alpha=0.78, linewidths=0)
            ax2d.scatter([cx0_pt], [cy0_pt], s=34, c=[color],
                         edgecolors="#0f172a", linewidths=0.7, zorder=6)
            if i == 0:
                ax2d.annotate(scenario_label, (cx0_pt, cy0_pt),
                              xytext=(4, -12), textcoords="offset points",
                              fontsize=6.5, color="#1f2937")
            # 3D
            pz = np.full_like(px, z_level)
            ax3d.scatter(px, py, pz, s=10, c=[color], alpha=0.78, depthshade=True)
            ax3d.scatter([cx0_pt], [cy0_pt], [z_level], s=30, c=[color],
                         alpha=0.92, depthshade=True)

        ax3d.plot([slash[0][0], slash[1][0]], [slash[0][1], slash[1][1]],
                  [z_level, z_level], color=color, linewidth=1.6, alpha=0.88)
        ax3d.plot([backslash[0][0], backslash[1][0]], [backslash[0][1], backslash[1][1]],
                  [z_level, z_level], color=color, linewidth=1.6, alpha=0.88)
        ax3d.scatter([o[0]], [o[1]], [z_level], s=48, c=[color],
                     edgecolors="#111111", linewidths=0.7)

    # Softness legend annotation
    ax2d.plot([], [], color="#888888", linewidth=1.8, linestyle="--", label="intuition lane")
    ax2d.plot([], [], color="#888888", linewidth=2.0, linestyle="-",  label="grounding lane")
    ax2d.text(x0 + 0.4, y1 - 0.7,
              "Softness: 50/50 start \u2192 adaptive convergence by D",
              fontsize=7.5, color="#374151")

    # Learning loop D → A feedback arc at bottom
    d_ox, a_ox = o_positions[-1][0], o_positions[0][0]
    loop_y = y0 + 1.1
    t_arc = np.linspace(0, 1, 80)
    loop_bx = (1 - t_arc) ** 2 * d_ox + 2 * (1 - t_arc) * t_arc * 0.0 + t_arc ** 2 * a_ox
    ax2d.plot(loop_bx, np.full_like(loop_bx, loop_y),
              color="#6a4c93", linewidth=2.2, linestyle="-.", alpha=0.85,
              label="learning loop D\u2192A")
    ax2d.annotate("", xy=(a_ox, loop_y), xytext=(a_ox + 1.2, loop_y),
                  arrowprops=dict(arrowstyle="->", color="#6a4c93", lw=1.6))
    ax2d.legend(loc="upper right", fontsize=7, framealpha=0.92)

    # 2D style
    ax2d.set_xlim(x0 - 0.6, x1 + 0.6)
    ax2d.set_ylim(y0 - 0.6, y1 + 0.6)
    ax2d.set_aspect("equal", adjustable="box")
    ax2d.set_facecolor("white")
    ax2d.set_xticks([]); ax2d.set_yticks([])
    ax2d.set_title("Graph Sheet — 4 Phase Cycles (A\u2192B\u2192C\u2192D + Loop)", fontsize=11)

    # 3D style
    ax3d.set_xlim(x0, x1)
    ax3d.set_ylim(y0, y1)
    ax3d.set_zlim(0.5, cycle.cycles + 0.8)
    ax3d.set_xlabel("x"); ax3d.set_ylabel("y"); ax3d.set_zlabel("iteration")
    ax3d.set_title("3D — Scenario Clusters per Learning Cycle", fontsize=11)
    ax3d.view_init(elev=24, azim=28)

    fig.suptitle(
        "Panel 4 — Phase Cycles: A (Field Intake) \u2192 B (Gate Mapping) \u2192 "
        "C (Research Bin) \u2192 D (Auto Seed)  |  Softness: 50/50\u2192adaptive",
        fontsize=11, y=0.98,
    )
    fig.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=190, bbox_inches="tight")

    return fig, (ax2d, ax3d)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 5 — Unified 360  (mirrors gruff_wide_360_render — final summary)
# ══════════════════════════════════════════════════════════════════════════════

def render_unified_360(
    paper: PaperSpec = PaperSpec(),
    scope: Render360Spec = Render360Spec(),
    gov: GovernanceSpec = GovernanceSpec(),
    att: AttentionSpec = AttentionSpec(),
    gate: GateSpec = GateSpec(),
    output_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Unified 360: all constraint layers on one field + polar projection.

    Left  = cartesian paper with all layers overlaid:
            governance rails, attention clusters, gate pivots, phase markers, learning loop.
    Right = polar 360 with constraint dimensions distributed by quadrant:
            Principles=N(270°), Mission=E(0°), Attention=S(90°), Gates=W(180°),
            Phases=NW(315°), Research=NE(45°).
    """
    fig, (ax_map, _ph) = plt.subplots(1, 2, figsize=(18, 8))
    _ph.remove()
    ax_polar = fig.add_subplot(1, 2, 2, projection="polar")

    x0, x1, y0, y1 = _paper_base(ax_map, paper)

    xs = np.arange(x0, x1 + paper.spacing, paper.spacing)
    ys = np.arange(y0, y1 + paper.spacing, paper.spacing)
    gx, gy = np.meshgrid(xs, ys)
    pts_x, pts_y = gx.ravel(), gy.ravel()
    radii = np.hypot(pts_x, pts_y)
    fg_mask = radii <= att.foreground_radius
    bg_mask = (radii > att.foreground_radius) & (radii <= att.background_radius)

    # Scatter
    ax_map.scatter(pts_x[~fg_mask & ~bg_mask], pts_y[~fg_mask & ~bg_mask],
                   s=5, c="#d4d4d4", alpha=0.25, linewidths=0)
    ax_map.scatter(pts_x[bg_mask], pts_y[bg_mask],
                   s=9, c="#9ca3af", alpha=0.48, linewidths=0, label="background")
    ax_map.scatter(pts_x[fg_mask], pts_y[fg_mask],
                   s=20, c="#1e3a5f", alpha=0.94, linewidths=0, label="foreground")

    # 360 radial sweep
    for deg in range(0, 360, scope.angle_step_deg):
        rad = np.deg2rad(deg)
        ax_map.plot([0.0, scope.max_radius * np.cos(rad)],
                    [0.0, scope.max_radius * np.sin(rad)],
                    color="#1f1f1f", alpha=0.13, linewidth=0.8)

    # Attention rings
    for rr, lw, alpha in [(att.foreground_radius, 2.2, 0.85), (att.background_radius, 1.5, 0.60)]:
        ax_map.add_patch(plt.Circle((0.0, 0.0), rr, fill=False,
                                     edgecolor="#121212", linewidth=lw, alpha=alpha))

    # Vision scope circle (governance)
    ax_map.add_patch(plt.Circle((0.0, 0.0), gov.vision_radius,
                                 fill=False, edgecolor=_GOV["vision"],
                                 linewidth=2.2, linestyle="--", alpha=0.65))
    ax_map.text(gov.vision_radius * 0.72, gov.vision_radius * 0.72,
                "Vision", fontsize=7.5, color=_GOV["vision"])

    # Hard-stop rails
    for i, label in enumerate(["identity", "belongings", "security"]):
        yv = gov.hard_stop_y - i * 0.65
        ax_map.plot([x0, x1], [yv, yv],
                    color=_GOV["hard_stop"], linewidth=1.3, linestyle="--",
                    alpha=0.80 - i * 0.10)
        ax_map.text(x1 - 0.2, yv + 0.10, f"\u26d4 {label}",
                    fontsize=6.5, color=_GOV["hard_stop"], ha="right")

    # Gate integration-X pivots
    for px, py, color in [
        (gate.anomaly_x,    gate.pivot_y, "#264653"),
        (gate.conflict_x,   gate.pivot_y, "#2a9d8f"),
        (gate.corruption_x, gate.pivot_y, "#e76f51"),
    ]:
        _ix(ax_map, (px, py), gate.diag_len * 0.80, color)

    # Phase markers along lower band
    cx_spec = CompassXSpec()
    cycle_spec = ShiftCycleSpec(cycles=4)
    phase_ox = [
        cx_spec.x_anchor + (i - (cycle_spec.cycles - 1) / 2.0) * cycle_spec.shift_x
        for i in range(4)
    ]
    for ox, color, label in zip(phase_ox, _PHASE_COLORS, ["A", "B", "C", "D"]):
        ax_map.scatter([ox], [y0 + 1.9], s=52, c=[color],
                       edgecolors="#111111", linewidths=0.8, zorder=6)
        ax_map.text(ox, y0 + 2.15, label, fontsize=9, ha="center",
                    color=color, fontweight="bold")

    # Learning loop arc at bottom
    arc_t = np.linspace(0, math.pi, 80)
    arc_r = (phase_ox[-1] - phase_ox[0]) / 2.0
    arc_cx = (phase_ox[0] + phase_ox[-1]) / 2.0
    ax_map.plot(arc_cx + arc_r * np.cos(arc_t + math.pi),
                y0 + 1.9 + arc_r * 0.14 * np.sin(arc_t + math.pi),
                color="#6a4c93", linewidth=1.8, linestyle="-.", alpha=0.72)

    ax_map.legend(loc="upper right", fontsize=7.5, framealpha=0.92)
    _style(ax_map, x0, x1, y0, y1, "Unified Cartesian Field — All Constraint Layers")

    # Polar: constraint dimensions by quadrant
    dim_angle = {
        "Principles": np.deg2rad(270),
        "Mission":    np.deg2rad(0),
        "Attention":  np.deg2rad(90),
        "Gates":      np.deg2rad(180),
        "Phases A\u2013D": np.deg2rad(315),
        "Research":   np.deg2rad(45),
    }
    dim_color = {
        "Principles": _GOV["principles"],
        "Mission":    _GOV["mission"],
        "Attention":  "#1e3a5f",
        "Gates":      "#e76f51",
        "Phases A\u2013D": "#2a9d8f",
        "Research":   "#e9c46a",
    }
    dim_r = {
        "Principles": 6.8, "Mission": 5.8, "Attention": 4.8,
        "Gates": 5.2, "Phases A\u2013D": 3.8, "Research": 2.6,
    }
    rng = np.random.default_rng(42)
    spread = np.deg2rad(22)
    for name, base_angle in dim_angle.items():
        theta_pts = base_angle + rng.uniform(-spread, spread, 14)
        r_pts = rng.uniform(dim_r[name] - 1.1, dim_r[name] + 0.8, 14)
        ax_polar.scatter(theta_pts, r_pts, s=22, c=dim_color[name], alpha=0.88, label=name)

    ax_polar.set_theta_zero_location("E")
    ax_polar.set_theta_direction(-1)
    ax_polar.set_thetagrids(np.arange(0, 360, scope.angle_step_deg))
    ax_polar.set_rmax(scope.max_radius)
    ax_polar.grid(True, alpha=0.28)
    ax_polar.legend(loc="upper right", bbox_to_anchor=(1.38, 1.18),
                    fontsize=7, framealpha=0.92)
    ax_polar.set_title("360 Polar — Constraint Dimensions Distributed", va="bottom", fontsize=11)

    fig.suptitle("Panel 5 — Unified 360: Full Constraint Profile Scope",
                 fontsize=14, y=0.99)
    fig.tight_layout()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    return fig, (ax_map, ax_polar)


# ══════════════════════════════════════════════════════════════════════════════
# Demo entry point
# ══════════════════════════════════════════════════════════════════════════════

def demo_routine_field(out_dir: str = "out") -> list[str]:
    """Render all 5 constraint profile panels. Returns list of output paths."""
    renders: list[tuple[str, object]] = [
        ("routine_governance.png",    lambda p: render_governance(output_path=p)),
        ("routine_attention.png",     lambda p: render_attention_field(output_path=p)),
        ("routine_gate_contrast.png", lambda p: render_gate_contrast(output_path=p)),
        ("routine_phases.png",        lambda p: render_phase_cycles(output_path=p)),
        ("routine_unified_360.png",   lambda p: render_unified_360(output_path=p)),
    ]
    outputs = []
    for fname, fn in renders:
        path = str(Path(out_dir) / fname)
        fig, _ = fn(path)
        plt.close(fig)
        outputs.append(path)
    return outputs
