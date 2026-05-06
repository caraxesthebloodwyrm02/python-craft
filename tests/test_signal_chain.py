"""Verify simulate() reproduces the original hardcoded samples exactly.

These values were the "from simulation" constants in the pre-refactor
out/signal_chain_gruff.original.py. They are the ground truth the fixture
must reproduce — if they drift, the spec is mis-parameterized.
"""
from __future__ import annotations

import numpy as np
import pytest

from craft.signal_chain_spec import SignalChainSpec, simulate


RAW = np.array([0.10, 0.30, 0.50, 0.65, 0.80, 0.90, 1.00])

EXPECTED = {
    "compressed": [0.1150, 0.3450, 0.5750, 0.7475, 0.7968, 0.8296, 0.8625],
    "abrasive":   [0.2539, 0.6564, 0.8736, 0.9512, 0.9651, 0.9730, 0.9798],
    "limited":    [0.2539, 0.6564, 0.8736, 0.8913, 0.8913, 0.8913, 0.8913],
    "blended":    [0.1693, 0.4604, 0.6681, 0.7586, 0.8411, 0.8961, 0.9511],
    "out":        [0.1730, 0.4717, 0.6871, 0.7832, 0.8714, 0.8913, 0.8913],
    "prox":       [0.194,  0.529,  0.771,  0.879,  0.978,  1.000,  1.000],
}


@pytest.fixture
def samples():
    return simulate(SignalChainSpec(), RAW)


@pytest.mark.parametrize("key", list(EXPECTED.keys()))
def test_stage_matches_canonical(samples, key):
    got = samples[key]
    want = np.array(EXPECTED[key])
    np.testing.assert_allclose(got, want, atol=5e-4,
                               err_msg=f"stage '{key}' drifted from canonical samples")


def test_blend_is_parallel_not_series(samples):
    # Verify the fault F3 invariant: dry leg uses RAW, not COMPRESSED.
    spec = SignalChainSpec()
    expected = RAW * (1 - spec.wet_mix) + samples["limited"] * spec.wet_mix
    np.testing.assert_allclose(samples["blended"], expected, atol=1e-10)


def test_output_respects_ceiling(samples):
    spec = SignalChainSpec()
    assert np.all(samples["out"] <= spec.ceiling + 1e-10)


def test_determinism():
    a = simulate(SignalChainSpec(), RAW)
    b = simulate(SignalChainSpec(), RAW)
    for k in a:
        np.testing.assert_array_equal(a[k], b[k])
