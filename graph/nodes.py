# healthsync_ai/graph/nodes.py
#A graph node = a function that transforms system state
#Each step is implemented as a node that receives a CoachState 
#object and returns the same object with new fields filled in.

#Architectural Pattern: every function returns another function (node factory)
#make_* creates a new node and the returned function executes the node, this allows 4
#dependency injection 

from datetime import date
from typing import Callable

from db.repository import HealthDataRepository
from db.models import DailyContextPacket
from llm import LLMClient
from graph.state import CoachState, Intervention


def make_fetch_context_node(repo: HealthDataRepository) -> Callable[[CoachState], CoachState]:
    """
    Returns a node function bound to a specific repository instance.
    """

    def fetch_context(state: CoachState) -> CoachState:
        packet: DailyContextPacket = repo.get_daily_context_packet(
            participant_id=state.participant_id,
            target_date=state.target_date,
        )
        state.context_packet = packet
        return state

    return fetch_context


#still need to structure the answer provided by the llm, can make a class to structure the answer
def make_analyze_gap_node(llm: LLMClient) -> Callable[[CoachState], CoachState]:
    """
    Uses LLM to analyze physical vs mental state gap.
    """

    def analyze_gap(state: CoachState) -> CoachState:
        if not state.context_packet:
            # In a real system you'd handle missing data more gracefully.
            state.gap_explanation = "No data available for this date."
            return state

        packet = state.context_packet

        # Build a concise description from numeric data.
        # This is deliberately compact so it's easy to adjust later.
        checkin = packet.daily_checkin
        biometrics = packet.biometrics

        numeric_summary = {
            "mood": getattr(checkin, "mood_1_5", None) if checkin else None,
            "fatigue": getattr(checkin, "fatigue_1_5", None) if checkin else None,
            "stress": getattr(checkin, "stress_1_5", None) if checkin else None,
            "sleep_minutes": biometrics[0].sleep_duration_minutes if biometrics else None,
            "resting_hr": biometrics[0].resting_hr if biometrics else None,
            "hrv_rmssd": biometrics[0].hrv_rmssd if biometrics else None,
        }

        system_msg = {
            "role": "system",
            "content": (
                "You are a health coach assistant. "
                "Given daily metrics and self-reports, explain in a few sentences "
                "how the user's physical state compares to their mental/emotional state."
            ),
        }

        user_msg = {
            "role": "user",
            "content": (
                f"Date: {state.target_date}\n"
                f"Numeric summary: {numeric_summary}\n"
                f"Checkin free text: {getattr(checkin, 'free_text', None) if checkin else None}\n"
            ),
        }

        explanation = llm.chat([system_msg, user_msg], temperature=0.3)
        state.gap_explanation = explanation
        state.analysis_summary = explanation  # reuse for now
        return state

    return analyze_gap


def make_plan_interventions_node(llm: LLMClient) -> Callable[[CoachState], CoachState]:
    """
    Plans micro-interventions based on gap analysis + context.
    """

    def plan(state: CoachState) -> CoachState:
        packet = state.context_packet
        gap = state.gap_explanation or "No gap explanation."
        if not packet:
            return state

        system_msg = {
            "role": "system",
            "content": (
                "You are a just-in-time health coach. "
                "Given the daily context and gap explanation, propose 1–3 specific, "
                "small micro-interventions for today. "
                "Each intervention must be labeled as cognitive, physical, social, or behavioral, "
                "and be realistic for a college student with limited time."
            ),
        }

        user_msg = {
            "role": "user",
            "content": (
                f"Date: {state.target_date}\n"
                f"Gap explanation: {gap}\n"
                f"Daily checkin: {packet.daily_checkin}\n"
                f"Water intake: {packet.water}\n"
                f"Meals: {packet.meals}\n"
                f"Biometrics: {packet.biometrics}\n"
                f"Chat progress: {packet.chat_progress}\n"
                "Respond in JSON with a list under 'interventions', "
                "each item having keys: kind, title, description, suggested_time."
            ),
        }

        raw = llm.chat([system_msg, user_msg], temperature=0.4)

        # For now, be conservative and parse with a try/except.
        # You can later replace this with a structured output parser.
        import json

        interventions: list[Intervention] = []
        try:
            parsed = json.loads(raw)
            for item in parsed.get("interventions", []):
                interventions.append(Intervention(**item))
        except Exception:
            # Fallback: treat whole message as one generic intervention
            interventions.append(
                Intervention(
                    kind="cognitive",
                    title="General advice",
                    description=raw,
                )
            )

        state.micro_interventions = interventions
        state.plan_notes = raw
        return state

    return plan


def make_generate_messages_node(llm: LLMClient) -> Callable[[CoachState], CoachState]:
    """
    Generates the final morning summary text and nicely phrased micro-interventions.
    """

    def generate(state: CoachState) -> CoachState:
        packet = state.context_packet

        system_msg = {
            "role": "system",
            "content": (
                "You are a warm, concise health coach. "
                "Write a short morning summary and bullet-point micro-interventions. "
                "Do not add new advice beyond what is in the interventions list."
            ),
        }

        user_msg = {
            "role": "user",
            "content": (
                f"Date: {state.target_date}\n"
                f"Gap explanation: {state.gap_explanation}\n"
                f"Interventions: {state.micro_interventions}\n"
                "Format your response as:\n"
                "MORNING_SUMMARY:\n"
                "<short paragraph>\n\n"
                "MICRO_INTERVENTIONS:\n"
                "- ...\n- ...\n"
            ),
        }

        text = llm.chat([system_msg, user_msg], temperature=0.4)
        state.morning_summary = text  # You can later parse sections if needed
        return state

    return generate
