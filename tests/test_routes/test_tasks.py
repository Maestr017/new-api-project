from fastapi import status


async def test_add_and_get_task(async_client):
    await async_client.post("/register", params={
        "user_email": "taskuser@example.com",
        "password": "pass123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    })
    login_resp = await async_client.post("/login", data={"username": "taskuser@example.com", "password": "pass123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post("/tasks", params={"title": "Test Task", "description": "desc"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "task_id" in data

    response_get = await async_client.get("/tasks", headers=headers)
    assert response_get.status_code == status.HTTP_200_OK
    task_data = response_get.json()

    assert isinstance(task_data, list)
    assert len(task_data) > 0
    assert task_data[0]["title"] == "Test Task"
    assert task_data[0]["description"] == "desc"
