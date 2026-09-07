import requests

BASE_URL = "http://localhost:8000"
EMAIL = "owner-a@example.com"
PASSWORD = "Password123!"


def get_token():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_authenticated_widget_read():
    token = get_token()

    response = requests.get(
        f"{BASE_URL}/widgets/6209ce7f-ad51-473a-9155-0f7691a033ce",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "6209ce7f-ad51-473a-9155-0f7691a033ce"


def test_tenant_isolation():
    token = get_token()

    response = requests.get(
        f"{BASE_URL}/widgets/3b0321d6-4543-4a33-b4f4-bfbf90aa6cbc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
def test_widget_update():
    token = get_token()

    response = requests.put(
        f"{BASE_URL}/widgets/6209ce7f-ad51-473a-9155-0f7691a033ce",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Automated Test Widget"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Automated Test Widget"


def test_invalid_widget_type():
    token = get_token()

    response = requests.put(
        f"{BASE_URL}/widgets/6209ce7f-ad51-473a-9155-0f7691a033ce",
        headers={"Authorization": f"Bearer {token}"},
        json={"widget_type": "invalid_type"},
    )

    assert response.status_code == 422
def test_public_widget_config():
    response = requests.get(
        f"{BASE_URL}/widgets/6209ce7f-ad51-473a-9155-0f7691a033ce/config"
    )

    assert response.status_code == 200
    assert response.json()["id"] == "6209ce7f-ad51-473a-9155-0f7691a033ce"
    assert "Cache-Control" in response.headers
    assert "max-age=60" in response.headers["Cache-Control"]


def test_widget_script_cache():
    response = requests.get(f"{BASE_URL}/widget.v1.js")

    assert response.status_code == 200
    assert "application/javascript" in response.headers["Content-Type"]
    assert "max-age=31536000" in response.headers["Cache-Control"]
    assert "immutable" in response.headers["Cache-Control"]
def test_invalid_submission_widget_id():
    response = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "widget_id": "not-a-uuid",
            "data": {"name": "Test"},
            "honeypot": "",
        },
    )

    assert response.status_code == 400


def test_honeypot_submission_not_stored():
    token = get_token()

    before = requests.get(
        f"{BASE_URL}/dashboard/submissions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert before.status_code == 200
    before_count = len(before.json())

    response = requests.post(
        f"{BASE_URL}/submissions",
        json={
            "widget_id": "6209ce7f-ad51-473a-9155-0f7691a033ce",
            "data": {"name": "Bot Test"},
            "honeypot": "spam",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    after = requests.get(
        f"{BASE_URL}/dashboard/submissions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert after.status_code == 200
    assert len(after.json()) == before_count


def test_idempotency():
    key = "pytest-idempotency-test-" + str(__import__("uuid").uuid4())

    payload = {
        "widget_id": "6209ce7f-ad51-473a-9155-0f7691a033ce",
        "data": {"name": "Pytest Idempotency"},
        "honeypot": "",
    }

    first = requests.post(
        f"{BASE_URL}/submissions",
        headers={"Idempotency-Key": key},
        json=payload,
    )

    second = requests.post(
        f"{BASE_URL}/submissions",
        headers={"Idempotency-Key": key},
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True
    assert first.json()["id"] == second.json()["id"]
