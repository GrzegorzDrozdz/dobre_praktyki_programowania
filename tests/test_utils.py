# tests/test_utils.py
import pytest
from src import utils

def test_is_palindrome_examples():
    assert utils.is_palindrome("kajak") is True
    assert utils.is_palindrome("Kobyła ma mały bok") is True
    assert utils.is_palindrome("python") is False
    assert utils.is_palindrome("") is True
    assert utils.is_palindrome("A") is True
    assert utils.is_palindrome(None) is False

def test_fibonacci_examples_and_errors():
    assert utils.fibonacci(0) == 0
    assert utils.fibonacci(1) == 1
    assert utils.fibonacci(5) == 5
    assert utils.fibonacci(10) == 55
    with pytest.raises(ValueError):
        utils.fibonacci(-1)
    with pytest.raises(TypeError):
        utils.fibonacci(2.5)

def test_count_vowels_examples():
    # W "Python" samogłoski to 'o' oraz 'y'
    assert utils.count_vowels("Python") == 2
    assert utils.count_vowels("AEIOUY") == 6
    assert utils.count_vowels("bcd") == 0
    assert utils.count_vowels("") == 0
    # W "Próba żółwia" samogłoski to ó, a, ó, i, a -> łącznie 5
    assert utils.count_vowels("Próba żółwia") == 5

def test_calculate_discount_basic():
    assert utils.calculate_discount(100, 0.2) == 80.0
    assert utils.calculate_discount(50, 0) == 50.0
    assert utils.calculate_discount(200, 1) == 0.0

def test_calculate_discount_errors():
    with pytest.raises(ValueError):
        utils.calculate_discount(100, -0.1)
    with pytest.raises(ValueError):
        utils.calculate_discount(100, 1.5)
    with pytest.raises(TypeError):
        utils.calculate_discount("price", 0.1)

def test_flatten_list_examples():
    assert utils.flatten_list([1, 2, 3]) == [1, 2, 3]
    assert utils.flatten_list([1, [2, 3], [4, 5]]) == [1, 2, 3, 4, 5]
    assert utils.flatten_list([]) == []
    assert utils.flatten_list([[[1]]]) == [1]
    assert utils.flatten_list([1, [2, [3, [4]]]]) == [1, 2, 3, 4]

def test_word_frequencies_examples():
    assert utils.word_frequencies("To be or not to be") == {"to": 2, "be": 2, "or": 1, "not": 1}
    assert utils.word_frequencies("Hello, hello!") == {"hello": 2}
    assert utils.word_frequencies("") == {}
    assert utils.word_frequencies("Python Python python") == {"python": 3}
    # Test z polskimi znakami - sprawdzamy dokładny wynik
    text = "Ala ma kota, a kot ma Ale."
    expected = {"ala": 1, "ma": 2, "kota": 1, "a": 1, "kot": 1, "ale": 1}
    assert utils.word_frequencies(text) == expected

def test_is_prime_examples():
    assert utils.is_prime(2) is True
    assert utils.is_prime(3) is True
    assert utils.is_prime(4) is False
    assert utils.is_prime(0) is False
    assert utils.is_prime(1) is False
    assert utils.is_prime(5) is True
    assert utils.is_prime(97) is True
    with pytest.raises(TypeError):
        utils.is_prime(3.14)