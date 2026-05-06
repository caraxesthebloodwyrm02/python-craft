"""Canonical Gridstral profile metadata for python-craft artifacts."""

from __future__ import annotations

import os

GRIDSTRAL_AGENT_ID = os.environ.get("GRIDSTRAL_AGENT_ID", "ag_019adec4bd40701496ebca54ed32e8b6")
GRIDSTRAL_AGENT_VERSION = int(os.environ.get("GRIDSTRAL_AGENT_VERSION", "21"))
GRIDSTRAL_LABEL = "Gridstral / Mistral AI"


def short_agent_id(agent_id: str = GRIDSTRAL_AGENT_ID) -> str:
    """Return a short, log-safe agent identifier."""
    if len(agent_id) <= 12:
        return agent_id
    return f"{agent_id[:11]}..."
