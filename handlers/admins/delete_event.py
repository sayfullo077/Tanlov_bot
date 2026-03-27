from aiogram.fsm.context import FSMContext
from filters.is_admin import IsBotAdmin
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.default.default_buttons import event_menu_button
from keyboards.inline.inline_buttons import get_admin_events_paginated_kb
from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import ADMINS
from database.models import Events
from states.all_states import EventState
from database.orm_query import delete_event_by_id, orm_get_all_events


admin_router = Router()


@admin_router.callback_query(F.data.startswith("admin_event_delete_"), IsBotAdmin())
async def confirmation_delete_event(call: types.CallbackQuery, session: AsyncSession):
    event_id = int(call.data.split("_")[-1])
    event_item = await session.get(Events, event_id)

    if not event_item:
        await call.answer("Tanlov topilmadi!")
        return

    status = "Aktiv 🟢" if event_item.is_active else "Noaktiv 🔴"
    caption = (
        f"🏆 Sarlavhasi:<b> {event_item.title}</b>\n\n"
        f"📝 Tavsifi:\n{event_item.desc}\n\n"
        f"📊 Holati: {status}\n"
        f"📅 Yaratilgan vaqti: {event_item.joined_at.strftime('%Y-%m-%d %H:%M')}\n\nO'chirishni tadiqlaysizmi?"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data=f"confirm_delete_event_{event_id}")
    kb.button(text="❌ Bekor qilish", callback_data=f"cancel_delete_event_{event_id}")
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


@admin_router.callback_query(F.data.startswith("confirm_delete_event_"), IsBotAdmin())
async def confirm_event_delete(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    event_id = int(call.data.split("_")[-1])
    await call.message.delete()
    event_menu_kb = await event_menu_button()
    succes = await delete_event_by_id(session, event_id)
    if succes:
        await call.message.answer("✅ Tanlov o'chirildi!", reply_markup=event_menu_kb)    
    else:
        await call.message.answer("❗️ Xatolik yuz berdi qayta urinib ko'ring!", reply_markup=event_menu_kb)        
    await state.set_state(EventState.menu)
    
    
@admin_router.callback_query(F.data.startswith("cancel_delete_event_"), IsBotAdmin())
async def cancel_event_delete(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    event_menu_kb = await event_menu_button()
    await call.message.answer("❌ Tanlov o'chirish bekor qilindi!", reply_markup=event_menu_kb)    
    await state.set_state(EventState.menu)
    
    
