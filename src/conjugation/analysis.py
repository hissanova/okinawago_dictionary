from pprint import pprint
from typing import Dict

from wanakana import is_japanese

from okinawago_dictionary.dictionary import oki_dict
from conjugations import parse_pos_notation

verbs = list(
    filter(
        lambda v: any(pos in v["pos"] for pos in ["自", "他", "動"]),
        oki_dict._content_dict.values(),
    ))

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


# for notation, endings in conj_types.items():
#     if "/" in notation:
#         notation, remark = notation.split("/")
#     if notation.startswith("自･不規則"):
#         print("自･不規則")
#         print("\t" + str(endings))
#     elif notation.startswith("他･不規則"):
#         print("他･不規則")
#         print("\t" + str(endings))
#     elif notation.startswith("自･他") or notation.startswith("他･自"):
#         head, conjs = notation[2], notation[3:].split(",")
#         print(head)
#         print("\t" + str(endings))
#         print(f"\tconjs:{conjs}")
#     elif notation.startswith("自") or notation.startswith("他"):
#         head, conjs = notation[0], notation[1:].split(",")
#         print(head)
#         print("\t" + str(endings))
#         print(f"\tconjs:{conjs}")
#     else:
#         print("Others")
#         print("\t" + str(endings))
#         print(f"\tnotation:{notation}")

# head, rest = notation[0], notation[1:].split(",")
# print(f"{endings}")
# if rest[0] == '':
#     print("0 conjs")
#     print(f"\thead:{head}\trest:{rest}")
# elif is_japanese(head) and all(is_romaji(c) for c in rest):
#     if len(rest) == 1:
#         print("1 conjs")
#         print(f"\thead:{head}\trest:{rest}")
#     elif len(rest) == 2:
#         print("2 conjs")
#         print(f"\thead:{head}\trest:{rest}")
#     elif len(rest) == 3:
#         print("3 conjs")
#         print(f"\thead:{head}\trest:{rest}")
#     else:
#         print("More conjs")
#         print(f"\thead:{head}\trest:{rest}")
# else:
#     print("Else")
#     print(f"\tnotation:{notation}")

count = 0
ends_with_a = []
for v in verbs[:]:
    pronunc = v["pronunciation"]
    pos_notation = v["pos"].replace(" ", "")
    if pos_notation.count("=") == 0:
        count += 1
        pprint([pronunc, pos_notation])
        # print(f"Root ends with -a?:{pronunc.split('=')[0].endswith('a')}")
        ends_with_a.append(pronunc.split("=")[0].endswith("a"))
        part_of_speech = parse_pos_notation(pronunc, pos_notation)
        pprint(part_of_speech)

print(count, all(ends_with_a))
