from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, security
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not security.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    payload_data = {
        "sub": user.username,
        "roles": user.roles
    }

    token = security.create_access_token(data=payload_data)

    return {"access_token": token, "token_type": "bearer"}


@app.post("/users", response_model=schemas.UserDisplay, status_code=status.HTTP_201_CREATED)
def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(get_db),
        admin_payload: dict = Depends(security.is_admin)
):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Użytkownik o tej nazwie już istnieje")

    hashed_pw = security.hash_password(user_data.password)

    db_user = models.User(
        username=user_data.username,
        hashed_password=hashed_pw,
        roles=user_data.roles
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/user_details", response_model=schemas.UserDisplay)
def get_user_details(
        current_user_payload: dict = Depends(security.get_current_user_payload)
):
    return schemas.UserDisplay(
        username=current_user_payload.get("sub"),
        roles=current_user_payload.get("roles", [])
    )


@app.get("/protected_resource")
def get_protected_resource(
        current_user_payload: dict = Depends(security.get_current_user_payload)
):
    username = current_user_payload.get("sub")
    return {"message": f"Witaj {username}, masz dostęp do tego zasobu!"}