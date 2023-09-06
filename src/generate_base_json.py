import argparse
import json
from typing import List
from csv import DictReader
from enum import Enum
from pathlib import Path
import re

from wanakana import is_char_en_num, is_japanese, is_romaji, to_hiragana

from utils import create_index2id_table
from kanahyouki import generate_phonetics, SocialClass
from pos import get_pos

unicode_ranges = {
    "hiragana": "\u3041-\u3096",
    "katakana": "\u30A0-\u30FF",
    "kanji": "\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A",
    "kanji_radicals": "\u2E80-\u2FD5",
    "hankaku_katakana": "\uFF5F-\uFF9F",
    "punctuations": "\u3000-\u303F",
    "zenkaku_alphanum_puncs": "\uFF01-\uFF5E",
    "misc": "\u31F0-\u31FF\u3220-\u3243\u3280-\u337F",
}

total_uni_ranges = "".join([r for r in unicode_ranges.values()])


class Oki2YamatoConverter():
    source = "./resources/base_lists/okinawa_01.tsv"
    # oki_dict meaning string のパース用regex
    okinawan_in_sentence_pattern = re.compile(r"([-～a-zA-Z?\s']+)")
    example_sentences_pattern = re.compile(r"([-～a-zA-Z?\s',]+\.)")

    @classmethod
    def convert(cls, tsv_row):
        res = {}
        res["page-in-dict"] = tsv_row["辞書\nページ"]
        pronunciation = tsv_row["見出し語"]
        pos = get_pos(tsv_row["品詞"], pronunciation)
        res["pos"] = pos.to_dict()
        phonetics = generate_phonetics(pronunciation)
        phonetics = phonetics.to_dict()
        res["phonetics"] = phonetics
        pronunciation = phonetics["pronunciation"]
        indices = pronunciation["HEIMIN"]["kana"].copy()
        if indices_ := pronunciation.get("SHIZOKU"):
            indices += indices_["kana"]
        res["index"] = indices
        res["accent"] = tsv_row["アクセント型"]
        res["bungo-type"] = tsv_row["文語などの\n種別"]
        res["amendment"] = tsv_row["補足"]
        keys = ['意味 1.', '意味 2.', '意味 3.', '意味 4.', '意味 5.']
        res["meaning"] = [tsv_row[key] for key in keys]
        res["remarks"] = tsv_row["備考"]
        return res


class Yamato2OkiConverter():
    source = "./resources/base_lists/okinawa_02.tsv"

    @classmethod
    def convert(cls, tsv_row):
        res = {}
        res["page-in-dict"] = tsv_row["辞書\nページ"]
        res["index"] = [to_hiragana(tsv_row["見出し"])]
        res["kanji"] = tsv_row["見出しの漢字"]
        res["explanation"] = tsv_row["見出しの説明"]
        res["contents"] = cls._parse_contents(tsv_row["内容"])
        return res

    @classmethod
    def _make_oki_item(cls, item_symbols):
        item_symbols = item_symbols.replace(" ", "")
        vocabulary = {"reference": False}
        if item_symbols.startswith("→"):
            item_symbols = item_symbols[1:]
            vocabulary["reference"] = True
        if is_romaji(item_symbols):
            vocabulary.update({
                "lang":
                "Okinawa",
                "phonetics":
                generate_phonetics(item_symbols).to_dict()
            })
        # 関連フレーズ: "(敬語|小児語|卑語|時刻|植物名)\w+" の形のもの
        elif m := re.match(r"\((\w+)\)([\w→'?-]+)", item_symbols):
            connotation, item_symbols = m.groups()
            vocabulary.update({"connotation": connotation})
        elif m := re.match(r"([a-zA-Z'?-]+)\(([\w，' ]+)\)\(?([\w，' ]*)\)?",
                           item_symbols):
            m_groups = m.groups()
            vocabulary.update({
                "lang":
                "Okinawa",
                "phonetics":
                generate_phonetics(m_groups[0]).to_dict()
            })
            rest = m_groups[1:]
            for related in rest:
                if related:
                    if m_ := re.match(r"(敬語)([\w'，]+)", related):
                        vocabulary.update({
                            "related": {
                                "lang":
                                "Okinawa",
                                "phonetics":
                                generate_phonetics(m_.groups()[1]).to_dict(),
                                "connotation":
                                "敬語"
                            }
                        })
                    elif m_ := re.match(r"([\w']+)(の種類)([\w'，]+)", related):
                        m_groups = m_.groups()
                        related_okinawans = m_groups[2]
                        related_okinawans_list = [
                            cls._make_oki_item(
                                generate_phonetics(m_groups[0]).pronunciations[
                                    SocialClass.HEIMIN].kana[0] + "の種類")
                        ]
                        for related_okinawan in related_okinawans.split("，"):
                            related_okinawans_list.append(
                                cls._make_oki_item(related_okinawan))
                        vocabulary.update({"related": related_okinawans_list})
        else:
            vocabulary.update({"lang": "Yamato", "kana": item_symbols})
        # if "(" in item_symbols:
        #     print(item_symbols)
        #     print(vocabulary)

        return vocabulary

    @classmethod
    def _parse_contents(cls, content_obj):
        contents_dict = {}
        translations = content_obj.split('/')
        base_translations = []
        for pronunciation in translations.pop(0).strip(".").split('，'):
            base_translations.append(cls._make_oki_item(pronunciation))

        contents_dict["base"] = base_translations
        contents_dict["related"] = []
        for related_str in translations:
            related_str = related_str.replace(' ', '')
            related_phrases = cls._split_related_words_str(related_str)
            related_phrases = cls._flatten_period(related_phrases)
            contents_dict["related"].append(
                [cls._make_oki_item(phrase) for phrase in related_phrases])
        return contents_dict

    @classmethod
    def _split_related_words_str(cls, related_words: str) -> List[str]:
        """
        WIP:正規表現に書き換える
        """
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

    @classmethod
    def _flatten_period(cls, target_list):
        nested_list = [e.split('.') for e in target_list]
        return [e for sublist in nested_list for e in sublist]


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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dict_type',
                        choices=['o2y', 'y2o'],
                        help="""
        o2y:沖日辞典(resources/base_lists/okinawa_01.tsv からjsonへ変換)。\ny2o: 日沖辞典(resources/base_lists/okinawa_02.tsv からjsonへ変換)"""
                        )
    return parser.parse_args()


converter_dict = {"o2y": Oki2YamatoConverter, "y2o": Yamato2OkiConverter}


def main():
    args = parse_args()
    converter = converter_dict[args.dict_type]
    entry_list = []
    target_dir = Path(__file__).parent / "okinawago_dictionary"
    new_path = target_dir / Path(converter.source).name.replace(
        ".tsv", ".json")
    index_table_path = target_dir / Path(converter.source).name.replace(
        ".tsv", "_index-table.json")

    with open(converter.source, 'r') as base_file:
        base_tsv = DictReader(base_file, delimiter='\t')

        for i, entry in enumerate(base_tsv):
            new_entry = {"id": i}
            # print(converter.convert(entry))
            new_entry.update(converter.convert(entry))
            entry_list.append(new_entry)

    with open(new_path, 'w') as base_json:
        json.dump(entry_list, base_json, ensure_ascii=False)

    with open(index_table_path, 'w') as table_json_path:
        json.dump(create_index2id_table(entry_list),
                  table_json_path,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()
