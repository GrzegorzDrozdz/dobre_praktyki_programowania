
-----
# 🎓 Dobre Praktyki Programowania
Repozytorium poświęcone zadaniom realizowanym w ramach przedmiotu **"Dobre Praktyki Programowania"** na studiach.
-----

## 🗂️ Struktura Repozytorium (Branches)

Kod został podzielony na gałęzie tematyczne. Aby zobaczyć rozwiązanie konkretnego zadania, należy przełączyć się na odpowiedni branch.

### 1\.  Gałąź: `unit-tests` (Testy Jednostkowe)

Na tej gałęzi zaimplementowałem zestaw funkcji algorytmicznych oraz pokryłem je testami jednostkowymi przy użyciu biblioteki `pytest`.

  * **Implementacja:** Funkcje takie jak `is_palindrome`, `fibonacci`, `count_vowels`, `calculate_discount`, `flatten_list`.
  * **Testy:** Weryfikacja poprawności logicznej, obsługa błędów i przypadków brzegowych.


### 2\.  Gałąź: `python_api` (Wstęp do API)

**Temat:** Budowa pierwszego API i obsługa danych.
Wstęp do frameworka FastAPI. Stworzenie prostego serwera zwracającego dane w formacie JSON.

  * **Endpointy:** `/` (Hello World) oraz `/movies` (lista filmów).
  * **Dane:** Odczyt danych z plików CSV i mapowanie ich na obiekty klas Pythonowych.
  * **Technologie:** FastAPI, CSV handling.


  ### 3\.  Gałąź: `JSON_Web_Token` (Autoryzacja i JWT)

**Temat:** Bezpieczeństwo, haszowanie haseł i tokeny JWT.
Wdrożenie mechanizmów uwierzytelniania i autoryzacji użytkowników.

  * **Auth:** Endpoint `/login` generujący tokeny JWT (JSON Web Tokens).
  * **Security:** Haszowanie haseł (nie przechowujemy ich jawnym tekstem).
  * **Role:** Podział na użytkowników i administratorów (RBAC). Zabezpieczenie endpointów (np. `POST /users` tylko dla admina).



### 4\.  Gałąź: `feat/crud-endpoints` (CRUD + Testy Integracyjne)

**Temat:** Pełna obsługa zasobów i testy integracyjne.
Rozbudowa API o możliwość modyfikacji danych oraz zaawansowane testowanie całych procesów.

  * **CRUD:** Implementacja 16 endpointów (POST, GET, PUT, DELETE) dla zasobów: `Movies`, `Links`, `Ratings`, `Tags`.
  * **Baza danych:** Przejście na SQLAlchemy i SQLite.
  * **Testy Integracyjne:** Testowanie endpointów na bazie w pamięci (`:memory:`) z wykorzystaniem fixtur. Weryfikacja kodów statusu (201, 204, 404).


-----

##  Jak uruchomić projekt?
 

**1. Przygotuj środowisko:**

```bash
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**2. Uruchom aplikację lub testy (zależnie od gałęzi):**

  * **Dla gałęzi `feat/crud-endpoints` (CRUD):**

    ```bash
    uvicorn api:app --reload
    pytest tests/test_crud.py
    ```

  * **Dla gałęzi `JSON_Web_Token` (Auth):**

    ```bash
    uvicorn auth_project.main:app --reload
    pytest tests/test_main_auth.py
    ```

  * **Dla gałęzi `unit-tests`:**

    ```bash
    pytest tests/test_utils.py
    ```
