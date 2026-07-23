"""Router tests for the categories API (Phase 3.5, Amendment 2).

Additive endpoint set: GET/POST/PATCH/DELETE /api/categories (+ /palette).
Nothing here touches the existing task/template contract.
"""

from jacer.models import CATEGORY_PALETTE


def test_palette_endpoint_returns_the_preset_palette(client):
    response = client.get("/api/categories/palette")
    assert response.status_code == 200
    assert response.json() == CATEGORY_PALETTE


def test_list_categories_starts_empty(client):
    response = client.get("/api/categories/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_category_auto_assigns_palette_colour_round_robin(client):
    first = client.post("/api/categories/", json={"name": "Admin"})
    assert first.status_code == 201
    assert first.json()["colour"] == CATEGORY_PALETTE[0]
    assert first.json()["name"] == "Admin"

    second = client.post("/api/categories/", json={"name": "Deep work"})
    assert second.json()["colour"] == CATEGORY_PALETTE[1]


def test_create_category_accepts_an_explicit_palette_colour(client):
    response = client.post(
        "/api/categories/", json={"name": "Health", "colour": CATEGORY_PALETTE[3]}
    )
    assert response.status_code == 201
    assert response.json()["colour"] == CATEGORY_PALETTE[3]


def test_create_category_rejects_a_colour_outside_the_palette(client):
    response = client.post("/api/categories/", json={"name": "Rogue", "colour": "#ff0000"})
    assert response.status_code == 422


def test_get_unknown_category_returns_404(client):
    assert client.get("/api/categories/nope").status_code == 404


def test_update_category_name_and_colour(client):
    created = client.post("/api/categories/", json={"name": "Admin"}).json()
    response = client.patch(
        f"/api/categories/{created['id']}",
        json={"name": "Admin & ops", "colour": CATEGORY_PALETTE[5]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Admin & ops"
    assert body["colour"] == CATEGORY_PALETTE[5]


def test_update_category_rejects_a_colour_outside_the_palette(client):
    created = client.post("/api/categories/", json={"name": "Admin"}).json()
    response = client.patch(f"/api/categories/{created['id']}", json={"colour": "#123456"})
    assert response.status_code == 422


def test_update_unknown_category_returns_404(client):
    assert client.patch("/api/categories/nope", json={"name": "x"}).status_code == 404


def test_delete_unknown_category_returns_404(client):
    assert client.delete("/api/categories/nope").status_code == 404


def test_delete_category_clears_dangling_references(both_repos_client):
    """Deleting a category nulls it out on any referencing task or template
    item, so nothing points at a category that no longer exists. Proven across
    both adapters, since the markdown adapter has to reload the cleared field."""
    client = both_repos_client
    category = client.post("/api/categories/", json={"name": "Admin"}).json()
    cat_id = category["id"]

    task = client.post("/api/tasks/", json={"title": "Filed", "category_id": cat_id}).json()

    template = client.post("/api/templates/", json={"name": "Week"}).json()
    item = client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Standup", "category_id": cat_id},
    ).json()

    assert client.delete(f"/api/categories/{cat_id}").status_code == 200

    assert client.get(f"/api/tasks/{task['id']}").json()["category_id"] is None
    assert client.get(f"/api/template-items/{item['id']}").json()["category_id"] is None
    assert client.get(f"/api/categories/{cat_id}").status_code == 404
