from sqlalchemy import Integer, String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    state: Mapped[Boolean] = mapped_column(Boolean, default=True)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    welcome_message: Mapped[String] = mapped_column(String)
    time_delete: Mapped[Integer] = mapped_column(Integer, default=60)
    is_welcome_enabled: Mapped[Boolean] = mapped_column(Boolean, default=False)
    is_captcha_enabled: Mapped[Integer] = mapped_column(Integer, default=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    verify: Mapped[Boolean] = mapped_column(Boolean, default=True)
    blocked: Mapped[Boolean] = mapped_column(Boolean, default=False)


class ChatLink(Base):
    __tablename__ = "chat_links"

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    text: Mapped[String] = mapped_column(String, unique=True)
    link: Mapped[String] = mapped_column(String, unique=True)
    priority: Mapped[Integer] = mapped_column(Integer, default=0)
