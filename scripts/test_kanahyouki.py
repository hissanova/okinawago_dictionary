from kanahyouki import (
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
    _check_ending)


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
        _check_vowel('',['k'])

def test_check_vowel_single_vowel():
    assert ('a', []) == _check_vowel('',['a'])


def test_check_vowel_long_vowel():
    assert ('aa', []) == _check_vowel('',list('aa'))
    
def test_check_vowel_different_vowels():
    assert ('a', ['e']) == _check_vowel('',list('ae'))


def test_check_semi_vowels():
    assert ('ja', []) == _check_semi_vowels('', list("ja"))
    assert ('wa', []) == _check_semi_vowels('', list("wa"))
    assert ('a', []) == _check_semi_vowels('', list("a"))

def test_check_consonant():
    assert ('hwa', ['N']) == _check_consonant('', list('hwaN'))
    assert ('ca', []) == _check_consonant('', list('ca'))
    assert ('kja', []) == _check_consonant('', list('kja'))
    assert ('kaa', []) == _check_consonant('', list('kaa'))
    assert ('kjaa', []) == _check_consonant('', list('kjaa'))
    assert ('kjaa', ['N']) == _check_consonant('', list('kjaaN'))


def test_check_glottal_stop():
    assert ('?a', []) == _check_glottal_stop(list('?a'))
    assert ("'e", []) == _check_glottal_stop(list("'e"))
    assert ("?jaa", []) == _check_glottal_stop(list("?jaa"))
    assert ("?jaa", ["N"]) == _check_glottal_stop(list("?jaaN"))
