"""
国立国語研究所の沖縄語辞典のxlsx化されたデータを読み込んで、tsvファイルに変換します。
"""

import argparse
from csv import writer
from pathlib import Path

from openpyxl import load_workbook

path_dict = {"o2y": "./resources/okinawa_01.xlsx", "y2o": "./resources/okinawa_02.xlsx"}

zen2han_dict = {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}
zen2han_dict.update({'、': ','})


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        choices=['o2y', 'y2o'],
                        help="o2y:沖日辞典(okinawa_01.xlsx)。\ny2o: 日沖辞典(okinawa_02.xlsx)")
    return parser.parse_args()


def main():
    args = parse_args()
    target_filename = path_dict[args.filename]
    print(target_filename)
    workbook = load_workbook(target_filename)

    def cells2values(row):
        """xlsx形式の行を文字列の行に変換します。"""
        new_row = [e.value for e in row]
        new_row[1] = new_row[1].translate(str.maketrans(zen2han_dict))
        return new_row

    rows = [cells2values(row) for row in list(workbook.worksheets[0].rows)]
    new_filename = target_filename.replace(".xlsx", ".tsv")
    if Path(new_filename).exists():
        raise Exception(f"{new_filename}は既に存在します。上書きできません。")
    with open(new_filename, 'w') as tsv_file:
        tsv_writer = writer(tsv_file, delimiter="\t")
        for row in rows:
            tsv_writer.writerow(row)


if __name__ == '__main__':
    main()
