"""
Конфигурация приложения и переменные окружения
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== DATABASE CONFIG =====
SQLITE_URL = "sqlite:///./users.db"
POSTGRES_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:zhus@localhost:5432/fitness_db"
)

# ===== JWT CONFIG =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# ===== ADMIN CONFIG =====
ADMIN_EMAIL = "admin.athletix@gmail.com"
ADMIN_PASSWORD = "Ghmsloser1"

# ===== GROQ API CONFIG =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env")
