import os
from aiogram.fsm.context import FSMContext
from filters.is_admin import IsBotAdmin
from states.all_states import TokenState, AdminState
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.orm_query import get_single_token, delete_ai_token
from keyboards.default.default_buttons import event_menu_button, back_button
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import ADMINS
from database.models import Events
from states.all_states import EventState
from database.orm_query import orm_get_all_events, export_event_participants_to_excel
from keyboards.inline.inline_buttons import get_admin_events_paginated_kb
from loader import bot


admin_router = Router()

    
@admin_router.callback_query(F.data.startswith("admin_event_page_"), IsBotAdmin())
@admin_router.message(F.text == "🗃 Hammasi", IsBotAdmin())
async def list_events_admin(event: types.Message | types.CallbackQuery, session: AsyncSession, state: FSMContext):
    # Callback yoki Message ekanligini aniqlash
    page = 0
    if isinstance(event, types.CallbackQuery):
        page = int(event.data.split("_")[-1])
        await event.answer()

    events = await orm_get_all_events(session)
    
    if not events:
        text = "Hozircha birorta ham tanlov yaratilmagan."
        if isinstance(event, types.Message):
            await event.answer(text)
        else:
            await event.message.edit_text(text)
        return

    kb = get_admin_events_paginated_kb(events, page=page)
    text=f"(Jami: {len(events)} ta)"
    back_kb = await back_button()

    if isinstance(event, types.Message):
        await event.answer("📌 Tanlovlar ro'yxati", reply_markup=back_kb)
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")
        
    else:
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await state.set_state(EventState.get_events)
    
    
@admin_router.callback_query(F.data.startswith("admin_event_detail_"), IsBotAdmin())
async def detail_event_admin(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    event_id = int(call.data.split("_")[-1])
    event_item = await session.get(Events, event_id)

    if not event_item:
        await call.answer("Event topilmadi!")
        return

    status = "Aktiv 🟢" if event_item.is_active else "Noaktiv 🔴"
    caption = (
        f"🏆 Sarlavhasi:<b> {event_item.title}</b>\n\n"
        f"📝 Tavsifi:\n{event_item.desc}\n\n"
        f"📊 Holati: {status}\n"
        f"📅 Yaratilgan vaqti: {event_item.joined_at.strftime('%Y-%m-%d %H:%M')}"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 O'chirish", callback_data=f"admin_event_delete_{event_id}")
    kb.button(text="🔄 O'zgartirish", callback_data=f"admin_event_edit_{event_id}")
    kb.button(text="📥 Excelga olish", callback_data=f"admin_event_excel_{event_id}")
    kb.adjust(2, 1)

    await call.message.delete()
    
    if event_item.image:
        await call.message.answer_photo(
            photo=event_item.image,
            caption=caption,
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
    else:
        await call.message.answer(
            text=caption,
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        
    await state.set_state(EventState.detail_event)
    
    
@admin_router.callback_query(F.data.startswith("admin_event_excel_"), IsBotAdmin())
async def get_excel_event(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    event_id = int(call.data.split("_")[-1])
    event_item = await session.get(Events, event_id)
    
    await call.answer("Hisobot tayyorlanmoqda, iltimos kuting...")
    
    if not event_item:
        await call.answer("Event topilmadi!")
        return
    
    # Excel faylni yaratamiz
    file_path, status = await export_event_participants_to_excel(session, event_id)

    if status == "OK" and file_path:
        if os.path.exists(file_path): # Endi bu yerda xato bo'lmaydi, chunki file_path - string
            document = FSInputFile(path=file_path, filename=file_path)
            await call.message.answer_document(
                document, 
                caption=f"📊 Event ID: {event_id} bo'yicha ro'yxatdan o'tganlar ro'yxati"
            )
        os.remove(file_path)
    else:
        await call.message.answer("Ushbu tadbirga hali hech kim ro'yxatdan o'tmagan.")
        
    await state.set_state(EventState.detail_event)