import pytest
from fastapi.testclient import TestClient


def test_create_category(client: TestClient, auth_headers: dict):
    response = client.post("/categories", json={"name": "Breakfast"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Breakfast"
    assert "id" in data


def test_create_duplicate_category(client: TestClient, auth_headers: dict):
    client.post("/categories", json={"name": "Lunch"}, headers=auth_headers)
    response = client.post("/categories", json={"name": "Lunch"}, headers=auth_headers)
    assert response.status_code == 400


def test_get_categories(client: TestClient, auth_headers: dict):
    client.post("/categories", json={"name": "Dinner"}, headers=auth_headers)
    client.post("/categories", json={"name": "Snack"}, headers=auth_headers)

    response = client.get("/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_update_category(client: TestClient, auth_headers: dict):
    create_response = client.post("/categories", json={"name": "Dessert"}, headers=auth_headers)
    category_id = create_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "Sweet Dessert"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sweet Dessert"


def test_update_category_duplicate_name(client: TestClient, auth_headers: dict):
    client.post("/categories", json={"name": "Italian"}, headers=auth_headers)
    response2 = client.post("/categories", json={"name": "Chinese"}, headers=auth_headers)
    category_id = response2.json()["id"]

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "Italian"},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_delete_category(client: TestClient, auth_headers: dict):
    create_response = client.post("/categories", json={"name": "Mexican"}, headers=auth_headers)
    category_id = create_response.json()["id"]

    response = client.delete(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 204


def test_assign_recipes_to_category(client: TestClient, auth_headers: dict):
    category_response = client.post("/categories", json={"name": "Vegan"}, headers=auth_headers)
    category_id = category_response.json()["id"]

    recipe1 = client.post("/recipes", headers=auth_headers)
    recipe2 = client.post("/recipes", headers=auth_headers)
    recipe_ids = [recipe1.json()["id"], recipe2.json()["id"]]

    response = client.post(
        "/categories/assign",
        json={"recipe_ids": recipe_ids, "category_id": category_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(r["category_id"] == category_id for r in data)


def test_unassign_category_from_recipes(client: TestClient, auth_headers: dict):
    category_response = client.post("/categories", json={"name": "Gluten-Free"}, headers=auth_headers)
    category_id = category_response.json()["id"]

    recipe = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe.json()["id"]

    client.post(
        "/categories/assign",
        json={"recipe_ids": [recipe_id], "category_id": category_id},
        headers=auth_headers
    )

    response = client.post(
        "/categories/assign",
        json={"recipe_ids": [recipe_id], "category_id": None},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["category_id"] is None


def test_assign_nonexistent_category(client: TestClient, auth_headers: dict):
    recipe = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe.json()["id"]

    response = client.post(
        "/categories/assign",
        json={"recipe_ids": [recipe_id], "category_id": 99999},
        headers=auth_headers
    )
    assert response.status_code == 404
