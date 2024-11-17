from typing import Sequence
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, id_tg: int) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == id_tg))
        return result.scalars().first()

    async def add_user_if_is_missing(self, id_tg: int) -> None:
        if not await self.get_user(id_tg):
            await self.db.execute(insert(User).values(id=id_tg))
            await self.db.commit()

    async def get_blocked_users(self) -> Sequence[User]:
        result = await self.db.execute(select(User).filter(User.blocked == True))
        return result.scalars().all()

    async def add_to_blacklist(self, id_tg: int) -> None:
        await self.db.execute(insert(User).values(id=id_tg, blocked=True))
        await self.db.commit()


def get_user_repository(db: AsyncSession) -> UserRepository:
    return UserRepository(db)
