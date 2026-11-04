import os

# Antes de importar la app: valores seguros para pruebas.
os.environ.setdefault("FIREBASE_PROJECT_ID", "demo-friendlyeats")

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_service
from app.main import app
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService
from tests.fake_firestore import FakeFirestore


@pytest.fixture
def repo():
    return RestaurantRepository(db=FakeFirestore())


@pytest.fixture
def client(repo):
    """Cliente HTTP conectado a un Firestore falso (cada prueba empieza vacía)."""
    service = RestaurantService(repository=repo)
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_restaurant(client):
    def _make(**overrides):
        payload = {
            "name": "Restaurante Test",
            "category": "Mexicana",
            "city": "Puebla",
            "price": 2,
        }
        payload.update(overrides)
        response = client.post("/api/v1/restaurants", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
