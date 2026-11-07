"""Normalisation des libellés et rapprochement au catalogue de référence."""
from __future__ import annotations
import re
import unicodedata
from typing import Any

ALIASES: dict[str, tuple[str, ...]] = {
    "P01": ("galaxya15",),
    "P02": ("galaxya25", "samsunga25"),
    "P03": ("galaxya55",),
    "P04": ("spark20",),
    "P05": ("camon30",),
    "P06": ("hot40i",),
    "P07": ("infinixnote40", "note40"),
    "P08": ("itela70",),
    "P09": ("iphone13",),
    "P10": ("redminote13",),
    "P11": ("hp250g9", "laptop250g9", "250g9"),
    "P12": ("lenovoideapad3",),
    "P13": ("dellinspiron15",),
    "P14": ("sandisk",),
    "P15": ("seagate",),
    "P16": ("logitechm185", "m185"),
    "P17": ("deskjet2720e",),
    "P18": ("archerc6",),
    "P19": ("samsung24monitor", "ecransamsung24", "samsung24"),
    "P20": ("hisensefridge", "frigohisense", "refrigerateurhisense"),
    "P21": ("nasco200", "congelateurnasco"),
    "P22": ("samsung43crystal", "samsung43"),
    "P23": ("hisense32",),
    "P24": ("climlg", "lgairconditioner", "climatiseurlg"),
    "P25": ("ventilobinatone", "binatone16"),
    "P26": ("moulinex",),
    "P27": ("philips",),
    "P28": ("microwave", "microondes", "microondesamsung"),
    "P29": ("bouilloire", "electrickettle", "kettle17"),
    "P30": ("hisenseairconditioner15", "climatiseurhisense15", "climhisense15"),
}

def normaliser(texte: Any) -> str:
    """Passe un libellé en minuscules ASCII alphanumériques."""
    texte = "" if texte is None else str(texte)
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(car for car in texte if not unicodedata.combining(car))
    return re.sub(r"[^a-z0-9]", "", texte.casefold())


def rapprocher(designation: Any) -> str | None:
    texte = normaliser(designation)
    candidats: list[tuple[int, str]] = []
    for produit_id, alias_liste in ALIASES.items():
        for alias in alias_liste:
            alias_normalise = normaliser(alias)
            if alias_normalise and alias_normalise in texte:
                candidats.append((len(alias_normalise), produit_id))
    if not candidats:
        return None
    longueur_max = max(longueur for longueur, _ in candidats)
    meilleurs = {produit_id for longueur, produit_id in candidats if longueur == longueur_max}
    return meilleurs.pop() if len(meilleurs) == 1 else None
