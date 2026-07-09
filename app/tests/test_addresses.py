"""Integration tests for the /api/v1/addresses endpoints."""

from fastapi.testclient import TestClient

SAMPLE_ADDRESS: dict = {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "USA",
    "latitude": 39.7817,
    "longitude": -89.6501,
}


# ── Create ────────────────────────────────────────────────────────────────


class TestCreateAddress:
    def test_success(self, client: TestClient) -> None:
        resp = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        assert resp.status_code == 201
        data = resp.json()
        assert data["street"] == "123 Main St"
        assert data["id"] is not None
        assert "created_at" in data
        assert "updated_at" in data

    def test_without_optional_fields(self, client: TestClient) -> None:
        payload = {k: v for k, v in SAMPLE_ADDRESS.items() if k not in ("state", "postal_code")}
        resp = client.post("/api/v1/addresses/", json=payload)
        assert resp.status_code == 201
        assert resp.json()["state"] is None
        assert resp.json()["postal_code"] is None

    def test_missing_required_field(self, client: TestClient) -> None:
        resp = client.post("/api/v1/addresses/", json={"street": "123 Main St"})
        assert resp.status_code == 422

    def test_invalid_latitude(self, client: TestClient) -> None:
        resp = client.post("/api/v1/addresses/", json={**SAMPLE_ADDRESS, "latitude": 100})
        assert resp.status_code == 422

    def test_invalid_longitude(self, client: TestClient) -> None:
        resp = client.post("/api/v1/addresses/", json={**SAMPLE_ADDRESS, "longitude": -200})
        assert resp.status_code == 422


# ── Read ──────────────────────────────────────────────────────────────────


class TestGetAddress:
    def test_success(self, client: TestClient) -> None:
        aid = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS).json()["id"]
        resp = client.get(f"/api/v1/addresses/{aid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == aid

    def test_not_found(self, client: TestClient) -> None:
        assert client.get("/api/v1/addresses/9999").status_code == 404


class TestListAddresses:
    def test_empty(self, client: TestClient) -> None:
        assert client.get("/api/v1/addresses/").json() == []

    def test_pagination(self, client: TestClient) -> None:
        for i in range(5):
            client.post("/api/v1/addresses/", json={**SAMPLE_ADDRESS, "street": f"S{i}"})
        resp = client.get("/api/v1/addresses/", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2


# ── Update ────────────────────────────────────────────────────────────────


class TestUpdateAddress:
    def test_partial_update(self, client: TestClient) -> None:
        aid = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS).json()["id"]
        resp = client.put(f"/api/v1/addresses/{aid}", json={"street": "456 Oak Ave"})
        assert resp.status_code == 200
        assert resp.json()["street"] == "456 Oak Ave"
        assert resp.json()["city"] == SAMPLE_ADDRESS["city"]  # unchanged

    def test_not_found(self, client: TestClient) -> None:
        assert client.put("/api/v1/addresses/9999", json={"street": "X"}).status_code == 404

    def test_empty_body_rejected(self, client: TestClient) -> None:
        aid = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS).json()["id"]
        assert client.put(f"/api/v1/addresses/{aid}", json={}).status_code == 422

    def test_update_coordinates(self, client: TestClient) -> None:
        aid = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS).json()["id"]
        resp = client.put(
            f"/api/v1/addresses/{aid}",
            json={"latitude": 48.8566, "longitude": 2.3522},
        )
        assert resp.status_code == 200
        assert resp.json()["latitude"] == 48.8566
        assert resp.json()["longitude"] == 2.3522


# ── Delete ────────────────────────────────────────────────────────────────


class TestDeleteAddress:
    def test_success(self, client: TestClient) -> None:
        aid = client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS).json()["id"]
        assert client.delete(f"/api/v1/addresses/{aid}").status_code == 204
        assert client.get(f"/api/v1/addresses/{aid}").status_code == 404

    def test_not_found(self, client: TestClient) -> None:
        assert client.delete("/api/v1/addresses/9999").status_code == 404


# ── Nearby search ─────────────────────────────────────────────────────────


class TestNearbySearch:
    def _search(self, client: TestClient, lat: float, lon: float, km: float):
        return client.get(
            "/api/v1/addresses/nearby",
            params={"latitude": lat, "longitude": lon, "distance_km": km},
        )

    def test_same_location(self, client: TestClient) -> None:
        client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        resp = self._search(client, 39.7817, -89.6501, 10)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["distance_km"] < 0.01

    def test_no_results(self, client: TestClient) -> None:
        client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        resp = self._search(client, 51.5074, -0.1278, 10)  # London
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_filters_by_radius(self, client: TestClient) -> None:
        client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        client.post(
            "/api/v1/addresses/",
            json={
                **SAMPLE_ADDRESS,
                "street": "NYC",
                "city": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
        )
        # 50 km radius around Springfield — NYC is ~1 200 km away
        resp = self._search(client, 39.7817, -89.6501, 50)
        results = resp.json()
        assert len(results) == 1
        assert results[0]["city"] == "Springfield"

    def test_large_radius_includes_all(self, client: TestClient) -> None:
        client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        client.post(
            "/api/v1/addresses/",
            json={
                **SAMPLE_ADDRESS,
                "street": "NYC",
                "city": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
        )
        resp = self._search(client, 39.7817, -89.6501, 2000)
        assert len(resp.json()) == 2

    def test_ordered_by_distance(self, client: TestClient) -> None:
        # Springfield, IL
        client.post("/api/v1/addresses/", json=SAMPLE_ADDRESS)
        # Chicago (~300 km away)
        client.post(
            "/api/v1/addresses/",
            json={
                **SAMPLE_ADDRESS,
                "street": "Chicago",
                "city": "Chicago",
                "latitude": 41.8781,
                "longitude": -87.6298,
            },
        )
        # New York (~1 200 km away)
        client.post(
            "/api/v1/addresses/",
            json={
                **SAMPLE_ADDRESS,
                "street": "NYC",
                "city": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
        )
        resp = self._search(client, 39.7817, -89.6501, 2000)
        distances = [r["distance_km"] for r in resp.json()]
        assert distances == sorted(distances)


# ── Health ────────────────────────────────────────────────────────────────


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}