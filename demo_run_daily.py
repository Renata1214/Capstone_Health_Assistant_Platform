from datetime import date

from db.repository import HealthDataRepository
from graph.build import build_health_coach_graph
from graph.state import CoachState


def main():
    repo = HealthDataRepository()
    app = build_health_coach_graph(repo=repo)

    # Use the demo participant from your SQL seed: participant_code = 'DEMO01'
    demo_participant = repo.get_participant_by_code("DEMO01")
    if not demo_participant:
        raise RuntimeError("Demo participant DEMO01 not found. Check your seed data.")

    participant_id = demo_participant.id
    target_date = date.today()   # or a specific date with data

    initial_state = CoachState(
        participant_id=participant_id,
        target_date=target_date,
    )

    final_state = app.invoke(initial_state)
    print(final_state.keys())

    print("=== Morning Summary ===")
    # ✅ Access as dictionary key instead of attribute
    print(final_state.get('morning_summary') or "No summary generated.")

    print("\n=== Micro-Interventions ===")
    # ✅ Access as dictionary key
    interventions = final_state.get('micro_interventions', [])
    for i, iv in enumerate(interventions, start=1):
        print(f"{i}. [{iv.kind}] {iv.title}: {iv.description} (when: {iv.suggested_time})")


if __name__ == "__main__":
    main()