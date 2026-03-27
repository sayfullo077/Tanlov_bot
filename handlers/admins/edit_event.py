from aiogram.fsm.context import FSMContext
from filters.is_admin import IsBotAdmin
from states.all_states import EventState
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton
from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import ADMINS
from database.models import Events
from database.orm_query import update_event_field


admin_router = Router()


@admin_router.callback_query(F.data.startswith("admin_event_edit_"), IsBotAdmin())
async def detail_event_admin(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    event_id = int(call.data.split("_")[-1])
    event_item = await session.get(Events, event_id)

    if not event_item:
        await call.answer("Tanlov topilmadi!")
        return
    
    await state.update_data(editing_event_id=event_id)
    await state.set_state(EventState.edit_event_menu)

    status = "Aktiv 🟢" if event_item.is_active else "Noaktiv 🔴"
    caption = (
        f"🏆 Sarlavhasi: <b>{event_item.title}</b>\n\n"
        f"📝 Tavsifi:\n{event_item.desc}\n\n"
        f"📊 Holati: {status}"
    )

    kb = ReplyKeyboardBuilder()
    if event_item.image:
        kb.add(KeyboardButton(text="🖼 Rasm"))
    kb.add(KeyboardButton(text="🏷 Sarlavha"))
    kb.add(KeyboardButton(text="📄 Tasnif"))
    kb.add(KeyboardButton(text="ℹ️ Status"))
    kb.add(KeyboardButton(text="◀️ Ortga qaytish"))
    
    kb.adjust(2, 2, 1) # Tugmalarni joylashuvi

    # Reply klaviatura doim ko'rinib turishi yoki bir marta chiqishi uchun sozlamalar
    markup = kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await call.message.delete()
    
    if event_item.image:
        await call.message.answer_photo(
            photo=event_item.image,
            caption=caption,
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        await call.message.answer(
            text=caption,
            reply_markup=markup,
            parse_mode="HTML"
        )