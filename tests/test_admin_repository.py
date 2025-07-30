import pytest
from app.infrastructure.db.repositories.admin import AdminRepository


@pytest.mark.asyncio
async def test_insert_and_check_admin(session):
    repo = AdminRepository(session)
    await repo.insert_admin(42)
    assert await repo.is_admin(42)
    admins = await repo.get_db_admins()
    assert len(admins) == 1
