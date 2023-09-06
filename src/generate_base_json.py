import argparse
import json
from typing import List
from csv import DictReader
from pathlib import Path
import re

from wanakana import is_romaji, to_hiragana

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
    # meaning string のパース用regex
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

    @classmethod
    def _parse_meaning_string(cls, sentence: str):
        split_s = cls.example_sentences_pattern.split(sentence)
        main_body = {
            "sentence": split_s[0],
            "okinawago": cls.okinawan_in_sentence_pattern.findall(split_s[0])
        }
        example_sentences = []
        examples = split_s[1:]
        if examples:
            for i in range(0, len(examples), 2):
                example_sentences.append({
                    "okinawa": examples[i],
                    "yamato": examples[i + 1]
                })
        return {"body": main_body, "examples": example_sentences}

    @classmethod
    def _convert_oki_sentence2kana(cls, sentence: str):
        pass


class Yamato2OkiConverter():
    source = "./resources/base_lists/okinawa_02.tsv"
    okinawan_in_related_words = re.compile(r"((?:\(\w+\))?→?[-a-zA-Z?\s']+)")

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
    def _parse_contents(cls, content_obj):
        print(content_obj)
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
            print(related_phrases)
            contents_dict["related"].append(
                [cls._make_oki_item(phrase) for phrase in related_phrases])
        return contents_dict

    @classmethod
    def _split_related_words_str(cls, related_str: str) -> List[str]:
        split_str = cls.okinawan_in_related_words.split(related_str)
        split_str = [s for s in split_str if re.match(r"[^，.]", s)]
        return split_str

    @classmethod
    def _make_oki_item(cls, item_symbols):
        item_symbols = item_symbols.replace(" ", "")
        vocabulary = {"reference": False}
        oki_vocab = {"lang": "Okinawa"}
        if item_symbols.startswith("→"):
            item_symbols = item_symbols[1:]
            vocabulary["reference"] = True
        if is_romaji(item_symbols):
            vocabulary.update(
                oki_vocab,
                **{"phonetics": generate_phonetics(item_symbols).to_dict()})
        # 関連フレーズ: "(敬語|小児語|卑語|時刻|植物名)\w+" の形のもの
        elif m := re.match(r"\((\w+)\)([\w→'?-]+)", item_symbols):
            connotation, item_symbols = m.groups()
            vocabulary.update({"connotation": connotation})
        elif m := re.match(r"([a-zA-Z'?-]+)\(([\w，' ]+)\)\(?([\w，' ]*)\)?",
                           item_symbols):
            m_groups = m.groups()
            vocabulary.update(
                oki_vocab,
                **{"phonetics": generate_phonetics(m_groups[0]).to_dict()})
            rest = m_groups[1:]
            for related in rest:
                if related:
                    if m_ := re.match(r"(敬語)([\w'，]+)", related):
                        vocabulary.update({
                            "related":
                            oki_vocab.update({
                                "phonetics":
                                generate_phonetics(m_.groups()[1]).to_dict(),
                                "connotation":
                                "敬語"
                            })
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

        return vocabulary

    @classmethod
    def _flatten_period(cls, target_list):
        nested_list = [e.split('.') for e in target_list]
        return [e for sublist in nested_list for e in sublist]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dict_type',
                        choices=['o2y', 'y2o'],
                        help="""
        o2y:沖日辞典(resources/base_lists/okinawa_01.tsv からjsonへ変換)。\n
        y2o: 日沖辞典(resources/base_lists/okinawa_02.tsv からjsonへ変換)""")
    return parser.parse_args()


converter_dict = {"o2y": Oki2YamatoConverter, "y2o": Yamato2OkiConverter}


def load_n_convert(converter):
    entry_list = []
    with open(converter.source, 'r') as base_file:
        base_tsv = DictReader(base_file, delimiter='\t')

        for i, entry in enumerate(base_tsv):
            new_entry = {"id": i}
            new_entry.update(converter.convert(entry))
            entry_list.append(new_entry)
    return entry_list


def main():
    args = parse_args()
    converter = converter_dict[args.dict_type]

    target_dir = Path(__file__).parent / "okinawago_dictionary"
    new_path = target_dir / Path(converter.source).name.replace(
        ".tsv", ".json")
    index_table_path = target_dir / Path(converter.source).name.replace(
        ".tsv", "_index-table.json")

    entry_list = load_n_convert(converter)
    with open(new_path, 'w') as base_json:
        json.dump(entry_list, base_json, ensure_ascii=False)

    with open(index_table_path, 'w') as table_json_path:
        json.dump(create_index2id_table(entry_list),
                  table_json_path,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()
