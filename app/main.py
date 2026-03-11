"""
Основное приложение FastAPI
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
import atexit
import traceback
from .database import Base, sqlite_engine, postgres_engine, SessionLocal, PostgresSession
from .models import (
    User, UserProfile, AIRequestLog, BodyMetrics,
    ChangeHistory, WorkoutPlan, TrainingSchedule
)
from .config import ADMIN_EMAIL, ADMIN_PASSWORD
from .services.auth import hash_password, verify_password
from .routes import (
    auth_router, pages_router, user_router, admin_router,
    chat_router, workout_router, dashboard_router
)

# ===== СОЗДАНИЕ ПРИЛОЖЕНИЯ =====
app = FastAPI(title="AthletixAI", version="2.0.0")

# ===== MIDDLEWARE =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== STATIC FILES =====
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/exer", StaticFiles(directory="exer"), name="exer")

# ===== СОЗДАНИЕ ТАБЛИЦ =====
Base.metadata.create_all(bind=sqlite_engine)
Base.metadata.create_all(bind=postgres_engine)

# ===== МИГРАЦИИ БД =====
try:
    inspector = inspect(sqlite_engine)
    columns = [col['name'] for col in inspector.get_columns('change_history')]
    if 'program_name' not in columns:
        with sqlite_engine.begin() as conn:
            conn.execute(text("ALTER TABLE change_history ADD COLUMN program_name TEXT DEFAULT ''"))
            print("✓ Added program_name column to change_history")
except Exception as e:
    print(f"Migration error: {str(e)}")
    traceback.print_exc()

# ===== ФУНКЦИЯ СИНХРОНИЗАЦИИ С POSTGRESQL =====
def sync_to_postgres():
    """Синхронизирует все данные из SQLite в PostgreSQL"""
    sqlite_session = SessionLocal()
    postgres_session = PostgresSession()
    
    tables = [
        ("users", User),
        ("user_profiles", UserProfile),
        ("ai_request_logs", AIRequestLog),
        ("body_metrics", BodyMetrics),
        ("change_history", ChangeHistory),
        ("workout_plans", WorkoutPlan),
        ("training_schedules", TrainingSchedule)
    ]
    
    try:
        for table_name, model_class in tables:
            # Очищаем таблицу в PostgreSQL
            postgres_session.execute(
                text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
            )
            
            # Копируем данные из SQLite
            records = sqlite_session.query(model_class).all()
            for record in records:
                record_dict = {
                    c.name: getattr(record, c.name)
                    for c in record.__table__.columns
                }
                new_record = model_class(**record_dict)
                postgres_session.merge(new_record)
        
        postgres_session.commit()
        print(f"✓ Синхронизация с PostgreSQL завершена")
    except Exception as e:
        postgres_session.rollback()
        print(f"✗ Ошибка синхронизации с PostgreSQL: {e}")
    finally:
        sqlite_session.close()
        postgres_session.close()


# Автоматическая синхронизация при завершении приложения
atexit.register(sync_to_postgres)

# ===== СОЗДАНИE АДМИНА =====
def ensure_admin_user():
    """Создание или синхронизация админ пользователя"""
    try:
        db = SessionLocal()
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        admin_hash = hash_password(ADMIN_PASSWORD)
        if not admin:
            admin = User(email=ADMIN_EMAIL, password_hash=admin_hash)
            db.add(admin)
            db.commit()
            print("✓ Admin user created")
        else:
            # Синхронизируем пароль админа с конфигом
            if not verify_password(ADMIN_PASSWORD, admin.password_hash):
                admin.password_hash = admin_hash
                db.commit()
                print("✓ Admin password reset to configured value")
    except Exception as e:
        print(f"[admin_seed] Error: {str(e)}")
    finally:
        db.close()


ensure_admin_user()

# ===== РЕГИСТРАЦИЯ МАРШРУТОВ =====
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(workout_router)
app.include_router(dashboard_router)

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok", "version": "2.0.0"}
