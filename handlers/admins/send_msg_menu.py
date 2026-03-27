import logging
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from filters.is_admin import IsBotAdmin
from states.all_states import AdminState
from keyboards.default.default_buttons import back_button, admin_menu_button
from aiogram import Router, types, F
from database.orm_query import select_all_users
from database.config import ADMINS
from loader import bot

logging.basicConfig(level=logging.INFO)


admin_router = Router()


@admin_router.message(F.text == "📨 Message", IsBotAdmin())
async def send_message_func(message: types.Message, state: FSMContext):
    back_btn = await back_button()
    await message.answer("What message do you want to send?", reply_markup=back_btn)
    await state.set_state(AdminState.send_message)


@admin_router.message(AdminState.send_message, IsBotAdmin())
async def sending_message_func(message: types.Message, state: FSMContext, session: AsyncSession):
    send_msg = message.text.strip()
    admin_menu_btn = await admin_menu_button()
    try:
        users = await select_all_users(session)
        if users:
            for user in users:
                logging.info(f"Sending to {user.telegram_id} | {user.full_name}")
                await bot.send_message(chat_id=user.telegram_id, text=send_msg)
            await message.answer("Your message has been sent to all users!", reply_markup=admin_menu_btn)

        else:
            print("Users is not!!!")

    except Exception as e:
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=f"Error while sending the message: {e}")
        await message.answer("Unexpected error! Please try again later ⁉️", reply_markup=admin_menu_btn)

    await state.set_state(AdminState.menu)