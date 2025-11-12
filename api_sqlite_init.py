import csv
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# KONFIGURACJA BAZY

engine = create_engine("sqlite:///movies.db", echo=True) #  tworzy połączenie do bazy danych.
Base = declarative_base() #pozwala tworzyć klasy “mapujące się” na tabele.
Session = sessionmaker(bind=engine) #do operacji typu dodawanie, modyfikacja, zapytania do bazy
session = Session() #tworzy konkretną sesję, przez którą można dodawać dane i wykonywać zapytania.

# MODELE SQLALCHEMY Z RELACJAMI


class Movie(Base):
    __tablename__ = "movies"
    movieId = Column(Integer, primary_key=True) #klucz główny.
    title = Column(String)
    genres = Column(String)

    links = relationship("Link", back_populates="movie")
    ratings = relationship("Rating", back_populates="movie")
    tags = relationship("Tag", back_populates="movie")

class Link(Base):
    __tablename__ = "links"
    movieId = Column(Integer, ForeignKey("movies.movieId"), primary_key=True) #wiele do jednego
    imdbId = Column(String)
    tmdbId = Column(String)

    movie = relationship("Movie", back_populates="links")

class Rating(Base):
    __tablename__ = "ratings"
    userId = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey("movies.movieId"), primary_key=True)
    rating = Column(Float)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="ratings")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)  # automatyczne nadawanie ID (dla Tag).
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    tag = Column(String)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="tags")

# Tworzenie tabel
Base.metadata.create_all(engine) #to jest takie create table w sql
"""SQLAlchemy patrzy na wszystkie klasy dziedziczące po Base i tworzy odpowiednie tabele w movies.db."""

# ========================
# FUNKCJA DO ŁADOWANIA CSV
# ========================

def load_csv_to_db(model_class, file_name):
    path = os.path.join("database", file_name)
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            obj_data = {}
            for k, v in row.items():
                if v.isdigit():
                    obj_data[k] = int(v)
                else:
                    try:
                        obj_data[k] = float(v)
                    except ValueError:
                        obj_data[k] = v
            obj = model_class(**obj_data)
            session.add(obj)
    session.commit()

# ========================
# ŁADOWANIE DANYCH
# ========================

def initialize_db():
    load_csv_to_db(Movie, "movies.csv")
    load_csv_to_db(Link, "links.csv")
    load_csv_to_db(Rating, "ratings.csv")
    load_csv_to_db(Tag, "tags.csv")

if __name__ == "__main__":
    initialize_db()
    print("Baza danych utworzona i załadowana z CSV.")
