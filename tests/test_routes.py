import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import AsyncMock
from src.repositories.repository import TaskRepository
from src.schemas.schemas import STask, STaskAdd, STaskId, STaskDelete


@pytest.mark.asyncio
async def test_get_tasks(mocker):
    mock_tasks = [
        STask(id=1, name="Mocked Task 1", description="Mock description 1"),
        STask(id=2, name="Mocked Task 2", description="Mock description 2"),
    ]
    mocker.patch.object(TaskRepository, "find_all", AsyncMock(return_value=mock_tasks))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks")

    assert response.status_code == 200
    data = [STask(**item) for item in response.json()]
    assert data == mock_tasks


@pytest.mark.asyncio
async def test_add_task(mocker):
    mock_task_id = 1
    mocker.patch.object(TaskRepository, "add_one", AsyncMock(return_value=mock_task_id))

    task_data = STaskAdd(name="New Task", description="New description")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/tasks", json=task_data.model_dump())

    assert response.status_code == 200
    response_data = STaskId(**response.json())
    assert response_data.task_id == mock_task_id


@pytest.mark.asyncio
async def test_update_task(mocker):
    updated_task = STask(id=1, name="Updated Task", description="Updated description")
    mocker.patch.object(TaskRepository, "update_one", AsyncMock(return_value=updated_task))

    task_data = STaskAdd(name="Updated Task", description="Updated description")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put("/tasks/1", json=task_data.model_dump())

    assert response.status_code == 200
    response_data = STask(**response.json())
    assert response_data == updated_task


@pytest.mark.asyncio
async def test_delete_task(mocker):
    mocker.patch.object(
        TaskRepository,
        "delete_one",
        AsyncMock(return_value={"ok": True, "message": "Deleted successfully"})
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/tasks/1")

    assert response.status_code == 200
    response_data = STaskDelete(**response.json())
    assert response_data.ok is True
