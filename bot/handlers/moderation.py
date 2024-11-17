from aiogram import types, Router, Bot
from aiogram.filters import Command

from bot.logger import logger
from bot.utils import other, filters
from bot.services import moderation
from database.repositories import UserRepository, ChatRepository, MessageRepository


router = Router()


def reply_required_error(message: types.Message, action: str) -> str:
    """Returns a standard error message for missing reply."""
    return f"Примените команду к сообщению человека, которого нужно {action}."


def is_user_check_error() -> str:
    """Returns a standard error message for invalid user check."""
    return "Это не пользователь или что-то пошло не так."


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("mute", prefix="!/"),
    filters.AnyAdminFilter(),
)
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
        mention = await other.get_mention(message.reply_to_message.from_user)
        text_mute = (
            f"{mention} в муте на {mute_duration.time} {mute_duration.unit}!\n\n"
            f"Дата размута: {mute_duration.formatted_until_date()}"
        )
        await message.reply_to_message.reply(text_mute)
        await message.delete()

    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")
        logger.error(f"Error while muting user: {err}")


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("unmute", prefix="!/"),
    filters.AnyAdminFilter(),
)
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
        mention = await other.get_mention(message.reply_to_message.from_user)
        await message.reply(f"Пользователь {mention} размучен!")
    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("ban", prefix="!/"),
    filters.AnyAdminFilter(),
)
async def ban_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "забанить"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    try:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        mention = await other.get_mention(message.reply_to_message.from_user)
        await message.reply(f"Пользователь {mention} забанен")
    except Exception as err:
        error_msg = await message.answer(f"Что-то пошло не так:\n\n{err}")
        await other.sleep_and_delete(error_msg, 10)

    await message.delete()


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("unban", prefix="!/"),
    filters.AnyAdminFilter(),
)
async def unban_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "разбанить"))
        return

    if not message.reply_to_message.from_user:
        await message.answer(is_user_check_error())
        return

    try:
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        mention = await other.get_mention(message.reply_to_message.from_user)
        await message.reply(f"Пользователь {mention} разбанен")
    except Exception as err:
        error_msg = await message.answer(f"Что-то пошло не так:\n\n{err}")
        await other.sleep_and_delete(error_msg, 10)

    await message.delete()


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("black", prefix="!/"),
    filters.AnyAdminFilter(),
)
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
        mention = await other.get_mention(message.reply_to_message.from_user)
        await message.reply_to_message.delete()
        await message.answer(f"{mention} добавлен в черный список.")
        await moderation.add_to_blacklist(user_repo.db, bot, id_user)
    except Exception as err:
        await message.answer(f"Произошла ошибка:\n\n{err}")
        logger.error(f"Error while adding user {id_user} to blacklist: {err}")


@router.message(
    filters.ChatTypeFilter(["group", "supergroup"]),
    Command("spam", prefix="!/"),
    filters.AnyAdminFilter(),
)
async def label_spam(message: types.Message, message_repo: MessageRepository, bot: Bot):
    if not message.reply_to_message:
        await message.answer(reply_required_error(message, "пометить как спам"))
        return

    spammer_message_id = message.reply_to_message.message_id
    spammer_chat_id = message.reply_to_message.chat.id
    spammer_user_id = message.reply_to_message.from_user.id

    await message_repo.label_spam(
        spammer_message_id,
        spammer_user_id,
    )
    await bot.delete_message(spammer_chat_id, spammer_message_id)
    await message.delete()

    user_messages = await message_repo.get_user_messages(spammer_user_id)
    for message_row in user_messages:
        try:
            await bot.ban_chat_member(message_row.chat_id, message_row.user_id, revoke_messages=True)
        except Exception as err:
            logger.error(f"Error while deleting message: {err}")


async def welcome_change(message: types.Message, chat_repo: ChatRepository):
    welcome_message = message.text.partition(" ")[2]
    await chat_repo.update_welcome_message(message.chat.id, welcome_message)
    await message.answer("<b>Приветственное сообщение изменено!</b>")
    await message.answer(welcome_message)
    await message.delete()
