import pandas as pd
import os
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete, exists, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

from database.models import Users, Channels, UserType, Tokens, UserRegistration, Events


################################ User #####################################


async def export_event_participants_to_excel(session: AsyncSession, event_id: int):
    # 1. Tadbir ma'lumotlarini va unga yozilgan userlarni bitta so'rovda olamiz
    # Avval tadbirning o'zini tekshiramiz (nomini olish uchun)
    event_stmt = select(Events).where(Events.id == event_id)
    event_result = await session.execute(event_stmt)
    event_item = event_result.scalar_one_or_none()

    if not event_item:
        return None, "Tadbir topilmadi"

    # 2. Userlarni olish
    stmt = (
        select(
            Users.full_name,
            Users.phone,
            Users.school,
            Users.grade,
            UserRegistration.registered_at
        )
        .join(UserRegistration, Users.id == UserRegistration.user_id)
        .where(UserRegistration.event_id == event_id)
    )
    
    result = await session.execute(stmt)
    rows = result.all()

    if not rows:
        return None, "Ro'yxat bo'sh"

    # 3. Ma'lumotlarni DataFrame-ga o'tkazish
    data = [{
        "F.I.SH": r.full_name,
        "Telefon": r.phone,
        "Maktab": r.school,
        "Sinf": r.grade,
        "Sana": r.registered_at.strftime("%d.%m.%Y %H:%M")
    } for r in rows]

    df = pd.DataFrame(data)

    clean_title = re.sub(r'[^\w\s-]', '', event_item.title).strip().replace(' ', '_')
    
    file_name = f"{clean_title}.xlsx"
    
    df.to_excel(file_name, index=False)
    
    return file_name, "OK"


async def orm_add_user(
    session: AsyncSession,
    telegram_id: int,
    full_name: str | None = None,
    phone: str | None = None,
) -> tuple[Users, bool]:

    query = select(Users).where(Users.telegram_id == telegram_id)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        new_user = Users(
            telegram_id=telegram_id,
            full_name=full_name or "No name",
            phone=phone or None,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user, True
    else:
        return existing_user, False


async def orm_block_user(
    session: AsyncSession,
    user_id: int,
    is_active: bool,
) -> Users | None:
    user = await session.get(Users, user_id)

    if not user:
        return None

    user.is_active = is_active
    await session.commit()
    await session.refresh(user)

    return user


async def select_user(telegram_id: int, session: AsyncSession):
    query = select(Users).filter(Users.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.scalars().first()
    return user


async def orm_update_user(session: AsyncSession, telegram_id: int, **data):
    try:
        query = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(**data)
        )
        await session.execute(query)
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        print(f"Update xatosi: {e}")
        return False


async def orm_get_user_event_history(session: AsyncSession, telegram_id: int):
    """
    Foydalanuvchi qatnashgan barcha tadbirlar ro'yxatini qaytaradi.
    """
    try:
        # 1. Avval Users jadvalidan ichki ID ni topamiz va unga tegishli registrationlarni olamiz
        query = (
            select(UserRegistration)
            .join(Users)
            .where(Users.telegram_id == telegram_id)
            .options(joinedload(UserRegistration.event)) # Event ma'lumotlarini ham birga yuklaymiz
            .order_by(UserRegistration.registered_at.desc()) # Oxirgisini birinchi ko'rsatamiz
        )
        
        result = await session.execute(query)
        registrations = result.scalars().all()
        
        return registrations # Bu list ichida UserRegistration obyektlari bo'ladi
    except Exception as e:
        print(f"Tarixni olishda xatolik: {e}")
        return []
    

async def orm_get_available_events(session: AsyncSession, telegram_id: int):
    # User ID subquery
    user_id_sub = select(Users.id).where(Users.telegram_id == telegram_id).scalar_subquery()
    
    query = (
        select(Events)
        .where(
            Events.is_active == True,
            ~exists().where(
                (UserRegistration.event_id == Events.id) & 
                (UserRegistration.user_id == user_id_sub)
            )
        )
        .order_by(Events.joined_at.desc()) # Yangilarini birinchi ko'rsatish
        .limit(10) # Faqat oxirgi 10 tasi
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_event(session: AsyncSession, data: dict):

    try:
        new_event = Events(
            title=data.get("title"),
            desc=data.get("desc"),
            image=data.get("image"),
            is_active=True
        )
        session.add(new_event)
        await session.commit()
        await session.refresh(new_event)
        return new_event
    except Exception as e:
        await session.rollback()
        print(f"Event qo'shishda xatolik: {e}")
        return None


async def update_event_field(session: AsyncSession, event_id: int, field_name: str, new_value):
    """
    Event modelidagi istalgan ustunni dinamik yangilash uchun funksiya.
    field_name: 'title', 'desc', 'image', 'is_active' va h.k. bo'lishi mumkin.
    """
    try:
        # 1. Ob'ektni bazadan olamiz
        event_item = await session.get(Events, event_id)

        if not event_item:
            return {"status": "error", "message": "Tadbir topilmadi."}

        if hasattr(event_item, field_name):
            setattr(event_item, field_name, new_value)
            
            await session.commit()
            return {"status": "success", "message": f"{field_name} muvaffaqiyatli yangilandi!"}
        else:
            return {"status": "error", "message": f"Modelda {field_name} degan ustun mavjud emas."}

    except Exception as e:
        await session.rollback()
        print(f"Yangilashda xatolik: {e}")
        return {"status": "error", "message": "Xatolik yuz berdi."}


async def orm_get_all_events(session: AsyncSession):
    query = select(Events).order_by(Events.id.desc())
    result = await session.execute(query)
    return result.scalars().all()


async def delete_event_by_id(session: AsyncSession, event_id: int):

    try:
        stmt = delete(Events).where(Events.id == event_id)
        result = await session.execute(stmt)
        
        if result.rowcount == 0:
            return {"status": "not_found", "message": "Bunday ID dagi tadbir topilmadi."}

        await session.commit()
        return {"status": "success", "message": f"ID: {event_id} bo'lgan tadbir muvaffaqiyatli o'chirildi."}

    except Exception as e:
        await session.rollback()
        print(f"O'chirishda xatolik: {e}")
        return {"status": "error", "message": "Xatolik yuz berdi, o'chirish imkonsiz."}


async def register_user_for_event(session: AsyncSession, telegram_id: int, event_id: int):
    """
    Foydalanuvchini eventga ro'yxatdan o'tkazish funksiyasi.
    """
    try:
        # 1. Avval telegram_id orqali foydalanuvchining ichki ID sini topamiz
        user_stmt = select(Users).where(Users.telegram_id == telegram_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            return {"status": "error", "message": "Foydalanuvchi topilmadi."}

        # 2. Foydalanuvchi allaqachon bu eventga ro'yxatdan o'tganmi tekshiramiz
        check_stmt = select(UserRegistration).where(
            and_(
                UserRegistration.user_id == user.id,
                UserRegistration.event_id == event_id
            )
        )
        check_result = await session.execute(check_stmt)
        existing_reg = check_result.scalar_one_or_none()

        if existing_reg:
            return {"status": "already_exists", "message": "Siz allaqachon ushbu tadbirga ro'yxatdan o'tgansiz."}

        # 3. Yangi ro'yxatdan o'tish yozuvini yaratamiz
        new_registration = UserRegistration(
            user_id=user.id,
            event_id=event_id
        )
        
        session.add(new_registration)
        await session.commit() # Ma'lumotni DBga saqlaymiz
        
        return {"status": "success", "message": "Muvaffaqiyatli ro'yxatdan o'tdingiz!"}

    except Exception as e:
        await session.rollback() # Xatolik bo'lsa ortga qaytaramiz
        print(f"Xatolik yuz berdi: {e}")
        return {"status": "error", "message": "Tizimda xatolik yuz berdi."}
    

async def is_user_active(telegram_id: int, session: AsyncSession) -> bool | None:
    
    try:
        query = select(Users.is_active).where(Users.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    except Exception as e:
        print(f"Xatolik: {e}")
        return None


async def select_all_users(session: AsyncSession):
    query = select(Users)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_all_users(session: AsyncSession):
    try:
        query = delete(Users)
        await session.execute(query)
        await session.commit()

    except Exception as e:
        await session.rollback()
        print(f"Error deleting users: {e}")


async def count_daily_users(session: AsyncSession):
    today = datetime.now().date()
    query = select(func.count()).where(Users.joined_at >= today)
    result = await session.execute(query)
    return result.scalar()


async def count_weekly_users(session: AsyncSession):
    last_week = datetime.now().date() - timedelta(days=7)
    query = select(func.count()).where(Users.joined_at >= last_week)
    result = await session.execute(query)
    return result.scalar()


async def count_monthly_users(session: AsyncSession):
    last_month = datetime.now().date() - timedelta(days=30)
    query = select(func.count()).where(Users.joined_at >= last_month)
    result = await session.execute(query)
    return result.scalar()


async def count_users(session: AsyncSession):
    query = select(func.count()).select_from(Users)
    result = await session.execute(query)
    return result.scalar()


async def orm_admin_exist(session: AsyncSession, admin_id: int) -> bool:
    stmt = select(exists().where(Users.telegram_id == admin_id))
    result = await session.execute(stmt)
    return result.scalar()


async def orm_add_admin(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    company_id: int,
    branch_id: int,
    user_type: UserType = UserType.ADMIN,   # default ADMIN
):
    new_admin = Users(
        telegram_id=telegram_id,
        full_name=full_name,
        company_id=company_id,
        branch_id=branch_id,
        user_type=user_type,
        is_active=True
    )
    session.add(new_admin)

    try:
        await session.commit()
        await session.refresh(new_admin)
        return new_admin
    except IntegrityError:
        await session.rollback()
        return None


async def orm_delete_admin_by_id(session: AsyncSession, admin_id: int):
    query = delete(Users).where(Users.telegram_id == admin_id)
    await session.execute(query)
    await session.commit()


async def orm_delete_by_id(session: AsyncSession, telegram_id: int):
    query = delete(Users).where(Users.telegram_id == telegram_id)
    await session.execute(query)
    await session.commit()


######################## Channel #######################################


async def select_channel(session: AsyncSession, channel_id: int):
    query = select(Channels).where(Channels.channel_id == channel_id)
    result = await session.execute(query)
    return result.scalars().first()


async def delete_channels(session: AsyncSession):
    query = delete(Channels)
    await session.execute(query)
    await session.commit()

######################## Channel #######################################


async def save_single_token(title: str, token: str, session: AsyncSession):
    try:
        await session.execute(delete(Tokens))
        await session.commit()

        new_token = Tokens(
            title=title,
            token=token,
            count=0
        )

        session.add(new_token)
        await session.commit()
        await session.refresh(new_token)

        return new_token

    except Exception as e:
        await session.rollback()
        raise e


async def get_single_token(session: AsyncSession) -> Tokens | None:
    query = await session.execute(select(Tokens))
    return query.scalar_one_or_none()


async def update_single_token(
    token_id: int,
    session: AsyncSession,
    title: str = None,
    token: str = None
):
    query = await session.execute(select(Tokens).where(Tokens.id == token_id))
    token_obj = query.scalar_one_or_none()

    if not token_obj:
        return None

    if title is not None:
        token_obj.title = title

    if token is not None and token != token_obj.token:
        token_obj.token = token
        token_obj.count = 0

    await session.commit()
    await session.refresh(token_obj)

    return token_obj


async def delete_ai_token(session: AsyncSession, token_id: int) -> bool:
    result = await session.execute(
        select(Tokens).where(Tokens.id == token_id)
    )
    token_obj = result.scalar_one_or_none()

    if not token_obj:
        return False

    await session.delete(token_obj)
    await session.commit()

    return True


async def increment_token_count(session: AsyncSession, token_id: int):
    await session.execute(
        update(Tokens)
        .where(Tokens.id == token_id)
        .values(count=Tokens.count + 1)
    )
    await session.commit()
