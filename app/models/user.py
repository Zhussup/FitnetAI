"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    gender = Column(String)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    created_at = Column(String, default=datetime.now().isoformat())


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    user_request = Column(Text)
    ai_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BodyMetrics(Base):
    __tablename__ = "body_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    measured_at = Column(DateTime, default=datetime.utcnow)


class ChangeHistory(Base):
    __tablename__ = "change_history"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    water_intake_ml = Column(Float)
    protein_g = Column(Float)
    calories_kcal = Column(Float)
    program_name = Column(String, default="")
    recorded_at = Column(DateTime, default=datetime.utcnow)


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    video_url = Column(String)
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingSchedule(Base):
    __tablename__ = "training_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    monday = Column(String, default="")
    tuesday = Column(String, default="")
    wednesday = Column(String, default="")
    thursday = Column(String, default="")
    friday = Column(String, default="")
    saturday = Column(String, default="")
    sunday = Column(String, default="")
    available_days = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
