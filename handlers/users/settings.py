import re
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loader import dp
from aiogram import Router, types, F
from states.all_states import UserSettings, UserStart
from keyboards.inline.inline_buttons import settings_button, back_button
from keyboards.default.default_buttons import phone_keyboard
from database.orm_query import select_user, orm_update_user

user_router = Router()


@user_router.callback_query(F.data == "user_info")
async def user_info_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    user = await select_user(telegram_id, session)
    full_name = user.full_name
    school = user.school
    grade = user.grade
    phone = user.phone
    text = (f"📋 Profil info:\n"
            f"👤 Ism-familya: {full_name}\n"
            f"🏫 Maktab: {school}\n"
            f"📖 Sinf: {grade}\n"
            f"📞 Tel raqam: {phone}")
    back_kb = await back_button()
    await call.message.edit_text(text=text, reply_markup=back_kb)
    await state.set_state(UserStart.info)


@user_router.callback_query(F.data == "settings_btn")
async def settings_func(call: types.CallbackQuery, state: FSMContext):
    settings_kb = await settings_button()
    await call.message.edit_text("🛠 Sozlamalar", reply_markup=settings_kb)
    await state.set_state(UserSettings.menu)
    
    
@user_router.callback_query(F.data == "edit_fullname")
async def edit_fullname_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    user = await select_user(telegram_id, session)
    full_name = user.full_name
    back_kb = await back_button()
    await call.message.edit_text(f"<b>Joriy ism-familiyangiz: {full_name}\n\nYangi Ism-Familiyangizni kiriting:</b>", reply_markup=back_kb)
    await state.set_state(UserSettings.change_fullname)
    
    
@user_router.message(UserSettings.change_fullname)
async def save_fullname_func(message: types.Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    full_name = message.text.strip()
    settings_kb = await settings_button()
    await orm_update_user(session, telegram_id, full_name=full_name)
    await message.answer(f"Yangi ism-familiya saqlandi: {full_name}\n\n🛠 Sozlamalar", reply_markup=settings_kb)
    await state.set_state(UserSettings.menu)
    
    
@user_router.callback_query(F.data == "edit_school")
async def edit_school_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    user = await select_user(telegram_id, session)
    school = user.school
    back_kb = await back_button()
    await call.message.edit_text(f"<b>Joriy maktabingiz: {school}\n\nYangi maktab nomini kiriting:</b>", reply_markup=back_kb)
    await state.set_state(UserSettings.change_school)
    
    
@user_router.message(UserSettings.change_school)
async def save_school_func(message: types.Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    school = message.text.strip()
    settings_kb = await settings_button()
    await orm_update_user(session, telegram_id, school=school)
    await message.answer(f"Yangi maktab nomi saqlandi: {school}\n\n🛠 Sozlamalar", reply_markup=settings_kb)
    await state.set_state(UserSettings.menu)
    
    
@user_router.callback_query(F.data == "edit_grade")
async def edit_grade_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    user = await select_user(telegram_id, session)
    grade = user.grade
    back_kb = await back_button()
    await call.message.edit_text(f"<b>Joriy sinfingiz: {grade}\n\nYangi sinfni kiriting:</b>", reply_markup=back_kb)
    await state.set_state(UserSettings.change_grade)
    
    
@user_router.message(UserSettings.change_grade)
async def save_grade_func(message: types.Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    grade = message.text.strip()
    settings_kb = await settings_button()
    await orm_update_user(session, telegram_id, grade=grade)
    await message.answer(f"Yangi sinf saqlandi: {grade}\n\n🛠 Sozlamalar", reply_markup=settings_kb)
    await state.set_state(UserSettings.menu)
    

@user_router.callback_query(F.data == "edit_phone")
async def edit_phone_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    user = await select_user(telegram_id, session)
    phone = user.phone
    back_kb = await back_button()
    phone_btn = phone_keyboard()  
    await call.message.edit_text(f"<b>Joriy tel raqamingiz: {phone}\n\nYangi tel raqamni kiriting:</b>", reply_markup=back_kb)
    await call.message.answer("Masalan: <i>+998901234567</i>", reply_markup=phone_btn)
    await state.set_state(UserSettings.change_phone)
    
    
@user_router.message(UserSettings.change_phone)
async def save_phone_func(message: types.Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()

        if not re.match(r"^\+998\d{9}$", phone):
            await message.answer("<b>Telefon raqamni to‘g‘ri formatda kiriting:\n+998901234567</b>")
            return
    settings_kb = await settings_button()
    await orm_update_user(session, telegram_id, phone=phone)
    await message.answer(text=f"Yangi tel raqam saqlandi: {phone}\n\n", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text="🛠 Sozlamalar", reply_markup=settings_kb)
    await state.set_state(UserSettings.menu)