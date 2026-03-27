from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from aiogram import F
import logging
from states.all_states import RegistrationState, UserMessageState, UserSettings, UserStart
from keyboards.inline.inline_buttons import back_button, start_button, main_menu_button, settings_button, event_menu_button


user_router = Router()
logger = logging.getLogger(__name__)


@user_router.callback_query(F.data == "back")
async def back_handler(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    telegram_id = call.from_user.id
    logger.info("Back pressed by %s, state=%s", call.from_user.id, current_state)
    back_btn = await back_button()
    
    if current_state in [RegistrationState.full_name.state,
                        UserMessageState.waiting_for_message,
                        UserSettings.menu,
                        UserStart.info,
                        UserStart.event_menu,
                        ]:
        main_menu_btn = await main_menu_button()
        await call.message.edit_text("🔎 Bosh sahifa", reply_markup=main_menu_btn)
        await state.clear()
        
    elif current_state in [UserSettings.change_fullname,
                        UserSettings.change_school,
                        UserSettings.change_grade,        
                        ]:
        settings_kb = await settings_button()
        await call.message.edit_text("🛠 Sozlamalar", reply_markup=settings_kb)
        await state.set_state(UserSettings.menu)
        
    elif current_state == UserSettings.change_phone:
        settings_kb = await settings_button()
        await call.message.delete()
        await call.message.answer("◀️ Ortga qaytish", reply_markup=types.ReplyKeyboardRemove())
        await call.message.answer("🛠 Sozlamalar", reply_markup=settings_kb)
        await state.set_state(UserSettings.menu)
        
    elif current_state in [UserStart.my_events,
                           UserStart.new_events,
                           ]:
        event_menu_kb = await event_menu_button()
        await call.message.edit_text("📌 Tanlovlar", reply_markup=event_menu_kb)
        await state.set_state(UserStart.event_menu)
        
    elif current_state == RegistrationState.school.state:
        await call.message.edit_text(
            "<b>Ism-Familyangizni kiriting:</b>\n\nMasalan: <i>Aliyev Vali</i>",
            reply_markup=back_btn,
            parse_mode="HTML"
        )
        await state.set_state(RegistrationState.full_name)

    elif current_state == RegistrationState.course.state:
        await call.message.edit_text(
            "<b>Nechinchi sinfda o'qiysiz?:</b>\n\nMasalan: <i>7-sinf</i>",
            reply_markup=back_btn,
            parse_mode="HTML"
        )
        await state.set_state(RegistrationState.school)

    elif current_state == RegistrationState.about.state:
        await call.message.edit_text(
            "<b>Qaysi fandan tayyorlanmoqchisiz?:</b>\n\nMasalan: <i>Ingliz tili</i>",
            reply_markup=back_btn,
            parse_mode="HTML"
        )
        await state.set_state(RegistrationState.course)

    elif current_state == RegistrationState.phone.state:
        await call.message.edit_text(
            "<b>Biz haqimizda qayerdan eshitgansiz?:</b>\n\nMasalan: <i>Instagram</i>",
            reply_markup=back_btn,
            parse_mode="HTML"
        )
        await state.set_state(RegistrationState.about)

    await call.answer()