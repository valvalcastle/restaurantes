"""Prueba contra el emulador REAL de Firestore.

Se omite por defecto. Para correrla:
  1) firebase emulators:start --only firestore
  2) RUN_EMULATOR_TESTS=1 pytest -v tests/test_emulator_integration.py
"""
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = [
    pytest.mark.emulator,
    pytest.mark.skipif(
        os.getenv("RUN_EMULATOR_TESTS") != "1",
        reason="Define RUN_EMULATOR_TESTS=1 con el emulador corriendo",
    ),
]


def test_crud_roundtrip_against_emulator():
    client = TestClient(app)  # sin overrides: usa el Firestore real/emulador
    created = client.post(
        "/api/v1/restaurants",
        json={"name": "Integración", "category": "Test", "city": "Puebla", "price": 1},
    )
    assert created.status_code == 201
    rid = created.json()["id"]
    try:
        assert client.get(f"/api/v1/restaurants/{rid}").json()["name"] == "Integración"
        patched = client.patch(f"/api/v1/restaurants/{rid}", json={"name": "Integración 2"})
        assert patched.json()["name"] == "Integración 2"
    finally:
        assert client.delete(f"/api/v1/restaurants/{rid}").status_code == 204
    assert client.get(f"/api/v1/restaurants/{rid}").status_code == 404
