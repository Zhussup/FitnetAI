"""
Маршруты для дашборда и питания
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
from ..database import get_db
from ..models import User, UserProfile, ChangeHistory, BodyMetrics
from ..schemas import DashboardData
from ..services.nutrition import calculate_nutrition_norms
from datetime import datetime

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.post("/dashboard-submit")
async def dashboard_submit(data: DashboardData, db: Session = Depends(get_db)):
    """Сохранение данных дашборда (вода, белок, калории)"""
    try:
        # Проверяем пользователя
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"error": "User not found"}
            )
        
        # Получаем профиль для рисунка и веса
        profile = db.query(UserProfile).filter(
            UserProfile.email == data.email
        ).first()
        
        height = profile.height if profile and profile.height else 0.0
        weight = profile.weight if profile and profile.weight else 0.0
        
        # Расчет BMI
        bmi = 0.0
        if height > 0 and weight > 0:
            bmi = weight / ((height / 100) ** 2)
        
        # Создание записи истории
        record = ChangeHistory(
            email=data.email,
            height=height,
            weight=weight,
            bmi=bmi,
            water_intake_ml=data.water_intake_ml,
            protein_g=data.protein_g,
            calories_kcal=data.calories_kcal,
            program_name=data.program_name,
            recorded_at=datetime.utcnow()
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return {
            "status": "ok",
            "message": "Dashboard data saved",
            "id": record.id
        }
    except Exception as e:
        print(f"[dashboard_submit] Error: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/history")
async def get_history(email: str, db: Session = Depends(get_db)):
    """Получение истории изменений пользователя"""
    try:
        records = db.query(ChangeHistory).filter(
            ChangeHistory.email == email
        ).order_by(ChangeHistory.recorded_at.desc()).all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "date": record.recorded_at.strftime("%d.%m.%Y"),
                "time": record.recorded_at.strftime("%H:%M:%S"),
                "water_ml": record.water_intake_ml,
                "protein_g": record.protein_g,
                "calories_kcal": record.calories_kcal,
                "weight": record.weight,
                "height": record.height,
                "bmi": record.bmi,
                "program_name": record.program_name
            })
        
        return {"status": "ok", "history": history}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@router.get("/change-history")
async def get_change_history(email: str, db: Session = Depends(get_db)):
    """Получение полной истории изменений"""
    try:
        records = db.query(ChangeHistory).filter(
            ChangeHistory.email == email
        ).order_by(ChangeHistory.recorded_at.desc()).all()
        
        return {
            "status": "ok",
            "history": [
                {
                    "id": r.id,
                    "height": r.height,
                    "weight": r.weight,
                    "bmi": r.bmi,
                    "water_intake_ml": r.water_intake_ml,
                    "protein_g": r.protein_g,
                    "calories_kcal": r.calories_kcal,
                    "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None
                }
                for r in records
            ]
        }
    except Exception as e:
        print(f"[get_change_history] Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/dashboard-norms")
async def get_dashboard_norms(email: str, db: Session = Depends(get_db)):
    """Получение дневных норм и текущего потребления"""
    try:
        # Получаем профиль пользователя
        profile = db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
        if not profile:
            return JSONResponse(
                status_code=404,
                content={"error": "Профиль не найден"}
            )
        
        # Получаем последнюю запись (потребление сегодня)
        latest_record = db.query(ChangeHistory).filter(
            ChangeHistory.email == email
        ).order_by(ChangeHistory.recorded_at.desc()).first()
        
        # Получаем программу из последней записи или используем по умолчанию
        program_name = (
            latest_record.program_name 
            if latest_record and latest_record.program_name 
            else "Поддержание"
        )
        
        # Расчет норм
        norms = calculate_nutrition_norms(
            weight=profile.weight or 70,
            height=profile.height or 170,
            age=profile.age or 30,
            gender=profile.gender or "М",
            program_name=program_name
        )
        
        # Текущее потребление (значения за сегодня)
        current_consumption = {
            "calories": latest_record.calories_kcal if latest_record else 0,
            "protein": latest_record.protein_g if latest_record else 0,
            "water": latest_record.water_intake_ml if latest_record else 0
        }
        
        # Расчет оставшегося
        remaining = {
            "calories": max(0, norms["target_calories"] - current_consumption["calories"]),
            "protein": max(0, norms["target_protein"] - current_consumption["protein"]),
            "water": max(0, norms["target_water"] - current_consumption["water"])
        }
        
        return {
            "status": "ok",
            "norms": norms,
            "current": current_consumption,
            "remaining": remaining,
            "program_name": program_name
        }
    except Exception as e:
        print(f"[get_dashboard_norms] Error: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
