from typing import Set
from itertools import islice
# from collections import Counter, defaultdict
from csv import DictWriter
from pprint import pprint
import json

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

path = r'./20210312Uchinaaguchi_e.pdf'
page_start = 17
page_end = 577

output_path = "extracted_text.tsv"


FONTNAMES = ['ITLECO+STIXGeneral-Regular',
             'MAROHK+STIXMathCalligraphy-Regular',
             'SNHJEW+STIXGeneral-Bold',
             'UNGZJN+IPAexMincho',
             'WBGMYU+IPAexGothic']

BOLDFONTS = [FONTNAMES[-1]]


def get_char_obj(line_obj):
    # return line_obj._objs[0]._objs
    ret = [obj for line in line_obj._objs for obj in line._objs]
    return ret


with open(output_path, 'w') as fp:
    heading = ["Page", "Head_Coord", "Height", "Text"]
    tsv_writer = DictWriter(fp, heading, delimiter="\t")
    tsv_writer.writeheader()
    # h_coord_counter = Counter()
    # height_counter = Counter()
    mid_pos = []
    right_outliers = []
    anno_set: Set = set()
    pages = {}
    for page_num, page_layout in enumerate(islice(extract_pages(path),
                                                  page_start,
                                                  page_end), page_start):
        left_col = []
        right_col = []
        for h_box in islice(page_layout, 1, None):
            if isinstance(h_box, LTTextContainer):
                head_x_coord = round(h_box.x0)
                height = round(h_box.height, 1)
                line = {"Page": page_num,
                        "Head_Coord": head_x_coord,
                        "Height": height,
                        "Text": h_box.get_text().replace("\n", "")}
                # h_coord_counter.update([head_x_coord])
                # height_counter.update([height])
                if head_x_coord < 100:
                    left_col.append(h_box)
                elif 280 < head_x_coord < 300:
                    mid_pos.append(h_box)
                else:
                    # 右端のページ見出し語の除去.ただし p.433 のはルビなので除去しない
                    if 400 < head_x_coord and page_num != 433:
                        right_outliers.append(h_box)
                    else:
                        right_col.append(h_box)
        pages[page_num] = left_col + right_col
        # for row in left_col + right_col:
        #     tsv_writer.writerow(row)
# print(sorted(h_coord_counter.items()))
# print(sorted(height_counter.items()))
# X
# print(all(l["Text"].strip("\n").isdigit() for l in mid_pos))
# for entry in right_outliers:
#     print(entry)

# font_stats = defaultdict(Counter)
# font_letter_stats = defaultdict(lambda: defaultdict(set))

items = []
current_bold_text = ""
index_x_coord = 0
index_size = 0.
current_contents = ""
for page_num, page in pages.items():
    for i, h_box in enumerate(page):
        # if page_num == 96:
        #     print(i, h_box)
        #     if i == 31:
        #         print(get_char_obj(h_box))
        for j, char_obj in enumerate(get_char_obj(h_box)):
            if page_num == 17 and i == 0 and j == 0:
                index_x_coord = round(char_obj.x0)
                index_size = round(char_obj.height, 1)
            if isinstance(char_obj, LTChar):
                fontname = char_obj.fontname
                if fontname == FONTNAMES[-1] or (fontname == FONTNAMES[2] and char_obj.get_text() in ["/", "(", ")"]):
                    if current_contents and current_bold_text:
                        items.append({"page": page_num,
                                      "index": current_bold_text,
                                      "index_x_coord": index_x_coord,
                                      "index_size": index_size,
                                      "contents": current_contents})
                        current_bold_text = char_obj._text
                        index_x_coord = round(char_obj.x0)
                        index_size = round(char_obj.height, 1)
                        current_contents = ""
                    elif not current_contents:
                        current_bold_text += char_obj._text
                    else:
                        raise Exception(f"{current_bold_text}::{current_contents}")
                else:
                    current_contents += char_obj._text
                # font_stats[char_obj.fontname].update([char_obj.adv])
                # font_letter_stats[char_obj.fontname][char_obj.adv].add(char_obj._text)
if current_contents and current_bold_text:
    items.append({"page": page_num,
                  "index": current_bold_text,
                  "index_x_coord": index_x_coord,
                  "index_size": index_size,
                  "contents": current_contents})


# print(dictionary)
# pprint(anno_set)
# pprint(font_stats)
# print(font_letter_stats)

with open("dict_items.jsonl", 'w') as fp:
    for item in items:
        json.dump(item, fp, ensure_ascii=False)
        fp.write("\n")


# pattern = '(' + index + ' *〈[\w（）、]+〉? *)'
# split_contents = re.split(pattern, line)
