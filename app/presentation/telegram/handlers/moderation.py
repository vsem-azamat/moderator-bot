from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from typing import cast
from app.presentation.telegram.logger import logger
from app.presentation.telegram.utils import other, BlacklistConfirm
from app.application.services import moderation as moderation_services
from app.application.services import spam as spam_service
from app.infrastructure.db.repositories import ChatRepository, MessageRepository


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
async def full_ban(message: types.Message, bot: Bot, message_repo: MessageRepository, db: AsyncSession):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "добавить в черный список"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        logger.warning(f"User {message.reply_to_message.from_user} is not a user.")
        return

    target = message.reply_to_message
    id_user = target.from_user.id
    chats_count = await message_repo.count_user_chats(id_user)
    messages_count = await message_repo.count_user_messages(id_user)
    spam_flag = await spam_service.detect_spam(db, target)

    info_text = (
        "<b>Вы уверены?</b>\n\n"
        "<b>Информация:</b>\n"
        f"- {chats_count} чатов\n"
        f"- {messages_count} сообщений\n"
        f"- {'спам обнаружен' if spam_flag else 'спам не обнаружен'}"
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Yes",
        callback_data=BlacklistConfirm(
            user_id=id_user,
            chat_id=target.chat.id,
            message_id=target.message_id,
        ).pack(),
    )
    builder.button(text="No", callback_data="cancel_blacklist")
    builder.adjust(2)
    await message.answer(info_text, reply_markup=builder.as_markup())
    await message.delete()


@router.message(Command("spam", prefix="!/"))
async def label_spam(message: types.Message, message_repo: MessageRepository, db: AsyncSession, bot: Bot):
    if not message.reply_to_message:
        answer = await message.answer(reply_required_error(message, "пометить как спам"))
        await message.delete()
        await other.sleep_and_delete(answer, 10)
        return

    target = message.reply_to_message
    spammer_user_id = target.from_user.id
    chats_count = await message_repo.count_user_chats(spammer_user_id)
    messages_count = await message_repo.count_user_messages(spammer_user_id)
    spam_flag = await spam_service.detect_spam(db, target)

    info_text = (
        "<b>Вы уверены?</b>\n\n"
        "<b>Информация:</b>\n"
        f"- {chats_count} чатов\n"
        f"- {messages_count} сообщений\n"
        f"- {'спам обнаружен' if spam_flag else 'спам не обнаружен'}"
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Yes",
        callback_data=BlacklistConfirm(
            user_id=spammer_user_id,
            chat_id=target.chat.id,
            message_id=target.message_id,
            revoke=1,
            mark_spam=1,
        ).pack(),
    )
    builder.button(text="No", callback_data="cancel_blacklist")
    builder.adjust(2)
    await message.answer(info_text, reply_markup=builder.as_markup())
    await message.delete()


async def welcome_change(message: types.Message, chat_repo: ChatRepository):
    welcome_message = message.text.partition(" ")[2]
    await chat_repo.update_welcome_message(message.chat.id, welcome_message)
    await message.answer("<b>Приветственное сообщение изменено!</b>")
    await message.answer(welcome_message)
    await message.delete()


@router.callback_query(BlacklistConfirm.filter())
async def process_blacklist_confirm(
    callback: types.CallbackQuery,
    callback_data: BlacklistConfirm,
    bot: Bot,
    db: AsyncSession,
    message_repo: MessageRepository,
):
    user_id = callback_data.user_id
    chat_id = callback_data.chat_id
    message_id = callback_data.message_id
    revoke = bool(callback_data.revoke)
    mark_spam = bool(callback_data.mark_spam)

    if mark_spam:
        await message_repo.label_spam(chat_id=chat_id, message_id=message_id)

    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as err:
        logger.warning(f"Failed to delete message {message_id}: {err}")

    try:
        await bot.ban_chat_member(callback.message.chat.id, user_id)
        member = await bot.get_chat_member(callback.message.chat.id, user_id)
        mention = await other.get_user_mention(member.user)
        await moderation_services.add_to_blacklist(db, bot, user_id, revoke_messages=revoke)
        await callback.message.edit_text(f"{mention} добавлен в черный список.")
    except Exception as err:
        await callback.message.edit_text(f"Произошла ошибка:\n\n{err}")
        logger.error(f"Error while adding user {user_id} to blacklist: {err}")

    await callback.answer()


@router.callback_query(lambda c: c.data == "cancel_blacklist")
async def process_blacklist_cancel(callback: types.CallbackQuery):
    await callback.message.edit_text("Действие отменено")
    await callback.answer()
