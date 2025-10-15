# queries_ultimate.py
import os
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker
from api_sqlite_init import Base, Movie, Link, Rating, Tag

# ========================
# KONFIGURACJA SESJI
# ========================
engine = create_engine("sqlite:///movies.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# ========================
# SELECT – pobieranie danych
# ========================

print("\n--- SELECT: pierwszy film ---")
first_movie = session.query(Movie).first()
print(first_movie.title, "-", first_movie.genres)

print("\n--- SELECT: filmy z Comedy lub Action ---")
movies_filtered = session.query(Movie) \
    .filter(or_(Movie.genres.like("%Comedy%"), Movie.genres.like("%Action%"))) \
    .order_by(Movie.title) \
    .limit(5).all()
for m in movies_filtered:
    print(m.title, "-", m.genres)

print("\n--- SELECT: średnia ocena filmu ID=1 ---")
avg_rating = session.query(func.avg(Rating.rating)) \
    .filter(Rating.movieId == 1).scalar()
print("Średnia ocena:", avg_rating)

print("\n--- SELECT: liczba tagów dla filmu ID=1 ---")
tags_count = session.query(func.count(Tag.id)) \
    .filter(Tag.movieId == 1).scalar()
print("Liczba tagów:", tags_count)

# ========================
# INSERT – dodawanie danych
# ========================

print("\n--- INSERT: dodanie demo taga ---")
new_tag = Tag(userId=999, movieId=1, tag="Ultimate Demo", timestamp=9999999999)

# Sprawdzenie czy już nie istnieje
existing_tag = session.query(Tag).filter(
    Tag.userId == new_tag.userId, Tag.movieId == new_tag.movieId, Tag.tag == new_tag.tag
).first()

if not existing_tag:
    session.add(new_tag)
    session.commit()
    print("Dodano nowy tag")
else:
    print("Tag już istnieje")

# ========================
# UPDATE – zmiana danych
# ========================

print("\n--- UPDATE: zmiana oceny użytkownika 1 dla filmu 1 ---")
rating_to_update = session.query(Rating).filter(
    Rating.userId == 1, Rating.movieId == 1
).first()
if rating_to_update:
    old = rating_to_update.rating
    rating_to_update.rating = 4.5
    session.commit()
    print(f"Ocena zmieniona z {old} na {rating_to_update.rating}")

# ========================
# DELETE – usuwanie danych
# ========================

print("\n--- DELETE: usunięcie demo taga ---")
demo_tag = session.query(Tag).filter(
    Tag.userId == 999, Tag.movieId == 1, Tag.tag == "Ultimate Demo"
).first()
if demo_tag:
    session.delete(demo_tag)
    session.commit()
    print("Demo tag usunięty")

# ========================
# RELACJE – dostęp do powiązanych obiektów
# ========================

print("\n--- RELACJE: linki, oceny, tagi dla filmu ID=1 ---")
movie = session.query(Movie).filter(Movie.movieId == 1).first()
if movie:
    print("Linki:", [l.imdbId for l in movie.links][:3])
    print("Oceny:", [r.rating for r in movie.ratings][:3])
    print("Tagi:", [t.tag for t in movie.tags][:3])

# ========================
# TRANSAKCJE i ROLLBACK
# ========================

print("\n--- TRANSAKCJA DEMO ---")
from sqlalchemy.exc import SQLAlchemyError

try:
    # Tworzymy transakcję
    tag1 = Tag(userId=888, movieId=1, tag="Trans Tag 1", timestamp=1111111111)
    tag2 = Tag(userId=888, movieId=1, tag="Trans Tag 2", timestamp=2222222222)
    session.add_all([tag1, tag2])

    # Celowo wywołamy błąd: duplikat PK (movieId+userId dla Rating, np.)
    faulty_rating = Rating(userId=1, movieId=1, rating=5.0, timestamp=123)
    session.add(faulty_rating)  # jeśli byłby duplikat, rzuci wyjątek

    session.commit()
except SQLAlchemyError as e:
    print("Wystąpił błąd, rollback transakcji:", e)
    session.rollback()

# ========================
# ZŁOŻONE ZAPYTANIA / JOINY
# ========================

print("\n--- JOIN: średnia ocena filmów z gatunku Comedy ---")
results = session.query(
    Movie.title, func.avg(Rating.rating).label("avg_rating")
).join(Rating).filter(Movie.genres.like("%Comedy%")).group_by(Movie.movieId).all()

for title, avg in results[:5]:
    print(title, "-", round(avg, 2))
