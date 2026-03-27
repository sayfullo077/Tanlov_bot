from loader import bot
from database.config import ADMINS


async def start():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i, text="Bot activated!")

        except:
            pass


async def shutdown():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i, text="Bot stop!")

        except:
            pass