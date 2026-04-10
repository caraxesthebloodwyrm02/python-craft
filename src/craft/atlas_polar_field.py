"""Atlas Polar Field — Multi-Dimensional Animation Artifact.

Bridges the personalization void identified in binary-brewing-sifakis:
mood and consent tokens from the Atlas 7-item batch have no transport path.
This renderer gives them one.

Dimensions encoded:
  G (grounding)   → particle brightness / alpha
  score           → particle radius
  layer (0-3)     → parallax depth / orbital speed
  mood (7 states) → color palette
  beat (0-N)      → animation clock / rhythm

Seeds (from cheerful-dazzling-kite, SEEDS dict):
  grounding-gate    (G=1.0, score=1.0, layer=2)  — agentic, governance predicate
  struggle-point    (G=1.0, score=0.8, layer=3)  — hierarchy, connective node
  token-bridge      (G=0.8, score=0.7, layer=3)  — hierarchy, signal mapping
  scaffold-boundary (G=0.6, score=0.6, layer=2)  — agentic, test boundary

Output: out/atlas_polar_field.gif  (1456×910, 90 frames, 55ms/frame)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap

# ── Constants ─────────────────────────────────────────────────────────────────

WIDTH_PX = 1456
HEIGHT_PX = 910
DPI = 96
FRAMES = 90
INTERVAL_MS = 55
OUT_DIR = Path(__file__).parent.parent.parent / "out"

# ── Seed entities (from cheerful-dazzling-kite) ───────────────────────────────


@dataclass
class EntityPoint:
    entity_id: str
    g: float  # grounding score [0, 1]
    score: float  # dimension score [0, 1]
    layer: int  # atlas stack depth: 0=collective, 1=context, 2=agentic, 3=hierarchy
    label: str = ""

    @property
    def theta(self) -> float:
        """Polar angle in radians — atan2(score, g)."""
        return math.atan2(self.score, self.g)

    @property
    def radius(self) -> float:
        """Distance from origin — √(g² + score²)."""
        return math.hypot(self.g, self.score)

    @property
    def orbital_speed(self) -> float:
        """Layer-derived orbital speed: deeper layers orbit slower."""
        # layer 0=fast, 3=slow; invert and normalize
        speeds = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.3}
        return speeds.get(self.layer, 0.5)

    @property
    def base_size(self) -> float:
        """Particle visual radius from score."""
        return 80 + self.score * 320

    @property
    def alpha(self) -> float:
        """Particle brightness from G."""
        return 0.4 + self.g * 0.6


SEEDS: list[EntityPoint] = [
    EntityPoint("grounding-gate", g=1.0, score=1.0, layer=2, label="Grounding Gate"),
    EntityPoint("struggle-point", g=1.0, score=0.8, layer=3, label="Struggle Point"),
    EntityPoint("token-bridge", g=0.8, score=0.7, layer=3, label="Token Bridge"),
    EntityPoint("scaffold-boundary", g=0.6, score=0.6, layer=2, label="Scaffold Boundary"),
]

# ── Mood palette system (7 moods, Atlas token #d4a87e = dominant playful) ─────

MOOD_PALETTES: dict[str, dict[str, Any]] = {
    "enthusiastic": {
        "bg": "#0a0012",
        "colors": ["#ff6b35", "#f7c59f", "#efefd0", "#ff4757", "#ffa502"],
        "glow": "#ff6b35",
        "arc": "#ff4757aa",
    },
    "curious": {
        "bg": "#000d1a",
        "colors": ["#0097e6", "#00d2d3", "#c4e0f9", "#7bed9f", "#eccc68"],
        "glow": "#00d2d3",
        "arc": "#0097e6aa",
    },
    "supportive": {
        "bg": "#001a0d",
        "colors": ["#2ed573", "#7bed9f", "#a8e6cf", "#dcedc1", "#ffd3b6"],
        "glow": "#2ed573",
        "arc": "#2ed573aa",
    },
    "playful": {  # dominant Atlas mood — #d4a87e token
        "bg": "#0f0520",
        "colors": ["#d4a87e", "#c56af0", "#a29bfe", "#fd79a8", "#fdcb6e"],
        "glow": "#d4a87e",
        "arc": "#c56af0aa",
    },
    "focused": {
        "bg": "#0a0a14",
        "colors": ["#636e72", "#b2bec3", "#dfe6e9", "#74b9ff", "#0984e3"],
        "glow": "#74b9ff",
        "arc": "#0984e3aa",
    },
    "calm": {
        "bg": "#080818",
        "colors": ["#6c5ce7", "#a29bfe", "#dfe6e9", "#81ecec", "#00cec9"],
        "glow": "#a29bfe",
        "arc": "#6c5ce7aa",
    },
    "creative": {
        "bg": "#0d0810",
        "colors": ["#e84393", "#fd79a8", "#fdcb6e", "#e17055", "#d63031"],
        "glow": "#fd79a8",
        "arc": "#e84393aa",
    },
}

# Default: playful (matches Hermes dominant mood from archetype portrait)
ACTIVE_MOOD = "playful"

# ── Layer label overlay ────────────────────────────────────────────────────────

LAYER_LABELS = {0: "Collective", 1: "Context", 2: "Agentic", 3: "Hierarchy"}
LAYER_RADII = {0: 0.35, 1: 0.55, 2: 0.80, 3: 1.05}  # orbital ring radii in data coords

# ── Collinear spine: y = 0.5x + 0.3 (from cheerful-dazzling-kite) ─────────────


def _spine_y(x: float) -> float:
    return 0.5 * x + 0.3


# ── Particle trail system ──────────────────────────────────────────────────────


@dataclass
class Trail:
    positions: list[tuple[float, float]] = field(default_factory=list)
    max_len: int = 18

    def push(self, x: float, y: float) -> None:
        self.positions.append((x, y))
        if len(self.positions) > self.max_len:
            self.positions.pop(0)


# ── Build the figure ──────────────────────────────────────────────────────────


def _make_fig(palette: dict[str, Any]) -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(
        figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI),
        dpi=DPI,
        facecolor=palette["bg"],
    )
    ax = fig.add_subplot(111, aspect="equal", facecolor=palette["bg"])
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.axis("off")
    return fig, ax


def _draw_static_layer(ax: plt.Axes, palette: dict[str, Any]) -> None:
    """Draw orbital rings, collinear spine, and G-score radial grid — once."""
    bg = palette["bg"]
    arc_color = palette["arc"]

    # Radial grid (faint concentric circles)
    for r in [0.35, 0.55, 0.80, 1.05, 1.25]:
        ring = plt.Circle((0, 0), r, fill=False, color="#ffffff08", linewidth=0.6, zorder=1)
        ax.add_patch(ring)

    # Layer orbital rings (labeled)
    for lyr, r in LAYER_RADII.items():
        ring = plt.Circle((0, 0), r, fill=False, color=arc_color, linewidth=1.0, linestyle="--", alpha=0.35, zorder=2)
        ax.add_patch(ring)
        lbl = LAYER_LABELS[lyr]
        ax.text(
            0,
            r + 0.04,
            lbl,
            color=arc_color,
            fontsize=6.5,
            ha="center",
            va="bottom",
            alpha=0.55,
            zorder=3,
            fontfamily="monospace",
        )

    # Collinear spine: y = 0.5x + 0.3 — scaffold-boundary → grounding-gate
    xs = np.linspace(-1.2, 1.2, 200)
    ys = 0.5 * xs + 0.3
    mask = (ys >= -1.4) & (ys <= 1.4)
    ax.plot(
        xs[mask], ys[mask], color="#ffffff", alpha=0.08, linewidth=0.8, linestyle=":", zorder=2, label="collinear spine"
    )

    # Radial axis labels (G-score)
    for gval in [0.4, 0.6, 0.8, 1.0]:
        ax.text(
            gval,
            -0.06,
            f"G={gval}",
            color="#ffffff22",
            fontsize=5.5,
            ha="center",
            va="top",
            fontfamily="monospace",
            zorder=2,
        )

    # Angular axis (score)
    for sval in [0.4, 0.6, 0.8, 1.0]:
        ax.text(
            -0.06,
            sval,
            f"s={sval}",
            color="#ffffff22",
            fontsize=5.5,
            ha="right",
            va="center",
            fontfamily="monospace",
            zorder=2,
        )

    # Origin marker
    ax.plot(0, 0, "o", color="#ffffff33", markersize=3, zorder=3)

    # Title
    ax.text(
        0,
        1.35,
        "ATLAS POLAR FIELD",
        color=palette["glow"],
        fontsize=11,
        ha="center",
        va="top",
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.85,
        zorder=10,
    )
    ax.text(
        0,
        1.25,
        f"mood: {ACTIVE_MOOD}  |  4 seeds  |  2 layers",
        color="#ffffff55",
        fontsize=6.5,
        ha="center",
        va="top",
        fontfamily="monospace",
        zorder=10,
    )


# ── Animation state ───────────────────────────────────────────────────────────


def _orbital_position(seed: EntityPoint, beat: float) -> tuple[float, float]:
    """
    Compute current (x, y) for a seed particle.

    Orbit: the seed's native angle (theta) plus time-driven revolution,
    scaled by orbital_speed and base radius. Layers add parallax wobble.
    """
    base_theta = seed.theta
    revolution = 2 * math.pi * seed.orbital_speed * beat / FRAMES
    # Add a Lissajous-style wobble proportional to layer depth
    wobble = 0.04 * seed.layer * math.sin(3 * revolution + seed.theta)
    theta = base_theta + revolution
    r = seed.radius * 0.72 + wobble  # scale to fit axes
    return r * math.cos(theta), r * math.sin(theta)


def _sidewalk_drift(seed: EntityPoint, beat: float) -> float:
    """
    sidewalkDrift from binary-brewing-sifakis — temporal momentum decay.
    Returns a drift offset that grows then decays over the animation cycle.
    """
    t = beat / FRAMES
    # Bell curve centered at 0.5, amplitude scaled by layer
    return 0.06 * seed.layer * math.exp(-18 * (t - 0.5) ** 2)


# ── Main render ───────────────────────────────────────────────────────────────


def render(mood: str = ACTIVE_MOOD, out_path: Path | None = None) -> Path:
    palette = MOOD_PALETTES.get(mood, MOOD_PALETTES["playful"])
    colors = palette["colors"]
    glow = palette["glow"]

    out_path = out_path or (OUT_DIR / "atlas_polar_field.gif")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = _make_fig(palette)
    _draw_static_layer(ax, palette)

    trails: list[Trail] = [Trail() for _ in SEEDS]

    # Dynamic objects (will be cleared/redrawn each frame)
    scatter_artists: list[Any] = []
    trail_artists: list[Any] = []
    label_artists: list[Any] = []
    beat_text: list[Any] = []
    glow_artists: list[Any] = []
    arc_artists: list[Any] = []

    def _clear_dynamic() -> None:
        for a in scatter_artists + trail_artists + label_artists + beat_text + glow_artists + arc_artists:
            a.remove()
        scatter_artists.clear()
        trail_artists.clear()
        label_artists.clear()
        beat_text.clear()
        glow_artists.clear()
        arc_artists.clear()

    def _draw_frame(beat: int) -> list[Any]:
        if beat > 0:
            _clear_dynamic()

        # Beat counter
        bt = ax.text(
            1.3,
            -1.32,
            f"beat {beat:02d}",
            color="#ffffff33",
            fontsize=6,
            ha="right",
            va="bottom",
            fontfamily="monospace",
            zorder=10,
        )
        beat_text.append(bt)

        # Sidewalk drift indicator
        total_drift = sum(_sidewalk_drift(s, beat) for s in SEEDS)
        dr = ax.text(
            -1.3,
            -1.32,
            f"drift {total_drift:.3f}",
            color="#ffffff22",
            fontsize=6,
            ha="left",
            va="bottom",
            fontfamily="monospace",
            zorder=10,
        )
        beat_text.append(dr)

        # Arc from origin to each seed at native theta (attention span)
        for i, seed in enumerate(SEEDS):
            color = colors[i % len(colors)]
            θ = seed.theta
            arc_x = [0, 0.9 * math.cos(θ)]
            arc_y = [0, 0.9 * math.sin(θ)]
            pulse = 0.08 * math.sin(2 * math.pi * beat / FRAMES * seed.orbital_speed * 4)
            arc_alpha = max(0.0, min(1.0, 0.07 + pulse))
            al = ax.plot(arc_x, arc_y, color=color, alpha=arc_alpha, linewidth=0.6, zorder=2)[0]
            arc_artists.append(al)

        # Per-seed particles
        for i, seed in enumerate(SEEDS):
            color = colors[i % len(colors)]
            x, y = _orbital_position(seed, beat)
            drift = _sidewalk_drift(seed, beat)
            x += drift * math.cos(seed.theta + math.pi / 2)
            y += drift * math.sin(seed.theta + math.pi / 2)

            trails[i].push(x, y)

            # Trail
            trail = trails[i].positions
            if len(trail) > 1:
                txs = [p[0] for p in trail]
                tys = [p[1] for p in trail]
                alphas = np.linspace(0.02, seed.alpha * 0.55, len(trail))
                sizes = np.linspace(seed.base_size * 0.05, seed.base_size * 0.45, len(trail))
                for j in range(len(trail) - 1):
                    ta = ax.scatter(txs[j], tys[j], s=sizes[j], c=color, alpha=float(alphas[j]), zorder=5)
                    trail_artists.append(ta)

            # Outer glow halo
            g1 = ax.scatter(x, y, s=seed.base_size * 3.2, c=color, alpha=seed.alpha * 0.12, zorder=6)
            g2 = ax.scatter(x, y, s=seed.base_size * 1.8, c=color, alpha=seed.alpha * 0.22, zorder=7)
            glow_artists.extend([g1, g2])

            # Core particle
            sc = ax.scatter(
                x, y, s=seed.base_size, c=color, alpha=seed.alpha, zorder=8, edgecolors=glow, linewidths=0.8
            )
            scatter_artists.append(sc)

            # Layer-depth marker (small inner dot for hierarchy depth)
            layer_scale = 0.15 + seed.layer * 0.12
            ld = ax.scatter(x, y, s=seed.base_size * layer_scale, c=palette["bg"], alpha=0.9, zorder=9)
            scatter_artists.append(ld)

            # Seed label (fades in over first 20 frames)
            label_alpha = min(1.0, beat / 20) * 0.72
            lbl = ax.text(
                x + 0.04,
                y + 0.04,
                seed.label,
                color=color,
                fontsize=5.8,
                alpha=label_alpha,
                fontfamily="monospace",
                zorder=11,
                ha="left",
                va="bottom",
            )
            label_artists.append(lbl)

            # G and score readout on hover (show at peak drift)
            if abs(drift) > 0.02:
                meta = ax.text(
                    x - 0.04,
                    y - 0.06,
                    f"G={seed.g} s={seed.score} L{seed.layer}",
                    color="#ffffff55",
                    fontsize=4.8,
                    alpha=0.65,
                    fontfamily="monospace",
                    zorder=11,
                    ha="right",
                    va="top",
                )
                label_artists.append(meta)

        # Attention web: lines between seeds weighted by angular proximity
        for i in range(len(SEEDS)):
            for j in range(i + 1, len(SEEDS)):
                a, b = SEEDS[i], SEEDS[j]
                ang_dist = abs(a.theta - b.theta) * 180 / math.pi
                # Only draw if within 30° attention window (explorer preset)
                if ang_dist <= 30:
                    ax_i, ay_i = _orbital_position(a, beat)
                    ax_j, ay_j = _orbital_position(b, beat)
                    attention = max(0.0, 1.0 - ang_dist / 30)
                    drift_i = _sidewalk_drift(a, beat)
                    drift_j = _sidewalk_drift(b, beat)
                    ax_i += drift_i * math.cos(a.theta + math.pi / 2)
                    ay_i += drift_i * math.sin(a.theta + math.pi / 2)
                    ax_j += drift_j * math.cos(b.theta + math.pi / 2)
                    ay_j += drift_j * math.sin(b.theta + math.pi / 2)
                    web = ax.plot(
                        [ax_i, ax_j], [ay_i, ay_j], color=glow, alpha=attention * 0.28, linewidth=0.9, zorder=4
                    )[0]
                    arc_artists.append(web)

        return scatter_artists + trail_artists + label_artists + beat_text + glow_artists + arc_artists

    anim = FuncAnimation(
        fig,
        _draw_frame,
        frames=FRAMES,
        interval=INTERVAL_MS,
        blit=False,
    )

    writer = PillowWriter(fps=1000 // INTERVAL_MS)
    anim.save(str(out_path), writer=writer, dpi=DPI)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    import sys

    mood = sys.argv[1] if len(sys.argv) > 1 else ACTIVE_MOOD
    if mood not in MOOD_PALETTES:
        print(f"Unknown mood '{mood}'. Available: {', '.join(MOOD_PALETTES)}")
        sys.exit(1)

    print(f"Rendering atlas_polar_field.gif — mood={mood} — {FRAMES} frames...")
    out = render(mood=mood)
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"Done: {out}  ({size_mb:.1f} MB)")
