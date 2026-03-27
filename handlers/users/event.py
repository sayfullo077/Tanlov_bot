import re
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loader import dp
from aiogram import Router, types, F
from states.all_states import UserStart
from database.models import Events
from keyboards.inline.inline_buttons import event_menu_button, back_button, get_event_pagination_keyboard
from database.orm_query import select_user, orm_get_user_event_history, orm_get_available_events, register_user_for_event

user_router = Router()


@user_router.callback_query(F.data == "events_btn")
async def event_menu_func(call: types.CallbackQuery, state: FSMContext):
    event_menu_kb = await event_menu_button()
    await call.message.edit_text("📌 Tanlovlar", reply_markup=event_menu_kb)
    await state.set_state(UserStart.event_menu)
    
    
@user_router.callback_query(F.data == "my_events")
async def my_event_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = call.from_user.id
    registrations = await orm_get_user_event_history(session, telegram_id)
    back_kb = await back_button()
    if not registrations:
        await call.message.edit_text("❗️ Siz hali birorta ham tadbirga ro'yxatdan o'tmagansiz.", reply_markup=back_kb)
        await state.set_state(UserStart.my_events)
        return

    text = "🗓 **Sizning ro'yxatdan o'tgan tadbirlaringiz:**\n\n"
    
    for i, reg in enumerate(registrations, 1):
        # registered_at vaqtini chiroyli formatga keltiramiz
        reg_date = reg.registered_at.strftime("%d.%m.%Y %H:%M")
        event_title = reg.event.title if reg.event else "Noma'lum tadbir"
        
        text += f"{i}. **{event_title}**\n   📆 Vaqti: {reg_date}\n\n"
    
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await state.set_state(UserStart.my_events)
    
    
@user_router.callback_query(F.data == "new_events")
@user_router.callback_query(F.data.startswith("events_page_"))
async def new_events_func(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    # Sahifa raqamini aniqlash (standart 0)
    page = 0
    if call.data.startswith("events_page_"):
        page = int(call.data.split("_")[-1])

    # 1. Faqat 10 ta eventni olamiz
    telegram_id = call.from_user.id
    events = await orm_get_available_events(session, telegram_id)
    
    if not events:
        await call.answer("Hozircha yangi tadbirlar yo'q. 😊", show_alert=True)
        return

    # 2. Paginatsiyali klaviaturani yaratish
    reply_markup = get_event_pagination_keyboard(events, page=page, limit=5)

    # 3. Xabarni yangilash yoki yangi yuborish
    text = "📌 Yangi tanlovlar"
    
    try:
        await call.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        await call.message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    await call.answer()
    await state.set_state(UserStart.new_events)
    
    
@user_router.callback_query(F.data.startswith("view_event_"))
async def user_event_detail(call: types.CallbackQuery, session: AsyncSession):
    event_id = int(call.data.split("_")[-1])
    
    # Bazadan event ma'lumotlarini olamiz
    event = await session.get(Events, event_id)
    
    if not event:
        await call.answer("Kechirasiz, ushbu musobaqa topilmadi.", show_alert=True)
        return

    text = (
        f"<b>{event.title}</b>\n\n"
        f"{event.desc}\n\n"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="📝 Ro'yxatdan o'tish", 
        callback_data=f"participate_event_{event_id}"
    ))
    builder.row(types.InlineKeyboardButton(
        text="⬅️ Ro'yxatga qaytish", 
        callback_data="new_events"
    ))

    # Agar eventda rasm bo'lsa, rasm bilan yuboramiz
    if event.image:
        # Avvalgi ro'yxat xabarini o'chirib, rasm bilan yangi xabar chiqaramiz
        await call.message.delete()
        await call.message.answer_photo(
            photo=event.image,
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    else:
        # Rasm bo'lmasa, mavjud xabarni tahrirlaymiz
        await call.message.edit_text(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    
    await call.answer()
    
    
@user_router.callback_query(F.data.startswith("participate_event_"))
async def process_participation(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    event_id = int(call.data.split("_")[-1])
    telegram_id = call.from_user.id

    success = await register_user_for_event(session, telegram_id, event_id)
    if success:
        await call.message.delete()
        event_menu_kb = await event_menu_button()
        await call.message.answer("✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!", reply_markup=event_menu_kb)
        await state.set_state(UserStart.event_menu)
    else:
        await call.message.delete()
        event_menu_kb = await event_menu_button()
        await call.message.answer("❌ Xatolik yuz berdi, birozdan so'ng urinib ko'ring!", reply_markup=event_menu_kb)
        await state.set_state(UserStart.event_menu)