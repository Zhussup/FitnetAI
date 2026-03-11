"""
Pydantic схемы для HTTP запросов/ответов
"""
from .auth import (
    SignupRequest,
    LoginRequest,
    UpdatePasswordRequest,
    UpdateEmailRequest
)
from .user import UserFormData, AdminUserUpdate
from .workout import (
    TrainingScheduleRequest,
    TrainingScheduleData,
    TrainingProgramRequest,
    BodyMetricsData,
    WorkoutPlanData
)
from .nutrition import DashboardData
from .chat import Message

__all__ = [
    "SignupRequest",
    "LoginRequest",
    "UpdatePasswordRequest",
    "UpdateEmailRequest",
    "UserFormData",
    "AdminUserUpdate",
    "TrainingScheduleRequest",
    "TrainingScheduleData",
    "TrainingProgramRequest",
    "BodyMetricsData",
    "WorkoutPlanData",
    "DashboardData",
    "Message"
]
