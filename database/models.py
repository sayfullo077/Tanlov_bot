from sqlalchemy import DateTime, String, Text, BigInteger, Boolean, Enum, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates, relationship
from datetime import datetime
from sqlalchemy.sql import func
import re
import enum


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class UserRegistration(Base):
    __tablename__ = 'user_registrations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete="CASCADE"))
    
    # Ro'yxatdan o'tgan vaqtini alohida saqlash foydali
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship (ixtiyoriy, ma'lumot olishni osonlashtiradi)
    user = relationship("Users", back_populates="registrations")
    event = relationship("Events", back_populates="participants")


class UserType(enum.Enum):
    ADMIN = "Admin"
    STUDENT = "Student"
    TEACHER = "Teacher"


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.STUDENT)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(13), nullable=True, unique=True)
    school: Mapped[str | None] = mapped_column(String(150), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    registrations = relationship("UserRegistration", back_populates="user")

    @validates("phone")
    def validate_phone(self, key, value):
        if value is None:
            return value  # phone hali kiritilmagan bo‘lsa ruxsat beramiz

        if not re.match(r"^\+998\d{9}$", value):
            raise ValueError("Invalid phone format")

        return value


class Events(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=True)
    desc: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    participants = relationship("UserRegistration", back_populates="event")

class Channels(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)


class Tokens(Base):
    __tablename__ = 'tokens'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)