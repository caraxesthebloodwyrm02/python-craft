"""Context Weave — Programmable Reference Engine.

De-categorizes from low-value automation by encoding persona, memory,
preference, role, geolocation, season/color, community, and research
data into a dynamically shifting-cycle artifact with deep pattern
recognition and fold-architecture visibility.

Layers:
  1. Identity     → persona, role, station, archetype
  2. Geography    → geolocation metadata (Dhaka, Paris, Fort Worth)
  3. Temporal     → timestamps, filters, creation dates, seasons
  4. Preference   → warm tones, color spectrum, fluorescence
  5. Community    → class of 2021, Python safety, cross-references
  6. Research     → 4-wave sprint data (Talonflame, Bastiodon, GRID grep, Ori)
  7. Eligibility  → attribute catalog, dimensions, conditions
  8. Contrast     → fold architecture, shift-cycle, iterative delta

Output: out/context_weave.html (self-contained, warm-toned, geolocation-aware)
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# ── Constants ─────────────────────────────────────────────────────────────────

OUT_DIR = Path(__file__).parent.parent.parent / "out"
CREATED_AT = "2026-04-09T00:00:00+06:00"  # Dhaka timezone, session date

# ── Geolocation Registry ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class GeoAnchor:
    """A named geolocation with cultural and chromatic metadata."""

    id: str
    label: str
    city: str
    country: str
    lat: float
    lon: float
    timezone: str
    season: str  # current season at this location
    color_family: list[str] = field(default_factory=list)
    metaphor: str = ""
    cultural_note: str = ""


GEOANCHORS: dict[str, GeoAnchor] = {
    "prince": GeoAnchor(
        id="prince",
        label="Prince / Irfan",
        city="Dhaka",
        country="Bangladesh",
        lat=23.8103,
        lon=90.4125,
        timezone="Asia/Dhaka",
        season="pre-monsoon",  # April in Dhaka = Chaitra/Boishakh transition
        color_family=["#D4A017", "#FF6B35", "#E8963E", "#C73E1D", "#F4A460"],
        metaphor="গাঁদা ফুল গাছ — marigold pollinator, persistent warm bloom",
        cultural_note="Pohela Boishakh (Bengali New Year) falls mid-April; "
        "the transition from Chaitra to Boishakh is the hottest, "
        "most electric period before monsoon relief",
    ),
    "gridstral": GeoAnchor(
        id="gridstral",
        label="Gridstral / Mistral AI",
        city="Paris",
        country="France",
        lat=48.8566,
        lon=2.3522,
        timezone="Europe/Paris",
        season="spring",  # April in Paris
        color_family=["#4A90D9", "#7BB3F0", "#B8D4F0", "#E8E8E8", "#F5F5DC"],
        metaphor="Mistral wind — cold dry northerly that clears the sky, named for the wind that scours Provence clean",
        cultural_note="Founded 2023 by ex-DeepMind/Meta researchers; "
        "headquarters at 4 rue de Londres, 9th arrondissement",
    ),
    "twu": GeoAnchor(
        id="twu",
        label="Texas Wesleyan University",
        city="Fort Worth",
        country="USA",
        lat=32.7157,
        lon=-97.3269,
        timezone="America/Chicago",
        season="spring",  # April in Texas
        color_family=["#003087", "#FFD700", "#8B4513", "#228B22"],
        metaphor="Smaller. Smarter. — the TWU tagline; constraint as design, not limitation",
        cultural_note="CS 2019 cohort; the constraint of a small program produced focused, cross-domain practitioners",
    ),
}


# ── Persona Layer ─────────────────────────────────────────────────────────────


@dataclass
class PersonaBlock:
    """Wrapped identity block with metadata envelope."""

    id: str
    name: str
    station: str
    archetype: str
    traits: dict[str, float]
    geo_anchor: str
    scope: list[str]
    created: str = CREATED_AT
    version: str = "1.0.0"

    @property
    def fingerprint(self) -> str:
        """Deterministic content hash for provenance."""
        raw = f"{self.id}:{self.name}:{self.station}:{self.version}:{self.created}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def to_wrapped(self) -> dict[str, Any]:
        """Export as wrapped block with metadata envelope."""
        return {
            "_meta": {
                "type": "persona",
                "fingerprint": self.fingerprint,
                "created": self.created,
                "version": self.version,
                "geo_anchor": self.geo_anchor,
                "scope_filter": "last_6_months",
            },
            "payload": {
                "id": self.id,
                "name": self.name,
                "station": self.station,
                "archetype": self.archetype,
                "traits": self.traits,
                "scope": self.scope,
            },
        }


# ── Temporal Layer ────────────────────────────────────────────────────────────


@dataclass
class TemporalFilter:
    """Time-scoped filter with season and cultural awareness."""

    scope: str  # "last_24h", "last_7d", "last_6_months", "session"
    anchor_time: str = CREATED_AT
    geo_anchor: str = "prince"

    @property
    def season_context(self) -> dict[str, str]:
        geo = GEOANCHORS.get(self.geo_anchor)
        if not geo:
            return {"season": "unknown", "note": ""}
        return {
            "season": geo.season,
            "timezone": geo.timezone,
            "cultural_note": geo.cultural_note,
        }

    @property
    def scope_label(self) -> str:
        labels = {
            "last_24h": "Last 24 Hours",
            "last_7d": "Last 7 Days",
            "last_6_months": "Last 6 Months (Oct 2025 – Apr 2026)",
            "session": "Active Session",
        }
        return labels.get(self.scope, self.scope)


# ── Research Wave Layer ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class ResearchWave:
    """A single research wave from the 8-wave sprint."""

    number: int
    codename: str
    pokemon: str
    typing: str
    core_insight: str
    grid_mapping: str
    constraint_as_design: str
    metrics: dict[str, Any] = field(default_factory=dict)


RESEARCH_WAVES: list[ResearchWave] = [
    ResearchWave(
        number=1,
        codename="Talonflame",
        pokemon="Talonflame",
        typing="Fire/Flying",
        core_insight="Incinerate (3.0 DPT, 4.0 EPT, 5 turns) — "
        "slow wind-up for devastating energy gain. "
        "Elite Fast TM scarcity gate = access control.",
        grid_mapping="BoundaryEngine: slow initialization, high throughput once warm. Elite TM = API key gating.",
        constraint_as_design="4x Rock weakness accepted because 1500 CP ceiling "
        "compresses stats into a design space where tradeoffs are the point.",
        metrics={"dpt": 3.0, "ept": 4.0, "turns": 5, "cp_ceiling": 1500},
    ),
    ResearchWave(
        number=2,
        codename="Bastiodon",
        pokemon="Bastiodon",
        typing="Rock/Steel",
        core_insight="10 type resistances, 4x weakness to Fighting+Ground. "
        "Shield Pokemon. Sturdy survives any hit at 1HP. "
        "Soundproof filters noise.",
        grid_mapping="Admission Gate: 10 policy checks pass, but one 4x bypass "
        "(profit-masking) collapses it. fail-closed clarity.",
        constraint_as_design="FAVORED by 1500 CP compression — Bastiodon's low speed "
        "becomes irrelevant when the ceiling normalizes it. "
        "100M year fossil persistence = data durability.",
        metrics={"def": 168, "spd": 138, "spe": 30, "resistances": 10, "age_my": 100},
    ),
    ResearchWave(
        number=3,
        codename="GRID Grep",
        pokemon="—",
        typing="Analysis",
        core_insight="struggle=0 (CRITICAL VOID), threshold=1482 (dominant), "
        "weight|bias=703, integrat=866, cycle=205, momentum=184, "
        "resilien=158, compress=149, tension=22, oscillat=1.",
        grid_mapping="The codebase has 1482 thresholds but zero struggle. "
        "Struggle is what makes threshold meaningful — "
        "it's the void that gives the wall its purpose.",
        constraint_as_design="The absence is the finding. struggle=0 means the system "
        "has no language for difficulty, only for boundaries.",
        metrics={
            "struggle": 0,
            "threshold": 1482,
            "weight_bias": 703,
            "integrat": 866,
            "cycle": 205,
            "momentum": 184,
            "resilien": 158,
            "compress": 149,
            "tension": 22,
            "oscillat": 1,
        },
    ),
    ResearchWave(
        number=4,
        codename="Ori Deep Read",
        pokemon="—",
        typing="Architecture",
        core_insight="17 modules, 6 layers, 23 MCP tools, 24 registered projects. "
        "10-frame sequential animation (Disney principles). "
        "probe-recommend oscillation = squash-and-stretch.",
        grid_mapping="Ori's probe→filter→recommend cycle mirrors "
        "Disney's squash-and-stretch principle: "
        "compress data, then expand into actionable form.",
        constraint_as_design="Notebook = vessel (stores observations). "
        "Heatmap = GRUFF compass (navigates). "
        "Conditional rendering = 1500 CP ceiling in code.",
        metrics={"modules": 17, "layers": 6, "tools": 23, "projects": 24, "frames": 10},
    ),
]


# ── Community Layer ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CommunityRef:
    """A cross-reference to a community, cohort, or design lineage."""

    id: str
    label: str
    year: int | None
    domain: str
    acknowledgement: str
    safety_note: str = ""


COMMUNITY_REFS: list[CommunityRef] = [
    CommunityRef(
        id="twu-cs-2019",
        label="Texas Wesleyan CS Class of 2019",
        year=2019,
        domain="Computer Science",
        acknowledgement="Foundation: algorithms, data structures, software engineering. "
        "Smaller program = closer mentorship, cross-domain exposure.",
        safety_note="The constraint of a small cohort made each member visible — no hiding in the crowd.",
    ),
    CommunityRef(
        id="python-safety-2024",
        label="Python Safety & Design Community",
        year=2024,
        domain="Python / Open Source",
        acknowledgement="APIGuard on PyPI. GRID local-first. ruff as formatter. "
        "uv as package manager. Type hints as documentation. "
        "Python 3.13+ as baseline.",
        safety_note="fail-closed by convention. Type narrowing over type: ignore. Never bare except. Always specific.",
    ),
    CommunityRef(
        id="mcp-2025",
        label="Model Context Protocol Ecosystem",
        year=2025,
        domain="AI Infrastructure",
        acknowledgement="12 TypeScript MCP servers. shared-types as contract layer. "
        "Eligibility engine. Echoes audit trail. "
        "Zod v4, TypeScript v6 canonical.",
        safety_note="Cross-server contracts (audit.ndjson, snapshots, GATE) "
        "are the load-bearing walls — never break the schema.",
    ),
    CommunityRef(
        id="mistral-2023",
        label="Mistral AI Research Community",
        year=2023,
        domain="AI Research / Paris",
        acknowledgement="Founded by ex-DeepMind/Meta researchers. "
        "Open-weight philosophy. Mistral Large, Codestral, Devstral, "
        "Pixtral, Magistral, Voxtral, Leanstral.",
        safety_note="Gridstral agent (ag_019adec4) is the ecosystem's "
        "first external AI participant — provenance tracked.",
    ),
]


# ── Eligibility Dimension Snapshot ────────────────────────────────────────────


@dataclass(frozen=True)
class EligibilityDimension:
    """Snapshot of an eligibility attribute for the fold architecture."""

    id: str
    label: str
    dimension: str
    polarity: str
    band: tuple[float, float]
    hooks: list[str]


ELIGIBILITY_DIMS: list[EligibilityDimension] = [
    EligibilityDimension(
        "provenance-traceability",
        "Provenance traceability",
        "governance",
        "positive",
        (0.62, 0.84),
        ["show provenance in summaries"],
    ),
    EligibilityDimension(
        "fail-closed-clarity",
        "Fail-closed clarity",
        "governance",
        "positive",
        (0.54, 0.76),
        ["name the failure boundary"],
    ),
    EligibilityDimension(
        "operator-clarity", "Operator clarity", "usability", "positive", (0.57, 0.80), ["prefer short labels"]
    ),
    EligibilityDimension(
        "entry-friction",
        "Entry friction",
        "usability",
        "negative",
        (0.24, 0.48),
        ["annotate where the entry path feels heavy"],
    ),
    EligibilityDimension(
        "tool-call-fit",
        "Tool-call fit",
        "integration",
        "positive",
        (0.50, 0.76),
        ["show which tool surfaces are natural fits"],
    ),
    EligibilityDimension(
        "credit-visibility",
        "Credit visibility",
        "observability",
        "positive",
        (0.56, 0.82),
        ["credit every row to its source"],
    ),
    EligibilityDimension(
        "formula-readiness",
        "Formula readiness",
        "observability",
        "positive",
        (0.52, 0.82),
        ["keep output formula-friendly"],
    ),
    EligibilityDimension(
        "exclusive-boundary",
        "Exclusive boundary",
        "operational_fit",
        "positive",
        (0.58, 0.84),
        ["keep responsibility exclusive"],
    ),
]


# ── Color Spectrum (Warm Tones) ───────────────────────────────────────────────

WARM_SPECTRUM = {
    "amber": "#FFBF00",
    "gold": "#FFD700",
    "ember": "#E8601C",
    "coral": "#FF7F50",
    "marigold": "#D4A017",
    "saffron": "#F4C430",
    "terracotta": "#E2725B",
    "copper": "#B87333",
    "papaya": "#FF6B35",
    "sienna": "#E8963E",
}

COOL_CONTRAST = {
    "mistral_blue": "#4A90D9",
    "paris_sky": "#7BB3F0",
    "lavender": "#B8D4F0",
    "silver": "#C0C0C0",
}

FLUORESCENCE = {
    "pre_monsoon_glow": "linear-gradient(135deg, #FFBF00 0%, #FF6B35 50%, #C73E1D 100%)",
    "spring_paris": "linear-gradient(135deg, #4A90D9 0%, #7BB3F0 50%, #F5F5DC 100%)",
    "fold_contrast": "linear-gradient(135deg, #D4A017 0%, #4A90D9 50%, #E2725B 100%)",
}


# ── Shift-Cycle Engine ────────────────────────────────────────────────────────


@dataclass
class ShiftCycle:
    """Iterative shifting-cycle that makes the fold architecture visible."""

    beat: int = 0
    layers: list[str] = field(
        default_factory=lambda: [
            "identity",
            "geography",
            "temporal",
            "preference",
            "community",
            "research",
            "eligibility",
            "contrast",
        ]
    )

    @property
    def active_layer(self) -> str:
        return self.layers[self.beat % len(self.layers)]

    @property
    def cycle_number(self) -> int:
        return self.beat // len(self.layers)

    @property
    def phase_angle(self) -> float:
        """Radians through the current cycle."""
        return (self.beat % len(self.layers)) / len(self.layers) * 2 * math.pi

    def advance(self) -> str:
        """Advance one beat, return the newly active layer."""
        self.beat += 1
        return self.active_layer


# ── Fold Architecture ─────────────────────────────────────────────────────────


def compute_fold_contrast(geo_a: str, geo_b: str) -> dict[str, Any]:
    """Compute the contrast between two geo-anchored contexts.

    The 'fold' is where two contexts meet — Dhaka's pre-monsoon heat
    against Paris's spring clarity. The contrast makes both visible.
    """
    a = GEOANCHORS.get(geo_a)
    b = GEOANCHORS.get(geo_b)
    if not a or not b:
        return {"error": "unknown geo anchor"}

    # Haversine distance (km)
    R = 6371
    dlat = math.radians(b.lat - a.lat)
    dlon = math.radians(b.lon - a.lon)
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(a.lat)) * math.cos(math.radians(b.lat)) * math.sin(dlon / 2) ** 2
    )
    distance_km = 2 * R * math.asin(math.sqrt(h))

    # Season contrast
    season_pair = f"{a.season} × {b.season}"

    # Color blend point (midpoint of first colors)
    def hex_to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    c1 = hex_to_rgb(a.color_family[0]) if a.color_family else (128, 128, 128)
    c2 = hex_to_rgb(b.color_family[0]) if b.color_family else (128, 128, 128)
    blend = rgb_to_hex(
        (c1[0] + c2[0]) // 2,
        (c1[1] + c2[1]) // 2,
        (c1[2] + c2[2]) // 2,
    )

    return {
        "pair": f"{a.city} ↔ {b.city}",
        "distance_km": round(distance_km),
        "season_contrast": season_pair,
        "color_blend": blend,
        "metaphor_contrast": f"{a.metaphor.split('—')[0].strip()} × {b.metaphor.split('—')[0].strip()}",
        "fold_gradient": f"linear-gradient(135deg, {a.color_family[0]} 0%, {blend} 50%, {b.color_family[0]} 100%)",
    }


# ── HTML Artifact Generator ──────────────────────────────────────────────────


def _build_persona_section(persona: PersonaBlock) -> str:
    geo = GEOANCHORS.get(persona.geo_anchor)
    geo_badge = f"{geo.city}, {geo.country}" if geo else "Unknown"
    season_badge = geo.season if geo else "—"
    traits_rows = "\n".join(
        f'          <tr><td class="trait-name">{k}</td>'
        f'<td><div class="trait-bar"><div class="trait-fill" style="width:{v * 100:.0f}%"></div></div></td>'
        f"<td>{v:.2f}</td></tr>"
        for k, v in sorted(persona.traits.items(), key=lambda x: -x[1])
    )
    return f"""
    <section class="layer" id="layer-identity">
      <div class="layer-header">
        <span class="layer-number">01</span>
        <h2>Identity</h2>
        <span class="geo-badge">{geo_badge}</span>
        <span class="season-badge">{season_badge}</span>
      </div>
      <div class="persona-card">
        <div class="persona-meta">
          <span class="fingerprint">fp:{persona.fingerprint}</span>
          <span class="station">{persona.station}</span>
          <span class="version">v{persona.version}</span>
        </div>
        <h3>{persona.name}</h3>
        <p class="archetype">{persona.archetype}</p>
        <table class="trait-table">
          <thead><tr><th>Trait</th><th>Level</th><th>Value</th></tr></thead>
          <tbody>
{traits_rows}
          </tbody>
        </table>
      </div>
    </section>"""


def _build_geography_section() -> str:
    fold = compute_fold_contrast("prince", "gridstral")
    cards = ""
    for gid, geo in GEOANCHORS.items():
        colors = " ".join(f'<span class="color-dot" style="background:{c}"></span>' for c in geo.color_family[:5])
        cards += f"""
      <div class="geo-card" data-anchor="{gid}">
        <h4>{geo.label}</h4>
        <p class="geo-location">{geo.city}, {geo.country} ({geo.lat:.1f}, {geo.lon:.1f})</p>
        <p class="geo-season">{geo.season} · {geo.timezone}</p>
        <p class="geo-metaphor">{geo.metaphor}</p>
        <div class="color-row">{colors}</div>
        <p class="cultural-note">{geo.cultural_note}</p>
      </div>"""

    return f"""
    <section class="layer" id="layer-geography">
      <div class="layer-header">
        <span class="layer-number">02</span>
        <h2>Geography</h2>
        <span class="fold-badge">{fold["pair"]} · {fold["distance_km"]:,} km</span>
      </div>
      <div class="geo-grid">{cards}
      </div>
      <div class="fold-strip" style="background:{fold["fold_gradient"]}">
        <span class="fold-label">{fold["season_contrast"]}</span>
        <span class="fold-metaphor">{fold["metaphor_contrast"]}</span>
      </div>
    </section>"""


def _build_temporal_section() -> str:
    filters = [
        TemporalFilter("session"),
        TemporalFilter("last_24h"),
        TemporalFilter("last_7d"),
        TemporalFilter("last_6_months"),
    ]
    items = ""
    for f in filters:
        ctx = f.season_context
        items += f"""
      <div class="temporal-card">
        <h4>{f.scope_label}</h4>
        <p>{ctx["season"]} · {ctx.get("timezone", "")}</p>
        <p class="cultural-note">{ctx.get("cultural_note", "")}</p>
      </div>"""

    return f"""
    <section class="layer" id="layer-temporal">
      <div class="layer-header">
        <span class="layer-number">03</span>
        <h2>Temporal</h2>
        <span class="date-badge">{CREATED_AT}</span>
      </div>
      <div class="temporal-grid">{items}
      </div>
    </section>"""


def _build_research_section() -> str:
    cards = ""
    for w in RESEARCH_WAVES:
        metric_pills = " ".join(f'<span class="metric-pill">{k}: {v}</span>' for k, v in list(w.metrics.items())[:5])
        cards += f"""
      <div class="research-card wave-{w.number}">
        <div class="wave-header">
          <span class="wave-number">W{w.number}</span>
          <h4>{w.codename}</h4>
          <span class="typing-badge">{w.typing}</span>
        </div>
        <p class="insight">{w.core_insight}</p>
        <p class="grid-mapping"><strong>GRID →</strong> {w.grid_mapping}</p>
        <p class="constraint"><strong>Constraint as Design →</strong> {w.constraint_as_design}</p>
        <div class="metric-row">{metric_pills}</div>
      </div>"""

    return f"""
    <section class="layer" id="layer-research">
      <div class="layer-header">
        <span class="layer-number">06</span>
        <h2>Research Waves (1–4)</h2>
        <span class="count-badge">4 waves · 8 planned</span>
      </div>
      <div class="research-grid">{cards}
      </div>
    </section>"""


def _build_community_section() -> str:
    cards = ""
    for c in COMMUNITY_REFS:
        yr = str(c.year) if c.year else "—"
        cards += f"""
      <div class="community-card">
        <div class="community-header">
          <h4>{c.label}</h4>
          <span class="year-badge">{yr}</span>
          <span class="domain-badge">{c.domain}</span>
        </div>
        <p>{c.acknowledgement}</p>
        <p class="safety-note">{c.safety_note}</p>
      </div>"""

    return f"""
    <section class="layer" id="layer-community">
      <div class="layer-header">
        <span class="layer-number">05</span>
        <h2>Community</h2>
        <span class="count-badge">{len(COMMUNITY_REFS)} references</span>
      </div>
      <div class="community-grid">{cards}
      </div>
    </section>"""


def _build_eligibility_section() -> str:
    rows = ""
    for d in ELIGIBILITY_DIMS:
        pol_class = "positive" if d.polarity == "positive" else "negative"
        low, high = d.band
        width = (high - low) * 100
        left = low * 100
        rows += f"""
      <div class="elig-row">
        <span class="elig-label">{d.label}</span>
        <span class="elig-dim">{d.dimension}</span>
        <span class="elig-pol {pol_class}">{d.polarity}</span>
        <div class="band-bar">
          <div class="band-fill" style="left:{left:.0f}%;width:{width:.0f}%"></div>
        </div>
        <span class="elig-hook">{d.hooks[0] if d.hooks else ""}</span>
      </div>"""

    return f"""
    <section class="layer" id="layer-eligibility">
      <div class="layer-header">
        <span class="layer-number">07</span>
        <h2>Eligibility Dimensions</h2>
        <span class="count-badge">{len(ELIGIBILITY_DIMS)} attributes · 5 dimensions</span>
      </div>
      <div class="elig-grid">{rows}
      </div>
    </section>"""


def _build_contrast_section() -> str:
    fold = compute_fold_contrast("prince", "gridstral")
    fold_twu = compute_fold_contrast("prince", "twu")

    # Shift-cycle demonstration
    cycle = ShiftCycle()
    beats = []
    for _ in range(16):
        beats.append(
            {
                "beat": cycle.beat,
                "layer": cycle.active_layer,
                "cycle": cycle.cycle_number,
                "angle": f"{math.degrees(cycle.phase_angle):.0f}°",
            }
        )
        cycle.advance()

    beat_items = "\n".join(
        f'        <div class="beat-item" data-layer="{b["layer"]}">'
        f'<span class="beat-num">#{b["beat"]}</span>'
        f'<span class="beat-layer">{b["layer"]}</span>'
        f'<span class="beat-angle">{b["angle"]}</span></div>'
        for b in beats
    )

    return f"""
    <section class="layer" id="layer-contrast">
      <div class="layer-header">
        <span class="layer-number">08</span>
        <h2>Fold Architecture</h2>
        <span class="fold-badge">Contrast makes both sides visible</span>
      </div>
      <div class="fold-pair">
        <div class="fold-card" style="background:{fold["fold_gradient"]}">
          <h4>{fold["pair"]}</h4>
          <p>{fold["distance_km"]:,} km · {fold["season_contrast"]}</p>
          <p class="fold-metaphor">{fold["metaphor_contrast"]}</p>
        </div>
        <div class="fold-card" style="background:{fold_twu["fold_gradient"]}">
          <h4>{fold_twu["pair"]}</h4>
          <p>{fold_twu["distance_km"]:,} km · {fold_twu["season_contrast"]}</p>
          <p class="fold-metaphor">{fold_twu["metaphor_contrast"]}</p>
        </div>
      </div>
      <div class="shift-cycle">
        <h4>Shift-Cycle (16 beats × 8 layers = 2 full cycles)</h4>
        <div class="beat-grid">
{beat_items}
        </div>
      </div>
    </section>"""


def _build_preference_section() -> str:
    warm_swatches = "\n".join(
        f'      <div class="swatch" style="background:{v}"><span>{k}</span></div>' for k, v in WARM_SPECTRUM.items()
    )
    cool_swatches = "\n".join(
        f'      <div class="swatch cool" style="background:{v}"><span>{k}</span></div>'
        for k, v in COOL_CONTRAST.items()
    )
    gradient_strips = "\n".join(
        f'      <div class="gradient-strip" style="background:{v}"><span>{k}</span></div>'
        for k, v in FLUORESCENCE.items()
    )

    return f"""
    <section class="layer" id="layer-preference">
      <div class="layer-header">
        <span class="layer-number">04</span>
        <h2>Preference</h2>
        <span class="geo-badge">Warm Tones Canonical</span>
      </div>
      <div class="palette-section">
        <h4>Warm Spectrum</h4>
        <div class="swatch-grid">{warm_swatches}
        </div>
        <h4>Cool Contrast (Gridstral / Paris)</h4>
        <div class="swatch-grid">{cool_swatches}
        </div>
        <h4>Fluorescence Gradients</h4>
        <div class="gradient-grid">{gradient_strips}
        </div>
      </div>
    </section>"""


def render(output_path: str | None = None) -> str:
    """Render the full Context Weave artifact as self-contained HTML.

    Returns the HTML string. Writes to file if output_path or default out/ given.
    """
    prince = PersonaBlock(
        id="prince",
        name="Prince / Irfan",
        station="claude",
        archetype="Principal-Architect-Governor (Machiavelli's Prince)",
        traits={
            "strategic_clarity": 1.00,
            "authority_over_infrastructure": 1.00,
            "escalation_target": 0.95,
            "ground_truth_orientation": 0.90,
            "legibility_drive": 0.85,
            "scope_arbitration": 0.80,
        },
        geo_anchor="prince",
        scope=["CascadeProjects", "canopy", "roots", "seed", "grove", "plugins", "scripts", "skills"],
    )

    sections = [
        _build_persona_section(prince),
        _build_geography_section(),
        _build_temporal_section(),
        _build_preference_section(),
        _build_community_section(),
        _build_research_section(),
        _build_eligibility_section(),
        _build_contrast_section(),
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Context Weave — Programmable Reference Engine</title>
<meta name="created" content="{CREATED_AT}">
<meta name="generator" content="python-craft/context_weave v1.0.0">
<meta name="geo.anchor.primary" content="Dhaka, Bangladesh (23.81, 90.41)">
<meta name="geo.anchor.secondary" content="Paris, France (48.86, 2.35)">
<meta name="season.primary" content="pre-monsoon (Chaitra→Boishakh)">
<meta name="season.secondary" content="spring (Paris)">
<style>
:root {{
  --amber: #FFBF00;
  --gold: #FFD700;
  --ember: #E8601C;
  --coral: #FF7F50;
  --marigold: #D4A017;
  --saffron: #F4C430;
  --terracotta: #E2725B;
  --copper: #B87333;
  --papaya: #FF6B35;
  --sienna: #E8963E;
  --mistral-blue: #4A90D9;
  --paris-sky: #7BB3F0;
  --bg: #1a1410;
  --bg-card: #231e18;
  --bg-section: #1e1914;
  --text: #f0e6d8;
  --text-dim: #a89880;
  --text-accent: var(--gold);
  --border: #3a3028;
  --radius: 8px;
  --font-mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.6;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}}
header {{
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #1a1410 0%, #2a1f14 50%, #1a1410 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}}
header h1 {{
  font-size: 2rem;
  background: linear-gradient(135deg, var(--amber), var(--coral), var(--mistral-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}}
header .subtitle {{
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 0.85rem;
}}
header .meta-row {{
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}}
header .meta-row span {{
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-dim);
  padding: 0.25rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 4px;
}}
.layer {{
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background: var(--bg-section);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}}
.layer-header {{
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}}
.layer-number {{
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--marigold);
  background: rgba(212, 160, 23, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(212, 160, 23, 0.3);
}}
.layer-header h2 {{
  font-size: 1.25rem;
  color: var(--text-accent);
}}
.geo-badge, .season-badge, .fold-badge, .date-badge, .count-badge {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  padding: 0.15rem 0.5rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-left: auto;
}}
/* Persona Card */
.persona-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}}
.persona-meta {{
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}}
.persona-meta span {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border);
  border-radius: 3px;
}}
.fingerprint {{ color: var(--copper) !important; }}
.persona-card h3 {{ font-size: 1.1rem; color: var(--amber); margin-bottom: 0.25rem; }}
.archetype {{ color: var(--text-dim); font-style: italic; margin-bottom: 1rem; }}
.trait-table {{ width: 100%; border-collapse: collapse; }}
.trait-table th {{ text-align: left; color: var(--text-dim); font-size: 0.75rem; padding: 0.4rem 0; border-bottom: 1px solid var(--border); }}
.trait-table td {{ padding: 0.4rem 0; font-size: 0.85rem; }}
.trait-name {{ font-family: var(--font-mono); color: var(--saffron); }}
.trait-bar {{ width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; }}
.trait-fill {{ height: 100%; background: linear-gradient(90deg, var(--marigold), var(--amber)); border-radius: 3px; transition: width 0.6s ease; }}
/* Geo Cards */
.geo-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }}
.geo-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}}
.geo-card h4 {{ color: var(--amber); margin-bottom: 0.5rem; }}
.geo-location {{ font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-dim); }}
.geo-season {{ color: var(--saffron); font-size: 0.85rem; margin: 0.25rem 0; }}
.geo-metaphor {{ font-style: italic; color: var(--text-dim); font-size: 0.85rem; margin: 0.5rem 0; }}
.color-row {{ display: flex; gap: 6px; margin: 0.5rem 0; }}
.color-dot {{ width: 20px; height: 20px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.1); }}
.cultural-note {{ font-size: 0.8rem; color: var(--text-dim); margin-top: 0.5rem; }}
.fold-strip {{
  margin-top: 1rem;
  padding: 1rem 1.5rem;
  border-radius: var(--radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.fold-label {{ font-weight: 600; color: #1a1410; font-size: 0.9rem; }}
.fold-metaphor {{ font-style: italic; color: rgba(26,20,16,0.7); font-size: 0.85rem; }}
/* Temporal */
.temporal-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }}
.temporal-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
}}
.temporal-card h4 {{ color: var(--saffron); margin-bottom: 0.5rem; }}
/* Research */
.research-grid {{ display: grid; gap: 1rem; }}
.research-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}}
.wave-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }}
.wave-number {{
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--ember);
  background: rgba(232, 96, 28, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(232, 96, 28, 0.3);
}}
.wave-header h4 {{ color: var(--coral); }}
.typing-badge {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  margin-left: auto;
}}
.insight {{ margin-bottom: 0.5rem; }}
.grid-mapping, .constraint {{ font-size: 0.85rem; color: var(--text-dim); margin-bottom: 0.25rem; }}
.metric-row {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem; }}
.metric-pill {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--marigold);
  background: rgba(212, 160, 23, 0.08);
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  border: 1px solid rgba(212, 160, 23, 0.2);
}}
/* Community */
.community-grid {{ display: grid; gap: 1rem; }}
.community-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}}
.community-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; flex-wrap: wrap; }}
.community-header h4 {{ color: var(--amber); }}
.year-badge, .domain-badge {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border);
  border-radius: 3px;
}}
.safety-note {{
  font-size: 0.8rem;
  color: var(--copper);
  font-style: italic;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border);
}}
/* Eligibility */
.elig-grid {{ display: grid; gap: 0.5rem; }}
.elig-row {{
  display: grid;
  grid-template-columns: 180px 110px 70px 1fr 200px;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-size: 0.85rem;
}}
.elig-label {{ font-family: var(--font-mono); color: var(--saffron); font-size: 0.8rem; }}
.elig-dim {{ color: var(--text-dim); font-size: 0.75rem; }}
.elig-pol {{ font-family: var(--font-mono); font-size: 0.7rem; padding: 0.1rem 0.3rem; border-radius: 3px; }}
.elig-pol.positive {{ color: #4ade80; background: rgba(74, 222, 128, 0.08); }}
.elig-pol.negative {{ color: #f87171; background: rgba(248, 113, 113, 0.08); }}
.band-bar {{ width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; position: relative; }}
.band-fill {{ position: absolute; height: 100%; background: linear-gradient(90deg, var(--copper), var(--amber)); border-radius: 3px; }}
.elig-hook {{ color: var(--text-dim); font-size: 0.75rem; font-style: italic; }}
/* Palette */
.swatch-grid {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 0.75rem 0 1.5rem; }}
.swatch {{
  width: 90px;
  height: 48px;
  border-radius: 6px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 4px;
  border: 1px solid rgba(255,255,255,0.08);
}}
.swatch span {{
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: rgba(0,0,0,0.6);
  text-shadow: 0 0 4px rgba(255,255,255,0.3);
}}
.swatch.cool span {{ color: rgba(255,255,255,0.6); text-shadow: none; }}
.gradient-grid {{ display: grid; gap: 8px; margin: 0.75rem 0; }}
.gradient-strip {{
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding-left: 1rem;
}}
.gradient-strip span {{
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: rgba(0,0,0,0.5);
  text-shadow: 0 0 4px rgba(255,255,255,0.3);
}}
/* Fold / Contrast */
.fold-pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }}
.fold-card {{
  padding: 1.25rem;
  border-radius: var(--radius);
  color: #1a1410;
}}
.fold-card h4 {{ font-size: 1rem; margin-bottom: 0.25rem; }}
.fold-card p {{ font-size: 0.85rem; }}
.fold-card .fold-metaphor {{ font-style: italic; opacity: 0.7; margin-top: 0.25rem; }}
/* Shift Cycle */
.shift-cycle {{ margin-top: 1rem; }}
.shift-cycle h4 {{ color: var(--saffron); margin-bottom: 0.75rem; }}
.beat-grid {{ display: flex; gap: 4px; flex-wrap: wrap; }}
.beat-item {{
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.4rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px;
  min-width: 64px;
  font-size: 0.7rem;
}}
.beat-num {{ font-family: var(--font-mono); color: var(--text-dim); }}
.beat-layer {{ color: var(--marigold); font-family: var(--font-mono); font-size: 0.65rem; }}
.beat-angle {{ color: var(--text-dim); font-size: 0.6rem; }}
.beat-item[data-layer="identity"] {{ border-color: var(--amber); }}
.beat-item[data-layer="geography"] {{ border-color: var(--mistral-blue); }}
.beat-item[data-layer="temporal"] {{ border-color: var(--saffron); }}
.beat-item[data-layer="preference"] {{ border-color: var(--coral); }}
.beat-item[data-layer="community"] {{ border-color: var(--copper); }}
.beat-item[data-layer="research"] {{ border-color: var(--ember); }}
.beat-item[data-layer="eligibility"] {{ border-color: var(--terracotta); }}
.beat-item[data-layer="contrast"] {{ border-color: var(--papaya); }}
/* Footer */
footer {{
  text-align: center;
  margin-top: 3rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border);
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 0.75rem;
}}
footer .provenance {{ margin-top: 0.5rem; }}
@media (max-width: 768px) {{
  .elig-row {{ grid-template-columns: 1fr; }}
  .fold-pair {{ grid-template-columns: 1fr; }}
  .geo-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
  <header>
    <h1>Context Weave</h1>
    <p class="subtitle">Programmable Reference Engine — Fold Architecture v1.0.0</p>
    <div class="meta-row">
      <span>created: {CREATED_AT}</span>
      <span>geo: Dhaka ↔ Paris ↔ Fort Worth</span>
      <span>layers: 8</span>
      <span>waves: 4/8</span>
      <span>fp: {prince.fingerprint}</span>
    </div>
  </header>

{"".join(sections)}

  <footer>
    <p>Context Weave · python-craft · {CREATED_AT}</p>
    <p class="provenance">
      Prince/Irfan · caraxesthebloodwyrm02 · Uttara, Dhaka · CS TWU 2019<br>
      Gridstral · ag_019adec4bd40 · Mistral AI · Paris, France · 2023<br>
      Fold: pre-monsoon × spring · {compute_fold_contrast("prince", "gridstral")["distance_km"]:,} km
    </p>
  </footer>
</body>
</html>"""

    if output_path:
        out = Path(output_path)
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / "context_weave.html"

    out.write_text(html, encoding="utf-8")
    return html


def demo() -> None:
    """Generate the Context Weave artifact to out/context_weave.html."""
    html = render()
    print(f"Context Weave rendered → {OUT_DIR / 'context_weave.html'} ({len(html):,} bytes)")


if __name__ == "__main__":
    demo()
