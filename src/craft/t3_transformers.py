from __future__ import annotations

from typing import Any

from .quiet_defaults import apply_quiet_env_defaults

apply_quiet_env_defaults()

from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


def build_embedding_model(model_name: str = "BAAI/bge-small-en-v1.5") -> SentenceTransformer:
    return SentenceTransformer(model_name, device="cpu")


def quick_generate(prompt: str, model_name: str = "distilgpt2", max_new_tokens: int = 32) -> str:
    # Demo template: unpinned Hub pulls; pin revision for production (SECURITY_CONTINUITY.md).
    tok = AutoTokenizer.from_pretrained(model_name)  # nosec B615
    model = AutoModelForCausalLM.from_pretrained(model_name)  # nosec B615
    gen = pipeline("text-generation", model=model, tokenizer=tok, device=-1)
    outputs: list[dict[str, Any]] = gen(prompt, max_new_tokens=max_new_tokens, do_sample=False)
    return str(outputs[0]["generated_text"])
