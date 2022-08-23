from csv import writer

from openpyxl import load_workbook


XLSX_OKI2YAMATO = "./okinawa_01.xlsx"

def main():
    wb = load_workbook(XLSX_OKI2YAMATO)
    def cells2values(row):
        return [e.value for e in row]
    rows = [cells2values(row) for row in list(wb.worksheets[0].rows)]
    file_name = XLSX_OKI2YAMATO.replace(".xlsx", ".tsv")
    with open(file_name, 'w') as fp:
        tsv_writer = writer(fp, delimiter="\t")
        for row in rows:
            tsv_writer.writerow(row)
    

if __name__ == '__main__':
    main()
