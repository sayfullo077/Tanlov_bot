import handlers, middlewares
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
import asyncio
import logging
import sys

from loader import dp, bot
from utils.notify_admins import start, shutdown
from sqlalchemy.ext.asyncio import AsyncSession
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.users import user_router
from handlers.admins import admin_router
from utils.set_bot_commands import commands
from aiogram.types import BotCommandScopeDefault


async def main(session: AsyncSession):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        dp.update.middleware(DataBaseSession(session_pool=session_maker))

        # Routerni ro‘yxatdan o‘tkazamiz
        dp.include_router(admin_router)
        dp.include_router(user_router)

        # Create Users Table
        try:
            # await drop_db()

            await create_db()

        except Exception as e:
            print(f"Error creating {e}")
        #############################
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    async_session = session_maker()
    asyncio.run(main(async_session))
