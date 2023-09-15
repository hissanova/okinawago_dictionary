from typing import Dict, List
from collections import defaultdict, OrderedDict


def create_index2id_table(entry_list: List) -> OrderedDict:
    index2id_table: Dict[str, List[str]] = defaultdict(list)
    for entry in entry_list:
        word_id = entry["id"]
        indices = entry["index"]
        for index in indices:
            index2id_table[index] += [word_id]
    return OrderedDict(index2id_table)
