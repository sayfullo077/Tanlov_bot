from aiogram.fsm.context import FSMContext
from filters.is_admin import IsBotAdmin
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.all_states import TokenState, AdminState
from aiogram.filters import Command
from database.orm_query import orm_add_event
from keyboards.default.default_buttons import event_menu_button, back_button, admin_confirm_button
from aiogram import Router, types, F
from aiogram.types import ContentType
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import ADMINS
from states.all_states import AddEventState, EventState
from loader import bot
from database.config import PRIVATE_CHANNEL


admin_router = Router()


@admin_router.message(F.text == "➕ Qo'shish", IsBotAdmin())
async def start_add_event(message: types.Message, state: FSMContext):
    back_kb = await back_button()
    await message.answer("Tanlov uchun rasm yuboring (yoki o'tkazib yuborish uchun /skip):", reply_markup=back_kb)
    await state.set_state(AddEventState.image)


@admin_router.message(AddEventState.image, F.content_type == ContentType.PHOTO, IsBotAdmin())
async def set_image_check(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    back_kb = await back_button()

    if message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Rasm yuboring!")
        return

    file_info = await bot.get_file(photo.file_id)
    file_extension = file_info.file_path.split(".")[-1].lower()
    valid_extensions = ["jpg", "jpeg", "png", "webp"]

    if file_extension not in valid_extensions:
        await message.answer(
            "Rasm formati noto‘g‘ri! Faqat jpg, jpeg, png, yoki webp formatlari qabul qilinadi.", reply_markup=back_kb
        )
        return
    
    await message.answer("Tanlov nomini kiriting", reply_markup=back_kb)
    await state.set_state(AddEventState.title)
    
    
@admin_router.message(Command("skip"), AddEventState.image, IsBotAdmin())
async def add_title_func(message: types.Message, state: FSMContext):
    await state.update_data(image=None)
    back_kb = await back_button()
    await message.answer("Tanlov nomini kiriting", reply_markup=back_kb)
    await state.set_state(AddEventState.title)
    
    
@admin_router.message(AddEventState.title, IsBotAdmin())
async def add_desc_func(message: types.Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    back_kb = await back_button()
    await message.answer("Tanlov tasnifini kiriting", reply_markup=back_kb)
    await state.set_state(AddEventState.description)
    
    
@admin_router.message(AddEventState.description, IsBotAdmin())
async def confirmation_func(message: types.Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)
    data = await state.get_data()
    image = data.get("image")
    title = data.get("title")
    admin_confirm_kb = await admin_confirm_button()
    
    text = (f"{title}\n"
            f"{description}\n\n")
    
    if image:
        await message.answer_photo(
            photo=image,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=text,
            parse_mode="HTML"
        )
    
    await message.answer(text="Ushbu ma'lumotlar to'grimi?", reply_markup=admin_confirm_kb)
    await state.set_state(AddEventState.check)
    
    
# -1002103581219
@admin_router.message(F.text == "✅ Tasdiqlash", AddEventState.check, IsBotAdmin())
async def confirm_event_save(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        data = await state.get_data()
        # Eventni saqlaymiz va ob'ektni olamiz
        new_event = await orm_add_event(session, {
            "title": data["title"],
            "desc": data["description"],
            "image": data["image"]
        })
        
        # Tanlangan kanallar ro'yxatini saqlash uchun FSMga id ni qo'yamiz
        await state.update_data(current_event_id=new_event.id, selected_channels=[])
        
        # Kanallar ro'yxatini chiqaruvchi inline tugma
        kb = InlineKeyboardBuilder()
        for ch_id in PRIVATE_CHANNEL:
            # Bu yerda kanal nomini olish qiyin bo'lsa, ID ko'rsatiladi
            kb.button(text=f"Kanal: {ch_id}", callback_data=f"select_ch_{ch_id}")
        
        kb.button(text="🚀 Yuborish", callback_data="send_to_channels")
        kb.adjust(1)

        await message.answer(
            f"✅ Tanlov bazaga qo'shildi (ID: {new_event.id}).\n"
            f"Endi e'lon qilinadigan kanallarni tanlang:",
            reply_markup=kb.as_markup()
        )
        await state.set_state(AddEventState.select_channels) # Yangi state qo'shing

    except Exception as e:
        await message.answer(f"Xatolik: {e}")


@admin_router.message(F.text == "❌ Bekor qilish", AddEventState.check, IsBotAdmin())
async def cancel_token_save_func(message: types.Message, state: FSMContext):
    event_menu_kb = await event_menu_button()
    await state.clear()
    await message.answer("❌ Tanlov qo'shish bekor qilindi!", reply_markup=event_menu_kb)
    await state.set_state(EventState.menu)