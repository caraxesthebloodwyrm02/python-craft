# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "mistralai>=2.0.0",
# ]
# ///
"""
Mistral Conversations API — beta.conversations.start
Agent: ag_019adec4bd40701496ebca54ed32e8b6 v21
"""

import os

from mistralai import Mistral
from craft.gridstral_profile import GRIDSTRAL_AGENT_ID, GRIDSTRAL_AGENT_VERSION

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

inputs = [{"role": "user", "content": "Hello!"}]

response = client.beta.conversations.start(
    agent_id=GRIDSTRAL_AGENT_ID,
    agent_version=GRIDSTRAL_AGENT_VERSION,
    inputs=inputs,
)

if os.environ.get("CRAFT_VERBOSE", "").lower() in ("1", "true", "yes"):
    print(response)
