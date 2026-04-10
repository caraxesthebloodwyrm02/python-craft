from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class SylveonSpec:
    paper_width: float = 20.0
    paper_height: float = 14.0
    grid_resolution: int = 220
    logic_ratio: float = 0.65
    pattern_ratio: float = 0.35
    interval_low_s: float = 4.0
    interval_high_s: float = 6.0
    hotspots: int = 8
    seed: int = 42


@dataclass(frozen=True)
class CompassAddonSpec:
    spine_length: float = 5.6
    hook_span: float = 1.2
    needle_length: float = 1.3


@dataclass(frozen=True)
class TodoRecommendation:
    id: str
    entry_point: tuple[float, float]
    lsp_target: str
    priority: str
    task: str
    rationale: str
    best_practice: str


@dataclass
class SylveonRun:
    dwell_seconds: list[float]
    centers: list[tuple[float, float]]
    recommendations: list[TodoRecommendation]


def _gaussian(x: np.ndarray, y: np.ndarray, cx: float, cy: float, sx: float, sy: float, amp: float) -> np.ndarray:
    gx = ((x - cx) ** 2) / (2.0 * sx * sx)
    gy = ((y - cy) ** 2) / (2.0 * sy * sy)
    return amp * np.exp(-(gx + gy))


def _normalize(z: np.ndarray) -> np.ndarray:
    zmin = float(z.min())
    zmax = float(z.max())
    if abs(zmax - zmin) < 1e-9:
        return np.zeros_like(z)
    return (z - zmin) / (zmax - zmin)


def _build_layers(spec: SylveonSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(spec.seed)
    x = np.linspace(-spec.paper_width / 2.0, spec.paper_width / 2.0, spec.grid_resolution)
    y = np.linspace(-spec.paper_height / 2.0, spec.paper_height / 2.0, spec.grid_resolution)
    xx, yy = np.meshgrid(x, y)

    # 65% logic layer: deliberate structures, lanes, and probes.
    logic = (
        _gaussian(xx, yy, -4.0, 1.2, 2.1, 1.0, 1.0)
        + _gaussian(xx, yy, 0.0, 0.0, 1.8, 1.4, 1.3)
        + _gaussian(xx, yy, 4.2, -1.0, 2.0, 1.1, 0.95)
    )
    for yline in (-2.6, -0.4, 1.8):
        logic += _gaussian(xx, yy, 0.0, yline, 8.2, 0.26, 0.55)

    # 35% pattern layer: phosphorescent ornaments, distributed random glows.
    pattern = np.zeros_like(logic)
    for _ in range(18):
        cx = rng.uniform(-spec.paper_width / 2.0, spec.paper_width / 2.0)
        cy = rng.uniform(-spec.paper_height / 2.0, spec.paper_height / 2.0)
        sx = rng.uniform(0.35, 1.35)
        sy = rng.uniform(0.35, 1.25)
        amp = rng.uniform(0.15, 0.55)
        pattern += _gaussian(xx, yy, cx, cy, sx, sy, amp)

    logic_n = _normalize(logic)
    pattern_n = _normalize(pattern)
    heat = _normalize(spec.logic_ratio * logic_n + spec.pattern_ratio * pattern_n)
    return xx, yy, logic_n, pattern_n, heat


def _pick_hotspots(heat: np.ndarray, xx: np.ndarray, yy: np.ndarray, count: int) -> list[tuple[float, float]]:
    flat = heat.ravel()
    idx = np.argpartition(flat, -count)[-count:]
    idx_sorted = idx[np.argsort(flat[idx])[::-1]]
    centers = [(float(xx.ravel()[i]), float(yy.ravel()[i])) for i in idx_sorted]
    return centers


def _build_recommendation(i: int, center: tuple[float, float], strength: float) -> TodoRecommendation:
    priority = "high" if strength > 0.82 else "medium"
    task = (
        "Enforce precise type contracts at heat-entry path"
        if priority == "high"
        else "Refine naming and docstring clarity for context hook"
    )
    rationale = (
        "Hot red probe lane indicates fast parallel data flow; unsafe drift risk rises without strict types."
        if priority == "high"
        else "Lime ornament region indicates broad decorative spread; maintain readability and intent traceability."
    )
    best_practice = (
        "Use typed dataclasses + narrow interfaces + deterministic tests for hook payload schemas."
        if priority == "high"
        else "Prefer small pure functions, explicit side-effects, and lint-clean style for maintainable mapping."
    )
    return TodoRecommendation(
        id=f"sylveon-{i + 1:02d}",
        entry_point=center,
        lsp_target="basepyright",
        priority=priority,
        task=task,
        rationale=rationale,
        best_practice=best_practice,
    )


def _parallel_pull_recommendations(
    centers: list[tuple[float, float]], heat: np.ndarray, xx: np.ndarray, yy: np.ndarray
) -> list[TodoRecommendation]:
    def strength_at(point: tuple[float, float]) -> float:
        x, y = point
        d = (xx - x) ** 2 + (yy - y) ** 2
        idx = int(np.argmin(d))
        return float(heat.ravel()[idx])

    payloads = [(i, center, strength_at(center)) for i, center in enumerate(centers)]
    with ThreadPoolExecutor(max_workers=min(8, len(payloads) or 1)) as ex:
        recs = list(ex.map(lambda p: _build_recommendation(*p), payloads))
    return recs


def _draw_compass_addon(ax: plt.Axes, center: tuple[float, float], addon: CompassAddonSpec) -> None:
    cx, cy = center
    tail = (cx, cy - addon.spine_length / 2.0)
    tip = (cx, cy + addon.spine_length / 2.0)

    # V -> | transform: vertical spine.
    ax.plot([tail[0], tip[0]], [tail[1], tip[1]], color="#111827", linewidth=3.0, zorder=6)

    # Push/pull hooks on both sides of tail.
    ax.plot([tail[0] - addon.hook_span, tail[0] - 0.2], [tail[1], tail[1]], color="#0369a1", linewidth=2.2, zorder=6)
    ax.plot([tail[0] + 0.2, tail[0] + addon.hook_span], [tail[1], tail[1]], color="#0369a1", linewidth=2.2, zorder=6)

    # Sharp needle head.
    ax.plot([tip[0], tip[0]], [tip[1], tip[1] + addon.needle_length], color="#b91c1c", linewidth=2.5, zorder=7)
    ax.scatter([tip[0]], [tip[1] + addon.needle_length], s=45, c="#7f1d1d", marker="^", zorder=8)


def sylveon_render(
    spec: SylveonSpec = SylveonSpec(),
    addon: CompassAddonSpec = CompassAddonSpec(),
    output_path: str | None = None,
    animation_path: str | None = None,
) -> tuple[plt.Figure, tuple[plt.Axes, Any], SylveonRun]:
    """Render Sylveon: 65% backend logic + 35% frontend pattern context heatmap.

    Produces:
    - 2D pane with heatmap spectrum, hook overlays, and compass markers.
    - 3D pane with distributed heat surface and hotspot references.
    - parallel pulled actionable recommendations tied to entry points and basepyright.
    """
    xx, yy, _logic, _pattern, heat = _build_layers(spec)
    centers = _pick_hotspots(heat, xx, yy, spec.hotspots)
    recs = _parallel_pull_recommendations(centers, heat, xx, yy)

    rng = np.random.default_rng(spec.seed + 7)
    dwell = [float(rng.uniform(spec.interval_low_s, spec.interval_high_s)) for _ in centers]

    fig = plt.figure(figsize=(17, 8))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")

    x0, x1 = -spec.paper_width / 2.0, spec.paper_width / 2.0
    y0, y1 = -spec.paper_height / 2.0, spec.paper_height / 2.0

    # 2D heatmap pane
    ax2d.imshow(
        heat,
        extent=(x0, x1, y0, y1),
        origin="lower",
        cmap="turbo",
        alpha=0.88,
        interpolation="bilinear",
        aspect="auto",
    )

    # Sharp probing data: long horizontal red lanes.
    for yline in (-2.6, -0.4, 1.8):
        ax2d.plot([x0, x1], [yline, yline], color="#ef4444", linewidth=2.6, alpha=0.95)

    # Phosphorescent mangrove style ornaments (lime-green spread).
    for _ in range(45):
        px = float(rng.uniform(x0, x1))
        py = float(rng.uniform(y0, y1))
        sz = float(rng.uniform(10.0, 40.0))
        ax2d.scatter([px], [py], s=sz, c="#84cc16", alpha=0.23, linewidths=0)

    # Hook markers and recommended next central points.
    marker_artists: list[Any] = []
    label_artists: list[Any] = []
    for i, center in enumerate(centers, start=1):
        m = ax2d.scatter([center[0]], [center[1]], s=56, c="#111827", edgecolors="#e5e7eb", linewidths=0.8, zorder=7)
        t = ax2d.annotate(
            f"P{i} ({dwell[i - 1]:.1f}s)",
            center,
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=8,
            color="#e5e7eb",
            bbox={"facecolor": "#0f172a", "alpha": 0.55, "pad": 1.5, "edgecolor": "none"},
        )
        marker_artists.append(m)
        label_artists.append(t)

    # Compass add-on at top hotspot.
    top_center = centers[0] if centers else (0.0, 0.0)
    _draw_compass_addon(ax2d, top_center, addon)

    # 2D styling
    ax2d.set_facecolor("#05090f")
    ax2d.set_xlim(x0, x1)
    ax2d.set_ylim(y0, y1)
    ax2d.set_xticks([])
    ax2d.set_yticks([])
    ax2d.set_title("Sylveon Heatmap Context Pane", fontsize=12)

    # 3D pane: distributed context categorization surface.
    stride = max(1, spec.grid_resolution // 70)
    surf = ax3d.plot_surface(
        xx[::stride, ::stride],
        yy[::stride, ::stride],
        heat[::stride, ::stride],
        cmap="viridis",
        linewidth=0,
        antialiased=True,
        alpha=0.92,
    )
    _ = surf
    for i, center in enumerate(centers, start=1):
        d = (xx - center[0]) ** 2 + (yy - center[1]) ** 2
        idx = int(np.argmin(d))
        z = float(heat.ravel()[idx])
        ax3d.scatter([center[0]], [center[1]], [z], s=42, c="#ef4444" if i <= 3 else "#84cc16", depthshade=True)

    ax3d.set_xlim(x0, x1)
    ax3d.set_ylim(y0, y1)
    ax3d.set_zlim(0.0, 1.0)
    ax3d.set_xlabel("x")
    ax3d.set_ylabel("y")
    ax3d.set_zlabel("context")
    ax3d.set_title("Sylveon Structured Distribution (3D)", fontsize=12)
    ax3d.view_init(elev=25, azim=40)

    fig.suptitle("Sylveon: 65% Logic + 35% Pattern Context Rendering", fontsize=15, y=0.98)
    fig.tight_layout()

    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=180, bbox_inches="tight")

    if animation_path and centers:
        # 4-6 second interval guidance between central points.
        frames_per_second = 4
        counts = [max(2, int(sec * frames_per_second)) for sec in dwell]
        cumulative = np.cumsum([0] + counts)
        total_frames = int(cumulative[-1])

        # Start with all labels dimmed.
        for m in marker_artists:
            m.set_alpha(0.2)
        for t in label_artists:
            t.set_alpha(0.3)

        def update(frame: int) -> list[Any]:
            idx = int(np.searchsorted(cumulative[1:], frame, side="right"))
            idx = min(idx, len(centers) - 1)
            for j, m in enumerate(marker_artists):
                m.set_alpha(1.0 if j == idx else 0.2)
            for j, t in enumerate(label_artists):
                t.set_alpha(1.0 if j == idx else 0.3)
            ax3d.view_init(elev=25, azim=40 + frame * 2)
            return []

        anim = FuncAnimation(fig, update, frames=total_frames, interval=250, blit=False)
        target = Path(animation_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        anim.save(target, writer="pillow", dpi=115)

    run = SylveonRun(dwell_seconds=dwell, centers=centers, recommendations=recs)
    return fig, (ax2d, ax3d), run


def demo_sylveon(
    output_path: str = "out/sylveon_heatmap.png",
    animation_path: str = "out/sylveon_heatmap.gif",
) -> tuple[str, str, int]:
    fig, _axes, run = sylveon_render(output_path=output_path, animation_path=animation_path)
    plt.close(fig)
    return output_path, animation_path, len(run.recommendations)
