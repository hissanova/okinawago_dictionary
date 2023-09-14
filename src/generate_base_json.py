import argparse
import json
from typing import List
from csv import DictReader
from pathlib import Path
import re
# from pprint import pprint

from wanakana import is_romaji, to_hiragana

from utils import create_index2id_table
from kanahyouki import generate_phonetics, WordPhonetics, PhonemeSymols, Pronunciation, SocialClass
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
    # meaning string のパース用regex.
    # okinawan_in_sentence_pattern は、e.g.〔?i~i~Ci~i~〕のパターン(IPA&鼻音あり)を除く
    okinawan_in_sentence_pattern = re.compile(
        r"((?<!〔)[-～a-zA-Z?\s'=\]]+(?!~))")
    ipa_in_sentence_pattern = re.compile(r"〔([-~～a-zA-Z?\s']{2,})〕")
    roman_ipa_dict = {
        "C": "ç",
        "?": "ʔ",
        "i~": "ĩ",
        "o~": "õ",
    }
    example_sentences_pattern = re.compile(r"([-～a-zA-Z?\s',=\]]{2,}\.)")

    @classmethod
    def _refine_oki_phoneme(cls, oki_phonemes: str) -> str:
        return re.sub(r"[(=)\]]", r"", oki_phonemes)

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
        # print(phonetics["phonemes"]["simplified"])
        res["meaning"] = [
            cls._parse_meaning_string(tsv_row[key].replace(
                "～",
                cls._refine_oki_phoneme(phonetics["phonemes"]["simplified"]) +
                " ")) for key in keys if tsv_row[key]
        ]
        res["remarks"] = tsv_row["備考"]
        # print(res)
        return res

    @classmethod
    def _join_phonetics_sentence(cls, phonetics_list):
        joined = WordPhonetics(PhonemeSymols("", ""),
                               {SocialClass.HEIMIN: Pronunciation("", [""])})
        for maybe_phonetics in phonetics_list:
            if not isinstance(maybe_phonetics, WordPhonetics):
                new_phonetics = WordPhonetics(
                    PhonemeSymols(maybe_phonetics, maybe_phonetics), {
                        SocialClass.HEIMIN:
                        Pronunciation(maybe_phonetics, [maybe_phonetics])
                    })
            else:
                new_phonetics = maybe_phonetics
            joined += new_phonetics
        return joined.to_dict()

    @classmethod
    def _oki_sentence2kana(cls, sentence: str) -> str:
        oki_word_in_sentence_pattern = re.compile(r"([a-zA-Z?']+)")
        split_sen = oki_word_in_sentence_pattern.split(sentence)
        # print("oki_sentence: ", split_sen)
        kana_sentence = []
        for word in split_sen:
            if word and oki_word_in_sentence_pattern.match(word):
                word = generate_phonetics(word)
            kana_sentence.append(word)
        # print(kana_sentence)
        return cls._join_phonetics_sentence(kana_sentence)

    @classmethod
    def _kanafy_okinawan_in_yamato(cls, sentence: str):
        found_okis = cls.okinawan_in_sentence_pattern.findall(sentence)

        okinawan_list = [
            cls._oki_sentence2kana(phoneme) for phoneme in found_okis
            if not re.fullmatch(
                r"(\]?[a-zA-Z?\s～]\.?|-self|apocopated\s?form)", phoneme)
        ]
        ipa_in_sentence = cls.ipa_in_sentence_pattern.findall(sentence)
        if ipa_in_sentence:
            # print("IPA:", ipa_in_sentence)
            new_ipas = []
            for ipa in ipa_in_sentence:
                roman = ipa.replace("~", "").replace("C", "h")
                phonetics = generate_phonetics(roman)
                for k, v in cls.roman_ipa_dict.items():
                    ipa = ipa.replace(k, v)
                ipa = re.sub(r"([ĩõ])\1", r"\1ː", ipa)
                new_ipas.append(ipa)
                phonetics_dict = phonetics.to_dict()
                # print(phonetics)
                phonetics_dict["pronunciation"]["HEIMIN"]["IPA"] = ipa
                okinawan_list.append(phonetics_dict)
            # print(new_ipas)
        # print(okinawan_list)
        return okinawan_list

    @classmethod
    def _parse_meaning_string(cls, sentence: str):
        paragraphs = []
        # print("Original: ", sentence)
        split_s = cls.example_sentences_pattern.split(sentence)
        sentence = split_s[0]
        okinawago = cls._kanafy_okinawan_in_yamato(sentence)
        # pprint("SPLIT_S: ")
        # pprint(split_s)
        # pprint("OKINAWAGO:")
        # pprint(okinawago)
        first_paragraph = {"yamato": sentence}
        if okinawago:
            first_paragraph.update({"okinawago": okinawago})
        paragraphs.append(first_paragraph)
        remains = split_s[1:]
        if remains:
            for i in range(0, len(remains), 2):
                # print(remains[i])
                paragraphs.append(
                    {"okinawago": cls._oki_sentence2kana(remains[i])})
                yamato_para = {"yamato": remains[i + 1]}
                okinawago = cls._kanafy_okinawan_in_yamato(remains[i + 1])
                if okinawago:
                    yamato_para.update({"okinawago": okinawago})
                paragraphs.append(yamato_para)
        # print("PARAGRAPHS:")
        # pprint(paragraphs)
        return paragraphs

    @classmethod
    def _convert_oki_sentence2kana(cls, sentence: str):
        pass


class Yamato2OkiConverter():
    source = "./resources/base_lists/okinawa_02.tsv"
    okinawan_in_related_words = re.compile(
        r"((?:\([\w，'?\s]+\))?→?[-a-zA-Z?\s']+(?:\([\w，'?\s]+\))*)")

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
        # pprint(content_obj)
        contents_dict = {}
        translations = content_obj.split('/')
        base_translations = []
        for pronunciation in translations.pop(0).strip(".").split('，'):
            base_translations.append(cls._make_oki_item(pronunciation))

        contents_dict["base"] = base_translations
        contents_dict["related"] = []
        for related_str in translations:
            related_str = related_str.replace(' ', '').replace('　', '')
            related_phrases = cls._split_related_words_str(related_str)
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
        vocabulary = {"reference": False, "lang": "Okinawa"}
        if item_symbols.startswith("→"):
            item_symbols = item_symbols[1:]
            vocabulary["reference"] = True
        if is_romaji(item_symbols):
            vocabulary.update(
                {"phonetics": generate_phonetics(item_symbols).to_dict()})
        # 関連フレーズ: "(敬語|小児語|卑語|時刻|植物名)\w+" の形のもの
        elif m := re.match(r"\((\w+)\)([\w→'?-]+)", item_symbols):
            connotation, item_symbols = m.groups()
            if item_symbols.startswith("→"):
                vocabulary["reference"] = True
                item_symbols = item_symbols[1:]
            if is_romaji(item_symbols):
                vocabulary.update({
                    "phonetics":
                    generate_phonetics(item_symbols).to_dict(),
                    "connotation":
                    connotation
                })
            else:
                vocabulary["lang"] = "Yamato"
                vocabulary["kana"] = item_symbols
        elif m := re.match(r"([a-zA-Z'?-]+)\(([\w，' ]+)\)\(?([\w，' ]*)\)?",
                           item_symbols):
            m_groups = m.groups()
            vocabulary.update(
                {"phonetics": generate_phonetics(m_groups[0]).to_dict()})
            rest = m_groups[1:]
            related_okinawans_list = []
            for related in rest:
                if related:
                    if m_ := re.match(r"(敬語)([\w'，]+)", related):
                        related_okinawans_list.append({
                            "lang":
                            "Okinawa",
                            "phonetics":
                            generate_phonetics(m_.groups()[1]).to_dict(),
                            "connotation":
                            "敬語"
                        })
                    elif m_ := re.match(r"([\w']+)\s*(の種類)\s*([\w'，]+)",
                                        related):
                        m_groups = m_.groups()
                        related_okinawans = m_groups[2]
                        related_okinawans_list.append(
                            cls._make_oki_item(
                                generate_phonetics(m_groups[0]).pronunciations[
                                    SocialClass.HEIMIN].kana[0] + "の種類"))
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
        json.dump(
            entry_list,
            base_json,
            ensure_ascii=False,
            indent=4,
        )

    with open(index_table_path, 'w') as table_json_path:
        json.dump(create_index2id_table(entry_list),
                  table_json_path,
                  ensure_ascii=False,
                  indent=4)


if __name__ == "__main__":
    main()
