from typing import Dict, List, Tuple
import json
from collections import defaultdict, OrderedDict
from pprint import pprint
import re

import pandas as pd

vowels = r'([aiueo])'

with open("resources/phonetics-table.json", 'r') as fp:
    phonetics_table = json.load(fp)
with open("resources/roman-to-ipa-dict.json", 'r') as fp:
    roman_to_ipa = json.load(fp)

excel2Original_dict = {
    "?": "ʔ",
    "C": "ç",
    "Z": "ʐ",
    "S": "ş",
}


def excel2original(excel_str: str) -> str:
    for k, v in excel2Original_dict.items():
        excel_str = excel_str.replace(k, v)
    return excel_str


consonant2syllables_dict: Dict[str, OrderedDict] = defaultdict(
    lambda: OrderedDict([(v, {}) for v in "aiueo-"]))


def separate_vowel(syllable: str) -> Tuple[str, str]:
    phonemes = re.split(vowels, syllable)
    if len(phonemes) == 1:
        return phonemes[0], ""
    else:
        consonant, vowel, _ = phonemes
        return consonant, vowel


def merge_dict(d1, d2):
    # print("d1: ", d1)
    # print("d2: ", d2)
    new_d = {}
    ipa = d1.setdefault("IPA", {})
    ipa.update(d2["IPA"])
    new_d.setdefault("IPA", ipa)
    new_roman = d1.setdefault("roman", []) + d2.setdefault("roman", [])
    new_d["roman"] = sorted(set(excel2original(s) for s in new_roman))
    kana = d1.setdefault("kana", {"HEIMIN": []})
    for k, v in d2.setdefault("kana", {"HEIMIN": []}).items():
        kana[k] = sorted(set(kana.setdefault(k, []) + v))
    new_d["kana"] = kana
    return new_d


for phonetics_entry in phonetics_table:
    # print(phonetics_entry)
    for syllable in phonetics_entry["roman"]:
        consonant, vowel = separate_vowel(syllable)
        m = re.match(r"[’']?([jw]?)", consonant)
        if m and m.group():
            key = m.groups()[0]
        else:
            key = consonant
        # if re.match(r"[^snh'?][jw]", consonant):
        #     key = consonant[0]
        # else:
        #     m = re.match(r"[’']?([jw]?)", consonant)
        #     if m and m.group():
        #         key = m.groups()[0]
        #     else:
        #         key = consonant
        # consonant2syllables_dict[key] += [phonetics_entry]
        # print(consonant2syllables_dict)
        row_dict = consonant2syllables_dict[key]
        if vowel:
            row_dict[vowel] = merge_dict(row_dict[vowel], phonetics_entry)
        else:
            row_dict["-"] = merge_dict(row_dict["-"], phonetics_entry)
        # consonant2syllables_dict[key]

# for k, v in consonant2syllables_dict.items():
#     print(k, len(v))
#     print(v)

# with open("resources/phonetics-table.html", 'w') as fp:
#     fp.write(json2html.json2html.convert(consonant2syllables_dict))
# print(dict(consonant2syllables_dict))
df = pd.DataFrame.from_dict(consonant2syllables_dict)
df = df.transpose()
# print(df.values[:2, :])
print([list(item.values()) for item in df.iloc[0].values])
row = pd.DataFrame.from_dict(
    dict(df.iloc[0]),
    orient="index",
    columns=["roman", "IPA", "kana"],
).transpose()
print(row)
df.iloc[0] = row
print(df)
# print(
#     df.apply(lambda row: pd.DataFrame.from_dict(
#         dict(row),
#         orient="index",
#         columns=["roman", "IPA", "kana"],
#     ).transpose(),
#              axis=1))

# print(df.apply(pd.DataFrame.from_dict))
# print(df.transpose().to_html())
