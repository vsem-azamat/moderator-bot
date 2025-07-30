from typing import Sequence
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, id_tg: int) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == id_tg))
        return result.scalars().first()

    async def merge_user(
        self,
        id_tg: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> None:
        user = User(
            id=id_tg,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        await self.db.merge(user)
        await self.db.commit()

    async def get_blocked_users(self) -> Sequence[User]:
        result = await self.db.execute(select(User).filter(User.blocked == True))
        return result.scalars().all()

    async def add_to_blacklist(self, id_tg: int) -> None:
        user = await self.get_user(id_tg)
        if user:
            await self.db.execute(update(User).where(User.id == id_tg).values(blocked=True))
        else:
            await self.db.execute(insert(User).values(id=id_tg, blocked=True))
        await self.db.commit()

    async def remove_from_blacklist(self, id_tg: int) -> None:
        await self.db.execute(update(User).where(User.id == id_tg).values(blocked=False))
        await self.db.commit()


def get_user_repository(db: AsyncSession) -> UserRepository:
    return UserRepository(db)
