import csv
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base  # <--- Zmiana importu

# KONFIGURACJA BAZY

engine = create_engine("sqlite:///movies.db", echo=True)
Base = declarative_base() # Teraz korzysta z poprawnego importu z sqlalchemy.orm
Session = sessionmaker(bind=engine)
session = Session()

# MODELE SQLALCHEMY Z RELACJAMI

class Movie(Base):
    __tablename__ = "movies"
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

    links = relationship("Link", back_populates="movie")
    ratings = relationship("Rating", back_populates="movie")
    tags = relationship("Tag", back_populates="movie")

class Link(Base):
    __tablename__ = "links"
    movieId = Column(Integer, ForeignKey("movies.movieId"), primary_key=True)
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    tag = Column(String)
    timestamp = Column(Integer)

    movie = relationship("Movie", back_populates="tags")

# Tworzenie tabel
Base.metadata.create_all(engine)

# ========================
# FUNKCJA DO ŁADOWANIA CSV
# ========================

def load_csv_to_db(model_class, file_name):
    path = os.path.join("database", file_name)
    # Sprawdzenie czy plik istnieje, żeby uniknąć błędów przy braku danych
    if not os.path.exists(path):
        print(f"Pominięto ładowanie {file_name} - plik nie istnieje.")
        return

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
    print("Baza danych utworzona.")