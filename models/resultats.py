"""Accès aux résultats enregistrés par l’application."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .constantes import DOSSIER_SORTIES


FICHIERS_RESULTATS = {
    "comparatif": "comparatif.csv",
    "panier_totaux": "panier_totaux.csv",
    "historique_black_friday": "historique_black_friday.csv",
    "complexite": "complexite.csv",
    "journal_nettoyage": "journal_nettoyage.csv",
    "synthese": "synthese.csv",
}


def charger_resultats() -> dict[str, list[dict[str, Any]]]:
    """Charge les tableaux disponibles; la lecture des fichiers reste côté modèle."""
    resultats: dict[str, list[dict[str, Any]]] = {}
    for cle, nom_fichier in FICHIERS_RESULTATS.items():
        chemin = DOSSIER_SORTIES / nom_fichier
        if not chemin.is_file():
            continue
        with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
            resultats[cle] = list(csv.DictReader(fichier))
    return resultats


def charger_rapport() -> str | None:
    """Retourne le rapport enregistré, ou None s’il n’existe pas encore."""
    chemin: Path = DOSSIER_SORTIES / "rapport_synthese.md"
    if not chemin.is_file():
        return None
    return chemin.read_text(encoding="utf-8")
