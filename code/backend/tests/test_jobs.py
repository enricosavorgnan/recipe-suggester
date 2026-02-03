import pytest
from fastapi.testclient import TestClient
import time


def test_create_ingredients_job(client: TestClient, auth_headers: dict):
    recipe_response = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe_response.json()["id"]

    response = client.post(f"/jobs/ingredients/{recipe_id}", headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["status"] == "running"
    assert "id" in data


def test_create_duplicate_ingredients_job(client: TestClient, auth_headers: dict):
    recipe_response = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe_response.json()["id"]

    client.post(f"/jobs/ingredients/{recipe_id}", headers=auth_headers)
    response = client.post(f"/jobs/ingredients/{recipe_id}", headers=auth_headers)
    assert response.status_code == 400


def test_get_ingredients_job(client: TestClient, auth_headers: dict):
    recipe_response = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe_response.json()["id"]

    create_response = client.post(f"/jobs/ingredients/{recipe_id}", headers=auth_headers)
    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/ingredients/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["status"] in ["running", "completed", "failed"]


def test_get_ingredients_job_not_found(client: TestClient, auth_headers: dict):
    response = client.get("/jobs/ingredients/99999", headers=auth_headers)
    assert response.status_code == 404


def test_ingredients_job_isolation(client: TestClient, auth_headers: dict):
    recipe_response = client.post("/recipes", headers=auth_headers)
    recipe_id = recipe_response.json()["id"]
    job_response = client.post(f"/jobs/ingredients/{recipe_id}", headers=auth_headers)
    job_id = job_response.json()["id"]

    # Create another user
    other_user = client.post("/auth/signup", json={
        "email": "other2@example.com",
        "password": "password123"
    })
    other_headers = {"Authorization": f"Bearer {other_user.json()['access_token']}"}

    # Other user should not be able to access this job
    response = client.get(f"/jobs/ingredients/{job_id}", headers=other_headers)
    assert response.status_code == 404
