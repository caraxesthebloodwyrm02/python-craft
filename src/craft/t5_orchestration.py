from __future__ import annotations

from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph
from pydantic import BaseModel


class PromptSpec(BaseModel):
    query: str
    max_steps: int = 2


class FlowState(TypedDict):
    query: str
    answer: str


def build_chain() -> RunnableLambda:
    return RunnableLambda(lambda x: {"query": x["query"], "answer": f"echo:{x['query']}"})


def build_langgraph() -> object:
    graph = StateGraph(FlowState)

    def run_step(state: FlowState) -> FlowState:
        return {"query": state["query"], "answer": f"ok:{state['query']}"}

    graph.add_node("run", run_step)
    graph.set_entry_point("run")
    graph.add_edge("run", END)
    return graph.compile()
