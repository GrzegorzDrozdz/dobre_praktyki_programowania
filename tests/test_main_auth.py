import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# --- Konfiguracja ścieżek ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_project.main import app
from auth_project.database import Base, get_db
from auth_project.models import User
from auth_project.security import hash_password

# --- Konfiguracja Testowej Bazy Danych ---
TEST_DATABASE_URL = "sqlite:///./test_integration.db"

# Usuwam starą bazę testową, jeśli istnieje, na samym początku
if os.path.exists(TEST_DATABASE_URL.replace("sqlite:///", "")):
    os.remove(TEST_DATABASE_URL.replace("sqlite:///", ""))

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# tworze tabele RAZ na początku sesji
Base.metadata.create_all(bind=engine)


# Dependency Override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="function")
def db():
    """
    Fixtura, która zapewnia czystą bazę danych PRZED KAŻDYM testem.
    niezawodny sposób na izolowanie testów.
    """
    # Wyczyść tabele przed każdym testem
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    _db = TestingSessionLocal()
    try:
        yield _db
    finally:
        _db.close()


@pytest.fixture(scope="function")
def client(db):
    """
    Fixtura klienta, która zależy od czystej bazy danych 'db'.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def admin_auth_headers(client, db):
    """
    Fixtura, która tworzy admina w czystej bazie i zwraca nagłówek.
    """
    # 1. Stwórz admina
    admin_user = User(
        username="test_admin",
        hashed_password=hash_password("admin_pass"),
        roles=["ROLE_USER", "ROLE_ADMIN"]
    )
    db.add(admin_user)
    db.commit()

    # 2. Zaloguj się
    response = client.post("/login", json={"username": "test_admin", "password": "admin_pass"})

    assert response.status_code == 200, "Logowanie admina w fixturze nie powiodło się"
    token = response.json()["access_token"]


    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_auth_headers(client, db):
    """
    Fixtura, która tworzy usera w czystej bazie i zwraca nagłówek.
    """
    # 1. Stwórz usera
    user = User(
        username="test_user",
        hashed_password=hash_password("user_pass"),
        roles=["ROLE_USER"]
    )
    db.add(user)
    db.commit()

    # 2. Zaloguj się
    response = client.post("/login", json={"username": "test_user", "password": "user_pass"})
    assert response.status_code == 200, "Logowanie usera w fixturze nie powiodło się"
    token = response.json()["access_token"]

    # 3. Zwróć nagłówek
    return {"Authorization": f"Bearer {token}"}


"""

 --- Testy Integracyjne  ---

"""


def test_login_success(client, db):
    """Testuje Zadanie 1 i 3: Poprawne logowanie"""
    # Musimy najpierw stworzyć usera, żeby móc się zalogować
    admin_user = User(
        username="temp_admin",
        hashed_password=hash_password("admin_pass"),
        roles=["ROLE_USER", "ROLE_ADMIN"]
    )
    db.add(admin_user)
    db.commit()


    response = client.post("/login", json={"username": "temp_admin", "password": "admin_pass"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Testuje Zadanie 3: Niepoprawne logowanie"""

    response = client.post("/login", json={"username": "nieistnieje", "password": "zlehaslo"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_user_details_success(client, admin_auth_headers):
    """Testuje Zadanie 5 i 7: Zabezpieczony endpoint /user_details"""
    response = client.get("/user_details", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_admin"
    assert "ROLE_ADMIN" in data["roles"]


def test_get_protected_resource_no_token_fails(client):
    """Testuje Zadanie 5: Dostęp do zabezpieczonego zasobu bez tokena"""
    response = client.get("/protected_resource")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_create_user_as_admin_success(client, admin_auth_headers):
    """Testuje Zadanie 4 i 6: Admin może tworzyć użytkowników"""
    new_user_data = {
        "username": "nowy_user_przez_admina",
        "password": "pass123",
        "roles": ["ROLE_USER"]
    }
    response = client.post("/users", json=new_user_data, headers=admin_auth_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == "nowy_user_przez_admina"
    assert data["roles"] == ["ROLE_USER"]


def test_create_user_as_non_admin_fails(client, user_auth_headers):
    """Testuje Zadanie 6: Zwykły user NIE MOŻE tworzyć użytkowników"""
    new_user_data = {
        "username": "nieudany_user",
        "password": "pass123",
        "roles": ["ROLE_USER"]
    }
    response = client.post("/users", json=new_user_data, headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Brak uprawnień administratora"


def test_create_user_duplicate_fails(client, admin_auth_headers):
    """Testuje logikę biznesową: Nie można stworzyć dwóch userów o tej samej nazwie"""
    # fixtura `admin_auth_headers` już stworzyła "test_admin"
    user_data = {
        "username": "test_admin",  # Próba stworzenia duplikatu
        "password": "pass123",
        "roles": ["ROLE_USER"]
    }
    response = client.post("/users", json=user_data, headers=admin_auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Użytkownik o tej nazwie już istnieje"