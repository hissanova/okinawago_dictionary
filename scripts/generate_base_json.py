import argparse
import json
from typing import List
from csv import DictReader
from enum import Enum

from wanakana import is_char_en_num, is_japanese, is_romaji, to_hiragana

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
        res["contents"] = _parse_contents(tsv_row["内容"])
        return res


def _make_oki_item(pronunciation):
    vocabulary = {"reference": False}
    if pronunciation.startswith("→"):
        pronunciation = pronunciation[1:]
        vocabulary["reference"] = True
    if is_romaji(pronunciation):
        vocabulary.update({"pronunciation": pronunciation,
                           "kana": convert2kana(pronunciation),
                           "lang": "Okinawa"})
    else:
        vocabulary.update({"pronunciation": None,
                           "kana": pronunciation,
                           "lang": "Yamato"})
    return vocabulary


class LangMode(Enum):
    JAP = "japanese"
    ENG = "english"
    COMMA = "comma"
    PARETH = "parenthesis"
    OTHERS = "others"


def _get_lang_mode(ch: str) -> LangMode:
    if ch == '(':
        return LangMode.PARETH
    elif ch == '，':
        return LangMode.COMMA
    elif is_japanese(ch) or is_char_en_num(ch):
        return LangMode.JAP
    elif is_romaji(ch):
        return LangMode.ENG
    else:
        return LangMode.OTHERS


def _split_related_words_str(related_words: str) -> List[str]:
    split_word = []
    current_mode = LangMode.JAP
    current_chunk = ""
    while related_words:
        ch = related_words[0]
        char_mode = _get_lang_mode(ch)
        if char_mode == LangMode.PARETH:
            closing_pos = related_words.index(")") + 1
            current_chunk += related_words[:closing_pos]
            related_words = related_words[closing_pos:]
            continue
        if char_mode == LangMode.COMMA:
            if current_mode == LangMode.JAP:
                current_chunk += ch
            else:
                if current_chunk:
                    split_word.append(current_chunk)
                current_chunk = ''
        elif char_mode == LangMode.OTHERS:
            if current_chunk:
                split_word.append(current_chunk)
            current_chunk = ch
        else:
            if current_mode == char_mode:
                current_chunk += ch
            else:
                if current_chunk:
                    if current_chunk != "→":
                        split_word.append(current_chunk)
                        current_chunk = ch
                    else:
                        current_chunk += ch
                else:
                    current_chunk = ch
                current_mode = char_mode
        related_words = related_words[1:]
    split_word.append(current_chunk)
    return split_word


def flatten_period(target_list):
    nested_list = [e.split('.') for e in target_list]
    return [e for sublist in nested_list for e in sublist]


def _parse_contents(content_obj):
    contents_dict = {}
    translations = content_obj.split('/')
    base_translations = []
    for pronunciation in translations.pop(0).strip(".").split('，'):
        base_translations.append(_make_oki_item(pronunciation))

    contents_dict["base"] = base_translations
    contents_dict["related"] = []
    for related_str in translations:
        related_str = related_str.replace(' ', '')
        related_phrases = _split_related_words_str(related_str)
        related_phrases = flatten_period(related_phrases)
        contents_dict["related"].append([_make_oki_item(phrase) for phrase in related_phrases])
    return contents_dict


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
