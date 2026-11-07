"""Cas d’usage principal : charge les données et construit tous les résultats."""

from typing import Any

from .analyse import (
    analyser_black_friday,
    calculer_panier,
    construire_comparatif,
    construire_indicateurs_rapport,
    indexer_offres_disponibles,
    mesurer_recherche,
)
from .chargement import (
    charger_baobab,
    charger_comptoir,
    charger_marche,
    lire_catalogue,
    lire_historique,
)


def executer_analyse() -> dict[str, Any]:
    """Exécute le cas d’usage et retourne ses données sans gérer l’affichage."""
    journal: list[dict[str, Any]] = []
    catalogue, _ = lire_catalogue(journal)
    offres: list[dict[str, Any]] = []
    charger_marche(catalogue, offres, journal)
    charger_baobab(catalogue, offres, journal)
    charger_comptoir(catalogue, offres, journal)

    index_offres = indexer_offres_disponibles(offres)
    comparatif, synthese = construire_comparatif(index_offres, catalogue)
    panier_detail, panier_totaux = calculer_panier(index_offres, catalogue)
    historique = lire_historique(journal)
    analyse_historique = analyser_black_friday(historique)
    complexite = mesurer_recherche(historique)
    statistiques_rapport = construire_indicateurs_rapport(
        offres, journal, comparatif, synthese
    )

    return {
        "catalogue": catalogue,
        "offres": offres,
        "journal": journal,
        "comparatif": comparatif,
        "synthese": synthese,
        "panier_detail": panier_detail,
        "panier_totaux": panier_totaux,
        "analyse_historique": analyse_historique,
        "complexite": complexite,
        "statistiques_rapport": statistiques_rapport,
    }
