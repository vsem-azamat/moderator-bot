import pytest
from app.infrastructure.db.repositories.chat import ChatRepository


@pytest.mark.asyncio
async def test_merge_and_get_chat(session):
    repo = ChatRepository(session)
    await repo.merge_chat(1, title="Test", is_forum=True)
    chat = await repo.get_chat(1)
    assert chat is not None
    assert chat.title == "Test"
    assert chat.is_forum is True
