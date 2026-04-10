from __future__ import annotations

import numpy as np
import pandas as pd
import torch


def summarize_tensor_and_frame(values: list[float]) -> dict[str, float]:
    tensor = torch.tensor(values, dtype=torch.float32)
    weights = torch.softmax(tensor, dim=0)
    weighted = tensor * weights
    frame = pd.DataFrame({"value": tensor.numpy(), "weight": weights.numpy(), "weighted": weighted.numpy()})
    matrix = np.stack([frame["value"].to_numpy(), frame["weighted"].to_numpy()], axis=0)
    return {
        "mean": float(matrix.mean()),
        "std": float(matrix.std()),
        "max_weight": float(frame["weight"].max()),
        "sum_weighted": float(frame["weighted"].sum()),
    }
