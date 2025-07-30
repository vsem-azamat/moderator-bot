import pytest
from app.infrastructure.db.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_add_and_remove_blacklist(session):
    repo = UserRepository(session)
    await repo.add_to_blacklist(123)
    blocked = await repo.get_blocked_users()
    assert len(blocked) == 1
    assert blocked[0].id == 123

    await repo.remove_from_blacklist(123)
    blocked_after = await repo.get_blocked_users()
    assert len(blocked_after) == 0
