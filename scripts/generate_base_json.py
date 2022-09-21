import argparse
import json
from csv import DictReader

from wanakana import to_hiragana

from kanahyouki import convert2kana


class Oki2YamatoConverter():
    source = "./resources/base_lists/okinawa_01.tsv"

    def convert(tsv_row):
        res = {}
        res["page-in-dict"] = tsv_row["辞書\nページ"]
        pronuc = tsv_row["見出し語"]
        res["pronunciation"] = pronuc
        res["index"] = convert2kana(pronuc)
        res["accent"] = tsv_row["アクセント型"]
        res["pos"] = tsv_row["品詞"]
        res["bungo-type"] = tsv_row["文語などの\n種別"]
        res["amendment"] = tsv_row["補足"]
        keys = ['意味 1.', '意味 2.', '意味 3.', '意味 4.', '意味 5.']
        res["meaning"] = [tsv_row[key] for key in keys]
        res["remarks"] = tsv_row["備考"]
        return res


class Yamato2OkiConverter():
    source = "./resources/base_lists/okinawa_02.tsv"

    def convert(tsv_row):
        res = {}
        res["page-in-dict"] = tsv_row["辞書\nページ"]
        res["index"] = [to_hiragana(tsv_row["見出し"])]
        res["kanji"] = tsv_row["見出しの漢字"]
        res["explanation"] = tsv_row["見出しの説明"]
        res["meaning"] = tsv_row["内容"]
        return res


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dict_type',
        choices=['o2y', 'y2o'],
        help=
        "o2y:沖日辞典(resources/base_lists/okinawa_01.tsv からjsonへ変換)。\ny2o: 日沖辞典(resources/base_lists/okinawa_02.tsv からjsonへ変換)"
    )
    return parser.parse_args()


converter_dict = {"o2y": Oki2YamatoConverter, "y2o": Yamato2OkiConverter}


def main():
    args = parse_args()
    converter = converter_dict[args.dict_type]
    entry_list = []
    with open(converter.source, 'r') as base_file:
        base_tsv = DictReader(base_file, delimiter='\t')

        for i, entry in enumerate(base_tsv):
            new_entry = {"id": i}
            new_entry.update(converter.convert(entry))
            entry_list.append(new_entry)
    new_path = converter.source.replace(".tsv", ".json")
    with open(new_path, 'w') as base_json:
        json.dump(entry_list, base_json, ensure_ascii=False)


if __name__ == "__main__":
    main()
