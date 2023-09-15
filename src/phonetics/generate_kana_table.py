from typing import Dict, Tuple
import json
from collections import defaultdict, OrderedDict
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


def default_dict_factory():
    return OrderedDict([(v, {
        "roman": [],
        "IPA": {
            "HEIMIN": ""
        },
        "kana": {
            "HEIMIN": []
        },
    }) for v in "aiueo-"])


consonant2syllables_dict: Dict[str, OrderedDict] = OrderedDict()

for phonetics_entry in phonetics_table:
    syllable = phonetics_entry["roman"][0]
    consonant, vowel = separate_vowel(syllable)
    m = re.match(r"[’']?([jwN]?)", consonant)
    if m and m.group():
        key = m.groups()[0]
    else:
        key = consonant
    row_dict = consonant2syllables_dict.setdefault(key, default_dict_factory())
    if vowel:
        row_dict[vowel] = merge_dict(row_dict[vowel], phonetics_entry)
    else:
        row_dict["-"] = merge_dict(row_dict["-"], phonetics_entry)


def _maybe_embrace(
    parenthes1: str,
    ipa: str,
    parenthes2: str,
) -> str:
    if ipa:
        return parenthes1 + ipa + parenthes2
    else:
        return ""


frames = []
for consonant, row in consonant2syllables_dict.items():
    index = pd.MultiIndex.from_tuples([
        (consonant, "音素"),
        (consonant, "IPA"),
        (consonant, "カナ"),
    ])
    row_list = []
    for vowel, element in row.items():
        vals = []
        for key in ["roman", "IPA", "kana"]:
            val = element[key]
            if key == "roman":
                vals.append(_maybe_embrace("/", ",".join(val), "/"))
            elif key == "IPA":
                st = "<br>".join(
                    list(
                        map(
                            lambda i: "".join(
                                [i[0], _maybe_embrace("〔", i[1], "〕")]),
                            val.items())))
                st = st.replace("HEIMIN", "").replace("SHIZOKU", "士族:")
                vals.append(st)
            else:
                st = "<br>".join(
                    list(
                        map(lambda i: "".join([i[0], ",".join(i[1])]),
                            val.items())))
                st = st.replace("HEIMIN", "").replace("SHIZOKU", "士族:")
                vals.append(st)
        column = pd.DataFrame(
            {vowel: vals},
            index=index,
        )
        row_list.append(column)
    df_row = pd.concat(row_list, axis=1)
    frames.append(df_row)

df = pd.concat(frames)

with open("resources/phonetics-table.html", 'w') as fp:
    df.style.set_uuid("phonetics").applymap(
        lambda cell: (None if cell else "background-color: grey")).to_html(
            fp,
            escape=False,
        )
