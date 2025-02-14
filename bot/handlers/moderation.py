from aiogram import types, Router, Bot
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from typing import cast
from bot.logger import logger
from bot.utils import other
from bot.services import moderation as moderation_services
from database.repositories import UserRepository, ChatRepository, MessageRepository


router = Router()


def reply_required_error(message: types.Message, action: str) -> str:
    """Returns a standard error message for missing reply."""
    return f"Примените команду к сообщению человека, которого нужно {action}."


def is_user_check_error() -> str:
    """Returns a standard error message for invalid user check."""
    return "Это не пользователь или что-то пошло не так."


@router.message(Command("mute", prefix="!/"))
async def mute_user(message: types.Message, bot: Bot):
    # Ensure command is used as a reply
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "замутить"))
        await message.delete()
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    mute_guide = (
        "Для мута пользователя используйте команду в формате:\n\n"
        "<code>!mute [время] [единица времени]</code>\n\n"
        "Примеры:\n<code>!mute 5m</code> - на 5 минут\n"
        "<code>!mute 1h</code> - на 1 час\n"
        "<code>!mute 1d</code> - на 1 день\n"
        "<code>!mute 1w</code> - на 1 неделю"
    )

    # Parse and validate mute duration
    try:
        mute_duration = other.calculate_mute_duration(message.text)
    except Exception as err:
        answer = await message.answer(f"Мне не удалось распознать время мута!\n\n{mute_guide}")
        await message.delete()
        await other.sleep_and_delete(answer, 10)
        return

    # Set permissions to mute the user
    read_only_permissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
    )

    try:
        await bot.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            permissions=read_only_permissions,
            until_date=mute_duration.until_date,
        )
        mention = await other.get_user_mention(message.reply_to_message.from_user)
        text_mute = (
            f"{mention} в муте на {mute_duration.time} {mute_duration.unit}!\n\n"
            f"Дата размута: {mute_duration.formatted_until_date()}"
        )
        await message.reply_to_message.reply(text_mute)
        await message.delete()

    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")
        logger.error(f"Error while muting user: {err}")


@router.message(Command("unmute", prefix="!/"))
async def unmute_member(message: types.Message):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "размутить"))
        await message.delete()
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    # Reset permissions to default chat permissions
    default_permissions = message.chat.permissions
    if not default_permissions:
        await message.answer("Похоже, что я нахожусь не в чате или у меня нет прав администратора.")
        return

    try:
        await message.chat.restrict(
            user_id=message.reply_to_message.from_user.id,
            permissions=default_permissions,
            until_date=0,
        )
        mention = await other.get_user_mention(message.reply_to_message.from_user)
        await message.reply(f"Пользователь {mention} размучен!")
    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")


@router.message(Command("ban", prefix="!/"))
async def ban_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "забанить"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    try:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        mention = await other.get_user_mention(message.reply_to_message.from_user)
        await message.answer(f"Пользователь {mention} забанен")
    except Exception as err:
        error_msg = await message.answer(f"Что-то пошло не так:\n\n{err}")
        await other.sleep_and_delete(error_msg, 10)

    await message.delete()


@router.message(Command("unban", prefix="!/"))
async def unban_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "разбанить"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    try:
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        mention = await other.get_user_mention(message.reply_to_message.from_user)
        await message.reply(f"Пользователь {mention} разбанен")
    except Exception as err:
        error_msg = await message.answer(f"Что-то пошло не так:\n\n{err}")
        await other.sleep_and_delete(error_msg, 10)

    await message.delete()


@router.message(Command("black", prefix="!/"))
async def full_ban(message: types.Message, bot: Bot, user_repo: UserRepository):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "добавить в черный список"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        logger.warning(f"User {message.reply_to_message.from_user} is not a user.")
        return

    id_user = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, id_user)
        mention = await other.get_user_mention(message.reply_to_message.from_user)
        await message.reply_to_message.delete()
        await message.answer(f"{mention} добавлен в черный список.")
        await moderation_services.add_to_blacklist(user_repo.db, bot, id_user)
        await message.delete()
    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")
        logger.error(f"Error while adding user {id_user} to blacklist: {err}")


@router.message(Command("spam", prefix="!/"))
async def label_spam(message: types.Message, message_repo: MessageRepository, db: AsyncSession, bot: Bot):
    if not message.reply_to_message:
        answer = await message.answer(reply_required_error(message, "пометить как спам"))
        await message.delete()
        await other.sleep_and_delete(answer, 10)
        return

    spammer_message_id = message.reply_to_message.message_id
    spammer_chat_id = message.reply_to_message.chat.id
    spammer_user_id = message.reply_to_message.from_user.id

    await message_repo.label_spam(
        chat_id=spammer_chat_id,
        message_id=spammer_message_id,
    )
    await moderation_services.add_to_blacklist(db, bot, spammer_user_id, revoke_messages=True)
    await message.delete()


async def welcome_change(message: types.Message, chat_repo: ChatRepository):
    welcome_message = message.text.partition(" ")[2]
    await chat_repo.update_welcome_message(message.chat.id, welcome_message)
    await message.answer("<b>Приветственное сообщение изменено!</b>")
    await message.answer(welcome_message)
    await message.delete()
