from aiogram import Router
from . import admin, back_button, send_msg_menu, events, add_event, delete_event, edit_event


admin_router = Router()

admin_router.include_router(admin.admin_router)
admin_router.include_router(back_button.admin_router)
admin_router.include_router(send_msg_menu.admin_router)
admin_router.include_router(events.admin_router)
admin_router.include_router(delete_event.admin_router)
admin_router.include_router(edit_event.admin_router)
admin_router.include_router(add_event.admin_router)

__all__ = ["admin_router"]