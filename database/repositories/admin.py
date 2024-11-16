from typing import Sequence
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Admin


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_db_admins(self) -> Sequence[Admin]:
        result = await self.db.execute(select(Admin))
        return result.scalars().all()

    async def insert_admin(self, id_tg: int) -> None:
        await self.db.execute(insert(Admin).values(id=id_tg))
        await self.db.commit()


def get_admin_repository(db: AsyncSession) -> AdminRepository:
    return AdminRepository(db)
