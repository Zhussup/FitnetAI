"""
Маршруты для администратора
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserProfile, ChangeHistory, BodyMetrics, WorkoutPlan, AIRequestLog
from ..schemas import AdminUserUpdate
from ..services.auth import get_email_from_auth_header, hash_password
from ..config import ADMIN_EMAIL

router = APIRouter(prefix="/api/admin", tags=["admin"])


def ensure_admin(auth_header: str) -> str:
    """Проверка, что пользователь админ"""
    email = get_email_from_auth_header(auth_header)
    if not email:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return email


@router.get("/users")
async def admin_list_users(request: Request, db: Session = Depends(get_db)):
    """Получить список всех пользователей (только для админа)"""
    ensure_admin(request.headers.get("Authorization"))
    
    users = db.query(User).all()
    profiles = {p.email: p for p in db.query(UserProfile).all()}

    result = []
    for u in users:
        p = profiles.get(u.email)
        result.append({
            "email": u.email,
            "gender": p.gender if p else "",
            "age": p.age if p else None,
            "height": p.height if p else None,
            "weight": p.weight if p else None,
            "created_at": p.created_at if p else None
        })
    return {"users": result}


@router.put("/users/{email}")
async def admin_update_user(
    email: str,
    payload: AdminUserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновление данных пользователя (только для админа)"""
    ensure_admin(request.headers.get("Authorization"))

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем пароль, если предоставлен
    if payload.password:
        user.password_hash = hash_password(payload.password)

    profile = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not profile:
        from datetime import datetime
        profile = UserProfile(email=email, created_at=datetime.now().isoformat())
        db.add(profile)

    if payload.gender is not None:
        profile.gender = payload.gender
    if payload.age is not None:
        profile.age = payload.age
    if payload.height is not None:
        profile.height = payload.height
    if payload.weight is not None:
        profile.weight = payload.weight

    db.commit()
    return {"status": "ok", "message": "Пользователь обновлен"}


@router.delete("/users/{email}")
async def admin_delete_user(
    email: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Удаление пользователя и его данных (только для админа)"""
    ensure_admin(request.headers.get("Authorization"))

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удаляем все данные пользователя
    db.query(UserProfile).filter(UserProfile.email == email).delete()
    db.query(ChangeHistory).filter(ChangeHistory.email == email).delete()
    db.query(BodyMetrics).filter(BodyMetrics.email == email).delete()
    db.query(WorkoutPlan).filter(WorkoutPlan.email == email).delete()
    db.query(AIRequestLog).filter(AIRequestLog.email == email).delete()
    db.delete(user)

    db.commit()
    return {"status": "ok", "message": "Пользователь удален"}
