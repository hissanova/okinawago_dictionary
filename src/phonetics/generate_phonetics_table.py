import json
from itertools import product

from wanakana import to_katakana

with open("resources/roman-to-ipa-dict.json") as fp:
    roman_ipa_dict = json.load(fp)

with open("resources/pronunciation-table.json") as fp:
    pronunc_table = json.load(fp)

new_table = []

glottal_stop_syms = [roman_ipa_dict["?"], "?", "ッ"]

for d in pronunc_table:
    romans = d['roman']
    ipas = {}
    if len(romans) > 1:
        ipas = {"HEIMIN": romans[0][-1]}
    else:
        for roman in romans:
            ipas = {"HEIMIN": roman}
            for k, v in roman_ipa_dict.items():
                if k in roman and "ts" not in roman:
                    ipa = [roman.replace(k, v_) for v_ in v.split("|")]
                    ipas.update({
                        s_class: phone
                        for s_class, phone in zip(["HEIMIN", "SHIZOKU"], ipa)
                    })
    kanas = {}
    kana = d['kana']
    if len(romans) == 1:
        r = romans[0]
        if r[0] == "?" and romans[0][1] not in ["a", "i", "u", "e", "o"]:
            print(d)
            syllables = list({syllable[1:] for syllable in kana})
            kana = [
                "".join(chrs) for chrs in product(glottal_stop_syms, syllables)
            ]
            print(kana)
    # for k in kana:
    #     if "ッ" in k or k.startswith("?"):
    #         print(d)
    if len(ipas) == 2:
        kanas.update({"HEIMIN": kana[:-1], "SHIZOKU": kana[-1:]})
        if romans[0] == "Zu":
            kanas["SHIZOKU"] += "ヅ"
    else:
        kanas.update({"HEIMIN": kana})
    d.update({"IPA": ipas})
    d.update({"kana": kanas})
    new_table.append(d)

with open("resources/phonetics-table.json", 'w') as fp:
    json.dump(new_table, fp, ensure_ascii=False)
