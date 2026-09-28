import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./instance/test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_register_login_and_home_plan():
    with TestClient(app) as client:
        email = "test@example.com"
        response = client.post("/register", json={"name":"Test User","email":email,"password":"password123"}, headers={"accept":"application/json"})
        assert response.status_code in (200, 409)
        client.post("/login", json={"email":email,"password":"password123"}, headers={"accept":"application/json"})
        token_response = client.post("/token", json={"email":email,"password":"password123"})
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]
        response = client.post("/api/generate-home", json={"budget":100000,"currency":"INR","rooms":["Living Room"],"style":"modern","notes":"","quantities":{}}, headers={"Authorization":f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["planner"] == "home"
