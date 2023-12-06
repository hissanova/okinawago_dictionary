from src.generate_base_json import Oki2YamatoConverter, split_sentence

import pytest

okinawan_in_sentence_pattern = Oki2YamatoConverter.okinawan_in_sentence_pattern
example_sentences_pattern = Oki2YamatoConverter.example_sentences_pattern


def test_split1():
    sentence_in = "泡。?aabukuともいう。～nutacuN.泡が立つ。"
    sentence_out = ["泡。?aabukuともいう。", "～nutacuN.", "泡が立つ。"]
    assert split_sentence(example_sentences_pattern,
                          sentence_in) == sentence_out


def test_split2():
    sentence_in = """1.ていさい。ありさま。身のこなし。風采。また,ぐあい。つごう。便利。'iitanari.（着こなしなどがいいこと。着物などがよくうつること。）～nu 'jutasjaN（'waQsaN）.つごうがいい（悪い）。便利がいい（悪い）。"""
    sentence_out = [
        "1.ていさい。ありさま。身のこなし。風采。また,ぐあい。つごう。便利。",
        "'iitanari.",
        "（着こなしなどがいいこと。着物などがよくうつること。）",
        "～nu 'jutasjaN（'waQsaN）.",
        "つごうがいい（悪い）。便利がいい（悪い）。",
    ]
    assert split_sentence(example_sentences_pattern,
                          sentence_in) == sentence_out


def test_split3():
    sentence_in = "雨。～nu hujuN.雨が降る。～nu harijuN.雨がやむ。雨があがる。（～nu'januN.とは元来はいわない。）"
    sentence_out = [
        "雨。",
        "～nu hujuN.",
        "雨が降る。",
        "～nu harijuN.",
        "雨がやむ。雨があがる。（～nu'januN.とは元来はいわない。）",
    ]
    assert split_sentence(example_sentences_pattern,
                          sentence_in) == sentence_out


def test_okinawan_search1():
    sentence_in = "[大主]?azi[按司]の家来の中の頭役。"
    detected = ["?azi"]
    assert okinawan_in_sentence_pattern.findall(sentence_in) == detected


def test_okinawan_search2():
    sentence_in = "この紙を燃やす彼岸の行事は'Ncabi,kabi?aNziiなどという。"
    detected = ["'Ncabi", "kabi?aNzii"]
    assert okinawan_in_sentence_pattern.findall(sentence_in) == detected
