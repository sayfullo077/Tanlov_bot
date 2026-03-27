from aiogram import Router
from . import start, feedback, back_handler, registration, settings, event, help

user_router = Router()

user_router.include_router(start.user_router)
user_router.include_router(back_handler.user_router)
user_router.include_router(feedback.user_router)
user_router.include_router(registration.user_router)
user_router.include_router(settings.user_router)
user_router.include_router(event.user_router)
user_router.include_router(help.user_router)

__all__ = ["user_router"]