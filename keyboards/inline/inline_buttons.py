import urllib.parse
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database.config import PRIVATE_CHANNEL
from aiogram import types
from loader import bot


USERS_PER_PAGE = 5


def build_users_keyboard(users, page: int):
    keyboard = InlineKeyboardBuilder()

    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    sliced_users = users[start:end]

    for idx, user in enumerate(sliced_users, start=start + 1):
        keyboard.button(
            text=f"{idx}. {user.full_name}",
            callback_data=f"user:{user.telegram_id}"
        )

    # Pagination buttons
    nav = InlineKeyboardBuilder()

    if page > 0:
        nav.button(text="⬅️ Prev", callback_data=f"users_page:{page - 1}")

    if end < len(users):
        nav.button(text="➡️ Next", callback_data=f"users_page:{page + 1}")

    nav.adjust(2)

    keyboard.adjust(1)
    keyboard.attach(nav)

    return keyboard.as_markup()


def get_event_pagination_keyboard(events: list, page: int = 0, limit: int = 5):
    builder = InlineKeyboardBuilder()
    
    # Sahifa chegaralarini hisoblash
    start = page * limit
    end = start + limit
    current_page_events = events[start:end]

    # Event tugmalari
    for ev in current_page_events:
        builder.button(text=f"🏆 {ev.title}", callback_data=f"view_event_{ev.id}")
    
    builder.adjust(1) # Eventlar har doim alohida qatorda

    # Navigatsiya tugmalari (Oldinga/Orqaga)
    navigation_btns = []
    if page > 0:
        navigation_btns.append(InlineKeyboardButton(text="⬅️ Avvalgi", callback_data=f"events_page_{page-1}"))
    
    if end < len(events):
        navigation_btns.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"events_page_{page+1}"))
    
    if navigation_btns:
        builder.row(*navigation_btns)

    # Eng pastdagi Ortga (Bosh menyuga) tugmasi
    builder.row(InlineKeyboardButton(text="◀️ Ortga qaytish", callback_data="back"))
    
    return builder.as_markup()


async def start_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="Oltiariq_bilimdonlari", url="https://t.me/oltiariq_bilimdonlari")
    btn.button(text="Neon o'quv markazi", url="https://t.me/neon_study_center")
    btn.button(text="Tekshirish", callback_data="check_sub")
    btn.adjust(1)
    return btn.as_markup()


async def confirm_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="✅ Tasdiqlash", callback_data="confirm_btn")
    btn.button(text="❌ Bekor qilish", callback_data="cancel_btn")
    btn.adjust(2)
    return btn.as_markup()


async def qaytish_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="◀️ Ortga qaytish", callback_data="qaytish")
    btn.adjust(1)
    return btn.as_markup()


async def back_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="◀️ Ortga qaytish", callback_data="back")
    btn.adjust(1)
    return btn.as_markup()


# async def check_member_button(CHANNEL_USERNAME):
#     # @ belgisi bo‘lsa olib tashlaymiz
#     clean_username = CHANNEL_USERNAME.replace("@", "")

#     btn = InlineKeyboardBuilder()
#     btn.button(
#         text="📢 Subscribe to Channel",
#         url=f"https://t.me/{clean_username}"
#     )
#     btn.button(
#         text="✅ Check Subscription",
#         callback_data="check_sub"
#     )
#     btn.adjust(1)
#     return btn.as_markup()


async def check_member_button(CHANNEL_USERNAME):
    btn = InlineKeyboardBuilder()
    
    for username in CHANNEL_USERNAME:
        clean_username = username.replace("@", "").strip()
        
        # 1. Boshlang'ich qiymat beramiz (Xatolik bo'lsa shuni ishlatadi)
        channel_name = username 
        
        try:
            # Kanal nomini olishga harakat qilamiz
            chat = await bot.get_chat(username)
            channel_name = chat.title
        except Exception as e:
            # Xatolik bo'lsa, logda ko'rishimiz mumkin (ixtiyoriy)
            print(f"Kanal nomini olishda xato: {e}")
            # channel_name o'zgarmasdan (username ko'rinishida) qoladi
        
        # 2. Endi channel_name har doim mavjud bo'ladi
        btn.button(
            text=f"📢 {channel_name}", 
            url=f"https://t.me/{clean_username}"
        )
    
    # Tugmalarni 1 tadan qatorga taxlaymiz
    btn.adjust(1)
    
    # Tekshirish tugmasini alohida qatorda qo'shamiz
    btn.row(
        types.InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data="check_sub"
        )
    )
    
    return btn.as_markup()


def get_admin_events_paginated_kb(events: list, page: int = 0, limit: int = 5):
    builder = InlineKeyboardBuilder()
    
    # Sahifani hisoblash
    start = page * limit
    end = start + limit
    current_page_events = events[start:end]

    # Har bir event uchun tugma (Title bilan)
    for ev in current_page_events:
        status = "🟢" if ev.is_active else "🔴"
        builder.row(InlineKeyboardButton(
            text=f"{status} {ev.title}", 
            callback_data=f"admin_event_detail_{ev.id}"
        ))

    # Navigatsiya tugmalari (⬅️ Oldingi | Keyingi ➡️)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"admin_event_page_{page-1}"))
    
    if end < len(events):
        nav_buttons.append(InlineKeyboardButton(text="Oldinga ➡️", callback_data=f"admin_event_page_{page+1}"))

    if nav_buttons:
        builder.row(*nav_buttons)
    
    return builder.as_markup()


async def main_menu_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="👤 Profil info", callback_data="user_info")
    btn.button(text="📌 Tanlovlar", callback_data="events_btn")
    btn.button(text="📞 Bog'lanish", callback_data="connection_btn")
    btn.button(text="🛠 Sozlamalar", callback_data="settings_btn")
    btn.adjust(2)
    return btn.as_markup()


async def event_menu_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="📂 Mening tanlovlarim", callback_data="my_events")
    btn.button(text="📨 Yangi tanlovlar", callback_data="new_events")
    btn.button(text="◀️ Ortga qaytish", callback_data="back")
    btn.adjust(1)
    return btn.as_markup()


async def settings_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="👤 Ism-Familiyani o'zgartirish", callback_data="edit_fullname")
    btn.button(text="🏫 Maktabni o'zgartirish", callback_data="edit_school")
    btn.button(text="📖 Sinfni o'zgartirish", callback_data="edit_grade")
    btn.button(text="📞 Tel raqam o'zgartirish", callback_data="edit_phone")
    btn.button(text="◀️ Ortga qaytish", callback_data="back")
    btn.adjust(1)
    return btn.as_markup()


async def user_profile_button(telegram_id: int):
    btn = InlineKeyboardBuilder()
    btn.button(text="ℹ️ Profile info", url=f"tg://user?id={telegram_id}")
    btn.button(text="🚫 Bloklash", callback_data=f"block_{telegram_id}")
    btn.adjust(2)
    return btn.as_markup()


async def user_unblock_button(telegram_id: int):
    btn = InlineKeyboardBuilder()
    btn.button(text="ℹ️ Profile info", url=f"tg://user?id={telegram_id}")
    btn.button(text="❗️ Blokdan chiqarish", callback_data=f"unblock_{telegram_id}")
    btn.adjust(2)
    return btn.as_markup()


async def refresh_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="🌦 Weather update ", callback_data='weather_update')
    btn.button(text="🌎 Location update", callback_data='location_update')
    btn.adjust(1)
    return btn.as_markup()
