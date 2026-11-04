"""Pruebas del CRUD, filtros, paginación y validaciones (API)."""
API = "/api/v1/restaurants"


# --- Salud ---------------------------------------------------------------
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Crear (HU-01) -------------------------------------------------------
def test_create_restaurant(client):
    payload = {"name": "La Abuela", "category": "Mexicana", "city": "Puebla", "price": 2,
               "photoUrl": "https://example.com/foto.jpg"}
    response = client.post(API, json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == "La Abuela"
    assert body["avgRating"] == 0
    assert body["numRatings"] == 0


def test_create_persists_document(client, repo):
    created = client.post(API, json={"name": "A", "category": "B", "city": "C", "price": 1}).json()
    assert repo.get(created["id"])["name"] == "A"


def test_create_trims_spaces_in_text_and_photo_url(client):
    response = client.post(API, json={"name": "  Con espacios  ", "category": "X", "city": "Y",
                                      "price": 1, "photoUrl": " https://example.com/a.jpg "})
    assert response.json()["name"] == "Con espacios"
    assert response.json()["photoUrl"] == "https://example.com/a.jpg"


def test_create_ignores_empty_photo_url(client):
    response = client.post(API, json={"name": "A", "category": "B", "city": "C", "price": 1,
                                      "photoUrl": ""})
    assert response.status_code == 201
    assert response.json()["photoUrl"] is None


def test_create_invalid_price(client):
    for price in (0, 4, 10, -1):
        response = client.post(API, json={"name": "T", "category": "M", "city": "P", "price": price})
        assert response.status_code == 422, price


def test_create_missing_or_empty_required_fields(client):
    assert client.post(API, json={"category": "M", "city": "P", "price": 1}).status_code == 422
    assert client.post(API, json={"name": "", "category": "M", "city": "P", "price": 1}).status_code == 422
    assert client.post(API, json={"name": "   ", "category": "M", "city": "P", "price": 1}).status_code == 422


def test_create_invalid_photo_url(client):
    response = client.post(API, json={"name": "T", "category": "M", "city": "P", "price": 1,
                                      "photoUrl": "ftp://nope"})
    assert response.status_code == 422


def test_create_cannot_set_rating_fields(client):
    response = client.post(API, json={"name": "T", "category": "M", "city": "P", "price": 1,
                                      "avgRating": 5, "numRatings": 99})
    assert response.status_code == 422


# --- Obtener (HU-03) -----------------------------------------------------
def test_get_restaurant(client, make_restaurant):
    created = make_restaurant(name="Detalle")
    response = client.get(f"{API}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Detalle"


def test_get_restaurant_not_found(client):
    response = client.get(f"{API}/no-existe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurante no encontrado"


# --- Listar, filtrar, ordenar, paginar (HU-02) ---------------------------
def test_list_empty(client):
    response = client.get(API)
    assert response.status_code == 200
    assert response.json() == []


def test_list_default_order_by_name(client, make_restaurant):
    for name in ("Zeta", "Alfa", "Mango"):
        make_restaurant(name=name)
    names = [r["name"] for r in client.get(API).json()]
    assert names == ["Alfa", "Mango", "Zeta"]


def test_filter_by_city_category_and_price(client, make_restaurant):
    make_restaurant(name="A", city="Puebla", category="Pizza", price=1)
    make_restaurant(name="B", city="Puebla", category="Mexicana", price=2)
    make_restaurant(name="C", city="Veracruz", category="Mexicana", price=3)

    assert {r["name"] for r in client.get(API, params={"city": "Puebla"}).json()} == {"A", "B"}
    assert {r["name"] for r in client.get(API, params={"category": "Mexicana"}).json()} == {"B", "C"}
    assert {r["name"] for r in client.get(API, params={"price": 3}).json()} == {"C"}
    combined = client.get(API, params={"city": "Puebla", "category": "Mexicana", "price": 2}).json()
    assert [r["name"] for r in combined] == ["B"]


def test_list_invalid_price_filter(client):
    assert client.get(API, params={"price": 9}).status_code == 422


def test_list_invalid_order_by(client):
    assert client.get(API, params={"order_by": "city"}).status_code == 422


def test_order_by_rating_descending(client, make_restaurant, repo):
    ids = {}
    for name, rating in (("Bajo", 2.0), ("Alto", 4.9), ("Medio", 3.5)):
        ids[name] = make_restaurant(name=name)["id"]
        repo.collection.document(ids[name]).update({"avgRating": rating})
    names = [r["name"] for r in client.get(API, params={"order_by": "avgRating"}).json()]
    assert names == ["Alto", "Medio", "Bajo"]


def test_pagination_with_limit_and_cursor(client, make_restaurant):
    for name in ("A", "B", "C", "D", "E"):
        make_restaurant(name=name)

    first = client.get(API, params={"limit": 2})
    assert [r["name"] for r in first.json()] == ["A", "B"]
    cursor = first.headers["X-Next-Cursor"]

    second = client.get(API, params={"limit": 2, "start_after": cursor})
    assert [r["name"] for r in second.json()] == ["C", "D"]

    last = client.get(API, params={"limit": 2, "start_after": second.headers["X-Next-Cursor"]})
    assert [r["name"] for r in last.json()] == ["E"]
    assert "X-Next-Cursor" not in last.headers  # ya no hay más páginas


# --- Editar (HU-04) ------------------------------------------------------
def test_patch_updates_only_sent_fields(client, make_restaurant):
    created = make_restaurant(name="Original", city="Puebla", price=1)
    response = client.patch(f"{API}/{created['id']}", json={"name": "Nuevo nombre"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nuevo nombre"
    assert body["city"] == "Puebla"
    assert body["price"] == 1
    assert client.get(f"{API}/{created['id']}").json()["name"] == "Nuevo nombre"


def test_patch_can_clear_photo_url(client, make_restaurant):
    created = make_restaurant(photoUrl="https://example.com/a.jpg")
    response = client.patch(f"{API}/{created['id']}", json={"photoUrl": None})
    assert response.status_code == 200
    assert response.json()["photoUrl"] is None


def test_patch_not_found(client):
    assert client.patch(f"{API}/no-existe", json={"name": "X"}).status_code == 404


def test_patch_empty_body(client, make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={}).status_code == 400


def test_patch_rejects_non_editable_fields(client, make_restaurant):
    created = make_restaurant()
    for field, value in (("avgRating", 5), ("numRatings", 100), ("id", "otro")):
        response = client.patch(f"{API}/{created['id']}", json={field: value})
        assert response.status_code == 422, field
    assert client.get(f"{API}/{created['id']}").json()["avgRating"] == 0


def test_patch_validates_values(client, make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={"price": 7}).status_code == 422
    assert client.patch(f"{API}/{created['id']}", json={"name": ""}).status_code == 422
    assert client.patch(f"{API}/{created['id']}", json={"name": None}).status_code == 422


# --- Eliminar (HU-05) ----------------------------------------------------
def test_delete_restaurant(client, make_restaurant):
    created = make_restaurant()
    response = client.delete(f"{API}/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{API}/{created['id']}").status_code == 404
    assert client.get(API).json() == []


def test_delete_not_found(client):
    assert client.delete(f"{API}/no-existe").status_code == 404
