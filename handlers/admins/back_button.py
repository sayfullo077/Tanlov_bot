from loader import dp
from aiogram.types import Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from filters.is_admin import IsBotAdmin
from states.all_states import AdminState, AddEventState, EventState
from keyboards.inline.inline_buttons import build_users_keyboard, get_admin_events_paginated_kb
from keyboards.default.default_buttons import admin_menu_button, back_button, event_menu_button
from database.orm_query import select_all_users, orm_get_all_events


admin_router = Router()


@dp.message(F.text == "◀️ Ortga qaytish", IsBotAdmin())
async def back_state_func(message: Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    text = "💼 Admin panel"
    back_btn = await back_button()
    if current_state in [
        AdminState.info,
        AdminState.send_message,
        AdminState.user_list,
        EventState.menu
        ]:
        await state.clear()
        admin_menu_btn = await admin_menu_button()
        await message.answer(text, reply_markup=admin_menu_btn)
        await state.set_state(AdminState.menu)

    elif current_state in [
        AddEventState.image,
        EventState.get_events,
        ]:
        event_menu_kb = await event_menu_button()
        await message.answer("Kerakli bo'limni tanlang:", reply_markup=event_menu_kb)
        await state.set_state(EventState.menu)
    
    elif current_state == AddEventState.title:
        back_kb = await back_button()
        await message.answer("Tanlov uchun rasm yuboring (yoki o'tkazib yuborish uchun /skip):", reply_markup=back_kb)
        await state.set_state(AddEventState.image)
    
    elif current_state == AddEventState.description:
        back_kb = await back_button()
        await message.answer("Tanlov nomini kiriting", reply_markup=back_kb)
        await state.set_state(AddEventState.title)
    
    elif current_state == EventState.detail_event:
        page = 0
        events = await orm_get_all_events(session)
        kb = get_admin_events_paginated_kb(events, page=page)
        text=f"(Jami: {len(events)} ta)"
        back_kb = await back_button()
        await message.answer("📌 Tanlovlar ro'yxati", reply_markup=back_kb)
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")
        await state.set_state(EventState.get_events)
    
    elif current_state == AdminState.user_detail:
        users = await select_all_users(session)
        back_btn = await back_button()
        await message.answer("📋", reply_markup=back_btn)

        if not users:
            await message.answer("Sorry, there are currently no saved users ❗️")
            return

        await state.update_data(users=users)

        keyboard = build_users_keyboard(users, page=0)

        await message.answer(
            text="Users list (page 1)",
            reply_markup=keyboard
        )

        await state.set_state(AdminState.user_list)