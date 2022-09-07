import json
from csv import DictReader

from kanahyouki import convert2kana


def convert(tsv_row):
    res = {}
    res["page-in-dict"] = tsv_row["辞書\nページ"]
    pronuc = tsv_row["見出し語"]
    res["index"] = convert2kana(pronuc)
    res["accent"] = tsv_row["アクセント型"]
    res["pos"] = tsv_row["品詞"]
    res["bungo-type"] = tsv_row["文語などの\n種別"]
    res["amendment"] = tsv_row["補足"]
    keys = ['意味 1.', '意味 2.', '意味 3.', '意味 4.', '意味 5.']
    res["meaning"] = [tsv_row[key] for key in keys]
    res["remarks"] = tsv_row["備考"]
    return res


def main():
    entry_list = []
    with open("./resources/base_lists/okinawa_01.tsv", 'r') as base_file:
        base_tsv = DictReader(base_file, delimiter='\t')

        for i, entry in enumerate(base_tsv):
            new_entry = convert(entry)
            new_entry = {"id": i}
            new_entry.update(convert(entry))
            entry_list.append(new_entry)
    with open("./resources/base_lists/okinawa_01.json", 'w') as base_json:
        json.dump(entry_list, base_json)


if __name__ == "__main__":
    main()
