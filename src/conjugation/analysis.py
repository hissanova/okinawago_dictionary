from pprint import pprint
from typing import Dict

from wanakana import is_japanese

from okinawago_dictionary.dictionary import oki_dict
from conjugations import parse_pos_notation, irregular_verb_conjs


def is_verb(pos: str) -> bool:
    return any(v_type in pos for v_type in ["自", "他", "動"])


verbs = list(
    filter(lambda v: is_verb(v["pos"]), oki_dict._content_dict.values()))

verb_types: Dict = {}
for v in verbs:
    pos_notation = v["pos"].replace(" ", "")
    pronuncs = verb_types.setdefault(pos_notation, [])
    verb_types[pos_notation] = pronuncs + [v["pronunciation"]]

conj_types = {}
for pos, pronuncs in verb_types.items():
    endings = set()
    others = set()
    for pronunc in pronuncs:
        pronunc = pronunc.replace("]", "")
        split_word = pronunc.split("=")
        if len(split_word) == 2:
            endings.add(split_word[1])
        else:
            others.add(pronunc)
    conj_types[pos] = {"endings": endings, "others": others}

with open("verb_notation_types.txt", "w") as fp:
    fp.write(str(verb_types))

verb_stat = {k: len(v) for k, v in verb_types.items()}
verb_notation_stats = sorted(verb_stat.items(),
                             key=lambda item: item[1],
                             reverse=True)

with open("verb_notation_stats.txt", "w") as fp:
    for item in verb_notation_stats:
        fp.write(item[0] + "\t" + str(item[1]) + "\n")


def tokenise(notation: str) -> str:
    return "".join(["J" if is_japanese(c) else "R" for c in notation])


count = 0
ends_with_a = []
for v in verbs[:]:
    pronunc = v["pronunciation"]
    pos_notation = v["pos"].replace(" ", "")
    pos = parse_pos_notation(pronunc, pos_notation)
    print(pronunc, pos_notation)
    print(pos)
    # if pos_notation.count("=") == 0:
    #     count += 1
    #     print(pronunc, pos_notation, end="")
    #     if irregular_verb_conjs.get(pronunc, False):
    #         print("")
    #     else:
    #         print("\tNo description yet")
    #     # print(f"Root ends with -a?:{pronunc.split('=')[0].endswith('a')}")
    #     ends_with_a.append(pronunc.split("=")[0].endswith("a"))
    #     part_of_speech = parse_pos_notation(pronunc, pos_notation)
    #     print("\t", end="")
    #     pprint(part_of_speech)
    #     print("")

# print(count, all(ends_with_a))
