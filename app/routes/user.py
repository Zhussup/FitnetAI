"""
Маршруты для управления профилем пользователя
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserProfile
from ..schemas import UserFormData, UpdatePasswordRequest, UpdateEmailRequest
from ..services.auth import hash_password, verify_password, get_email_from_auth_header

router = APIRouter(prefix="/api", tags=["user"])


@router.post("/form-submit")
async def submit_form(data: UserFormData, db: Session = Depends(get_db)):
    """Сохранение данных формы профиля"""
    try:
        # Проверяем существование профиля
        existing_profile = db.query(UserProfile).filter(
            UserProfile.email == data.email
        ).first()
        
        if existing_profile:
            # Обновляем существующий профиль
            existing_profile.gender = data.gender
            existing_profile.age = data.age
            existing_profile.height = data.height
            existing_profile.weight = data.weight
        else:
            # Создаем новый профиль
            new_profile = UserProfile(
                email=data.email,
                gender=data.gender,
                age=data.age,
                height=data.height,
                weight=data.weight
            )
            db.add(new_profile)
        
        db.commit()
        return {"message": "Данные успешно сохранены", "status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка сохранения: {str(e)}"
        )


@router.get("/user-profile")
async def get_user_profile(email: str, db: Session = Depends(get_db)):
    """Получение профиля пользователя"""
    try:
        profile = db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Профиль не найден"
            )
        
        return {
            "email": profile.email,
            "gender": profile.gender,
            "age": profile.age,
            "height": profile.height,
            "weight": profile.weight
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/user/password")
async def update_password(
    req: UpdatePasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновление пароля пользователя"""
    try:
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(
                status_code=401,
                detail="Требуется авторизация"
            )
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден"
            )
        
        if not verify_password(req.current_password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Неверный текущий пароль"
            )
        
        user.password_hash = hash_password(req.new_password)
        db.commit()
        
        return {"status": "ok", "message": "Пароль успешно изменен"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.put("/user/email")
async def update_email(
    req: UpdateEmailRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновление email пользователя"""
    try:
        from ..models import AIRequestLog, BodyMetrics, ChangeHistory, WorkoutPlan, TrainingSchedule
        from ..services.auth import create_access_token
        
        auth_header = request.headers.get("Authorization")
        email = get_email_from_auth_header(auth_header)
        if not email:
            raise HTTPException(
                status_code=401,
                detail="Требуется авторизация"
            )
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден"
            )
        
        if not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Неверный пароль"
            )
        
        # Проверяем, не занят ли новый email
        existing = db.query(User).filter(User.email == req.new_email).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email уже используется"
            )
        
        old_email = user.email
        user.email = req.new_email
        
        # Обновляем email во всех таблицах
        db.query(UserProfile).filter(
            UserProfile.email == old_email
        ).update({"email": req.new_email})
        db.query(AIRequestLog).filter(
            AIRequestLog.email == old_email
        ).update({"email": req.new_email})
        db.query(BodyMetrics).filter(
            BodyMetrics.email == old_email
        ).update({"email": req.new_email})
        db.query(ChangeHistory).filter(
            ChangeHistory.email == old_email
        ).update({"email": req.new_email})
        db.query(WorkoutPlan).filter(
            WorkoutPlan.email == old_email
        ).update({"email": req.new_email})
        db.query(TrainingSchedule).filter(
            TrainingSchedule.email == old_email
        ).update({"email": req.new_email})
        
        db.commit()
        
        # Создаем новый токен с новым email
        new_token = create_access_token(req.new_email)
        
        return {
            "status": "ok",
            "message": "Email успешно изменен",
            "access_token": new_token
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
