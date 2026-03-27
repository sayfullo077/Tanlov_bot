from aiogram.filters import Command
from loader import dp
from aiogram import types, Router


user_router = Router()


@user_router.message(Command('help'))
async def help_bot(message: types.Message):
    await message.answer(f"Main commands: \n/start ♻️ Start Bot\n"
                         f"/feedback ✉️ Send a message to the admin")
