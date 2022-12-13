from typing import Dict, NamedTuple, List


class Stems(NamedTuple):
    語根: str
    基本: str
    連用: str
    音便: str


class Conjugation(NamedTuple):
    stems: Stems
    基本派生形: Dict[str, str]
    連用派生形: Dict[str, str]
    音便派生形: Dict[str, str]


kihonkei_suffixes = {"否定形": "aN"}
rennyou_suffixes = {"連用形": "i"}
ombin_suffixes = {"過去形": "aN", "て形": "i", "継続形": "ooN"}


def make_derivatives(stem: str, suffix_dict: Dict[str, str]) -> Dict[str, str]:
    return {key: stem + suffix for key, suffix in suffix_dict.items()}


class PartOfSpeech(NamedTuple):
    type: str
    conjugation: Conjugation
    remark: str


def get_conjugations(pronunciation: str, conjs: List[str]) -> Conjugation:
    conjs = [e.strip("=") for e in conjs]
    pronunc = pronunciation.replace("]", "")
    root, ending = pronunc.split("=")
    conj_num = len(conjs)
    if conj_num == 1:
        return Conjugation(Stems(root, "", "", ""), {}, {}, {})
    elif conj_num == 2:
        stems = Stems(
            root,
            root + conjs[0][0],
            root + ending[0],
            root + conjs[1][:-1],
        )
        return Conjugation(
            stems,
            make_derivatives(stems.基本, kihonkei_suffixes),
            make_derivatives(stems.連用, rennyou_suffixes),
            make_derivatives(stems.音便, ombin_suffixes),
        )
    elif conj_num == 3:
        stems = Stems(
            root,
            root + f"({conjs[1][0]})",
            root + ending[0],
            root + conjs[2][:-1],
        )
        return Conjugation(
            stems,
            make_derivatives(stems.基本, kihonkei_suffixes),
            make_derivatives(stems.連用, rennyou_suffixes),
            make_derivatives(stems.音便, ombin_suffixes),
        )
    else:
        raise ValueError(f"{pronunciation}, {conjs}")


irregular_verb_conjs = {
    "?aN":
    Conjugation(
        Stems("", "?ar", "?aj", "?at"),
        {"否定形": "neeraN"},
        {"連用形": "?ai"},
        {
            "過去形": "?ataN",
            "て形": "?ati",
            "継続形": "?atooN"
        },
    ),
    "'uN":
    Conjugation(
        Stems("", "'ur", "'uj", "'ut"),
        {"否定形": "'uraN"},
        {"連用形": "'ui"},
        {
            "過去形": "'utaN",
            "て形": "'uti",
            "継続形": "'utooN"
        },
    ),
    "meeN":
    Conjugation(
        Stems("", "moor", "meej", "mooc"),
        {"否定形": "mooraN"},
        {"連用形": "meei"},
        {
            "過去形": "moocaN",
            "て形": "mooci",
            "継続形": "moocooN"
        },
    ),
    "moo=juN":
    Conjugation(
        Stems("", "moor", "mooj", "mooc"),
        {"否定形": "mooraN"},
        {"連用形": "mooi"},
        {
            "過去形": "moocaN",
            "て形": "mooci",
            "継続形": "moocooN"
        },
    ),
    "miSeeN":
    Conjugation(
        Stems("", "misjoor", "miSeej", "misjooc"),
        {"否定形": "misjooraN"},
        {"連用形": "miSeei"},
        {
            "過去形": "misjoocaN",
            "て形": "misjooci",
            "継続形": "misjoocooN"
        },
    ),
    "neeN":
    Conjugation(
        Stems("", "neeNdar", "neej", "neeNt"),
        {"否定形": "neeNdaraN"},
        {"連用形": "neeN"},
        {
            "過去形": "neeNtaN",
            "て形": "neeNti",
            "継続形": "neeNtooN"
        },
    ),
    "neeraN":
    Conjugation(
        Stems("", "neeNdar", "neej", "neeNt"),
        {"否定形": "neeNdaraN"},
        {"連用形": "neeN"},
        {
            "過去形": "neeNtaN",
            "て形": "neeNti",
            "継続形": "neeNtooN"
        },
    ),
    "nuuN":
    Conjugation(
        Stems("", "mir", "mij", "'NNc"),
        {"否定形": "miraN"},
        {"連用形": "mii"},
        {
            "過去形": "'NNcaN",
            "て形": "'NNci",
            "継続形": "'NNcooN"
        },
    ),
    "'NNzuN":
    Conjugation(
        Stems("", "'NNd", "'NNz", "'NNc"),
        {"否定形": "'NNdaN"},
        {"連用形": "'NNzi"},
        {
            "過去形": "'NNcaN",
            "て形": "'NNci",
            "継続形": "'NNcooN"
        },
    ),
    "?meNSeeN":
    Conjugation(
        Stems("", "?meNsjoor", "?meNSeej", "?meNsjooc"),
        {"否定形": "?meNsjooraN"},
        {"連用形": "?meNSeei"},
        {
            "過去形": "?meNsjoocaN",
            "て形": "?meNsjooci",
            "継続形": "?meNsjoocooN"
        },
    ),
    "meNseeN":
    Conjugation(
        Stems("", "meNsoor", "meNSeej", "meNsooc"),
        {"否定形": "meNsooraN"},
        {"連用形": "meNSeei"},
        {
            "過去形": "meNsoocaN",
            "て形": "meNsooci",
            "継続形": "meNsoocooN"
        },
    ),
    "sjuN":
    Conjugation(
        Stems("", "s|Qs", "s|sj", "sj"),
        {"否定形": "saN"},
        {"連用形": "sii"},
        {
            "過去形": "sjaN",
            "て形": "Qsi",
            "継続形": "sjooN"
        },
    ),
    "cuuN":
    Conjugation(
        Stems("", "k", "c", "c|Qc"),
        {"否定形": "kuuN"},
        {"連用形": "cii"},
        {
            "過去形": "caN",
            "て形": "Qci",
            "継続形": "cooN"
        },
    ),
    "?icuN":
    Conjugation(
        Stems("", "?ik", "?ic", "?Nz"),
        {"否定形": "?ikaN"},
        {"連用形": "?ici"},
        {
            "過去形": "?NzaN",
            "て形": "?Nzi",
            "継続形": "?NzooN"
        },
    ),
    "cii?icu]N":
    Conjugation(
        Stems("", "cii?ik", "cii?ic", "cii?Nz"),
        {"否定形": "cii?ikaN"},
        {"連用形": "cii?ici"},
        {
            "過去形": "cii?NzaN",
            "て形": "cii?Nzi",
            "継続形": "cii?NzooN"
        },
    ),
    "?juN":
    Conjugation(
        Stems("", "?j", "?j", "?ic"),
        {"否定形": "?jaN|?iraN"},
        {"連用形": "?ii"},
        {
            "過去形": "?icaN",
            "て形": "?ici",
            "継続形": "?icooN"
        },
    ),
    "si=nuN":
    Conjugation(
        Stems("si", "sin", "sin", "siz"),
        {"否定形": "sinaN"},
        {"連用形": "sini"},
        {
            "過去形": "sizaN",
            "て形": "sizi",
            "継続形": "sizooN"
        },
    ),
}


def parse_pos_notation(pronunciation: str, notation: str) -> PartOfSpeech:
    remark = ""
    if "/" in notation:
        notation, remark = notation.split("/")
    if notation.startswith("自･不規則"):
        return PartOfSpeech(
            "自･不規則",
            irregular_verb_conjs.get(
                pronunciation,
                Conjugation(Stems(pronunciation, "", "", ""), {}, {}, {})),
            remark,
        )
    elif notation.startswith("他･不規則"):
        return PartOfSpeech(
            "他･不規則",
            irregular_verb_conjs.get(
                pronunciation,
                Conjugation(Stems(pronunciation, "", "", ""), {}, {}, {})),
            remark,
        )
    elif notation.startswith("自･他") or notation.startswith("他･自"):
        pos_type, conjs = notation[2], notation[3:].split(",")
        return PartOfSpeech(
            pos_type,
            get_conjugations(pronunciation, conjs),
            remark,
        )
    elif len(notation) == 1:
        return PartOfSpeech(
            notation,
            Conjugation(Stems(pronunciation, "", "", ""), {}, {}, {}),
            remark,
        )
    else:
        pos_type, conjs = notation[0], notation[1:].split(",")
        return PartOfSpeech(
            pos_type,
            get_conjugations(pronunciation, conjs),
            remark,
        )
