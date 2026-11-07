"""Lecture et nettoyage des fichiers catalogue, enseignes et historique."""
from __future__ import annotations
import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any
from .constantes import COLONNES_JOURNAL, DOSSIER_DONNEES
from .rapprochement import normaliser, rapprocher

def lire_prix(valeur: Any) -> int | None:
    """Convertit un prix français en FCFA; une mention non numérique reste absente."""
    if valeur is None:
        return None
    texte = str(valeur).replace("FCFA", "").replace("XOF", "")
    chiffres = re.sub(r"[^0-9]", "", texte)
    return int(chiffres) if chiffres else None


def journaliser(journal: list[dict[str, Any]], source: str, ligne: Any,
                niveau: str, message: str) -> None:
    journal.append({"source": source, "ligne": ligne, "niveau": niveau, "message": message})


def construire_offre(*, produit_id: str | None, catalogue: dict[str, dict[str, str]],
                     enseigne: str, reference: Any, designation: Any,
                     prix_source: int | None, frais: int = 0, remise: Decimal = Decimal(0),
                     disponibilite: str = "", disponible: bool = False, quantite: Any = "",
                     note: Any = "", avis: Any = "") -> dict[str, Any]:
    prix_paye = None
    if prix_source is not None:
        prix_paye = int((Decimal(prix_source + frais) * (Decimal(100) - remise) / Decimal(100))
                        .quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    produit = catalogue.get(produit_id, {}).get("nom", "") if produit_id else ""
    return {
        "produit_id": produit_id or "", "produit": produit, "enseigne": enseigne,
        "reference_source": reference or "", "designation_source": designation or "",
        "prix_source_fcfa": prix_source if prix_source is not None else "",
        "frais_livraison_fcfa": frais, "remise_pct": str(remise),
        "prix_paye_fcfa": prix_paye if prix_paye is not None else "",
        "disponibilite": disponibilite, "disponible": disponible,
        "quantite": quantite if quantite is not None else "",
        "note_clients": note if note is not None else "", "nb_avis": avis if avis is not None else "",
    }


def lire_catalogue(journal: list[dict[str, Any]]) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    chemin = DOSSIER_DONNEES / "catalogue_reference.csv"
    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        lignes = list(csv.DictReader(fichier))
    par_id = {ligne["produit_id"]: ligne for ligne in lignes}
    par_nom = {normaliser(ligne["nom"]): ligne["produit_id"] for ligne in lignes}
    if len(par_id) != len(lignes):
        journaliser(journal, chemin.name, "", "ERREUR", "Identifiants produit dupliqués dans le catalogue.")
    return par_id, par_nom


def charger_marche(catalogue: dict[str, dict[str, str]], offres: list[dict[str, Any]],
                   journal: list[dict[str, Any]]) -> None:
    chemin = DOSSIER_DONNEES / "marche_lagune.csv"
    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    deja_vus: dict[str, tuple[Any, ...]] = {}
    for numero, ligne in enumerate(lignes, start=2):
        signature = tuple(ligne.get(c, "") for c in ligne)
        reference = ligne.get("reference", "")
        if reference in deja_vus and deja_vus[reference] == signature:
            journaliser(journal, chemin.name, numero, "INFO", f"Doublon identique ignoré ({reference}).")
            continue
        if reference in deja_vus:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Référence dupliquée avec contenu différent ({reference}).")
        else:
            deja_vus[reference] = signature

        designation = ligne.get("designation", "")
        produit_id = rapprocher(designation)
        prix = lire_prix(ligne.get("prix"))
        disponibilite = (ligne.get("disponibilite") or "").strip()
        if produit_id is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Désignation non rapprochée ou ambiguë : {designation!r}.")
        if prix is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Prix absent ou inexploitable : {ligne.get('prix')!r}.")
        ancien = lire_prix(ligne.get("ancien_prix"))
        if prix is not None and ancien is not None and prix > ancien * 2:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Prix affiché ({prix}) très supérieur à l'ancien prix ({ancien}); valeur source conservée.")
        stock_ok = disponibilite.casefold() != "rupture"
        offres.append(construire_offre(
            produit_id=produit_id, catalogue=catalogue, enseigne="Marché Lagune",
            reference=reference, designation=designation, prix_source=prix,
            disponibilite=disponibilite, disponible=stock_ok and prix is not None,
            note=(ligne.get("note_clients") or "").replace(",", "."), avis=ligne.get("nb_avis", ""),
        ))
        if disponibilite.casefold() == "rupture":
            journaliser(journal, chemin.name, numero, "INFO", "Offre en rupture exclue des comparaisons de prix.")


def charger_baobab(catalogue: dict[str, dict[str, str]], offres: list[dict[str, Any]],
                   journal: list[dict[str, Any]]) -> None:
    chemin = DOSSIER_DONNEES / "baobab_shop.json"
    with chemin.open("r", encoding="utf-8-sig") as fichier:
        donnees = json.load(fichier)
    for numero, article in enumerate(donnees.get("items", []), start=1):
        designation = article.get("title", "")
        produit_id = rapprocher(designation)
        pricing = article.get("pricing") or {}
        prix = lire_prix(pricing.get("amount"))
        frais = lire_prix(pricing.get("delivery_fee")) or 0
        stock = int(article.get("stock") or 0)
        devise = pricing.get("currency", "")
        if devise != "XOF":
            journaliser(journal, chemin.name, numero, "ALERTE", f"Devise inattendue : {devise!r}.")
        if produit_id is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Désignation non rapprochée ou ambiguë : {designation!r}.")
        if prix is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Prix absent ou inexploitable pour {designation!r}.")
        offres.append(construire_offre(
            produit_id=produit_id, catalogue=catalogue, enseigne="Baobab Shop",
            reference=article.get("sku", ""), designation=designation, prix_source=prix,
            frais=frais, disponibilite=f"Stock : {stock}", disponible=stock > 0 and prix is not None,
            quantite=stock, note=(article.get("rating") or {}).get("average", ""),
            avis=(article.get("rating") or {}).get("count", ""),
        ))
        if stock == 0:
            journaliser(journal, chemin.name, numero, "INFO", f"Stock nul : {designation!r}, offre exclue du moins cher.")


def indice_colonne(reference: str) -> int:
    """Convertit une référence XLSX telle que C12 en indice de colonne zéro-based."""
    lettres = re.match(r"[A-Z]+", reference.upper())
    if not lettres:
        raise ValueError(f"Référence de cellule XLSX invalide : {reference!r}")
    indice = 0
    for lettre in lettres.group(0):
        indice = indice * 26 + ord(lettre) - ord("A") + 1
    return indice - 1


def lire_valeur_cellule(cellule: ET.Element, chaines_partagees: list[str]) -> Any:
    espace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    type_cellule = cellule.attrib.get("t", "")
    if type_cellule == "inlineStr":
        noeud = cellule.find(f"{espace}is")
        return "".join(part.text or "" for part in noeud.iter(f"{espace}t")) if noeud is not None else ""
    valeur = cellule.find(f"{espace}v")
    if valeur is None or valeur.text is None:
        return None
    if type_cellule == "s":
        return chaines_partagees[int(valeur.text)]
    if type_cellule == "b":
        return valeur.text == "1"
    if type_cellule == "str":
        return valeur.text
    try:
        nombre = float(valeur.text)
        return int(nombre) if nombre.is_integer() else nombre
    except ValueError:
        return valeur.text


def lire_feuille_xlsx(chemin: Path, nom_feuille: str) -> dict[int, list[Any]]:
    """Lit les cellules utiles d'une feuille XLSX sans bibliothèque externe."""
    espace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    espace_rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    espace_pkg = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    with zipfile.ZipFile(chemin) as classeur:
        racine_livre = ET.fromstring(classeur.read("xl/workbook.xml"))
        feuilles = racine_livre.find(f"{espace}sheets")
        feuille_voulue = next((feuille for feuille in (list(feuilles) if feuilles is not None else [])
                               if feuille.attrib.get("name") == nom_feuille), None)
        if feuille_voulue is None:
            raise ValueError(f"Feuille {nom_feuille!r} absente du classeur.")
        identifiant_rel = feuille_voulue.attrib[f"{espace_rel}id"]
        relations = ET.fromstring(classeur.read("xl/_rels/workbook.xml.rels"))
        relation = next(rel for rel in relations.findall(f"{espace_pkg}Relationship")
                        if rel.attrib.get("Id") == identifiant_rel)
        cible = relation.attrib["Target"].lstrip("/")
        chemin_feuille = cible if cible.startswith("xl/") else f"xl/{cible}"

        chaines_partagees: list[str] = []
        if "xl/sharedStrings.xml" in classeur.namelist():
            racine_chaines = ET.fromstring(classeur.read("xl/sharedStrings.xml"))
            chaines_partagees = [
                "".join(part.text or "" for part in item.iter(f"{espace}t"))
                for item in racine_chaines.findall(f"{espace}si")
            ]

        racine_feuille = ET.fromstring(classeur.read(chemin_feuille))
        donnees = racine_feuille.find(f"{espace}sheetData")
        resultat: dict[int, list[Any]] = {}
        for ligne in (list(donnees) if donnees is not None else []):
            numero = int(ligne.attrib["r"])
            cellules: list[Any] = []
            for cellule in ligne.findall(f"{espace}c"):
                colonne = indice_colonne(cellule.attrib["r"])
                while len(cellules) <= colonne:
                    cellules.append(None)
                cellules[colonne] = lire_valeur_cellule(cellule, chaines_partagees)
            resultat[numero] = cellules
        return resultat


def charger_comptoir(catalogue: dict[str, dict[str, str]], offres: list[dict[str, Any]],
                   journal: list[dict[str, Any]]) -> None:
    chemin = DOSSIER_DONNEES / "comptoir_ivoire.xlsx"
    try:
        feuille = lire_feuille_xlsx(chemin, "Tarifs octobre 2026")
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as erreur:
        journaliser(journal, chemin.name, "", "ERREUR", f"Lecture du classeur impossible : {erreur}")
        return
    entetes = feuille.get(3, [])
    index = {str(nom).strip(): position for position, nom in enumerate(entetes) if nom is not None}
    requis = ["Code", "Article", "Prix catalogue (FCFA)", "Remise (%)", "Quantité en rayon"]
    absents = [nom for nom in requis if nom not in index]
    if absents:
        journaliser(journal, chemin.name, 3, "ERREUR", f"Colonnes manquantes : {', '.join(absents)}.")
        return
    for numero, cellules in feuille.items():
        if numero < 4 or not any(valeur is not None for valeur in cellules):
            continue
        valeur = lambda nom: cellules[index[nom]] if index[nom] < len(cellules) else None
        designation = valeur("Article")
        produit_id = rapprocher(designation)
        prix = lire_prix(valeur("Prix catalogue (FCFA)"))
        try:
            remise = Decimal(str(valeur("Remise (%)") or 0))
            quantite = int(valeur("Quantité en rayon") or 0)
        except (InvalidOperation, ValueError, TypeError):
            journaliser(journal, chemin.name, numero, "ALERTE", f"Remise ou quantité invalide pour {designation!r}.")
            remise, quantite = Decimal(0), 0
        if produit_id is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Désignation non rapprochée ou ambiguë : {designation!r}.")
        if prix is None:
            journaliser(journal, chemin.name, numero, "ALERTE", f"Prix catalogue absent ou illisible : {designation!r}.")
        offres.append(construire_offre(
            produit_id=produit_id, catalogue=catalogue, enseigne="Comptoir Ivoire",
            reference=valeur("Code"), designation=designation, prix_source=prix,
            remise=remise, disponibilite="En rayon" if quantite > 0 else "Rupture",
            disponible=quantite > 0 and prix is not None, quantite=quantite,
        ))
        if quantite == 0:
            journaliser(journal, chemin.name, numero, "INFO", f"Quantité nulle : {designation!r}, offre exclue du moins cher.")


def lire_historique(journal: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chemin = DOSSIER_DONNEES / "historique_prix.csv"
    lignes: list[dict[str, Any]] = []
    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        for numero, ligne in enumerate(csv.DictReader(fichier), start=2):
            try:
                lignes.append({
                    "date": date.fromisoformat(ligne["date"]),
                    "source": ligne["source"],
                    "produit_id": ligne["produit_id"],
                    "prix_fcfa": int(ligne["prix_fcfa"]),
                })
            except (KeyError, TypeError, ValueError):
                journaliser(journal, chemin.name, numero, "ALERTE", f"Ligne d'historique ignorée : {ligne!r}.")
    return lignes
