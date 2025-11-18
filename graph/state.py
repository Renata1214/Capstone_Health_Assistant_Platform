# healthsync_ai/graph/state.py
#add extra fields in CoachState if increase the number of functionalities
#The single source of truth about everything the agent knows, collects, derives, and produces during the reasoning cycle.
#This object is passed from node to node in the LangGraph graph.
#Each node reads some fields and writes others, gradually enriching the state until the final output is ready.


"""It defines:
The structure of all information needed by your agentic workflow.
The inputs, intermediate signals, and final outputs.
A central memory object shared across all nodes in LangGraph.
A safe, extensible format that won’t break when your schema changes."""


from datetime import date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

#imports from other files
from db.models import DailyContextPacket


class Intervention(BaseModel):
    """Define an intervetion based on the daily context packet 
        (we can change the format later)"""
    kind: str  # "cognitive", "physical", "social", "behavioral"
    title: str
    description: str
    suggested_time: Optional[str] = None  # e.g. "morning", "evening"


class CoachState(BaseModel):
    """
    Shared state for the LangGraph workflow.
    """
    participant_id: str
    target_date: date

    # Raw and derived context
    context_packet: Optional[DailyContextPacket] = None
    analysis_summary: Optional[str] = None
    gap_explanation: Optional[str] = None  # physical vs mental state
    plan_notes: Optional[str] = None

    # Outputs
    morning_summary: Optional[str] = None
    #Multiple micro_interventions
    micro_interventions: List[Intervention] = Field(default_factory=list)

    # For learning loop later
    metadata: Dict[str, Any] = Field(default_factory=dict)
