from functools import lru_cache
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.groq_client import get_llm_client
from app.agents.tools import (
    extract_competitive_intelligence,
    log_interaction,
    log_resource_request,
    verify_compliance_guidelines,
)
from app.schemas.interaction import InteractionDraft


class HcpAgentState(TypedDict, total=False):
    transcript: str
    interaction: dict[str, Any]
    compliance_status: str
    resource_request: str | None
    competitive_intelligence: str | None
    draft: InteractionDraft


def analyze_transcript(transcript: str) -> InteractionDraft:
    """Run the HCP interaction through the LangGraph agent workflow."""
    _ensure_langchain_globals()
    result = _compiled_graph().invoke({"transcript": transcript})
    return result["draft"]


@lru_cache(maxsize=1)
def _compiled_graph():
    graph = StateGraph(HcpAgentState)
    graph.add_node("log_interaction", _log_interaction_node)
    graph.add_node("verify_compliance", _verify_compliance_node)
    graph.add_node("log_resource_request", _log_resource_request_node)
    graph.add_node("extract_competitive_intelligence", _competitive_intelligence_node)
    graph.add_node("build_draft", _build_draft_node)

    graph.set_entry_point("log_interaction")
    graph.add_edge("log_interaction", "verify_compliance")
    graph.add_edge("verify_compliance", "log_resource_request")
    graph.add_edge("log_resource_request", "extract_competitive_intelligence")
    graph.add_edge("extract_competitive_intelligence", "build_draft")
    graph.add_edge("build_draft", END)
    return graph.compile()


def _log_interaction_node(state: HcpAgentState) -> HcpAgentState:
    transcript = state["transcript"]
    llm_client = get_llm_client()
    return {"interaction": log_interaction(transcript, llm_client=llm_client)}


def _verify_compliance_node(state: HcpAgentState) -> HcpAgentState:
    return {"compliance_status": verify_compliance_guidelines(state["transcript"])}


def _log_resource_request_node(state: HcpAgentState) -> HcpAgentState:
    return {"resource_request": log_resource_request(state["transcript"])}


def _competitive_intelligence_node(state: HcpAgentState) -> HcpAgentState:
    return {"competitive_intelligence": extract_competitive_intelligence(state["transcript"])}


def _build_draft_node(state: HcpAgentState) -> HcpAgentState:
    interaction = state["interaction"]
    summary = interaction.get("draft_summary") or (
        f"{interaction['hcp_name']} discussed {interaction['product']} with "
        f"{interaction['sentiment']} sentiment. Compliance status: {state['compliance_status']}."
    )

    return {
        "draft": InteractionDraft(
            hcp_name=interaction["hcp_name"],
            product=interaction["product"],
            sentiment=interaction["sentiment"],
            interaction_type=interaction.get("interaction_type", "Meeting"),
            date=interaction.get("date", ""),
            time=interaction.get("time", ""),
            action_items=interaction["action_items"],
            compliance_status=state["compliance_status"],
            resource_request=state.get("resource_request"),
            competitive_intelligence=state.get("competitive_intelligence"),
            draft_summary=summary,
        )
    }


def _ensure_langchain_globals() -> None:
    try:
        import langchain
    except ImportError:
        return

    if not hasattr(langchain, "debug"):
        langchain.debug = False
    if not hasattr(langchain, "verbose"):
        langchain.verbose = False
    if not hasattr(langchain, "llm_cache"):
        langchain.llm_cache = None