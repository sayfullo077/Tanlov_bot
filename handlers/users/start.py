import re
import json
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline.inline_buttons import start_button, check_member_button, user_profile_button, refresh_button, main_menu_button
from states.all_states import UserStart, RegistrationState
from database.config import PRIVATE_CHANNEL, CHANNEL_USERNAME, ADMINS
from database.orm_query import select_user, orm_add_user
from loader import bot
from datetime import datetime

user_router = Router()


# HTML escape function
def html_escape(text):
    escape_chars = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}
    return re.sub(r'[&<>"\']', lambda match: escape_chars[match.group(0)], text)


# check subscription member function
async def is_user_subscribed(user_id: int) -> bool:
    """Foydalanuvchi barcha kanallarga obuna bo'lganligini tekshiradi."""
    for channel_id in PRIVATE_CHANNEL:
        try:
            # bot obyekti loader.py dan import qilingan deb hisoblaymiz
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Kanalni tekshirishda xato ({channel_id}): {e}")
            return False
    return True


# User start functions
@user_router.message(CommandStart())
async def start_func(message: types.Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    username = message.from_user.username
    registration_date = datetime.now().strftime("%Y-%m-%d")
    is_premium = message.from_user.is_premium if message.from_user.is_premium else 'Unknown'
    lang_code = message.from_user.language_code if message.from_user.language_code else 'Unknown'
    user = await select_user(telegram_id, session)
    full_name = html_escape(message.from_user.full_name)
    subscribed = await is_user_subscribed(telegram_id)
    check_member_btn = await check_member_button(CHANNEL_USERNAME)
    start_btn = await start_button()
    user_profile_btn = await user_profile_button(telegram_id)

    if not user:
        try:
            await orm_add_user(session, telegram_id, full_name, phone=None)
            text=f"New 👤: {full_name}\nUsername📩: {f'@{username}' if username else 'None'}\nTelegram 🆔: {telegram_id}\nReg 📆: {registration_date}\nPremium🤑: {is_premium}\nLang: {lang_code}"
            await bot.send_message(chat_id=637914427, text=text, reply_markup=user_profile_btn)
            if not subscribed:
                await message.answer("Shu kabi tanlovlarni o'tkazib yubormaslik uchun bizning kanallarimizga obuna bo'lishingiz kerak 😊",
                                    reply_markup=start_btn)
                await state.set_state(UserStart.menu)
            else:
                await message.answer(
                    "<b>⚠️ Siz hali to'liq ro'yxatdan o'tmagansiz</b>\n\n"
                    "<b>Ism-familiyangizni kiriting:</b>\n(Misol: <i>Abdullayev Jahongir</i>)"
                )
            
            await state.set_state(RegistrationState.full_name)
                
        except Exception as e:
            for admin in ADMINS:
                await bot.send_message(chat_id=637914427, text=f"Error while creating new user: {e}", reply_markup=user_profile_btn)

    else:
        school = user.school
        if not subscribed:
            # Obuna bo'lmagan foydalanuvchi uchun
            await message.answer("Siz kanallarga obuna bo'lmagansiz!", reply_markup=check_member_btn)
            return
        
        elif school:
                main_menu_btn = await main_menu_button()
                await message.answer("Bosh menyu", reply_markup=main_menu_btn)
            await state.set_state(UserStart.menu)
        else:
            await message.answer(
                    "<b>⚠️ Siz hali to'liq ro'yxatdan o'tmagansiz</b>\n\n"
                    "<b>Ism-familiyangizni kiriting:</b>\n(Misol: <i>Abdullayev Jahongir</i>)"
                )
            await state.set_state(RegistrationState.full_name)
    


@user_router.callback_query(F.data == "check_sub")
async def check_subscription(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    user_id = call.from_user.id
    user = await select_user(user_id, session)
    school = user.school
    all_subscribed = True  # Hammasiga a'zo degan faraz bilan boshlaymiz

    try:
        # 1. Hammasini tekshirib chiqamiz
        for channel_id in PRIVATE_CHANNEL:
            try:
                member = await call.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    all_subscribed = False
                    break  # Bittasiga a'zo bo'lmasa, qolganini tekshirish shart emas
            except Exception:
                all_subscribed = False
                break

        # 2. Tekshiruv natijasiga qarab FAQAT BIR MARTA javob beramiz
        if all_subscribed:
            # Agar xabar o'chmagan bo'lsa o'chiramiz (Double click xatosini oldini olish uchun)
            try:
                await call.message.delete()
            except:
                pass
            
            if school:
                main_menu_btn = await main_menu_button()
                await call.message.answer("🔎 Bosh sahifa", reply_markup=main_menu_btn)
            else:
                await call.message.answer(
                    "Obuna bo'lganingiz uchun rahmat, endi to'liq ro'yxatdan o'tib olsangiz bo'ladi 😊\n\n"
                    "<b>Ism-familiyangizni kiriting:</b>\n(Misol: <i>Abdullayev Jahongir</i>)"
                )
            
            await state.set_state(RegistrationState.full_name)
            # Bu yerda foydalanuvchi ismini kutish uchun State ni ham o'zgartirishingiz mumkin
        else:
            # Hali obuna bo'lmagan bo'lsa, xabarni o'chirmaymiz, 
            # shunchaki "Obuna bo'lmagansiz" deb ogohlantirish (alert) chiqaramiz
            await call.answer(
                "⚠️ Siz hali barcha kanallarga obuna bo'lmagansiz!", 
                show_alert=True
            )

    except Exception as e:
        await call.message.answer(f"Xatolik yuz berdi: {e}")


