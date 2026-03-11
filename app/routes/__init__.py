from .auth import router as auth_router
from .pages import router as pages_router
from .user import router as user_router
from .admin import router as admin_router
from .chat import router as chat_router
from .workout import router as workout_router
from .dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "pages_router",
    "user_router",
    "admin_router",
    "chat_router",
    "workout_router",
    "dashboard_router"
]
