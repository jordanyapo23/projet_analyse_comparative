"""Mise en forme et export des tableaux et du rapport de synthèse."""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence


NOMS_FICHIERS = {
    "offres": "offres_normalisees.csv",
    "journal": "journal_nettoyage.csv",
    "comparatif": "comparatif.csv",
    "synthese": "synthese.csv",
    "panier_detail": "panier_detail.csv",
    "panier_totaux": "panier_totaux.csv",
    "analyse_historique": "historique_black_friday.csv",
    "complexite": "complexite.csv",
}


def exporter_csv(chemin: Path, lignes: list[dict[str, Any]], colonnes: list[str]) -> None:
    with chemin.open("w", encoding="utf-8-sig", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes, extrasaction="ignore")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def exporter_resultats(
    resultats: dict[str, Any],
    dossier_sorties: Path,
    colonnes_export: dict[str, list[str]],
    enseignes: Sequence[str],
) -> None:
    """Écrit les fichiers de sortie; le contrôleur fournit les chemins et schémas."""
    dossier_sorties.mkdir(exist_ok=True)
    for cle, nom_fichier in NOMS_FICHIERS.items():
        lignes = resultats[cle]
        if cle == "complexite":
            lignes = [lignes]
        exporter_csv(dossier_sorties / nom_fichier, lignes, colonnes_export[nom_fichier[:-4]])

    ecrire_rapport(
        resultats["statistiques_rapport"],
        resultats["panier_totaux"],
        resultats["analyse_historique"],
        resultats["complexite"],
        enseignes,
        dossier_sorties / "rapport_synthese.md",
    )


def ecrire_rapport(
    statistiques: dict[str, Any],
    panier_totaux: list[dict[str, Any]],
    analyse_historique: list[dict[str, Any]],
    complexite: dict[str, Any],
    enseignes: Sequence[str],
    chemin_sortie: Path,
) -> None:
    """Formate les données déjà calculées par le modèle en rapport Markdown."""
    def fcfa(valeur: Any) -> str:
        if valeur == "" or valeur is None:
            return "—"
        montant = Decimal(str(valeur))
        if montant == montant.to_integral_value():
            affiche = f"{int(montant):,}".replace(",", " ")
        else:
            affiche = f"{montant:,.2f}".replace(",", " ").replace(".", ",")
        return affiche + " FCFA"

    def nombre_fr(valeur: Any, decimales: int = 2) -> str:
        return f"{float(valeur):,.{decimales}f}".replace(",", " ").replace(".", ",")

    def secondes(valeur: Any) -> str:
        return f"{float(valeur):.6f}".replace(".", ",")

    nombre_lignes_historique = f"{int(complexite.get('lignes_historique', 0)):,}".replace(",", " ")
    lignes_rapport = [
        "# Synthèse de l’analyse comparative",
        "",
        "Les données de l’exercice sont fictives. Les offres en rupture, sans stock ou sans prix exploitable sont exclues du choix de l’enseigne la moins chère.",
        "",
        "## Couverture et qualité des données",
        "",
        f"Le programme a rapproché **{statistiques['offres_rapprochees']} offres sur {statistiques['nombre_offres']}** du catalogue, dont **{statistiques['offres_disponibles']} disponibles**. Le comparatif couvre **{statistiques['nombre_produits_comparables']} produits** disponibles dans au moins deux enseignes. Le journal contient **{statistiques['nombre_entrees_journal']} entrées**, dont **{statistiques['nombre_alertes']} alertes**.",
        "",
        "Le prix de **779 000 FCFA** affiché par Marché Lagune pour le Tecno Spark 20 est très supérieur à son ancien prix de 88 700 FCFA. La valeur source a été conservée et signalée; les comparaisons qui la concernent sont à lire avec prudence.",
        "",
        "## Résultats par enseigne",
        "",
        "| Enseigne | Produits au prix le plus bas | Écart moyen au prix le plus bas | Surcoût moyen |",
        "|---|---:|---:|---:|",
    ]
    for enseigne in enseignes:
        resultats_enseigne = statistiques["resultats_enseignes"][enseigne]
        ecart = fcfa(resultats_enseigne["ecart_moyen"])
        pct = resultats_enseigne["surcout_moyen"]
        pct_affiche = f"{nombre_fr(pct)} %" if pct != "" else "—"
        lignes_rapport.append(
            f"| {enseigne} | {resultats_enseigne['victoires']} | {ecart} | {pct_affiche} |"
        )

    lignes_rapport.extend([
        "",
        "Les égalités sont comptées pour chaque enseigne gagnante; le total des victoires peut donc dépasser le nombre de produits comparés. L’écart moyen est calculé uniquement sur les produits disponibles chez l’enseigne concernée.",
        "",
        "### Trois produits où comparer rapporte le plus",
        "",
        "| Produit | Écart entre le prix le plus bas et le plus haut |",
        "|---|---:|",
    ])
    for ligne in statistiques["top_economies"]:
        lignes_rapport.append(f"| {ligne['produit']} | {fcfa(ligne['ecart_max_min_fcfa'])} |")

    lignes_rapport.extend([
        "",
        "## Panier de rentrée",
        "",
        "| Option | Total | Panier complet | Articles absents |",
        "|---|---:|:---:|---|",
    ])
    for ligne in panier_totaux:
        lignes_rapport.append(
            f"| {ligne['enseigne']} | {fcfa(ligne['cout_fcfa']) if ligne['panier_complet'] else 'indisponible'} | "
            f"{'oui' if ligne['panier_complet'] else 'non'} | {ligne['produits_absents'] or '—'} |"
        )

    lignes_rapport.extend([
        "",
        "## Semaine du Black Friday",
        "",
        "Les moyennes annuelles et celles du 24 au 30 novembre 2025 sont calculées par produit, puis moyennées entre produits. L’historique du Comptoir Ivoire contient le prix catalogue, sans remise.",
        "",
        "| Enseigne | Moyenne annuelle | Moyenne du 24 au 30 novembre | Variation | Lecture |",
        "|---|---:|---:|---:|---|",
    ])
    for ligne in analyse_historique:
        lignes_rapport.append(
            f"| {ligne['enseigne']} | {fcfa(ligne['prix_moyen_annuel_fcfa'])} | "
            f"{fcfa(ligne['prix_moyen_24_30_nov_2025_fcfa'])} | "
            f"{nombre_fr(ligne['variation_black_friday_pct'])} % | {ligne['lecture']} |"
        )

    lignes_rapport.extend([
        "",
        "## Temps de recherche et complexité",
        "",
        f"L’historique contient **{nombre_lignes_historique} lignes**. Pour {complexite.get('requetes', 0)} recherches, un balayage séquentiel a pris en moyenne **{secondes(complexite.get('recherche_lineaire_60_requetes_s', 0))} s**; le dictionnaire indexé a pris **{secondes(complexite.get('recherche_indexee_60_requetes_s', 0))} s**, après **{secondes(complexite.get('construction_index_s', 0))} s** de construction de l’index.",
        "",
        "Le balayage coûte O(n) par recherche. Le dictionnaire demande O(n) à construire, puis O(1) en moyenne par recherche grâce à une clé composée de l’enseigne, du produit et de la date. Les temps sont ceux de cette exécution et peuvent varier selon l’ordinateur.",
        "",
    ])
    chemin_sortie.write_text("\n".join(lignes_rapport), encoding="utf-8")
