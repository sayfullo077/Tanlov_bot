from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


async def admin_menu_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📌 Tanlovlar")
    kb.button(text="📊 Bot info")
    kb.button(text="👤 Users")
    kb.button(text="📨 Message")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def event_menu_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🗃 Hammasi")
    kb.button(text="➕ Qo'shish")
    kb.button(text="◀️ Ortga qaytish")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def back_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="◀️ Ortga qaytish")
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def admin_confirm_button():
    kb = ReplyKeyboardBuilder()

    kb.button(text="✅ Tasdiqlash")
    kb.button(text="❌ Bekor qilish")

    kb.adjust(2)

    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)