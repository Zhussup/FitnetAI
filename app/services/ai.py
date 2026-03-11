"""
Сервис для работы с AI API (Groq)
"""
import httpx
import traceback
from typing import Optional
from sqlalchemy.orm import Session
from ..config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_BASE
from ..models import UserProfile, BodyMetrics


async def call_groq_api(
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None
) -> str:
    """Вызов Groq API для генерации ответа"""
    try:
        if not GROQ_API_KEY or GROQ_API_KEY.strip() == "":
            raise Exception("GROQ_API_KEY is empty or not set in .env")
        
        print(f"[groq] API key loaded: {GROQ_API_KEY[:10]}...")
        
        async with httpx.AsyncClient(verify=False) as client:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            url = f"{GROQ_API_BASE}/chat/completions"
            print(f"[groq] Calling {url} with model={GROQ_MODEL}")
            
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                print(f"[groq] API error {response.status_code}: {response.text}")
                raise Exception(f"Groq API returned {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Извлечение текста из OpenAI-compatible ответа
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            
            raise Exception(f"Unexpected Groq response format: {data}")
    
    except Exception as e:
        print(f"[groq] Exception: {str(e)}")
        traceback.print_exc()
        raise


def build_user_prompt(email: str, db: Session) -> str:
    """Построение системного промпта с данными пользователя"""
    profile = db.query(UserProfile).filter(UserProfile.email == email).first()
    metrics = db.query(BodyMetrics).filter(
        BodyMetrics.email == email
    ).order_by(BodyMetrics.measured_at.desc()).first()

    gender = profile.gender if profile and profile.gender else "неизвестно"
    age = profile.age if profile and profile.age else "неизвестно"
    height = profile.height if profile and profile.height else "неизвестно"
    weight = profile.weight if profile and profile.weight else "неизвестно"

    bmi = metrics.bmi if metrics else (
        profile.height and profile.weight and 
        (profile.weight / ((profile.height/100) ** 2))
    ) if profile else None
    bmi_text = f"{bmi:.1f}" if bmi else "неизвестно"

    return (
        "Ты — персональный фитнес‑тренер FitnetAI. Отвечай кратко и предметно, опираясь на данные пользователя.\n"
        f"Пользователь: {email}\n"
        f"Пол: {gender}\n"
        f"Возраст: {age}\n"
        f"Рост (см): {height}\n"
        f"Вес (кг): {weight}\n"
        f"BMI: {bmi_text}\n"
        "Если данных не хватает, сначала попроси их уточнить. Не предлагай медицины, работай в рамках фитнеса и питания."
    )
