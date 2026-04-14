"""Process-wide defaults to cut library chatter on sync/async ML and LangGraph paths.

Call :func:`apply_quiet_env_defaults` **before** importing ``transformers``,
``langchain_core``, or ``langgraph`` so env-based log levels take effect.
"""

from __future__ import annotations

import os
import warnings
from typing import Mapping

_QUIET_ENV: Mapping[str, str] = {
    # LangSmith / tracing noise on ainvoke/astream when keys are absent
    "LANGCHAIN_TRACING_V2": "false",
    "LANGCHAIN_VERBOSE": "false",
    # Hugging Face hub / transformers console spam
    "TRANSFORMERS_VERBOSITY": "error",
    "HF_HUB_DISABLE_PROGRESS_BARS": "1",
    # Avoid tokenizer fork warnings in threaded/async hosts
    "TOKENIZERS_PARALLELISM": "false",
}


def apply_quiet_env_defaults(**overrides: str) -> None:
    """Set default env keys with ``setdefault`` so explicit user exports win.

    After env, best-effort ``langchain_core`` globals (no-op if not installed).
    """
    for key, value in {**_QUIET_ENV, **overrides}.items():
        os.environ.setdefault(key, value)
    _filter_known_upstream_warnings()
    _langchain_globals_quiet()


def _filter_known_upstream_warnings() -> None:
    """Drop single-message churn from optional stacks (e.g. LC on Python 3.14+)."""
    warnings.filterwarnings(
        "ignore",
        message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
        category=UserWarning,
    )


def _langchain_globals_quiet() -> None:
    try:
        from langchain_core.globals import set_debug, set_verbose
    except ImportError:
        return
    set_debug(False)
    set_verbose(False)
