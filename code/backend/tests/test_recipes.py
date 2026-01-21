import pytest
from fastapi.testclient import TestClient
from io import BytesIO


def test_create_recipe(client: TestClient, auth_headers: dict):
    response = client.post("/recipes", headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "Recipe of" in data["title"]
    assert data["image"] is None


def test_get_recipes(client: TestClient, auth_headers: dict):
    client.post("/recipes", headers=auth_headers)
    client.post("/recipes", headers=auth_headers)

    response = client.get("/recipes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_recipe(client: TestClient, auth_headers: dict):
    create_response = client.post("/recipes", headers=auth_headers)
    recipe_id = create_response.json()["id"]

    response = client.get(f"/recipes/{recipe_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id


def test_get_recipe_not_found(client: TestClient, auth_headers: dict):
    response = client.get("/recipes/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_recipe_title(client: TestClient, auth_headers: dict):
    create_response = client.post("/recipes", headers=auth_headers)
    recipe_id = create_response.json()["id"]

    response = client.patch(
        f"/recipes/{recipe_id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_recipe(client: TestClient, auth_headers: dict):
    create_response = client.post("/recipes", headers=auth_headers)
    recipe_id = create_response.json()["id"]

    response = client.delete(f"/recipes/{recipe_id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/recipes/{recipe_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_upload_recipe_image(client: TestClient, auth_headers: dict):
    create_response = client.post("/recipes", headers=auth_headers)
    recipe_id = create_response.json()["id"]

    file_content = b"fake image content"
    files = {"file": ("test.jpg", BytesIO(file_content), "image/jpeg")}

    response = client.post(f"/recipes/{recipe_id}/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["image"] is not None
    assert data["image"].endswith(".jpg")


def test_recipe_isolation_between_users(client: TestClient, auth_headers: dict):
    response1 = client.post("/recipes", headers=auth_headers)
    recipe_id = response1.json()["id"]

    other_user = client.post("/auth/signup", json={
        "email": "other@example.com",
        "password": "password123"
    })
    other_headers = {"Authorization": f"Bearer {other_user.json()['access_token']}"}

    response = client.get(f"/recipes/{recipe_id}", headers=other_headers)
    assert response.status_code == 404
