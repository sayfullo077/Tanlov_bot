from aiogram.filters.state import State, StatesGroup


class UserStart(StatesGroup):
    menu = State()
    start = State()
    check = State()
    info = State()
    event_menu = State()
    my_events = State()
    new_events = State()


class RegistrationState(StatesGroup):
    full_name = State()
    school = State()
    grade = State()
    about = State()
    phone = State()
    check = State()
    finish = State()


class UserSettings(StatesGroup):
    menu = State()
    change_fullname = State()
    change_school = State()
    change_grade = State()
    change_phone = State()


class UserMessageState(StatesGroup):
    waiting_for_message = State()
    waiting_for_admin_reply = State()


class AdminState(StatesGroup):
    menu = State()
    info = State()
    send_message = State()
    user_list = State()
    user_detail = State()


class TokenState(StatesGroup):
    menu = State()
    edit = State()
    add_title = State()
    add_token = State()
    delete = State()
    check = State()


class EditTokenState(StatesGroup):
    menu = State()
    title = State()
    token = State()


class LocationState(StatesGroup):
    get_location = State()
    
    
class EventState(StatesGroup):
    menu = State()
    get_events = State()
    detail_event = State()
    add_events = State()
    delete_events = State()
    edit_event_menu = State()
    edit_event_image = State()
    edit_event_title = State()
    edit_event_desc = State()
    edit_event_status = State()
    
    
class AddEventState(StatesGroup):
    image = State()
    title = State()
    description = State()
    check = State()
    select_channels = State()


