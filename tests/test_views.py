"""Pruebas de las vistas HTML."""


def test_home_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Todavía no hay restaurantes" in response.text


def test_home_lists_restaurants_with_details_button(client, make_restaurant):
    created = make_restaurant(name="La Abuela")
    response = client.get("/")
    assert response.status_code == 200
    assert "La Abuela" in response.text
    assert f"/restaurants/{created['id']}" in response.text
    assert "Ver detalles" in response.text


def test_home_filters_by_query_params(client, make_restaurant):
    make_restaurant(name="En Puebla", city="Puebla")
    make_restaurant(name="En Veracruz", city="Veracruz")
    response = client.get("/", params={"city": "Veracruz"})
    assert "En Veracruz" in response.text
    assert "En Puebla" not in response.text.split("<ul class=\"grid\">")[-1]


def test_home_accepts_empty_filter_values_from_form(client, make_restaurant):
    make_restaurant(name="Visible")
    response = client.get("/?city=&category=&price=&order_by=name")
    assert response.status_code == 200
    assert "Visible" in response.text


def test_home_no_results_message(client, make_restaurant):
    make_restaurant(city="Puebla")
    response = client.get("/", params={"city": "Marte"})
    assert response.status_code == 200
    assert "Ningún restaurante coincide" in response.text


def test_new_form(client):
    response = client.get("/restaurants/new")
    assert response.status_code == 200
    assert 'data-mode="create"' in response.text


def test_detail_page(client, make_restaurant):
    created = make_restaurant(name="Detalle HTML")
    response = client.get(f"/restaurants/{created['id']}")
    assert response.status_code == 200
    assert "Detalle HTML" in response.text
    assert "Editar" in response.text
    assert "Eliminar" in response.text


def test_detail_page_not_found_is_friendly_html(client):
    response = client.get("/restaurants/no-existe")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "no existe" in response.text


def test_edit_form_is_prefilled(client, make_restaurant):
    created = make_restaurant(name="Editable")
    response = client.get(f"/restaurants/{created['id']}/edit")
    assert response.status_code == 200
    assert 'data-mode="edit"' in response.text
    assert 'value="Editable"' in response.text


def test_edit_form_not_found(client):
    assert client.get("/restaurants/no-existe/edit").status_code == 404


def test_flash_message_after_delete(client):
    response = client.get("/?msg=deleted")
    assert "Restaurante eliminado" in response.text


def test_api_404_stays_json(client):
    response = client.get("/api/v1/restaurants/no-existe")
    assert response.headers["content-type"].startswith("application/json")
