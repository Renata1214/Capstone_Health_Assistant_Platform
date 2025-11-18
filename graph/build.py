# healthsync_ai/graph/build.py
from langgraph.graph import StateGraph, END

from db.repository import HealthDataRepository
from llm import LLMClient
from graph.state import CoachState
from graph.nodes import (
    make_fetch_context_node,
    make_analyze_gap_node,
    make_plan_interventions_node,
    make_generate_messages_node,
)


def build_health_coach_graph(
    repo: HealthDataRepository | None = None,
    llm: LLMClient | None = None,
):
    """
    Build and compile the LangGraph app for the daily coaching workflow.
    """

    repo = repo or HealthDataRepository()
    llm = llm or LLMClient()
    #Nodes (with LLM help) functions
    fetch_context = make_fetch_context_node(repo)
    analyze_gap = make_analyze_gap_node(llm)
    plan_interventions = make_plan_interventions_node(llm)
    generate_messages = make_generate_messages_node(llm)

    workflow = StateGraph(CoachState)

    # Nodes
    workflow.add_node("fetch_context", fetch_context)
    workflow.add_node("analyze_gap", analyze_gap)
    workflow.add_node("plan_interventions", plan_interventions)
    workflow.add_node("generate_messages", generate_messages)

    # Edges (simple linear pipeline for now)
    workflow.set_entry_point("fetch_context")
    workflow.add_edge("fetch_context", "analyze_gap")
    workflow.add_edge("analyze_gap", "plan_interventions")
    workflow.add_edge("plan_interventions", "generate_messages")
    workflow.add_edge("generate_messages", END)

    app = workflow.compile()    
    return app
