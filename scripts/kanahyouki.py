from typing import List, Tuple


vowels = {'a', 'i', 'u', 'e', 'o'}
consonants = {'C', 'S', 'Z', 'b', 'c', 'd', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'z'}
semi_vowels = {'j', 'w'}
sokuon = {'Q'}
hatsuon = {'N'}
glottal_stops = { "'", '?'}
others ={' ', '(', ')', ',', '-', '=', ']'}

exceptions = ["hNN"] # 発音記号の例外

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


def delete_others(word: str) -> str:
    for other_chr in others:
        word = word.replace(other_chr, '')
    return word


def _check_glottal_stop(ch_list: List[str]) -> Tuple[str, List[str]]:
    ch = ch_list[0]
    if ch in glottal_stops:
        return _check_consonant(ch, ch_list[1:])
    else:
        return _check_consonant('', ch_list)


def _check_consonant(mora:str, ch_list: List[str]) -> Tuple[str, List[str]]:
    ch = ch_list[0]
    if ch in sokuon.union(hatsuon):
        return ch, ch_list[1:]
    elif ch in consonants:
        return _check_semi_vowels(mora + ch, ch_list[1:])
    else:
        return _check_semi_vowels(mora, ch_list)


def _check_semi_vowels(mora:str, ch_list: List[str]) -> Tuple[str, List[str]]:
    ch = ch_list[0]
    if ch in semi_vowels:
        return _check_vowel(mora + ch, ch_list[1:])
    else:
        return _check_vowel(mora, ch_list)
    

def _check_vowel(mora:str, ch_list: List[str]) -> Tuple[str, List[str]]:
    ch = ch_list[0]
    if ch in vowels:
        return _check_ending(mora + ch, ch_list[1:])
    else:
        raise Exception(f"{mora}の次は、母音{{aeiou}}が続きます。")


def _check_ending(mora:str, ch_list: List[str]) -> Tuple[str, List[str]]:
    if len(ch_list) == 0:
        return mora, ch_list
    ch = ch_list[0]
    if ch in vowels and mora[-1] == ch:
        return mora + ch, ch_list[1:]
    else:
        return mora, ch_list


def split_into_moras(word:str) -> List[str]:
    if word in exceptions:
        return [word]
    word = delete_others(word)
    chr_list = list(word)
    moras : List[str] = []
    while (len(chr_list)):
        m, chr_list = _check_glottal_stop(chr_list)
        moras.append(m)
            
    return moras

def convert2kana(pronunciation: str) -> str:
    pass
