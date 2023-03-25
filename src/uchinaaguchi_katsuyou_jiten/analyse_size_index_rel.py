from pprint import pprint
from csv import DictReader

texts = []
with open("./extracted_text.tsv") as tsv_fp:
    tsv_reader = DictReader(tsv_fp, delimiter='\t')
    for row in tsv_reader:
        texts.append(row)

group1 = list(filter(lambda e: float(e['Height']) < 11, texts))
group2 = list(filter(lambda e: 11 <= float(e['Height']) <12, texts))
group3 = list(filter(lambda e: 12 <= float(e['Height']), texts))

pprint(group1[:5])
pprint(group2)
pprint(group3[:5])

print(any("〈" in row["Text"] for row in group1))
print(any("〈" in row["Text"] for row in group2))
print(all("〈" in row["Text"] for row in group3))


exceptions1 = list(filter(lambda row: "〈" in row["Text"], group1))
exceptions2 = list(filter(lambda row: "〈" not in row["Text"], group3))

print(len(exceptions1))
print(len(exceptions2))

pprint(exceptions1[:5])
pprint(exceptions2[:5])
