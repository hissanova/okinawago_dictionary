import argparse
from collections import Counter, defaultdict
import json
import re
from pprint import pprint
from typing import Dict


non_alnum_chs = ['「', '⺟', '\u2003', '＝', '］', '⻨', '。', '⻑', '⻄', '-', '！', '〉', '\[', '〜', '⻭', '⻲', '⺠', '⻤', '…', '・', '≒', '．', '［', '〈', '⺒', '？', '」', '/', '⻯', '.', '*', '\]', '：', '‘', '⻫', '⻩', '̶', '’', '⻘', '、', ':', '／', '；']

# print(r"\(([\w" + r"".join(non_alnum_chs) + r"]+)\)")


chapters = [
    {
        "title": "名詞･動詞編",
        "range": [17, 413]
    },
    {
        "title": "形容詞編",
        "range": [415, 495]
    },
    {
        "title": "副詞編",
        "range": [497, 577]
    },
]


def separate_variations(index):
    index = index.replace("（", "(").replace("）", ")")
    return list(
        set([
            "".join(re.split(r"\(\w+\)", index)),
            "".join(re.split(r"\((\w+)\)", index))
        ]))


def split_recur(st, spl_lst):
    if not spl_lst:
        return separate_variations(st)
    else:
        return [
            x for lis in map(lambda s: split_recur(s, spl_lst[1:]),
                             st.split(spl_lst[0])) for x in lis
        ]


def is_in(val, interval) -> bool:
    return interval[0] <= val <= interval[1]


def add_pos(item):
    if is_in(item["page"], chapters[0]["range"]):
        if item.get("conjugation"):
            item["pos"] = "動"
        else:
            item["pos"] = "名"
    elif is_in(item["page"], chapters[1]["range"]):
        item["pos"] = "形"
    elif is_in(item["page"], chapters[2]["range"]):
        item["pos"] = "副"
    else:
        raise ValueError


def decompose_sample_sentences(contents):
    decomposed = []
    # print(contents)
    contents = contents.replace("。", "").replace("（", "(").replace("）", ")")
    letters = r"[\w" + r"".join(non_alnum_chs) + "]*"
    pattern = r"\((" + letters + r"(?:\(" + letters + r"\))?" + letters + r")\)、?"
    split_contents = re.split(pattern, contents)[:-1]
    # print(len(split_contents))
    # pprint(split_contents)
    for k in range(0, len(split_contents), 2):
        decomposed.append({"okinawa": split_contents[k] + "。",
                           "yamato": split_contents[k + 1] + "。"})
    return decomposed

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=['json', 'jsonl'], default="json")
    return parser.parse_args()


def main():
    args = parse_args()
    items = []
    with open("dict_items.jsonl", 'r') as fp:
        for line in fp:
            items.append(json.loads(line))
    index_pos_stats: Dict[int, Counter] = defaultdict(Counter)
    dictionary = []
    prev_main_entry = items[0]
    ch_sets = [set(), set()]
    for i, item in enumerate(items):
        original_contents = item["contents"]
        # 大和口での意味、その他の内容に分割する
        split_point = original_contents.index("〉")
        yamato, contents = original_contents[:split_point +
                                             1], original_contents[
                                                 split_point + 1:]
        # if any(s.isdigit() for s in yamato):
        #     print(i, yamato)
        #     print(contents)
        item["yamato"] = yamato
        # 見出し語の位置情報によって、親の語彙エントリーの関連語リストに登録する
        index_x_coord = item["index_x_coord"]
        index_size = item["index_size"]
        index_pos_stats[index_x_coord].update([index_size])
        if 71 <= index_x_coord <= 72 or index_x_coord == 315:
            prev_main_entry = item
        else:
            parent_related_list = prev_main_entry.get("related", [])
            parent_related_list.append({
                "index": item["index"].split("、"),
                "yamato": item["yamato"],
                "id": i
            })
            prev_main_entry["related"] = parent_related_list
        # if not yamato.startswith("〈"):
        #     print(item['index'], yamato)
        # if len(contents) == 0:
        #     print(item)

        # 活用、例文、参照項に分割して、それぞれアイテムのアトリビュートとする
        split_contents = re.split(r"(【\w】)", contents)[1:]
        if len(split_contents) % 2 == 1:
            raise Exception(f"{split_contents}")
        for j in range(0, len(split_contents), 2):
            section_head = split_contents[j]
            section = split_contents[j + 1]
            if section_head == "【活】":

                def decompose_verb_conj(contents):
                    return {c_type: conj for c_type, conj in zip(["過去形", "否定形", "てぃ形"], contents.split("、"))}

                item["conjugation"] = decompose_verb_conj(section)
            elif section_head == "【例】":
                for ch in section:
                    if ch.isalnum():
                        ch_sets[0].add(ch)
                    else:
                        ch_sets[1].add(ch)
                item["sample_sentences"] = decompose_sample_sentences(section)
            elif section_head == "【参】":
                item["reference"] = section
            else:
                raise NotImplementedError

            # item[key] = section_head + split_contents[i + 1]
        add_pos(item)
        # 最終的な辞書に要らない項目の削除
        item.pop("contents")
        item.pop("index_x_coord")
        item.pop("index_size")
        # 複数 index が"、"で区切られてるのをリストに分割。
        item["index"] = split_recur(item["index"].replace(" ", ""), ["、", "／"])
        item["id"] = i
        # 辞書リストに登録
        dictionary.append(item)
    # print(ch_sets[0])
    # print(ch_sets[1])
    file_format = args.format
    if file_format == "jsonl":
        with open("katsuyou_jiten.jsonl", "w") as fp:
            for dict_item in dictionary:
                json.dump(dict_item, fp, ensure_ascii=False)
                fp.write("\n")
    elif file_format == "json":
        with open("katsuyou_jiten.json", "w") as fp:
            json.dump(dictionary, fp, ensure_ascii=False)

    # print(all(item["yamato"].count("〈") == 1 for item in dictionary))
    # print(all(item["yamato"].endswith("〉") for item in dictionary))
    # pprint(index_pos_stats)


if __name__ == "__main__":
    main()
