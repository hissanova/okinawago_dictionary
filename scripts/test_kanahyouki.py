from kanahyouki import (
    consonants,
    glottal_stops,
    vowels,
    semi_vowels,
    hatsuon,
    sokuon,
    check_glottal_stop,
    check_consonant,
    check_semi_vowels,
    check_vowel,
    check_ending)


import pytest

def test_check_ending_non_vowels():
    non_vowels = consonants.union(semi_vowels).union(hatsuon).union(sokuon)
    for item in non_vowels:
        assert ('a', [item]) == check_ending('a', [item])
    

def test_check_ending_vowels():
    for item in vowels.difference({'a'}):
        assert ('a', [item]) == check_ending('a', [item])

    assert ('aa', ['N']) == check_ending('a', list('aN'))
    assert ('aa', []) == check_ending('a', list('a'))


def test_check_vowel_exception():
    with pytest.raises(Exception):
        check_vowel('',['k'])

def test_check_vowel_single_vowel():
    assert ('a', []) == check_vowel('',['a'])


def test_check_vowel_long_vowel():
    assert ('aa', []) == check_vowel('',list('aa'))
    
def test_check_vowel_different_vowels():
    assert ('a', ['e']) == check_vowel('',list('ae'))


def test_check_semi_vowels():
    assert ('ja', []) == check_semi_vowels('', list("ja"))
    assert ('wa', []) == check_semi_vowels('', list("wa"))
    assert ('a', []) == check_semi_vowels('', list("a"))

def test_check_consonant():
    assert ('hwa', ['N']) == check_consonant('', list('hwaN'))
    assert ('ca', []) == check_consonant('', list('ca'))
    assert ('kja', []) == check_consonant('', list('kja'))
    assert ('kaa', []) == check_consonant('', list('kaa'))
    assert ('kjaa', []) == check_consonant('', list('kjaa'))
    assert ('kjaa', ['N']) == check_consonant('', list('kjaaN'))


def test_check_glottal_stop():
    assert ('?a', []) == check_glottal_stop(list('?a'))
    assert ("'e", []) == check_glottal_stop(list("'e"))
    assert ("?jaa", []) == check_glottal_stop(list("?jaa"))
    assert ("?jaa", ["N"]) == check_glottal_stop(list("?jaaN"))
