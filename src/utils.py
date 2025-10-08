# src/utils.py

import re
import math
from typing import List, Any, Dict

def is_palindrome(text: str) -> bool:
    """Sprawdza czy tekst jest palindromem (ignoruje wielkość liter i spacje)."""
    if text is None:
        return False
    # Usuwamy znaki niealfanumeryczne i zamieniamy na małe litery
    cleaned = re.sub(r'[^A-Za-z0-9\u00C0-\u017F]', '', text).lower()
    return cleaned == cleaned[::-1]

def fibonacci(n: int) -> int:
    """Zwraca n-ty element ciągu Fibonacciego. fibonacci(0)=0, fibonacci(1)=1.
    Dla n < 0 -> ValueError."""
    if not isinstance(n, int):
        raise TypeError("n must be int")
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, a + b
    return b

def count_vowels(text: str) -> int:
    """Zlicza liczbę samogłosek (polskich i łacińskich) w tekście. Ignoruje wielkość liter."""
    if not text:
        return 0
    # W języku polskim samogłoskami są: a, e, i, o, u, y, ą, ę, ó.
    vowels = {"a", "e", "i", "o", "u", "y", "ą", "ę", "ó"}
    # Używamy .casefold() do obsługi różnych wielkości liter i sumujemy wystąpienia
    count = sum(1 for char in text.casefold() if char in vowels)
    return count

def calculate_discount(price: float, discount: float) -> float:
    """Zwraca cenę po uwzględnieniu zniżki.
    Discount musi być w [0,1]. W przeciwnym razie ValueError."""
    try:
        price_f = float(price)
        discount_f = float(discount)
    except (TypeError, ValueError):
        raise TypeError("price and discount must be numbers")
    if not (0 <= discount_f <= 1):
        raise ValueError("discount must be between 0 and 1 inclusive")
    return round(price_f * (1 - discount_f), 10)

def flatten_list(nested_list: list) -> list:
    """Spłaszcza listę z dowolnym poziomem zagnieżdżenia."""
    result: List[Any] = []
    def _flatten(x):
        if isinstance(x, list):
            for item in x:
                _flatten(item)
        else:
            result.append(x)
    _flatten(nested_list)
    return result

def word_frequencies(text: str) -> Dict[str, int]:
    """Zwraca słownik częstości występowania słów (ignorując wielkość liter i interpunkcję)."""
    if not text:
        return {}
    # Zamiana na małe litery i usunięcie znaków interpunkcyjnych
    cleaned = re.sub(r'[^\w\s\u00C0-\u017F]', '', text, flags=re.UNICODE)
    words = cleaned.lower().split()
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    return freqs

def is_prime(n: int) -> bool:
    """Sprawdza czy n jest liczbą pierwszą. Dla n < 2 -> False."""
    if not isinstance(n, int):
        raise TypeError("n must be int")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Sprawdzamy dzielniki nieparzyste do pierwiastka kwadratowego z n
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True