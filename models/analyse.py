"""Comparatifs, panier, analyse historique et mesure de complexité."""

from __future__ import annotations

import time
from datetime import date
from typing import Any

from .constantes import COLONNES_PRIX, ENSEIGNES, PANIER


def indexer_offres_disponibles(offres: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Indexe une offre par produit et enseigne pour des recherches directes."""
    index: dict[str, dict[str, dict[str, Any]]] = {}
    for offre in offres:
        if not offre["produit_id"] or not offre["disponible"] or offre["prix_paye_fcfa"] == "":
            continue
        par_enseigne = index.setdefault(offre["produit_id"], {})
        ancienne = par_enseigne.get(offre["enseigne"])
        if ancienne is None or offre["prix_paye_fcfa"] < ancienne["prix_paye_fcfa"]:
            par_enseigne[offre["enseigne"]] = offre
    return index


def construire_comparatif(
    index: dict[str, dict[str, dict[str, Any]]],
    catalogue: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lignes: list[dict[str, Any]] = []
    synthese: list[dict[str, Any]] = []
    ecarts_fcfa: dict[str, list[int]] = {enseigne: [] for enseigne in ENSEIGNES}
    ecarts_pct: dict[str, list[float]] = {enseigne: [] for enseigne in ENSEIGNES}
    victoires = {enseigne: 0 for enseigne in ENSEIGNES}

    for produit_id, par_enseigne in index.items():
        if len(par_enseigne) < 2:
            continue
        prix = {enseigne: offre["prix_paye_fcfa"] for enseigne, offre in par_enseigne.items()}
        minimum, maximum = min(prix.values()), max(prix.values())
        gagnants = [enseigne for enseigne, montant in prix.items() if montant == minimum]
        for gagnant in gagnants:
            victoires[gagnant] += 1
        ligne: dict[str, Any] = {
            "produit_id": produit_id,
            "produit": catalogue.get(produit_id, {}).get("nom", ""),
            "enseignes_disponibles": len(prix),
            "prix_min_fcfa": minimum,
            "enseignes_les_moins_cheres": " / ".join(gagnants),
            "ecart_max_min_fcfa": maximum - minimum,
            "gain_pct_sur_prix_max": round((maximum - minimum) / maximum * 100, 2) if maximum else 0.0,
        }
        for enseigne in ENSEIGNES:
            offre = par_enseigne.get(enseigne)
            ligne[COLONNES_PRIX[enseigne]] = offre["prix_paye_fcfa"] if offre else ""
            if offre:
                ecart = offre["prix_paye_fcfa"] - minimum
                ecarts_fcfa[enseigne].append(ecart)
                ecarts_pct[enseigne].append(ecart / minimum * 100 if minimum else 0.0)
        lignes.append(ligne)

    for enseigne in ENSEIGNES:
        fcfa = ecarts_fcfa[enseigne]
        pct = ecarts_pct[enseigne]
        synthese.extend([
            {
                "indicateur": "Prix le plus bas", "enseigne": enseigne,
                "valeur": victoires[enseigne],
                "unite": "produits (les égalités comptent pour chaque enseigne)",
            },
            {
                "indicateur": "Écart moyen au prix le plus bas", "enseigne": enseigne,
                "valeur": round(sum(fcfa) / len(fcfa), 2) if fcfa else "",
                "unite": "FCFA par produit disponible",
            },
            {
                "indicateur": "Surcoût moyen au prix le plus bas", "enseigne": enseigne,
                "valeur": round(sum(pct) / len(pct), 2) if pct else "",
                "unite": "% du prix le plus bas, sur les produits disponibles",
            },
        ])

    top = sorted(lignes, key=lambda ligne: ligne["ecart_max_min_fcfa"], reverse=True)[:3]
    for rang, ligne in enumerate(top, start=1):
        synthese.append({
            "indicateur": f"Produit avec le plus à gagner #{rang}",
            "enseigne": ligne["produit_id"],
            "valeur": ligne["ecart_max_min_fcfa"],
            "unite": f"FCFA — {ligne['produit']}",
        })
    return lignes, synthese


def construire_indicateurs_rapport(
    offres: list[dict[str, Any]],
    journal: list[dict[str, Any]],
    comparatif: list[dict[str, Any]],
    synthese: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prépare les indicateurs métier nécessaires au rapport de synthèse."""
    valeurs = {
        (ligne["indicateur"], ligne["enseigne"]): ligne["valeur"]
        for ligne in synthese
    }
    resultats_enseignes = {
        enseigne: {
            "victoires": valeurs.get(("Prix le plus bas", enseigne), 0),
            "ecart_moyen": valeurs.get(("Écart moyen au prix le plus bas", enseigne), ""),
            "surcout_moyen": valeurs.get(("Surcoût moyen au prix le plus bas", enseigne), ""),
        }
        for enseigne in ENSEIGNES
    }
    return {
        "nombre_offres": len(offres),
        "nombre_entrees_journal": len(journal),
        "nombre_produits_comparables": len(comparatif),
        "offres_rapprochees": sum(bool(offre["produit_id"]) for offre in offres),
        "offres_disponibles": sum(offre["disponible"] is True for offre in offres),
        "nombre_alertes": sum(entree["niveau"] == "ALERTE" for entree in journal),
        "top_economies": sorted(
            comparatif, key=lambda ligne: ligne["ecart_max_min_fcfa"], reverse=True
        )[:3],
        "resultats_enseignes": resultats_enseignes,
    }


def calculer_panier(
    index: dict[str, dict[str, dict[str, Any]]],
    catalogue: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    details: list[dict[str, Any]] = []
    totaux: list[dict[str, Any]] = []
    total_mixte = 0
    produits_mixte_absents: list[str] = []
    for enseigne in ENSEIGNES:
        sous_total = 0
        absents: list[str] = []
        for produit_id, quantite in PANIER.items():
            offre = index.get(produit_id, {}).get(enseigne)
            prix = offre["prix_paye_fcfa"] if offre else ""
            details.append({
                "enseigne": enseigne, "produit_id": produit_id,
                "produit": catalogue.get(produit_id, {}).get("nom", ""),
                "quantite": quantite, "prix_unitaire_fcfa": prix,
                "sous_total_fcfa": prix * quantite if offre else "",
                "disponible": bool(offre),
            })
            if offre:
                sous_total += prix * quantite
            else:
                absents.append(produit_id)
        totaux.append({
            "enseigne": enseigne,
            "cout_fcfa": sous_total if not absents else "",
            "cout_partiel_fcfa": sous_total,
            "panier_complet": not absents,
            "produits_absents": ", ".join(absents),
        })

    for produit_id, quantite in PANIER.items():
        offres = index.get(produit_id, {})
        if not offres:
            produits_mixte_absents.append(produit_id)
            continue
        meilleure_enseigne, meilleure_offre = min(
            offres.items(), key=lambda element: element[1]["prix_paye_fcfa"]
        )
        total_mixte += meilleure_offre["prix_paye_fcfa"] * quantite
        details.append({
            "enseigne": f"Au moins cher ({meilleure_enseigne})",
            "produit_id": produit_id,
            "produit": catalogue.get(produit_id, {}).get("nom", ""),
            "quantite": quantite,
            "prix_unitaire_fcfa": meilleure_offre["prix_paye_fcfa"],
            "sous_total_fcfa": meilleure_offre["prix_paye_fcfa"] * quantite,
            "disponible": True,
        })
    totaux.append({
        "enseigne": "Panier mixte au moins cher",
        "cout_fcfa": total_mixte if not produits_mixte_absents else "",
        "cout_partiel_fcfa": total_mixte,
        "panier_complet": not produits_mixte_absents,
        "produits_absents": ", ".join(produits_mixte_absents),
    })
    return details, totaux


def analyser_black_friday(historique: list[dict[str, Any]]) -> list[dict[str, Any]]:
    debut = date(2025, 11, 24)
    fin = date(2025, 11, 30)
    par_groupe: dict[tuple[str, str], dict[str, list[int]]] = {}
    for ligne in historique:
        cle = (ligne["source"], ligne["produit_id"])
        groupe = par_groupe.setdefault(cle, {"annee": [], "black_friday": []})
        groupe["annee"].append(ligne["prix_fcfa"])
        if debut <= ligne["date"] <= fin:
            groupe["black_friday"].append(ligne["prix_fcfa"])

    resultat: list[dict[str, Any]] = []
    for enseigne in ENSEIGNES:
        ecarts: list[float] = []
        prix_annuels: list[float] = []
        prix_bf: list[float] = []
        produits_comparables = 0
        for (source, _produit_id), valeurs in par_groupe.items():
            if source != enseigne or not valeurs["black_friday"]:
                continue
            moyenne_annuelle = sum(valeurs["annee"]) / len(valeurs["annee"])
            moyenne_bf = sum(valeurs["black_friday"]) / len(valeurs["black_friday"])
            if moyenne_annuelle:
                ecarts.append((moyenne_bf - moyenne_annuelle) / moyenne_annuelle * 100)
            prix_annuels.append(moyenne_annuelle)
            prix_bf.append(moyenne_bf)
            produits_comparables += 1
        delta = sum(ecarts) / len(ecarts) if ecarts else None
        resultat.append({
            "enseigne": enseigne,
            "produits_comparables": produits_comparables,
            "prix_moyen_annuel_fcfa": round(sum(prix_annuels) / len(prix_annuels), 2) if prix_annuels else "",
            "prix_moyen_24_30_nov_2025_fcfa": round(sum(prix_bf) / len(prix_bf), 2) if prix_bf else "",
            "variation_black_friday_pct": round(delta, 2) if delta is not None else "",
            "lecture": "moins cher que la moyenne annuelle" if delta is not None and delta < 0
                      else "plus cher que la moyenne annuelle" if delta is not None and delta > 0
                      else "au niveau de la moyenne" if delta == 0 else "données insuffisantes",
            "note": "Moyenne calculée par produit puis entre produits; prix catalogue sans remise pour Comptoir Ivoire.",
        })
    return resultat


def mesurer_recherche(historique: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare une recherche par balayage à un dictionnaire indexé."""
    index: dict[tuple[str, str, date], int] = {}
    debut_index = time.perf_counter()
    for ligne in historique:
        index[(ligne["source"], ligne["produit_id"], ligne["date"])] = ligne["prix_fcfa"]
    temps_index = time.perf_counter() - debut_index

    if not historique:
        return {
            "lignes_historique": 0, "cles_indexees": 0, "requetes": 0,
            "construction_index_s": 0, "recherche_lineaire_60_requetes_s": 0,
            "recherche_indexee_60_requetes_s": 0,
            "complexite": "Index: O(n) à construire, recherche moyenne O(1).",
        }

    nombre_requetes = min(60, len(historique))
    pas = max(1, len(historique) // nombre_requetes)
    requetes = [historique[position] for position in range(0, len(historique), pas)][:nombre_requetes]
    cles = [(ligne["source"], ligne["produit_id"], ligne["date"]) for ligne in requetes]
    repetitions = 3

    debut_lineaire = time.perf_counter()
    for _ in range(repetitions):
        for source, produit_id, jour in cles:
            next((ligne["prix_fcfa"] for ligne in historique
                  if ligne["source"] == source and ligne["produit_id"] == produit_id
                  and ligne["date"] == jour), None)
    temps_lineaire = (time.perf_counter() - debut_lineaire) / repetitions

    debut_indexe = time.perf_counter()
    for _ in range(repetitions):
        for cle in cles:
            index.get(cle)
    temps_indexe = (time.perf_counter() - debut_indexe) / repetitions
    return {
        "lignes_historique": len(historique), "cles_indexees": len(index), "requetes": len(cles),
        "construction_index_s": round(temps_index, 6),
        "recherche_lineaire_60_requetes_s": round(temps_lineaire, 6),
        "recherche_indexee_60_requetes_s": round(temps_indexe, 6),
        "gain_vitesse_approx": round(temps_lineaire / temps_indexe, 1) if temps_indexe else "",
        "complexite": "Balayage: O(n) par recherche. Dictionnaire: O(n) à construire puis O(1) en moyenne par recherche.",
    }
