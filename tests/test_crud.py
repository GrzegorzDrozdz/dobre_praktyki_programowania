import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Dodanie ścieżki do importów
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, get_db
from api_sqlite_init import Base

# Konfiguracja bazy testowej (w pamięci)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Tworzenie tabel przed każdym testem
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Czyszczenie bazy po teście
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ========================
# 1. MOVIES (4 testy)
# ========================

def test_create_movie(client):
    response = client.post("/movies", json={"title": "Test Movie", "genres": "Action"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Movie"


def test_read_movie(client):
    client.post("/movies", json={"title": "Test Movie", "genres": "Action"})
    response = client.get("/movies/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"


def test_update_movie(client):
    client.post("/movies", json={"title": "Old Title", "genres": "Action"})
    response = client.put("/movies/1", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_movie(client):
    client.post("/movies", json={"title": "To Delete", "genres": "Action"})
    del_response = client.delete("/movies/1")
    assert del_response.status_code == 204
    assert client.get("/movies/1").status_code == 404


# ========================
# 2. LINKS (4 testy)
# ========================

def test_create_link(client):
    # Wymaga filmu
    client.post("/movies", json={"title": "M", "genres": "G"})

    response = client.post("/links", json={"movieId": 1, "imdbId": "tt1", "tmdbId": "tm1"})
    assert response.status_code == 201
    assert response.json()["imdbId"] == "tt1"


def test_read_link(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/links", json={"movieId": 1, "imdbId": "tt1", "tmdbId": "tm1"})

    response = client.get("/links/1")
    assert response.status_code == 200
    assert response.json()["tmdbId"] == "tm1"


def test_update_link(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/links", json={"movieId": 1, "imdbId": "tt1", "tmdbId": "tm1"})

    response = client.put("/links/1", json={"imdbId": "tt2_new"})
    assert response.status_code == 200
    assert response.json()["imdbId"] == "tt2_new"


def test_delete_link(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/links", json={"movieId": 1, "imdbId": "tt1", "tmdbId": "tm1"})

    response = client.delete("/links/1")
    assert response.status_code == 204
    assert client.get("/links/1").status_code == 404


# ========================
# 3. RATINGS (4 testy)
# ========================

def test_create_rating(client):
    client.post("/movies", json={"title": "M", "genres": "G"})

    payload = {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 100}
    response = client.post("/ratings", json=payload)
    assert response.status_code == 201
    assert response.json()["rating"] == 4.5


def test_read_rating(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/ratings", json={"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 100})

    # Path: /ratings/{user_id}/{movie_id}
    response = client.get("/ratings/1/1")
    assert response.status_code == 200
    assert response.json()["rating"] == 4.5


def test_update_rating(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/ratings", json={"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 100})

    response = client.put("/ratings/1/1", json={"rating": 5.0})
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0


def test_delete_rating(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    client.post("/ratings", json={"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": 100})

    response = client.delete("/ratings/1/1")
    assert response.status_code == 204
    assert client.get("/ratings/1/1").status_code == 404


# ========================
# 4. TAGS (4 testy)
# ========================

def test_create_tag(client):
    client.post("/movies", json={"title": "M", "genres": "G"})

    payload = {"userId": 99, "movieId": 1, "tag": "Fun", "timestamp": 200}
    response = client.post("/tags", json=payload)
    assert response.status_code == 201
    assert response.json()["tag"] == "Fun"


def test_read_tag(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    resp_create = client.post("/tags", json={"userId": 99, "movieId": 1, "tag": "Fun", "timestamp": 200})
    tag_id = resp_create.json()["id"]

    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json()["tag"] == "Fun"


def test_update_tag(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    resp_create = client.post("/tags", json={"userId": 99, "movieId": 1, "tag": "Fun", "timestamp": 200})
    tag_id = resp_create.json()["id"]

    response = client.put(f"/tags/{tag_id}", json={"tag": "Super Fun"})
    assert response.status_code == 200
    assert response.json()["tag"] == "Super Fun"


def test_delete_tag(client):
    client.post("/movies", json={"title": "M", "genres": "G"})
    resp_create = client.post("/tags", json={"userId": 99, "movieId": 1, "tag": "Fun", "timestamp": 200})
    tag_id = resp_create.json()["id"]

    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 204
    assert client.get(f"/tags/{tag_id}").status_code == 404