from __future__ import annotations

from dataclasses import dataclass

import faiss
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class IndexStats:
    dimension: int
    items: int


def build_faiss_index(vectors: np.ndarray) -> IndexStats:
    if vectors.ndim != 2:
        raise ValueError("vectors must be 2D")
    dim = int(vectors.shape[1])
    index = faiss.IndexFlatIP(dim)
    payload = vectors.astype("float32")
    faiss.normalize_L2(payload)
    index.add(payload)
    return IndexStats(dimension=dim, items=int(index.ntotal))


def plot_similarity(scores: list[float]) -> None:
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(scores)
    ax.set_title("Similarity Trend")
    ax.set_xlabel("step")
    ax.set_ylabel("score")
    fig.tight_layout()
