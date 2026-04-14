from __future__ import annotations

from dataclasses import dataclass

from .quiet_defaults import apply_quiet_env_defaults

apply_quiet_env_defaults()

import torch
from accelerate import Accelerator
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class FinetuneSurface:
    model_name: str
    train_rows: int
    trainable_params: int


def build_lora_surface(model_name: str = "sshleifer/tiny-gpt2") -> FinetuneSurface:
    accelerator = Accelerator(cpu=True)
    # Demo template: unpinned Hub pulls; pin revision for production (SECURITY_CONTINUITY.md).
    tokenizer = AutoTokenizer.from_pretrained(model_name)  # nosec B615
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)  # nosec B615
    lora_cfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, bias="none", task_type=TaskType.CAUSAL_LM)
    peft_model = get_peft_model(model, lora_cfg)
    ds = Dataset.from_dict({"text": ["hello world", "transformers stack"]})
    prepared_model, _prepared_ds = accelerator.prepare(peft_model, ds)
    trainable = sum(p.numel() for p in prepared_model.parameters() if p.requires_grad)
    _ = tokenizer
    return FinetuneSurface(model_name=model_name, train_rows=len(ds), trainable_params=int(trainable))
