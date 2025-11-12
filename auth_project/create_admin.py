import sys
import os
from sqlalchemy.orm import Session

# aby skrypt "widział" inne moduły (database, models, security)Dodajemy nadrzędny folder do ścieżki Pythona
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from auth_project.database import SessionLocal, engine
from auth_project.models import Base, User
from auth_project.security import hash_password

Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

# ------------- DANE  ADMINA -------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
# ----------------------------------------

try:
    # Sprawdź, czy admin już istnieje
    existing_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()

    if existing_user:
        print(f"Użytkownik '{ADMIN_USERNAME}' już istnieje. Nic nie robię.")
    else:
        # Haszuje hasło
        hashed_pw = hash_password(ADMIN_PASSWORD)

        # Tworze admina
        admin_user = User(
            username=ADMIN_USERNAME,
            hashed_password=hashed_pw,
            roles=["ROLE_USER", "ROLE_ADMIN"]  # Dajemy mu obie role
        )

        db.add(admin_user)
        db.commit()
        print(f"Pomyślnie utworzono admina: '{ADMIN_USERNAME}'")

except Exception as e:
    print(f"Wystąpił błąd: {e}")
    db.rollback()
finally:
    db.close()