"""
Маршруты для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import SignupRequest, LoginRequest
from ..services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/signup")
async def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.email == req.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже существует"
            )
        
        # Хешируем пароль и создаем пользователя
        password_hash = hash_password(req.password)
        new_user = User(email=req.email, password_hash=password_hash)
        
        db.add(new_user)
        db.commit()
        
        # Создаем токен
        token = create_access_token(req.email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Успешная регистрация"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка регистрации: {str(e)}"
        )


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Вход пользователя"""
    try:
        # Ищем пользователя
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Неверный email или пароль"
            )
        
        # Проверяем пароль
        if not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Неверный email или пароль"
            )
        
        # Создаем токен
        token = create_access_token(req.email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Успешный вход"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка входа: {str(e)}"
        )
