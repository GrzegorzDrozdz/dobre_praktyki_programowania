from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict  # <--- Dodano ConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api_sqlite_init import Base, Movie, Link, Rating, Tag

# ========================
# KONFIGURACJA BAZY
# ========================

SQLALCHEMY_DATABASE_URL = "sqlite:///movies.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# ========================
# MODELE PYDANTIC (SCHEMAS)
# ========================

# --- Movie ---
class MovieCreate(BaseModel):
    title: str
    genres: str


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genres: Optional[str] = None


class MovieOut(MovieCreate):
    movieId: int
    # Zmiana na nową składnię Pydantic v2
    model_config = ConfigDict(from_attributes=True)


# --- Link ---
class LinkCreate(BaseModel):
    movieId: int
    imdbId: str
    tmdbId: str


class LinkUpdate(BaseModel):
    imdbId: Optional[str] = None
    tmdbId: Optional[str] = None


class LinkOut(LinkCreate):
    model_config = ConfigDict(from_attributes=True)


# --- Rating ---
class RatingCreate(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class RatingUpdate(BaseModel):
    rating: Optional[float] = None
    timestamp: Optional[int] = None


class RatingOut(RatingCreate):
    model_config = ConfigDict(from_attributes=True)


# --- Tag ---
class TagCreate(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int


class TagUpdate(BaseModel):
    tag: Optional[str] = None
    timestamp: Optional[int] = None


class TagOut(TagCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ========================
# ENDPOINTY CRUD
# ========================

@app.get("/")
def read_root():
    return {"hello": "world"}


# --- MOVIES ---

@app.post("/movies", response_model=MovieOut, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = Movie(title=movie.title, genres=movie.genres)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.get("/movies", response_model=List[MovieOut])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = db.query(Movie).offset(skip).limit(limit).all()
    return movies


@app.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.put("/movies/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, movie_update: MovieUpdate, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie_update.title is not None:
        db_movie.title = movie_update.title
    if movie_update.genres is not None:
        db_movie.genres = movie_update.genres

    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(db_movie)
    db.commit()
    return


# --- LINKS ---

@app.post("/links", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    if db.query(Link).filter(Link.movieId == link.movieId).first():
        raise HTTPException(status_code=400, detail="Link for this movie already exists")

    # Zmiana: użycie .model_dump() zamiast .dict()
    db_link = Link(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get("/links", response_model=List[LinkOut])
def get_links(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Link).offset(skip).limit(limit).all()


@app.get("/links/{movie_id}", response_model=LinkOut)
def get_link(movie_id: int, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.movieId == movie_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@app.put("/links/{movie_id}", response_model=LinkOut)
def update_link(movie_id: int, link_update: LinkUpdate, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    if link_update.imdbId is not None:
        db_link.imdbId = link_update.imdbId
    if link_update.tmdbId is not None:
        db_link.tmdbId = link_update.tmdbId

    db.commit()
    db.refresh(db_link)
    return db_link


@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(movie_id: int, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(db_link)
    db.commit()
    return


# --- RATINGS ---

@app.post("/ratings", response_model=RatingOut, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    existing = db.query(Rating).filter(Rating.userId == rating.userId, Rating.movieId == rating.movieId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rating already exists")

    # Zmiana: użycie .model_dump() zamiast .dict()
    db_rating = Rating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.get("/ratings", response_model=List[RatingOut])
def get_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Rating).offset(skip).limit(limit).all()


@app.get("/ratings/{user_id}/{movie_id}", response_model=RatingOut)
def get_rating(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    rating = db.query(Rating).filter(Rating.userId == user_id, Rating.movieId == movie_id).first()
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@app.put("/ratings/{user_id}/{movie_id}", response_model=RatingOut)
def update_rating(user_id: int, movie_id: int, rating_update: RatingUpdate, db: Session = Depends(get_db)):
    db_rating = db.query(Rating).filter(Rating.userId == user_id, Rating.movieId == movie_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    if rating_update.rating is not None:
        db_rating.rating = rating_update.rating
    if rating_update.timestamp is not None:
        db_rating.timestamp = rating_update.timestamp

    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.delete("/ratings/{user_id}/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(Rating).filter(Rating.userId == user_id, Rating.movieId == movie_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(db_rating)
    db.commit()
    return


# --- TAGS ---

@app.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    # Zmiana: użycie .model_dump() zamiast .dict()
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/tags", response_model=List[TagOut])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Tag).offset(skip).limit(limit).all()


@app.get("/tags/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, tag_update: TagUpdate, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag_update.tag is not None:
        db_tag.tag = tag_update.tag
    if tag_update.timestamp is not None:
        db_tag.timestamp = tag_update.timestamp

    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(db_tag)
    db.commit()
    return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)