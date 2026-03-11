"""
Скрипт миграции данных из SQLite в PostgreSQL
""" 
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к SQLite (старая база)
SQLITE_URL = "sqlite:///./users.db"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(bind=sqlite_engine)

# Подключение к PostgreSQL (новая база)
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://postgres:zhus@localhost:5432/fitness_db")
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine)

def migrate_table(table_name):
    """Переносит данные из одной таблицы в другую"""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    try:
        # Очищаем таблицу в PostgreSQL перед переносом
        postgres_session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        postgres_session.commit()
        
        # Читаем все данные из SQLite
        result = sqlite_session.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = result.fetchall()
        
        if not rows:
            print(f"  ✓ Таблица {table_name} пуста, пропускаем")
            return
        
        # Подготавливаем INSERT запрос для PostgreSQL
        columns_str = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in columns])
        insert_query = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})")
        
        # Вставляем данные в PostgreSQL
        for row in rows:
            row_dict = dict(zip(columns, row))
            postgres_session.execute(insert_query, row_dict)
        
        postgres_session.commit()
        print(f" Перенесено {len(rows)} записей из таблицы {table_name}")
        
    except Exception as e:
        print(f" Ошибка при переносе таблицы {table_name}: {e}")
        postgres_session.rollback()
    finally:
        sqlite_session.close()
        postgres_session.close()

def main():
    print("Начинаем миграцию данных из SQLite в PostgreSQL...\n")
    
    tables = [
        "users",
        "user_profiles",
        "ai_request_logs",
        "body_metrics",
        "change_history",
        "workout_plans",
        "training_schedules"
    ]
    
    for table in tables:
        print(f"Переносим таблицу: {table}")
        migrate_table(table)
    
    print("\nМиграция завершена!")

if __name__ == "__main__":
    main()
