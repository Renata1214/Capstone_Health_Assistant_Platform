# healthsync_ai/db/repository.py
#File that defines functions that extract through sql queries different insights about the data 
#Repository basically refers to class with methods to extract specific info or the summary from the user
from datetime import date, datetime, timedelta
from typing import Optional, List
import json
from supabase import create_client, Client

#Imports from other files (change later according to new added tables and so on)
from config import settings
from db.models import (
    Participant,
    Meal,
    WaterIntake,
    DailyCheckin,
    Biometric,
    ChatEntry,
    DailyChatProgress,
    DailyContextPacket,
)


def create_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


class HealthDataRepository:
    """
    Repository layer that encapsulates all DB access.
    If the schema changes, you mostly update this file.
    """

    def __init__(self, client: Optional[Client] = None):
        self.client: Client = client or create_supabase_client()

    # ---------- Participants ----------

    def get_participant_by_code(self, participant_code: str) -> Optional[Participant]:
        query = (
            self.client.table("participants")
            .select("*")
            .eq("participant_code", participant_code)
            .maybe_single()
        )
        resp = query.execute()
        if resp is None or getattr(resp, "data", None) is None:
            return None
        return Participant(**resp.data)

    # ---------- Daily context fetchers ----------

    def get_meals_for_date(self, participant_id: str, target_date: date) -> List[Meal]:
        """
        All meals eaten on target_date for this participant.
        """
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

        resp = (
            self.client.table("meals")
            .select("*")
            .eq("participant_id", participant_id)
            .gte("eaten_at", start.isoformat())
            .lt("eaten_at", end.isoformat())
            .execute()
        )
        rows = [] if resp is None or getattr(resp, "data", None) is None else resp.data
        return [Meal(**row) for row in rows]

    def get_water_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[WaterIntake]:
        query = (
            self.client.table("water_intake")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
        )
        resp = query.execute()
        if resp is None or getattr(resp, "data", None) is None:
            return None
        return WaterIntake(**resp.data)

    def get_daily_checkin_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[DailyCheckin]:
        query = (
            self.client.table("daily_checkins")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
        )
        resp = query.execute()
        if resp is None or getattr(resp, "data", None) is None:
            return None
        return DailyCheckin(**resp.data)

    def get_biometrics_for_date(
        self, participant_id: str, target_date: date
    ) -> List[Biometric]:
        """
        All biometric records recorded on target_date for this participant.
        """
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

        resp = (
            self.client.table("biometrics")
            .select("*")
            .eq("participant_id", participant_id)
            .gte("recorded_at", start.isoformat())
            .lt("recorded_at", end.isoformat())
            .execute()
        )
        rows = [] if resp is None or getattr(resp, "data", None) is None else resp.data
        return [Biometric(**row) for row in rows]

    def get_chat_entries_for_date(
        self, participant_id: str, target_date: date
    ) -> List[ChatEntry]:
        """
        All chat entries for this participant on target_date, ordered by time.
        """
        resp = (
            self.client.table("chat_entries")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .order("created_at", desc=False)
            .execute()
        )
        rows = [] if resp is None or getattr(resp, "data", None) is None else resp.data
        return [ChatEntry(**row) for row in rows]

    def get_chat_progress_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[DailyChatProgress]:
        query = (
            self.client.table("daily_chat_progress")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
        )
        resp = query.execute()
        if resp is None or getattr(resp, "data", None) is None:
            return None
        return DailyChatProgress(**resp.data)

    # ---------- Aggregated packet ----------

    def get_daily_context_packet(
        self, participant_id: str, target_date: date
    ) -> DailyContextPacket:
        """
        Main entrypoint for the agentic system.
        Fetches all relevant data for a participant on a given date.
        """
        meals = self.get_meals_for_date(participant_id, target_date)
        water = self.get_water_for_date(participant_id, target_date)
        checkin = self.get_daily_checkin_for_date(participant_id, target_date)
        biometrics = self.get_biometrics_for_date(participant_id, target_date)
        chat_entries = self.get_chat_entries_for_date(participant_id, target_date)
        chat_progress = self.get_chat_progress_for_date(participant_id, target_date)

        return DailyContextPacket(
            participant_id=participant_id,
            target_date=target_date,
            meals=meals,
            water=water,
            daily_checkin=checkin,
            biometrics=biometrics,
            chat_entries=chat_entries,
            chat_progress=chat_progress,
        )
