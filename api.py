from typing import List
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api_sqlite_init import Base, Movie, Link, Rating, Tag

# ========================
# KONFIGURACJA BAZY I SESJI
# ========================

engine = create_engine("sqlite:///movies.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# ========================
# FASTAPI
# ========================

app = FastAPI()

@app.get("/")
def read_root():
    return {"hello": "world"}

# Endpoint wszystkie filmy
@app.get("/movies")
def get_movies():
    movies = session.query(Movie).all()
    return [m.__dict__ for m in movies]

# Endpoint wszystkie links
@app.get("/links")
def get_links():
    links = session.query(Link).all()
    return [l.__dict__ for l in links]

# Endpoint wszystkie ratings
@app.get("/ratings")
def get_ratings():
    ratings = session.query(Rating).all()
    return [r.__dict__ for r in ratings]

# Endpoint wszystkie tags
@app.get("/tags")
def get_tags():
    tags = session.query(Tag).all()
    return [t.__dict__ for t in tags]

# Endpoint ratings dla konkretnego filmu
@app.get("/movies/{movie_id}/ratings")
def get_movie_ratings(movie_id: int):
    movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if movie:
        return [r.__dict__ for r in movie.ratings]
    return {"error": "Movie not found"}

# Endpoint tags dla konkretnego filmu
@app.get("/movies/{movie_id}/tags")
def get_movie_tags(movie_id: int):
    movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if movie:
        return [t.__dict__ for t in movie.tags]
    return {"error": "Movie not found"}

# Endpoint links dla konkretnego filmu
@app.get("/movies/{movie_id}/links")
def get_movie_links(movie_id: int):
    movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if movie:
        return [l.__dict__ for l in movie.links]
    return {"error": "Movie not found"}

# ========================
# URUCHOMIENIE
# ========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
