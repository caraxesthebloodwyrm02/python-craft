"""Signal chain spec and simulation — single source of truth.

Topology:
    raw
    → compress(threshold, ratio, makeup, hard knee)
    → abrasive(tanh drive)
    → limit(ceiling)
    → blend(wet_mix)               [parallel: dry=raw, wet=limited]
    → + send_a + send_b            [additive bus sends]
    → limit(ceiling)
    = out

All stage samples derive from one SignalChainSpec + raw array via simulate().
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SignalChainSpec:
    # Compressor (linear-domain, hard knee)
    threshold: float = 0.65
    ratio: float = 3.5
    makeup: float = 1.15
    # Saturation (abrasive)
    drive: float = 2.2
    # Limiter
    ceiling: float = 0.8913
    # Parallel blend
    wet_mix: float = 0.45
    # Bus sends (contribution = raw * level * modulator * bus_trim)
    send_a_level: float = 0.30
    send_a_modulator: float = 0.15
    send_b_level: float = 0.25
    send_b_modulator: float = 0.83
    bus_trim: float = 0.15
    # Render layout
    stage_labels: tuple[str, ...] = (
        "SOURCE", "COMPRESS", "ABRASIVE", "LIMIT", "BLEND", "SENDS\nA+B", "OUTPUT",
    )


def simulate(spec: SignalChainSpec, raw: np.ndarray) -> dict[str, np.ndarray]:
    """Pure: spec + raw samples → all stage samples. Deterministic."""
    raw = np.asarray(raw, dtype=float)

    # COMPRESS: threshold + linear-domain ratio + makeup, hard knee.
    # Below threshold: passthrough. Above: core = t + (x−t)/r. Then × makeup, clip to 1.0.
    compressed_core = np.where(
        raw > spec.threshold,
        spec.threshold + (raw - spec.threshold) / spec.ratio,
        raw,
    )
    compressed = np.minimum(1.0, compressed_core * spec.makeup)

    # ABRASIVE: normalized tanh saturation.
    abrasive = np.tanh(compressed * spec.drive) / np.tanh(spec.drive)

    # LIMIT: hard ceiling.
    limited = np.minimum(abrasive, spec.ceiling)

    # BLEND: parallel — dry leg is RAW, wet leg is LIMITED.
    blended = raw * (1.0 - spec.wet_mix) + limited * spec.wet_mix

    # SENDS: additive bus contributions. Scale with raw, per-bus modulators, shared trim.
    send_a = raw * spec.send_a_level * spec.send_a_modulator * spec.bus_trim
    send_b = raw * spec.send_b_level * spec.send_b_modulator * spec.bus_trim

    # OUTPUT: blended + sends, ceiling-limited.
    out = np.minimum(blended + send_a + send_b, spec.ceiling)

    prox = out / spec.ceiling

    return {
        "raw": raw,
        "compressed": compressed,
        "abrasive": abrasive,
        "limited": limited,
        "blended": blended,
        "send_a": send_a,
        "send_b": send_b,
        "out": out,
        "prox": prox,
    }
