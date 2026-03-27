from aiogram.filters import Filter
from aiogram import types
from database.config import ADMINS


class IsBotAdmin(Filter):
    async def __call__(self, event) -> bool:
        user = getattr(event, "from_user", None)
        if not user:
            return False
        return str(user.id) in ADMINS


# class IsBotAdmin(Filter):
#     async def __call__(self, message:types.Message) ->bool:
#         return str(message.from_user.id) in ADMINS
#
# class IsAssistantAdmin(Filter):
#     async def __call__(self, message: types.Message) -> bool:
#         assistant_admins = await db.select_all_admins()
#         admin_ids = [str(admin['telegram_id']) for admin in assistant_admins]
#         print("Assistant admin:", admin_ids)
#         return str(message.from_user.id) in admin_ids
