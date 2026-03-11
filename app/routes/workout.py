"""
Маршруты для программ тренировок и расписаний
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json
import traceback
from ..database import get_db
from ..models import User, UserProfile, TrainingSchedule, WorkoutPlan, BodyMetrics
from ..schemas import (
    TrainingScheduleRequest,
    TrainingScheduleData,
    TrainingProgramRequest,
    BodyMetricsData,
    WorkoutPlanData
)
from ..services.auth import get_email_from_auth_header
from ..services.workout import generate_training_plan
from ..services.nutrition import calculate_nutrition_norms
from ..utils import DAY_KEYS
from datetime import datetime

router = APIRouter(prefix="/api", tags=["workout"])


@router.post("/body-metrics")
async def body_metrics_submit(data: BodyMetricsData, db: Session = Depends(get_db)):
    """Сохранение параметров тела (рост, вес, BMI)"""
    try:
        # Проверяем пользователя
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"error": "User not found"}
            )
        
        # Расчет BMI
        height_m = data.height / 100
        bmi = data.weight / (height_m ** 2) if height_m > 0 else 0
        
        # Создание записи метрик
        metrics = BodyMetrics(
            email=data.email,
            height=data.height,
            weight=data.weight,
            bmi=bmi,
            measured_at=datetime.utcnow()
        )
        
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        
        return {
            "status": "ok",
            "message": "Body metrics saved",
            "id": metrics.id,
            "bmi": bmi
        }
    except Exception as e:
        print(f"[body_metrics] Error: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/workout-plan")
async def create_workout_plan(data: WorkoutPlanData, db: Session = Depends(get_db)):
    """Создание новой программы тренировок"""
    try:
        # Проверяем пользователя
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"error": "User not found"}
            )
        
        # Создание записи программы
        plan = WorkoutPlan(
            email=data.email,
            title=data.title,
            description=data.description,
            video_url=data.video_url,
            duration_minutes=data.duration_minutes,
            created_at=datetime.utcnow()
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        return {
            "status": "ok",
            "message": "Workout plan created",
            "id": plan.id
        }
    except Exception as e:
        print(f"[workout_plan] Error: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/workout-plans")
async def get_workout_plans(email: str, db: Session = Depends(get_db)):
    """Получение всех программ тренировок пользователя"""
    try:
        plans = db.query(WorkoutPlan).filter(
            WorkoutPlan.email == email
        ).order_by(WorkoutPlan.created_at.desc()).all()
        
        return {
            "status": "ok",
            "plans": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "video_url": p.video_url,
                    "duration_minutes": p.duration_minutes,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in plans
            ]
        }
    except Exception as e:
        print(f"[get_workout_plans] Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/training-schedule")
async def save_training_schedule(
    req: TrainingScheduleRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Сохранение доступных дней для тренировок"""
    try:
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        schedule = db.query(TrainingSchedule).filter(
            TrainingSchedule.email == email
        ).first()
        if schedule:
            schedule.available_days = json.dumps(req.available_days)
            schedule.updated_at = datetime.utcnow()
        else:
            schedule = TrainingSchedule(
                email=email,
                available_days=json.dumps(req.available_days),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(schedule)
        
        db.commit()
        return {"status": "ok", "message": "Дни тренировок сохранены"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/training-schedule")
async def get_training_schedule(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получение расписания тренировок пользователя"""
    try:
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        
        schedule = db.query(TrainingSchedule).filter(
            TrainingSchedule.email == email
        ).first()
        if not schedule:
            return {"status": "ok", "schedule": None}
        
        available_days = json.loads(
            schedule.available_days
        ) if schedule.available_days else []
        
        return {
            "status": "ok",
            "schedule": {
                "monday": json.loads(schedule.monday) if schedule.monday else None,
                "tuesday": json.loads(schedule.tuesday) if schedule.tuesday else None,
                "wednesday": json.loads(schedule.wednesday) if schedule.wednesday else None,
                "thursday": json.loads(schedule.thursday) if schedule.thursday else None,
                "friday": json.loads(schedule.friday) if schedule.friday else None,
                "saturday": json.loads(schedule.saturday) if schedule.saturday else None,
                "sunday": json.loads(schedule.sunday) if schedule.sunday else None,
                "available_days": available_days
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.put("/training-schedule/program")
async def update_training_program(
    req: TrainingScheduleData,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновление программы тренировок на конкретные дни"""
    try:
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        schedule = db.query(TrainingSchedule).filter(
            TrainingSchedule.email == email
        ).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Расписание не найдено")

        if req.monday is not None:
            schedule.monday = req.monday
        if req.tuesday is not None:
            schedule.tuesday = req.tuesday
        if req.wednesday is not None:
            schedule.wednesday = req.wednesday
        if req.thursday is not None:
            schedule.thursday = req.thursday
        if req.friday is not None:
            schedule.friday = req.friday
        if req.saturday is not None:
            schedule.saturday = req.saturday
        if req.sunday is not None:
            schedule.sunday = req.sunday

        schedule.updated_at = datetime.utcnow()
        db.commit()
        return {"status": "ok", "message": "Программа тренировок обновлена"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/training-program")
async def generate_training_program(
    req: TrainingProgramRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Генерация программы тренировок на основе доступных дней и цели"""
    try:
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        schedule = db.query(TrainingSchedule).filter(
            TrainingSchedule.email == email
        ).first()
        if not schedule:
            raise HTTPException(
                status_code=400,
                detail="Сначала выберите дни в расписании"
            )

        available_days = json.loads(
            schedule.available_days
        ) if schedule.available_days else []
        if not available_days:
            raise HTTPException(
                status_code=400,
                detail="Сначала выберите дни в расписании"
            )

        profile = db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
        height_cm = profile.height if profile else None
        weight_kg = profile.weight if profile else None

        goal = req.goal or "Рекомпозиция Тела"
        plan = generate_training_plan(available_days, goal, height_cm, weight_kg)

        for key in DAY_KEYS:
            data_for_day = plan.get(key, [])
            setattr(schedule, key, json.dumps(data_for_day))
        schedule.available_days = json.dumps(available_days)
        schedule.updated_at = datetime.utcnow()
        db.commit()

        return {
            "status": "ok",
            "program": plan,
            "available_days": available_days,
            "goal": goal
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
