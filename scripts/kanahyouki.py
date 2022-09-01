from typing import List, Tuple


vowels = {'a', 'i', 'u', 'e', 'o'}
conconants = {'C', 'S', 'Z', 'b', 'c', 'd', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'w', 'z'}
sokuon = {'Q'}
hatsuon = {'N'}
glottal_stops = { "'", '?'}
others ={' ', '(', ')', ',', '-', '=', ']'}

"""
日本語（沖縄語）の音節（モーラ？）のスキーム
[g]([P]|[C][v]V[V])
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

def _get_mora(mora:str, ch_list: List[str]) -> Tuple[str, List[str]]:
    if len(ch_list) == 0:
        return mora, ch_list
    if mora and mora[-1] in vowels and ch_list[0] in conconants.union(sokuon).union(hatsuon):
        return mora, ch_list
    ch = ch_list.pop(0)
    if ch in glottal_stops:
        if len(mora):
            raise Exception("glottal_stop を表す音素がモーラの先頭以外に来ることはありません。")
        mora = mora + ch
        m, ch_list_ = _get_mora(mora, ch_list)
    elif ch in conconants.union(vowels):
        mora = mora + ch
        m, ch_list_ = _get_mora(mora, ch_list)
    elif ch in sokuon.union(hatsuon):
        return mora + ch, ch_list
    return m, ch_list_


def split_into_moras(word:str) -> List[str]:
    word = delete_others(word)
    chr_list = list(word)
    moras : List[str] = []
    while (len(chr_list)):
        m, chr_list = _get_mora('', chr_list)
        moras.append(m)
            
    return moras

def convert2kana(pronunciation: str) -> str:
    pass
