from src.kanahyouki import (
    consonants,
    glottal_stops,
    vowels,
    semi_vowels,
    hatsuon,
    sokuon,
    _check_glottal_stop,
    _check_consonant,
    _check_semi_vowels,
    _check_vowel,
    _check_ending,
)

import pytest


def test_check_ending_non_vowels():
    non_vowels = consonants.union(semi_vowels).union(hatsuon).union(sokuon)
    for item in non_vowels:
        assert ('a', [item]) == _check_ending('a', [item])


def test_check_ending_vowels():
    for item in vowels.difference({'a'}):
        assert ('a', [item]) == _check_ending('a', [item])

    assert ('aa', ['N']) == _check_ending('a', list('aN'))
    assert ('aa', []) == _check_ending('a', list('a'))


def test_check_vowel_exception():
    with pytest.raises(Exception):
        _check_vowel('', ['k'])


def test_check_vowel_single_vowel():
    assert ('a', []) == _check_vowel('', ['a'])


def test_check_vowel_long_vowel():
    assert ('aa', []) == _check_vowel('', list('aa'))


def test_check_vowel_different_vowels():
    assert ('a', ['e']) == _check_vowel('', list('ae'))


def test_check_semi_vowels():
    targets = [
        ("ja", ('ja', [])),
        ("wa", ('wa', [])),
        ("a", ('a', [])),
    ]
    for in_strings, out_strings in targets:
        assert _check_semi_vowels('', list(in_strings)) == out_strings


def test_check_consonant():
    targets = [
        ('hwaN', ('hwa', ['N'])),
        ('ca', ('ca', [])),
        ('kja', ('kja', [])),
        ('kaa', ('kaa', [])),
        ('kjaa', ('kjaa', [])),
        ('kjaaN', ('kjaa', ['N'])),
    ]
    for in_strings, out_strings in targets:
        assert _check_consonant('', list(in_strings)) == out_strings


def test_check_glottal_stop():
    targets = [
        ('?a', ('?a', [])),
        ("'e", ("'e", [])),
        ("?jaa", ("?jaa", [])),
        ("?jaaN", ("?jaa", ["N"])),
    ]
    for in_strings, out_strings in targets:
        assert _check_glottal_stop(list(in_strings)) == out_strings
