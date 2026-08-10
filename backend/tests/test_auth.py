from app.models.user import User


def test_register_creates_unverified_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201
    assert response.json()["is_verified"] is False


def test_login_fails_before_verification(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "unverified@example.com", "password": "testpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "unverified@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 403


def test_login_succeeds_after_verification(client, db_session):
    client.post(
        "/api/v1/auth/register",
        json={"email": "verified@example.com", "password": "testpassword123"},
    )
    user = db_session.query(User).filter(User.email == "verified@example.com").first()

    verify_response = client.get(f"/api/v1/auth/verify-email?token={user.verification_token}")
    assert verify_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "verified@example.com", "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_verify_email_is_idempotent(client, db_session):
    """A verification link may be opened more than once (email security
    scanners, a duplicate click) — the second attempt must not error out."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "idempotent@example.com", "password": "testpassword123"},
    )
    user = db_session.query(User).filter(User.email == "idempotent@example.com").first()
    token = user.verification_token

    first = client.get(f"/api/v1/auth/verify-email?token={token}")
    second = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert first.status_code == 200
    assert second.status_code == 200


def test_verify_email_rejects_invalid_token(client):
    response = client.get("/api/v1/auth/verify-email?token=not-a-real-token")
    assert response.status_code == 400
