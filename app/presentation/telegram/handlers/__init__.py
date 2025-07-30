from aiogram import Router

from . import moderation, start, admin, groups, service
from app.presentation.telegram.middlewares import (
    admin as admin_middlewares,
    chat_type as chat_type_middlewares,
)

router = Router()

moderation.router.message.middleware(admin_middlewares.AdminMiddleware())
admin.router.message.middleware(chat_type_middlewares.ChatTypeMiddleware(["group", "supergroup"]))
admin.router.message.middleware(admin_middlewares.SuperAdminMiddleware())
groups.router.message.middleware(chat_type_middlewares.ChatTypeMiddleware(["group", "supergroup"]))
service.router.message.middleware(admin_middlewares.AdminMiddleware())

router.include_router(moderation.router)
router.include_router(start.router)
router.include_router(admin.router)
router.include_router(groups.router)
router.include_router(service.router)
