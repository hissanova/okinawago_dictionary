from typing import Any, Dict, List
import json
from collections import defaultdict
from pprint import pprint
import re

vowels = r'[aiueo]'

with open("resources/phonetics-table.json", 'r') as fp:
    phonetics_table = json.load(fp)

consonant2syllables_dict: Dict[str, List] = defaultdict(list)


def remove_vowel(phoneme: str) -> str:
    return re.sub(vowels, r'', phoneme)


for phonetics_entry in phonetics_table:
    for syllable in phonetics_entry["roman"]:
        consonant = remove_vowel(syllable)
        if re.match(r"[^snh'?][jw]", consonant):
            key = consonant[0]
        else:
            m = re.match(r"[’']?([jw]?)", consonant)
            if m and m.group():
                key = m.groups()[0]
            else:
                key = consonant
        consonant2syllables_dict[key] += [phonetics_entry]

for k, v in consonant2syllables_dict.items():
    print(k, len(v))
    pprint(v)
