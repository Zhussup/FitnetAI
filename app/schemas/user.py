"""
Схемы для пользовательских данных
"""
from pydantic import BaseModel
from typing import Optional


class UserFormData(BaseModel):
    email: str
    gender: str
    age: int
    height: float
    weight: float


class AdminUserUpdate(BaseModel):
    email: str
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    password: Optional[str] = None
