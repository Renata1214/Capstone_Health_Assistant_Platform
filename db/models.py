# healthsync_ai/db/models.py
from datetime import date, datetime, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

#BaseModel provides automatic validation and structure for data.
class Participant(BaseModel):
    id: str
    email: str
    participant_code: str
    role: str


class Meal(BaseModel):
    id: str
    eaten_at: datetime
    description: Optional[str] = None
    estimated_calories: Optional[int] = None
    storage_path: Optional[str] = None


class WaterIntake(BaseModel):
    date: date
    liters: float


class DailyCheckin(BaseModel):
    date: date
    mood_1_5: Optional[int] = None
    fatigue_1_5: Optional[int] = None
    soreness_1_5: Optional[int] = None
    stress_1_5: Optional[int] = None
    motivation_1_5: Optional[int] = None
    free_text: Optional[str] = None


class Biometric(BaseModel):
    recorded_at: datetime
    resting_hr: Optional[int] = None
    hrv_rmssd: Optional[float] = None
    sleep_duration_minutes: Optional[int] = None
    sleep_onset: Optional[time] = None
    sleep_offset: Optional[time] = None
    steps: Optional[int] = None
    rpe_0_10: Optional[int] = None
    source: Optional[str] = None


class ChatEntry(BaseModel):
    date: date
    role: str
    content: str
    field_context: Optional[str] = None
    created_at: datetime


class DailyChatProgress(BaseModel):
    date: date
    stress_context: Optional[str] = None
    recovery_action: Optional[str] = None
    nutrition_note: Optional[str] = None
    sleep_quality_text: Optional[str] = None


class DailyContextPacket(BaseModel):
    """
    This is the core object the agentic system will consume.
    It abstracts away the underlying tables so schema changes are localized.
    """
    participant_id: str
    target_date: date

    # Raw data
    meals: List[Meal] = []
    water: Optional[WaterIntake] = None
    biometrics: List[Biometric] = []
    daily_checkin: Optional[DailyCheckin] = None
    chat_entries: List[ChatEntry] = []
    chat_progress: Optional[DailyChatProgress] = None

    # Reserved for derived features (to be filled later)
    derived_features: Dict[str, Any] = {}
