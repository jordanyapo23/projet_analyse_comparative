"""Affichage et interaction dans le terminal."""

from decimal import Decimal, InvalidOperation
from typing import Any, Sequence


MENUS = {
    "2": ("comparatif", "Comparatif des prix", [
        ("produit_id", "ID"), ("produit", "Produit"),
        ("enseignes_les_moins_cheres", "Moins cher"),
        ("prix_min_fcfa", "Prix min (FCFA)"),
        ("ecart_max_min_fcfa", "Écart (FCFA)"),
        ("gain_pct_sur_prix_max", "Économie / prix haut (%)"),
    ]),
    "3": ("panier_totaux", "Totaux du panier", [
        ("enseigne", "Enseigne"), ("cout_fcfa", "Total complet (FCFA)"),
        ("cout_partiel_fcfa", "Total partiel"), ("panier_complet", "Complet"),
        ("produits_absents", "Articles absents"),
    ]),
    "4": ("historique_black_friday", "Historique : Black Friday / moyenne annuelle", [
        ("enseigne", "Enseigne"), ("prix_moyen_annuel_fcfa", "Moyenne annuelle"),
        ("prix_moyen_24_30_nov_2025_fcfa", "Semaine BF"),
        ("variation_black_friday_pct", "Variation (%)"), ("lecture", "Conclusion"),
    ]),
    "5": ("complexite", "Mesure de complexité", [
        ("lignes_historique", "Lignes"), ("requetes", "Recherches"),
        ("construction_index_s", "Construction index (s)"),
        ("recherche_lineaire_60_requetes_s", "Balayage (s)"),
        ("recherche_indexee_60_requetes_s", "Index (s)"),
        ("gain_vitesse_approx", "Gain approx."),
    ]),
    "6": ("journal_nettoyage", "Journal de nettoyage", []),
    "7": ("synthese", "Synthèse des comparaisons", [
        ("indicateur", "Indicateur"), ("enseigne", "Enseigne / produit"),
        ("valeur", "Valeur"), ("unite", "Unité"),
    ]),
}


FCFA_COLUMNS = {
    "prix_min_fcfa", "ecart_max_min_fcfa", "cout_fcfa", "cout_partiel_fcfa",
    "prix_moyen_annuel_fcfa", "prix_moyen_24_30_nov_2025_fcfa",
}
PERCENT_COLUMNS = {"gain_pct_sur_prix_max", "variation_black_friday_pct"}
TIME_COLUMNS = {
    "construction_index_s", "recherche_lineaire_60_requetes_s",
    "recherche_indexee_60_requetes_s",
}


def _format_nombre(valeur: str, decimales: int | None = None) -> str:
    try:
        nombre = Decimal(valeur)
    except InvalidOperation:
        return valeur
    if decimales is not None:
        texte = f"{nombre:,.{decimales}f}"
    elif nombre == nombre.to_integral_value():
        texte = f"{int(nombre):,}"
    else:
        texte = f"{nombre:,.2f}"
    return texte.replace(",", " ").replace(".", ",")


def _formater_cellule(cle: str, valeur: str) -> str:
    if valeur == "":
        return "—"
    if cle in {"panier_complet", "disponible"}:
        return "Oui" if valeur.casefold() == "true" else "Non" if valeur.casefold() == "false" else valeur
    if cle in FCFA_COLUMNS or cle == "valeur":
        return _format_nombre(valeur)
    if cle in PERCENT_COLUMNS:
        return _format_nombre(valeur, 2) + " %"
    if cle in TIME_COLUMNS:
        return _format_nombre(valeur, 6) + " s"
    if cle == "gain_vitesse_approx":
        return _format_nombre(valeur, 1) + "×"
    return valeur


def afficher_menu() -> str:
    print("\n=== ANALYSE COMPARATIVE DE MARCHÉ ===")
    print("1. Lancer l’analyse et régénérer les rapports")
    print("2. Consulter le comparatif des prix")
    print("3. Consulter les totaux du panier")
    print("4. Consulter l’analyse Black Friday")
    print("5. Consulter la mesure de complexité")
    print("6. Consulter le journal de nettoyage")
    print("7. Consulter la synthèse des comparaisons")
    print("8. Lire le rapport complet")
    print("0. Quitter")
    return input("\nVotre choix : ").strip()


def afficher_bilan_analyse(
    nombre_produits: int,
    statistiques: dict[str, Any],
    analyse_historique: Sequence[dict[str, Any]],
    dossier_sorties: Any,
) -> None:
    print(f"Catalogue : {nombre_produits} produits")
    print(
        f"Offres chargées : {statistiques['nombre_offres']} "
        f"({statistiques['offres_rapprochees']} rapprochées, "
        f"{statistiques['offres_disponibles']} disponibles)"
    )
    print(
        f"Anomalies et opérations journalisées : {statistiques['nombre_entrees_journal']} "
        f"({statistiques['nombre_alertes']} alertes)"
    )
    print(f"Produits comparables : {statistiques['nombre_produits_comparables']}")
    print("Synthèse Black Friday :")
    for ligne in analyse_historique:
        print(f"  {ligne['enseigne']}: {ligne['variation_black_friday_pct']} % ({ligne['lecture']})")
    print(f"Fichiers créés dans : {dossier_sorties}")


def afficher_message(message: str) -> None:
    print(message)


def _afficher_tableau(titre: str, lignes: Sequence[dict[str, str]], colonnes: list[tuple[str, str]]) -> None:
    print(f"\n=== {titre} ===")
    if not lignes:
        print("Aucune ligne à afficher.")
        return
    largeur_max = 38
    formatees = [
        {cle: _formater_cellule(cle, ligne.get(cle, "")) for cle, _ in colonnes}
        for ligne in lignes
    ]
    largeurs = {
        cle: min(largeur_max, max(len(titre_col), *(len(ligne[cle]) for ligne in formatees)))
        for cle, titre_col in colonnes
    }
    print(" | ".join(titre_col.ljust(largeurs[cle]) for cle, titre_col in colonnes))
    print("-+-".join("-" * largeurs[cle] for cle, _ in colonnes))
    for ligne in formatees:
        cellules = []
        for cle, _ in colonnes:
            valeur = ligne[cle]
            if len(valeur) > largeurs[cle]:
                valeur = valeur[:largeurs[cle] - 1] + "…"
            cellules.append(valeur.ljust(largeurs[cle]))
        print(" | ".join(cellules))


def _afficher_journal(lignes: Sequence[dict[str, str]]) -> None:
    print("\n=== Journal de nettoyage ===")
    if not lignes:
        print("Le journal est vide.")
        return
    for ligne in lignes:
        print(f"[{ligne.get('niveau', '')}] {ligne.get('source', '')}, ligne {ligne.get('ligne', '')}")
        print(f"  {ligne.get('message', '')}")


def _afficher_synthese(lignes: Sequence[dict[str, str]]) -> None:
    print("\n=== Synthèse des comparaisons ===")
    if not lignes:
        print("Aucune synthèse à afficher.")
        return
    for ligne in lignes:
        valeur = _formater_cellule("valeur", ligne.get("valeur", ""))
        print(f"- {ligne.get('indicateur', '')} — {ligne.get('enseigne', '')} : {valeur} {ligne.get('unite', '')}")


def afficher_resultat(
    choix: str,
    resultats: dict[str, list[dict[str, Any]]],
    rapport: str | None,
) -> None:
    if choix == "8":
        if rapport is None:
            print("Le rapport n’existe pas encore. Choisissez d’abord l’option 1.")
            return
        print("\n=== Rapport de synthèse ===\n")
        print(rapport)
        return

    cle, titre, colonnes = MENUS[choix]
    lignes = resultats.get(cle)
    if lignes is None:
        print("Les résultats ne sont pas encore générés. Choisissez d’abord l’option 1.")
        return
    if choix == "6":
        _afficher_journal(lignes)
    elif choix == "7":
        _afficher_synthese(lignes)
    else:
        _afficher_tableau(titre, lignes, colonnes)


def attendre_retour() -> None:
    input("\nAppuyez sur Entrée pour revenir au menu...")
