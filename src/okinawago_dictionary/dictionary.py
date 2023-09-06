from abc import ABC, abstractmethod
import json
from typing import List
from pathlib import Path

from wanakana import to_hiragana, to_katakana

current_dir = Path(__file__).parent

with open(current_dir / "okinawa_01.json", 'r') as raw_file:
    raw_oki_dict = json.load(raw_file)

with open(current_dir / "okinawa_01_index-table.json", 'r') as raw_file:
    raw_oki_ind_dict = json.load(raw_file)

with open(current_dir / "okinawa_02.json", 'r') as raw_file:
    raw_yamato_dict = json.load(raw_file)

with open(current_dir / "okinawa_02_index-table.json", 'r') as raw_file:
    raw_yamato_ind_dict = json.load(raw_file)

with open(current_dir / "katsuyou_jiten.json", 'r') as raw_file:
    raw_katsuyou_jiten = json.load(raw_file)

with open(current_dir / "katsuyou_jiten_index-table.json", 'r') as raw_file:
    raw_katsuyou_ind_jiten = json.load(raw_file)


class Dictionary(ABC):

    def __init__(self, raw_word_dict, index_to_key_dict):
        content_dict = {}
        for entry in raw_word_dict:
            content_dict[entry["id"]] = entry
        self._index_to_key_dict = index_to_key_dict
        self._content_dict = content_dict

    @property
    def index_words(self):
        return self._index_to_key_dict.keys()

    def get_keys(self, index_word: str) -> List[int]:
        return self._index_to_key_dict[index_word]

    def get_content(self, key: int):
        return self._content_dict[key]

    @abstractmethod
    def normalise_kana(self, kana_str: str) -> str:
        raise NotImplementedError


class OkinawagoDictionary(Dictionary):
    """Documentation for OkinawagoDictionary

    """

    def __init__(self, raw_oki_dict, index_to_key_dict):
        super(OkinawagoDictionary, self).__init__(raw_oki_dict,
                                                  index_to_key_dict)

    def normalise_kana(self, kana_str: str) -> str:
        return "".join([c if c == "’" else to_katakana(c) for c in kana_str])


class YamatogoDictionary(Dictionary):
    """Documentation for YamatoDictionary

    """

    def __init__(self, raw_yamato_dict, index_to_key_dict):
        super(YamatogoDictionary, self).__init__(raw_yamato_dict,
                                                 index_to_key_dict)

    def normalise_kana(self, kana_str: str) -> str:
        return to_hiragana(kana_str)


class KatsuyouDictionary(Dictionary):
    """Documentation for YamatoDictionary

    """

    def __init__(self, raw_yamato_dict, index_to_key_dict):
        super(KatsuyouDictionary, self).__init__(raw_katsuyou_jiten,
                                                 index_to_key_dict)

    def normalise_kana(self, kana_str: str) -> str:
        return to_katakana(kana_str)


oki_dict = OkinawagoDictionary(raw_oki_dict, raw_oki_ind_dict)
yamato_dict = YamatogoDictionary(raw_yamato_dict, raw_yamato_ind_dict)
katsuyou_jiten = KatsuyouDictionary(raw_katsuyou_jiten, raw_katsuyou_ind_jiten)
