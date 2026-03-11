"""
Схемы для тренировочных программ и расписаний
"""
from pydantic import BaseModel
from typing import Optional, List


class TrainingScheduleRequest(BaseModel):
    available_days: List[int]


class TrainingScheduleData(BaseModel):
    email: str
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None


class TrainingProgramRequest(BaseModel):
    goal: Optional[str] = None


class BodyMetricsData(BaseModel):
    email: str
    height: float
    weight: float


class WorkoutPlanData(BaseModel):
    email: str
    title: str
    description: str
    video_url: str
    duration_minutes: int
