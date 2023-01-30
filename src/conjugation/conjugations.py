from typing import Dict, NamedTuple, List, Optional


class Stems(NamedTuple):
    語根: str
    基本: str
    連用: str
    音便: str

    def to_dict(self):
        return {"語幹": self.語根, "基本": self.基本, "連用": self.連用, "音便": self.音便}


class Conjugation(NamedTuple):
    stems: Stems
    基本派生形: Dict[str, str]
    連用派生形: Dict[str, str]
    音便派生形: Dict[str, str]

    def to_dict(self):
        return {
            "stems": self.stems.to_dict(),
            "基本派生形": self.基本派生形,
            "連用派生形": self.連用派生形,
            "音便派生形": self.音便派生形
        }


class PartOfSpeech(NamedTuple):
    type: str
    conjugation: Optional[Conjugation]
    remark: str

    def to_dict(self):
        return {
            "type": self.type,
            "conjugation":
            self.conjugation.to_dict() if self.conjugation else None,
            "remark": self.remark
        }


kihonkei_suffixes = {"否定形": "aN"}
rennyou_suffixes = {"連用形": "i"}
ombin_suffixes = {"過去形": "aN", "て形": "i", "継続形": "ooN"}


def concat_suffix(stem: str, suffix: str) -> str:
    if suffix == "i" and stem.endswith("j"):
        return stem[:-1] + suffix
    return stem + suffix


def make_derivatives(stem: str, suffix_dict: Dict[str, str]) -> Dict[str, str]:
    return {
        key: concat_suffix(stem, suffix)
        for key, suffix in suffix_dict.items()
    }


def conjugate_from(stems: Stems) -> Conjugation:
    return Conjugation(
        stems,
        make_derivatives(stems.基本, kihonkei_suffixes),
        make_derivatives(stems.連用, rennyou_suffixes),
        make_derivatives(stems.音便, ombin_suffixes),
    )


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
        return conjugate_from(stems)
    elif conj_num == 3:
        stems = Stems(
            root,
            root + f"({conjs[1][0]})",
            root + ending[0],
            root + conjs[2][:-1],
        )
        return conjugate_from(stems)
    else:
        raise ValueError(f"{pronunciation}, {conjs}")


irregular_verb_conjs = {
    "-abijuN":
    Conjugation(
        Stems("", "-abir", "-abij", "-abit|-abiit"),
        {"否定形": "-abiraN"},
        {"連用形": "-abiii"},
        {
            "過去形(単純)": "-abitaN",
            "過去形(継続)": "-abiitaN",
            "て形": "-abiti",
        },
    ),
    "-agijuN":
    Conjugation(
        Stems("", "-agir", "-agij", "-agit|-agiit"),
        {"否定形": "-agiraN"},
        {"連用形": "-agii"},
        {
            "過去形(継続)": "-agiitaN",
            "て形": "-agiti",
            "継続形": "-agitooN"
        },
    ),
    "-juusjuN":
    Conjugation(
        Stems("", "-juus", "-juus", "-juus"),
        {"否定形": "-juusaN"},
        {"連用形": "-juusii"},
        {
            "過去形": "-juusjaN",
            "て形": "-juuQsi",
            "継続形": "-juusjooN"
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
    "?aNsju]N":
    Conjugation(
        Stems("", "?aNs|?aNQs", "?aNs|?aNsj", "?aNsj"),
        {"否定形": "?aNsaN"},
        {"連用形": "?aNsii"},
        {
            "過去形": "?aNsjaN",
            "て形": "?aNQsi",
            "継続形": "?aNsjooN"
        },
    ),
    "kaNsju]N":
    Conjugation(
        Stems("", "kaNs|kaNQs", "kaNs|kaNsj", "kaNsj"),
        {"否定形": "kaNsaN"},
        {"連用形": "kaNsii"},
        {
            "過去形": "kaNsjaN",
            "て形": "kaNQsi",
            "継続形": "kaNsjooN"
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
    "hacicuuN":
    Conjugation(
        Stems("", "hacik", "hacic", "hacic|haciQc"),
        {"否定形": "hacikuuN"},
        {"連用形": "hacicii"},
        {
            "過去形": "hacicaN",
            "て形": "haciQci",
            "継続形": "hacicooN"
        },
    ),
    "keehacicu]uN":
    Conjugation(
        Stems("", "keehacik", "keehacic", "keehacic|keehaciQc"),
        {"否定形": "keehacikuuN"},
        {"連用形": "keehacicii"},
        {
            "過去形": "keehacicaN",
            "て形": "keehaciQci",
            "継続形": "keehacicooN"
        },
    ),
    "?juN":
    Conjugation(
        stems := Stems("", "?j", "?j", "?ic"),
        {"否定形": "?jaN|?iraN"},
        {"連用形": "?ii"},
        make_derivatives(stems.音便, ombin_suffixes),
    ),
    "?aN":
    Conjugation(
        stems := Stems("", "?ar", "?aj", "?at"),
        {"否定形": "neeraN"},
        make_derivatives(stems.連用, rennyou_suffixes),
        make_derivatives(stems.音便, ombin_suffixes),
    ),
    "neeN":
    Conjugation(
        stems := Stems("", "neeNdar", "neej", "neeNt"),
        make_derivatives(stems.基本, kihonkei_suffixes),
        {"連用形": "neeN"},
        make_derivatives(stems.音便, ombin_suffixes),
    ),
    "neeraN":
    Conjugation(
        stems := Stems("", "neeNdar", "neej", "neeNt"),
        make_derivatives(stems.基本, kihonkei_suffixes),
        {"連用形": "neeN"},
        make_derivatives(stems.音便, ombin_suffixes),
    ),
    "'uN":
    conjugate_from(Stems("", "'ur", "'uj", "'ut")),
    "meeN":
    conjugate_from(Stems("", "moor", "meej", "mooc")),
    "?imeeN":
    conjugate_from(Stems("", "?imoor", "?imeej", "?imooc")),
    "moo=juN":
    conjugate_from(Stems("", "moor", "mooj", "mooc")),
    "miSeeN":
    conjugate_from(Stems("", "misjoor", "miSeej", "misjooc")),
    "-miSe]eN":
    conjugate_from(Stems("", "-misjoor", "-miSeej", "-misjooc")),
    "-NSe]eN":
    conjugate_from(Stems("", "-Nsjoor", "-NSeej", "-Nsjooc")),
    "?meNSeeN":
    conjugate_from(Stems("", "?meNsjoor", "?meNSeej", "?meNsjooc")),
    "?imeNSeeN":
    conjugate_from(Stems("", "?imeNsjoor", "?imeNSeej", "?imeNsjooc")),
    "meNseeN":
    conjugate_from(Stems("", "meNsoor", "meNSeej", "meNsooc")),
    "nuuN":
    conjugate_from(Stems("", "mir", "mij", "'NNc")),
    "'NNzuN":
    conjugate_from(Stems("", "'NNd", "'NNz", "'NNc")),
    "?icuN":
    conjugate_from(Stems("", "?ik", "?ic", "?Nz")),
    "kee?icu]N":
    conjugate_from(Stems("", "kee?ik", "kee?ic", "kee?Nz")),
    "cii?icu]N":
    conjugate_from(Stems("", "cii?ik", "cii?ic", "cii?Nz")),
    "si=nuN":
    conjugate_from(Stems("si", "sin", "sin", "siz")),
}

prefixes = [
    "?uceeN",
    "?uceeimi",
    "?ukumuimi",
    "?umikakimi",
    "?uSizirimi",
    "?usoozimi",
    "?utabimi",
    "?waacimi",
    "?weesimi",
    "?wiisimi",
]

sonkei_verbs = {
    prefix + "Se]eN": conjugate_from(
        Stems("", prefix + "sjoor", prefix + "Seej", prefix + "sjooc"))
    for prefix in prefixes
}

irregular_verb_conjs.update(sonkei_verbs)

no_conj_verbs = ["?acizaraN", "dijoori", "SiiraraN", "SiziraraN", "teewa"]
null_conjugation = Conjugation(Stems("", "", "", ""), {}, {}, {})
irregular_verb_conjs.update({v: null_conjugation for v in no_conj_verbs})


def parse_pos_notation(pronunciation: str, pos_notation: str) -> PartOfSpeech:
    if pronunciation in no_conj_verbs:
        return PartOfSpeech(
            pos_notation,
            irregular_verb_conjs[pronunciation],
            "活用なし。",
        )
    remark = ""
    if "/" in pos_notation:
        pos_notation, remark = pos_notation.split("/")
    if any("{}･不規則".format(v_type) in pos_notation
           for v_type in ["自", "他", "接尾"]):
        return PartOfSpeech(
            pos_notation,
            irregular_verb_conjs[pronunciation],
            remark,
        )
    elif pos_notation.startswith("接尾"):
        pos_type, conjs = pos_notation[:2], pos_notation[2:].split(",")
        return PartOfSpeech(
            "接尾動詞",
            get_conjugations(pronunciation, conjs),
            remark,
        )
    elif any(pos_notation.startswith(v_type) for v_type in ["自･他", "他･自"]):
        pos_type, conjs = pos_notation[:3], pos_notation[3:].split(",")
        return PartOfSpeech(
            pos_type,
            get_conjugations(pronunciation, conjs),
            remark,
        )
    elif len(pos_notation) == 1:
        raise NotImplementedError
    else:
        pos_type, conjs = pos_notation[0], pos_notation[1:].split(",")
        return PartOfSpeech(
            pos_type,
            get_conjugations(pronunciation, conjs),
            remark,
        )
