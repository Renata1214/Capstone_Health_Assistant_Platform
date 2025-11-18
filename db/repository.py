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

#Access to the database
def create_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


class HealthDataRepository:
    """
    Repository layer that encapsulates all DB access.
    If schema changes, you mostly update this file.
    """

    def __init__(self, client: Optional[Client] = None):
        self.client: Client = client or create_supabase_client() #define link/client to the database

    # -------- Participants --------
    def get_participant_by_code(self, participant_code: str) -> Optional[Participant]:
        resp = (
            self.client.table("participants") #creates a query builder for the "participants" table.
            .select("*")
            .eq("participant_code", participant_code)
            .maybe_single() #f more than 1 row → raise error, 0 return none, 1 return it
            .execute()
        )

        data = resp.data
        if not data:
            return None
        return Participant(**data)

    # -------- Daily context fetchers --------
    def get_meals_for_date(self, participant_id: str, target_date: date) -> List[Meal]:
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
        return [Meal(**row) for row in (resp.data or [])]

    def get_water_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[WaterIntake]:
        resp = (
            self.client.table("water_intake")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
            .execute()
        )
        data = resp.data
        return WaterIntake(**data) if data else None

    def get_daily_checkin_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[DailyCheckin]:
        resp = (
            self.client.table("daily_checkins")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
            .execute()
        )
        data = resp.data
        return DailyCheckin(**data) if data else None

    def get_biometrics_for_date(
        self, participant_id: str, target_date: date
    ) -> List[Biometric]:
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
        return [Biometric(**row) for row in (resp.data or [])]

    def get_chat_entries_for_date(
        self, participant_id: str, target_date: date
    ) -> List[ChatEntry]:
        resp = (
            self.client.table("chat_entries")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .order("created_at", desc=False)
            .execute()
        )
        return [ChatEntry(**row) for row in (resp.data or [])]

    def get_chat_progress_for_date(
        self, participant_id: str, target_date: date
    ) -> Optional[DailyChatProgress]:
        resp = (
            self.client.table("daily_chat_progress")
            .select("*")
            .eq("participant_id", participant_id)
            .eq("date", target_date.isoformat())
            .maybe_single()
            .execute()
        )
        data = resp.data
        return DailyChatProgress(**data) if data else None

    # -------- Aggregated context packet --------
    def get_daily_context_packet(
        self, participant_id: str, target_date: date
    ) -> DailyContextPacket:
        """
        Main entrypoint for the agentic system.
        Fetches all relevant data for a participant on a date.
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
