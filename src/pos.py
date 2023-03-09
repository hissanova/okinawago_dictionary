from typing import NamedTuple, Optional

from conjugations import Conjugation, irregular_verb_conjs, get_conjugations, no_conj_verbs


def is_verb(pos: str) -> bool:
    return any(v_type in pos for v_type in ["自", "他", "動", "接尾=", "接尾･不規則"])


class PartOfSpeech(NamedTuple):
    type: str
    conjugation: Optional[Conjugation] = None
    remark: Optional[str] = None

    def to_dict(self):
        return {
            "type": self.type,
            "conjugation":
            self.conjugation.to_dict() if self.conjugation else None,
            "remark": self.remark
        }


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


def get_pos(pos_notation: str, pronunciation: str) -> PartOfSpeech:
    if is_verb(pos_notation):
        return parse_pos_notation(pronunciation, pos_notation)
    return PartOfSpeech(pos_notation)
