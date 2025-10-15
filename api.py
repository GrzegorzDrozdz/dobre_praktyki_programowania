from typing import List
from fastapi import FastAPI
import csv
import os
import uvicorn

app = FastAPI()  # główna instancja aplikacji

# ========================
# KLASY DANYCH
# ========================

class Movie:
    def __init__(self, movieId: int, title: str, genres: str):
        self.movieId = movieId
        self.title = title
        self.genres = genres

class Link:
    def __init__(self, movieId: int, imdbId: str, tmdbId: str):
        self.movieId = movieId
        self.imdbId = imdbId
        self.tmdbId = tmdbId

class Rating:
    def __init__(self, userId: int, movieId: int, rating: float, timestamp: int):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp

class Tag:
    def __init__(self, userId: int, movieId: int, tag: str, timestamp: int):
        self.userId = userId
        self.movieId = movieId
        self.tag = tag
        self.timestamp = timestamp

# ========================
# FUNKCJA POMOCNICZA
# ========================

def load_csv(file_name: str) -> List[dict]:
    """Ładuje plik CSV z folderu 'database' i zwraca listę wierszy jako słowniki."""
    path = os.path.join("database", file_name)
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

# ========================
# ENDPOINTY
# ========================

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies")
def get_movies():
    movies_data = load_csv("movies.csv")
    movies = []
    for row in movies_data:
        movie = Movie(
            movieId=int(row["movieId"]),
            title=row["title"],
            genres=row["genres"]
        )
        movies.append(movie.__dict__)  # ręczna serializacja
    return movies

@app.get("/links")
def get_links():
    links_data = load_csv("links.csv")
    links = []
    for row in links_data:
        link = Link(
            movieId=int(row["movieId"]),
            imdbId=row["imdbId"],
            tmdbId=row["tmdbId"]
        )
        links.append(link.__dict__)
    return links

@app.get("/ratings")
def get_ratings():
    ratings_data = load_csv("ratings.csv")
    ratings = []
    for row in ratings_data:
        rating = Rating(
            userId=int(row["userId"]),
            movieId=int(row["movieId"]),
            rating=float(row["rating"]),
            timestamp=int(row["timestamp"])
        )
        ratings.append(rating.__dict__)
    return ratings

@app.get("/tags")
def get_tags():
    tags_data = load_csv("tags.csv")
    tags = []
    for row in tags_data:
        tag = Tag(
            userId=int(row["userId"]),
            movieId=int(row["movieId"]),
            tag=row["tag"],
            timestamp=int(row["timestamp"])
        )
        tags.append(tag.__dict__)
    return tags

# ========================
# URUCHOMIENIE
# ========================

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
