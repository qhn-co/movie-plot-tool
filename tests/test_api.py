import pytest
from conftest import INCEPTION
from fastapi.testclient import TestClient

ADMIN_ROUTES = [
    ("get", "/api/admin/films", None),
    ("post", "/api/admin/films", {"tmdb_id": INCEPTION.tmdb_id}),
    ("patch", "/api/admin/films/1", {"published": True}),
    ("delete", "/api/admin/films/1", None),
    ("get", "/api/admin/tmdb/search?q=incep", None),
]


@pytest.mark.parametrize(("method", "url", "body"), ADMIN_ROUTES)
def test_admin_routes_require_login(client: TestClient, method: str, url: str, body: dict | None) -> None:
    kwargs = {"json": body} if body else {}
    assert getattr(client, method)(url, **kwargs).status_code == 401


def test_wrong_password_is_rejected(client: TestClient) -> None:
    response = client.post("/api/admin/session", json={"password": "faux"})
    assert response.status_code == 401
    assert client.get("/api/admin/films").status_code == 401


def test_login_is_throttled_after_repeated_failures(client: TestClient) -> None:
    for _ in range(5):
        client.post("/api/admin/session", json={"password": "faux"})
    response = client.post("/api/admin/session", json={"password": "mot-de-passe-de-test"})
    assert response.status_code == 429


def test_logout_closes_admin(admin: TestClient) -> None:
    assert admin.delete("/api/admin/session").status_code == 204
    assert admin.get("/api/admin/films").status_code == 401


def test_admin_publishes_and_public_reads(admin: TestClient) -> None:
    created = admin.post("/api/admin/films", json={"tmdb_id": INCEPTION.tmdb_id})
    assert created.status_code == 201
    film_id = created.json()["id"]

    assert admin.get("/api/films").json() == []
    assert admin.get(f"/api/films/{film_id}").status_code == 404

    admin.patch(f"/api/admin/films/{film_id}", json={"published": True})
    cards = admin.get("/api/films").json()
    assert [c["title"] for c in cards] == ["Inception"]
    page = admin.get(f"/api/films/{film_id}").json()
    assert page["analysis"]["synopsis"] == "Synopsis de Inception"
    assert "tmdb_id" not in page and "published" not in page


def test_admin_edits_analysis(admin: TestClient) -> None:
    film_id = admin.post("/api/admin/films", json={"tmdb_id": INCEPTION.tmdb_id}).json()["id"]
    analysis = {"synopsis": "Revu", "timeline": ["a"], "ending": "b", "meta_analysis": "c"}
    response = admin.patch(f"/api/admin/films/{film_id}", json={"analysis": analysis})
    assert response.json()["analysis"]["synopsis"] == "Revu"


def test_admin_deletes_film(admin: TestClient) -> None:
    film_id = admin.post("/api/admin/films", json={"tmdb_id": INCEPTION.tmdb_id}).json()["id"]
    assert admin.delete(f"/api/admin/films/{film_id}").status_code == 204
    assert admin.get("/api/admin/films").json() == []


def test_tmdb_search(admin: TestClient) -> None:
    results = admin.get("/api/admin/tmdb/search", params={"q": "incep"}).json()
    assert results == [{"tmdb_id": INCEPTION.tmdb_id, "title": "Inception", "year": "2010"}]


def test_health_and_version_are_public(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/version").json() == {"commit": "dev"}
