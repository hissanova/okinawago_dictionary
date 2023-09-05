from typing import Any, Dict, List
import json
from collections import defaultdict
from pprint import pprint

vowels = ["a", "i", "u", "e", "o"]

with open("resources/phonetics-table.json", 'r') as fp:
    phonetics_table = json.load(fp)

consonant2syllables_dict: Dict[str, List] = defaultdict(list)


def remove_vowel(phoneme: str) -> str:
    for v in vowels:
        phoneme = phoneme.replace(v, "")
    return phoneme


for phonetics_entry in phonetics_table:
    for syllable in phonetics_entry["roman"]:
        consonant = remove_vowel(syllable)
        if len(consonant) == 2 and not (consonant[0] in ["n", "h", "'", "?"]
                                        ) and consonant[1] in ["j", "w"]:
            key = consonant[0]
        else:
            key = consonant
        consonant2syllables_dict[key] += [phonetics_entry]

for k, v in consonant2syllables_dict.items():
    print(k, len(v))
    pprint(v)
