import re
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from states.all_states import UserMessageState, UserStart
from filters.is_admin import IsBotAdmin
from loader import bot
from database.config import ADMINS
from database.orm_query import select_user, orm_block_user, orm_delete_all_users
from keyboards.inline.inline_buttons import back_button, start_button, user_unblock_button, user_profile_button


def html_escape(text):
    escape_chars = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}
    return re.sub(r'[&<>"\']', lambda match: escape_chars[match.group(0)], text)


user_router = Router()
user_message_map = {}


@user_router.message(Command("delete_users"), IsBotAdmin())
async def delete_all_users_handler(message: Message, session: AsyncSession):
    try:
        await orm_delete_all_users(session)
        await message.answer("All users are deleted ❗️")
    except Exception as e:
        await bot.send_message(chat_id=637914427, text=f"Error while deleting users: {e}")


@user_router.callback_query(F.data == "connection_btn")
async def connection_func(call: types.CallbackQuery, state: FSMContext):
    back_btn = await back_button()
    await call.message.edit_text("📭 Fikr-mulohazalaringizni qoldiring. Sizning fikringiz biz uchun muhim.", reply_markup=back_btn)
    await state.set_state(UserMessageState.waiting_for_message)


@user_router.message(Command("feedback"))
async def ask_for_feedback(message: Message, state: FSMContext):
    back_btn = await back_button()
    await message.answer("📭 Fikr-mulohazalaringizni qoldiring. Sizning fikringiz biz uchun muhim.", reply_markup=back_btn)
    await state.set_state(UserMessageState.waiting_for_message)


@user_router.message(UserMessageState.waiting_for_message)
async def forward_to_admins(message: Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = html_escape(message.from_user.full_name)
    username = message.from_user.username
    telegram_id = message.from_user.id
    registration_date = datetime.now().strftime("%Y-%m-%d")
    is_premium = message.from_user.is_premium if message.from_user.is_premium else 'Unknown'
    user_text = html_escape(message.text)

    for admin in ADMINS:
        callback_data = f"reply_{user_id}"
        user_message_map[callback_data] = user_id
        await bot.send_message(
            chat_id=admin,
            text=(
                f"👤 User : {full_name}\n"
                f"🔑 Username : {f'@{username}' if username else 'None'}\n"
                f"🆔 Telegram : {telegram_id}\n"
                f"📆 Data : {registration_date}\n"
                f"💎 Premium : {is_premium}\n"
                f"📨 Message : {user_text}"
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔰 Profil info", url=f"tg://user?id={telegram_id}"),
                    InlineKeyboardButton(text="📤 Javob berish", callback_data=callback_data),
                    InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"block_{telegram_id}"),
                ]
            ])
        )
    await message.delete()
    await message.answer("📬 Xabaringiz administratorga yetkazildi. Tez orada javob kuting!")
    await state.clear()


@user_router.callback_query(F.data.startswith("reply_"))
async def ask_reply_message(callback: CallbackQuery, state: FSMContext):
    user_id = user_message_map.get(callback.data)
    if user_id:
        await callback.message.answer("✉️ Javob xabaringizni kiriting:")
        await state.update_data(user_id=user_id)
        await state.set_state(UserMessageState.waiting_for_admin_reply)
    else:
        await callback.answer("❗️ Xato: User ID noto'g'ri formatda!")


@user_router.message(UserMessageState.waiting_for_admin_reply)
async def send_reply_to_user(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get("user_id")
    try:
        if user_id:
            await message.delete()
            await bot.send_message(user_id, f"<b>📥 Admin javobi</b>:\n{message.text}")
            await message.answer("✅ Javob foydalanuvchiga yuborildi!")
    except Exception as e:
        print(f"❗️ User 🆔 not found. Error : {e}")
    await state.clear()


@user_router.callback_query(F.data.startswith("block_"))
async def block_handler(call: types.CallbackQuery, session: AsyncSession):
    telegram_id = int(call.data.split("_")[1])
    user = await select_user(telegram_id, session)
    user_id = user.id
    is_blocked = user.is_active
    full_name = user.full_name
    phone = user.phone
    username = call.from_user.username
    is_premium = call.from_user.is_premium if call.from_user.is_premium else 'Unknown'
    lang_code = call.from_user.language_code if call.from_user.language_code else 'Unknown'
    text=f"New 👤: {full_name}\nUsername 🏷: {f'@{username}' if username else 'None'}\nIsm-Familya 👤: {full_name}\nTelegram 🆔: {telegram_id}\nPremium 🤑: {is_premium}\nTil 📚: {lang_code}\nTelefon raqam 📞: {phone}"
    user_profile_btn = await user_profile_button(telegram_id)
    
    if is_blocked:
        try:
            await orm_block_user(session=session, user_id=user_id, is_active=False)
            user_unblock_btn = await user_unblock_button(telegram_id)
            text = text + "\n\n✅ Ushbu foydalanuvchi bloklandi, uni blokldan chiqarmoqchimisiz?"
            await call.message.edit_text(text=text, reply_markup=user_unblock_btn)
        
        except Exception as e:
            await bot.send_message(chat_id=637914427, text=f"Error while blocking user: {e}", reply_markup=user_profile_btn)

    else:
        user_unblock_btn = await user_unblock_button(telegram_id)
        text = text + "\n\n❗️ Ushbu foydalanuvchi bloklangan, uni blokldan chiqarmoqchimisiz?"
        await call.message.edit_text(text=text, reply_markup=user_unblock_btn)
        
    
@user_router.callback_query(F.data.startswith("unblock_"))
async def unblock_handler(call: types.CallbackQuery, session: AsyncSession):
    telegram_id = int(call.data.split("_")[1])
    user = await select_user(telegram_id, session)
    user_id = user.id
    is_active = user.is_active
    full_name = user.full_name
    phone = user.phone
    username = call.from_user.username
    is_premium = call.from_user.is_premium if call.from_user.is_premium else 'Unknown'
    lang_code = call.from_user.language_code if call.from_user.language_code else 'Unknown'
    text=f"New 👤: {full_name}\nUsername 🏷: {f'@{username}' if username else 'None'}\nIsm-Familya 👤: {full_name}\nTelegram 🆔: {telegram_id}\nPremium 🤑: {is_premium}\nTil 📚: {lang_code}\nTelefon raqam 📞: {phone}"
    user_profile_btn = await user_profile_button(telegram_id)
    
    if is_active:
        text = text + "\n\n❗️ Ushbu foydalanuvchi bloklanmagan, uni bloklamoqchimisiz?"
        await call.message.edit_text(text=text, reply_markup=user_profile_btn)
        
    else:
        try:
            await orm_block_user(session=session, user_id=user_id, is_active=True)
            text = text + "\n\n✅ Ushbu foydalanuvchi blokdan chiqarildi, uni qayta bloklamoqchimisiz?"
            await call.message.edit_text(text=text, reply_markup=user_profile_btn)
        
        except Exception as e:
            await bot.send_message(chat_id=637914427, text=f"Error while blocking user: {e}", reply_markup=user_profile_btn)