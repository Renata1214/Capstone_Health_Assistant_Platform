# demo_run_daily_coach.py
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
        raise RuntimeError("Demo participant DEMO0v1 not found. Check your seed data.")

    participant_id = demo_participant["id"]
    target_date = date.today()   # or any date you have data for

    initial_state = CoachState(
        participant_id=participant_id,
        target_date=target_date,
    )

    final_state = app.invoke(initial_state)

    print("=== Morning Summary ===")
    print(final_state.morning_summary or "No summary generated.")

    print("\n=== Micro-Interventions ===")
    for i, iv in enumerate(final_state.micro_interventions, start=1):
        print(f"{i}. [{iv.kind}] {iv.title}: {iv.description} (when: {iv.suggested_time})")

if __name__ == "__main__":DailyContextPack
    main()
