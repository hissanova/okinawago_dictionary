import json

with open("resources/roman-to-ipa-dict.json") as fp:
    roman_ipa_dict = json.load(fp)

with open("resources/pronunciation-table.json") as fp:
    pronunc_table = json.load(fp)

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
    d["IPA"] = ipas
    print(d)
