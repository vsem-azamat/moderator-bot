from aiogram import Router

from . import moderation, start, admin

router = Router()

router.include_router(moderation.router)
router.include_router(start.router)
router.include_router(admin.router)
