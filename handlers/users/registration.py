import re
import json
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline.inline_buttons import back_button, confirm_button, start_button, user_profile_button, main_menu_button
from keyboards.default.default_buttons import phone_keyboard
from states.all_states import RegistrationState
from database.config import PRIVATE_CHANNEL, CHANNEL_USERNAME, ADMINS
from database.orm_query import select_user, orm_update_user
from loader import bot
from datetime import datetime
import logging


user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(RegistrationState.full_name)
async def add_full_name_func(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)
    back_btn = await back_button()
    await message.answer("<b>Qaysi maktabda o'qiysiz?:</b>\n\nMasalan: <i>7-maktab</i>",
                                 reply_markup=back_btn)
    await state.set_state(RegistrationState.school)


@user_router.message(RegistrationState.school)
async def add_school_func(message: types.Message, state: FSMContext):
    school = message.text.strip()
    await state.update_data(school=school)
    back_btn = await back_button()
    await message.answer("<b>Qaysi sinfda o'qiysiz?:</b>\n\nMasalan: <i>7-sinf</i>",
                                 reply_markup=back_btn)
    await state.set_state(RegistrationState.grade)


@user_router.message(RegistrationState.grade)
async def add_phone_func(message: types.Message, state: FSMContext):
    grade = message.text.strip()
    await state.update_data(grade=grade)
    phone_btn = phone_keyboard()
    back_btn = await back_button()
    await message.answer("<b>Iltimos, telefon raqamingizni yuboring yoki qo‘lda kiriting:</b>\n\n",
                                 reply_markup=back_btn)
    await message.answer("Masalan: <i>+998901234567</i>", reply_markup=phone_btn)
    await state.set_state(RegistrationState.check)


@user_router.message(RegistrationState.check)
async def check_phone_func(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()

        if not re.match(r"^\+998\d{9}$", phone):
            await message.answer(
                "Telefon raqamni to‘g‘ri formatda kiriting:\n"
                "+998901234567"
            )
            return

    data = await state.get_data()
    await state.update_data(phone=phone)
    full_name = data.get("full_name")
    school = data.get("school")
    grade = data.get("grade")
    text = (f"👤 Ism-Familya: {full_name}\n"
            f"📌 Maktab turi: {school}\n"
            f"📌 Sinf turi: {grade}\n"
            f"📞 Telefon raqam: {phone}")
    confirm_btn = await confirm_button()
    await state.update_data(data_text=text)
    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Ma'lumotlar to'g'rimi?", reply_markup=confirm_btn)
    await state.set_state(RegistrationState.finish)


@user_router.callback_query(F.data == "confirm_btn", RegistrationState.finish)
async def confirm_data_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    start_btn = await start_button()
    data = await state.get_data()
    data_text = data.get("data_text")
    telegram_id = call.from_user.id
    user_profile_btn = await user_profile_button(telegram_id)
    try:
        await orm_update_user(session, telegram_id, full_name=data.get("full_name"), school=data.get("school"), grade=data.get("grade"), phone=data.get("phone"))
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=f"📋 Yangi ariza!\n"
                                                       f"{data_text}", reply_markup=user_profile_btn)
    except Exception as e:
        await bot.send_message(chat_id=637914427, text=f"Error while sending to admin: {e}")
    main_menu_btn = await main_menu_button()
    await call.message.edit_text("Bosh menyu", reply_markup=main_menu_btn)
    await state.clear()


@user_router.callback_query(F.data == "cancel_btn", RegistrationState.finish)
async def cancel_data_func(call: types.CallbackQuery, state: FSMContext):
    start_btn = await start_button()
    await call.message.edit_text("<b>❌ Arizangiz bekor qilindi!</b>", reply_markup=start_btn)
    await state.clear()