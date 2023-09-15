from typing import Dict, NamedTuple, List

from kanahyouki import generate_phonetics, WordPhonetics


class Stems(NamedTuple):
    語根: str
    基本: str
    連用: str
    音便: str

    def to_dict(self):
        return {"語幹": self.語根, "基本": self.基本, "連用": self.連用, "音便": self.音便}


def _add_kana(conj_dict: Dict[str, str]) -> Dict[str, List[WordPhonetics]]:
    return {
        conj_type:
        [generate_phonetics(p).to_dict() for p in pronunc.split("|")]
        for conj_type, pronunc in conj_dict.items()
    }


class Conjugation(NamedTuple):
    stems: Stems
    基本派生形: Dict[str, str]
    連用派生形: Dict[str, str]
    音便派生形: Dict[str, str]

    def to_dict(self):
        return {
            "stems": self.stems.to_dict(),
            "基本派生形": _add_kana(self.基本派生形),
            "連用派生形": _add_kana(self.連用派生形),
            "音便派生形": _add_kana(self.音便派生形)
        }


kihonkei_suffixes = {"否定形": "aN"}
rennyou_suffixes = {"連用形": "i"}
ombin_suffixes = {"過去形": "aN", "て形": "i", "継続形": "ooN"}


def _concat_suffix(stem: str, suffix: str) -> str:
    if suffix == "i" and stem.endswith("j"):
        return stem[:-1] + suffix
    return stem + suffix


def _make_derivatives(stem: str, suffix_dict: Dict[str,
                                                   str]) -> Dict[str, str]:
    return {
        key: _concat_suffix(stem, suffix)
        for key, suffix in suffix_dict.items()
    }


def _conjugate_from(stems: Stems) -> Conjugation:
    return Conjugation(
        stems,
        _make_derivatives(stems.基本, kihonkei_suffixes),
        _make_derivatives(stems.連用, rennyou_suffixes),
        _make_derivatives(stems.音便, ombin_suffixes),
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
        return _conjugate_from(stems)
    elif conj_num == 3:
        stems = Stems(
            root,
            root + f"({conjs[1][0]})",
            root + ending[0],
            root + conjs[2][:-1],
        )
        return _conjugate_from(stems)
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
        _make_derivatives(stems.音便, ombin_suffixes),
    ),
    "?aN":
    Conjugation(
        stems := Stems("", "?ar", "?aj", "?at"),
        {"否定形": "neeraN"},
        _make_derivatives(stems.連用, rennyou_suffixes),
        _make_derivatives(stems.音便, ombin_suffixes),
    ),
    "neeN":
    Conjugation(
        stems := Stems("", "neeNdar", "neej", "neeNt"),
        _make_derivatives(stems.基本, kihonkei_suffixes),
        {"連用形": "neeN"},
        _make_derivatives(stems.音便, ombin_suffixes),
    ),
    "neeraN":
    Conjugation(
        stems := Stems("", "neeNdar", "neej", "neeNt"),
        _make_derivatives(stems.基本, kihonkei_suffixes),
        {"連用形": "neeN"},
        _make_derivatives(stems.音便, ombin_suffixes),
    ),
    "'uN":
    _conjugate_from(Stems("", "'ur", "'uj", "'ut")),
    "meeN":
    _conjugate_from(Stems("", "moor", "meej", "mooc")),
    "?imeeN":
    _conjugate_from(Stems("", "?imoor", "?imeej", "?imooc")),
    "moo=juN":
    _conjugate_from(Stems("", "moor", "mooj", "mooc")),
    "miSeeN":
    _conjugate_from(Stems("", "misjoor", "miSeej", "misjooc")),
    "-miSe]eN":
    _conjugate_from(Stems("", "-misjoor", "-miSeej", "-misjooc")),
    "-NSe]eN":
    _conjugate_from(Stems("", "-Nsjoor", "-NSeej", "-Nsjooc")),
    "?meNSeeN":
    _conjugate_from(Stems("", "?meNsjoor", "?meNSeej", "?meNsjooc")),
    "?imeNSeeN":
    _conjugate_from(Stems("", "?imeNsjoor", "?imeNSeej", "?imeNsjooc")),
    "meNseeN":
    _conjugate_from(Stems("", "meNsoor", "meNSeej", "meNsooc")),
    "nuuN":
    _conjugate_from(Stems("", "mir", "mij", "'NNc")),
    "'NNzuN":
    _conjugate_from(Stems("", "'NNd", "'NNz", "'NNc")),
    "?icuN":
    _conjugate_from(Stems("", "?ik", "?ic", "?Nz")),
    "kee?icu]N":
    _conjugate_from(Stems("", "kee?ik", "kee?ic", "kee?Nz")),
    "cii?icu]N":
    _conjugate_from(Stems("", "cii?ik", "cii?ic", "cii?Nz")),
    "si=nuN":
    _conjugate_from(Stems("si", "sin", "sin", "siz")),
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
    prefix + "Se]eN": _conjugate_from(
        Stems("", prefix + "sjoor", prefix + "Seej", prefix + "sjooc"))
    for prefix in prefixes
}

irregular_verb_conjs.update(sonkei_verbs)

no_conj_verbs = ["?acizaraN", "dijoori", "SiiraraN", "SiziraraN", "teewa"]
null_conjugation = Conjugation(Stems("", "", "", ""), {}, {}, {})
irregular_verb_conjs.update({v: null_conjugation for v in no_conj_verbs})
