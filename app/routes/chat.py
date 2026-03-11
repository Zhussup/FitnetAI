"""
Маршруты для чата с AI
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
from ..database import get_db
from ..models import AIRequestLog
from ..schemas import Message
from ..services.auth import get_email_from_auth_header
from ..services.ai import call_groq_api, build_user_prompt
from datetime import datetime

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/ai-health")
async def ai_health():
    """Проверка здоровья AI - небольшой тестовый вызов"""
    try:
        text = await call_groq_api("Hi", temperature=0.0, max_tokens=8)
        return {"status": "ok", "example": text or ""}
    except Exception as e:
        print("[ai_health] Error:", str(e))
        return JSONResponse(
            status_code=502,
            content={"status": "error", "detail": str(e)}
        )


@router.post("/chat")
async def api_chat(
    msg: Message,
    request: Request,
    db: Session = Depends(get_db)
):
    """Отправка сообщения в чат с AI"""
    try:
        # Валидация ввода
        if not getattr(msg, "message", None) or not msg.message.strip():
            return JSONResponse(
                status_code=400,
                content={"reply": "Пустое сообщение"}
            )

        # Проверка авторизации
        email = get_email_from_auth_header(request.headers.get("Authorization"))
        if not email:
            return JSONResponse(
                status_code=401,
                content={"reply": "Требуется вход в систему"}
            )

        # Логирование входящего сообщения
        try:
            print(f"[api_chat] {email}: {msg.message}")
        except Exception:
            print("[api_chat] Incoming message: <unserializable>")

        # Построение системного промпта с данными пользователя
        system_prompt = build_user_prompt(email, db)

        # Вызов Groq API
        try:
            text = await call_groq_api(
                msg.message,
                temperature=0.7,
                max_tokens=1024,
                system_prompt=system_prompt
            )

            # Логирование в ai_request_logs
            log_row = AIRequestLog(
                email=email,
                user_request=msg.message,
                ai_response=text,
                timestamp=datetime.utcnow(),
            )
            db.add(log_row)
            db.commit()

            return {"reply": text}
        except Exception as ai_exc:
            print("[api_chat] AI generation error:", str(ai_exc))
            traceback.print_exc()
            return JSONResponse(
                status_code=502,
                content={"reply": f"Ошибка AI: {str(ai_exc)}"}
            )
    
    except Exception as e:
        print("[api_chat] Unexpected error:", str(e))
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"reply": f"Ошибка сервера: {str(e)}"}
        )
