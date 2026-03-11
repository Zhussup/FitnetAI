"""
Сервис аутентификации
"""
import bcrypt
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from ..config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM


def hash_password(password: str) -> str:
    """Хеширование пароля с помощью bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hash_password: str) -> bool:
    """Проверка пароля против хеша"""
    return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))


def create_access_token(email: str, expires_delta: timedelta = None) -> str:
    """Создание JWT токена"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "email": email,
        "exp": (datetime.utcnow() + expires_delta).timestamp()
    }
    
    # JWT кодирование вручную (без внешних библиотек)
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).decode().rstrip('=')
    
    payload = base64.urlsafe_b64encode(
        json.dumps(to_encode).encode()
    ).decode().rstrip('=')
    
    message = f"{header}.{payload}"
    signature = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    
    token = f"{message}.{signature}"
    return token


def verify_token(token: str) -> Optional[str]:
    """Проверка JWT токена, возвращает email или None"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header, payload, signature = parts
        
        # Проверка подписи
        message = f"{header}.{payload}"
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        ).decode().rstrip('=')
        
        if signature != expected_signature:
            return None
        
        # Декодирование payload
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        
        # Проверка срока действия
        if decoded.get("exp") and datetime.fromtimestamp(decoded["exp"]) < datetime.utcnow():
            return None
        
        return decoded.get("email")
    except Exception:
        return None


def get_email_from_auth_header(auth_header: Optional[str]) -> Optional[str]:
    """Извлечение email из Bearer токена в заголовке Authorization"""
    if not auth_header:
        return None
    
    prefix = "Bearer "
    if not auth_header.startswith(prefix):
        return None
    
    token = auth_header[len(prefix):].strip()
    return verify_token(token)
