"""
Схемы для питания и дашборда
"""
from pydantic import BaseModel


class DashboardData(BaseModel):
    email: str
    water_intake_ml: float
    protein_g: float
    calories_kcal: float
    program_name: str = ""
