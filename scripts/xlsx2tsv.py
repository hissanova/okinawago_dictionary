"""
国立国語研究所の沖縄語辞典のxlsx化されたデータを読み込んで、tsvファイルに変換します。
"""

from csv import writer

from openpyxl import load_workbook

XLSX_OKI2YAMATO = "./data/okinawa_01.xlsx"

zen2han_dict = {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}
zen2han_dict.update({'、': ','})


def main():
    workbook = load_workbook(XLSX_OKI2YAMATO)

    def cells2values(row):
        """xlsx形式の行を文字列の行に変換します。"""
        new_row = [e.value for e in row]
        new_row[1] = new_row[1].translate(str.maketrans(zen2han_dict))
        return new_row

    rows = [cells2values(row) for row in list(workbook.worksheets[0].rows)]
    file_name = XLSX_OKI2YAMATO.replace(".xlsx", ".tsv")
    with open(file_name, 'w') as tsv_file:
        tsv_writer = writer(tsv_file, delimiter="\t")
        for row in rows:
            tsv_writer.writerow(row)


if __name__ == '__main__':
    main()
