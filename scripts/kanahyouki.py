"""
日本語（沖縄語）の音節（モーラ？）のスキーム
mora::=[g]([P]|[C][v]V[V])
word::=mora+...
- g:glottal stop ["'", "?"]
- P:pseudo-consonant ["Q", "N"]
- C:consonant
- v:semi-vowel
- V:vowel
"""
from typing import List, Tuple
import json
from itertools import product

vowels = {'a', 'i', 'u', 'e', 'o'}
consonants = {
    'C', 'S', 'Z', 'b', 'c', 'd', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'q', 'r',
    's', 't', 'z'
}
semi_vowels = {'j', 'w'}
sokuon = {'Q'}
hatsuon = {'N'}
glottal_stops = {"'", '?'}
others = {' ', '(', ')', ',', '-', '=', ']'}

exceptions = ["hNN"]  # 発音記号の例外


def _delete_others(pronunciation: str) -> str:
    """発音記号の文字列から、子音、半母音、母音以外の文字を消去します。"""
    for other_chr in others:
        word = pronunciation.replace(other_chr, '')
    return word


def _check_glottal_stop(ch_list: List[str]) -> Tuple[str, List[str]]:
    char = ch_list[0]
    if char in glottal_stops:
        return _check_consonant(char, ch_list[1:])
    return _check_consonant('', ch_list)


def _check_consonant(mora: str, ch_list: List[str]) -> Tuple[str, List[str]]:
    char = ch_list[0]
    if char in sokuon.union(hatsuon):
        return char, ch_list[1:]
    if char in consonants:
        return _check_semi_vowels(mora + char, ch_list[1:])
    return _check_semi_vowels(mora, ch_list)


def _check_semi_vowels(mora: str, ch_list: List[str]) -> Tuple[str, List[str]]:
    char = ch_list[0]
    if char in semi_vowels:
        return _check_vowel(mora + char, ch_list[1:])
    return _check_vowel(mora, ch_list)


def _check_vowel(mora: str, ch_list: List[str]) -> Tuple[str, List[str]]:
    char = ch_list[0]
    if char in vowels:
        return _check_ending(mora + char, ch_list[1:])
    raise Exception(f"{mora}の次は、母音{{aeiou}}が続きます。")


def _check_ending(mora: str, ch_list: List[str]) -> Tuple[str, List[str]]:
    if len(ch_list) == 0:
        return mora, ch_list
    char = ch_list[0]
    if char in vowels and mora[-1] == char:
        return mora + char, ch_list[1:]
    return mora, ch_list


def split_into_moras(pronunciation: str) -> List[str]:
    """発音記号の文字列をモーラに分解します。"""
    if pronunciation in exceptions:
        return [pronunciation]
    word = _delete_others(pronunciation)
    chr_list = list(word)
    moras: List[str] = []
    while chr_list:
        mora, chr_list = _check_glottal_stop(chr_list)
        moras.append(mora)
    return moras


def convert2kana(pronunciation: str) -> List[str]:
    """発音記号をかな表記に変換します。"""
    with open("resources/kana-table.json", 'r') as kana_list_file:
        pronunc_kana_dict = json.load(kana_list_file)
    kana_list = []
    for mora in split_into_moras(pronunciation):
        kana_list.append(pronunc_kana_dict[mora])
    converted = []
    for kana in product(*kana_list):
        converted.append("".join(kana))
    return converted
