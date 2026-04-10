from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LlamaSurface:
    model_path: str
    n_ctx: int
    n_gpu_layers: int


def create_llama_surface(model_path: str, n_ctx: int = 4096, n_gpu_layers: int = 0) -> LlamaSurface:
    from llama_cpp import Llama

    _ = Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=False)
    return LlamaSurface(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers)
