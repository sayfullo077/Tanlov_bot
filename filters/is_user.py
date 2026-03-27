from aiogram import types
from aiogram.filters import BaseFilter
from loader import db


class IsUser(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        user = db.is_user(user_id=user_id)
        return bool(user)


class IsGuest(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        user = db.is_user(user_id=user_id)
        return not bool(user)


class IsBlockUser(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        try:
            block_users = await db.select_all_block_users()
            blocked_ids = [str(user['telegram_id']) for user in block_users]
            return str(message.from_user.id) not in blocked_ids
        except Exception as e:
            print(f"Error checking blocked users: {e}")
            return False