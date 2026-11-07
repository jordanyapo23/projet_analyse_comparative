"""Chemins et réglages partagés par les modules du projet."""
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE / "donnees"
DOSSIER_SORTIES = RACINE / "sorties"
COLONNES_OFFRES = [
    "produit_id", "produit", "enseigne", "reference_source", "designation_source",
    "prix_source_fcfa", "frais_livraison_fcfa", "remise_pct", "prix_paye_fcfa",
    "disponibilite", "disponible", "quantite", "note_clients", "nb_avis",
]
COLONNES_JOURNAL = ["source", "ligne", "niveau", "message"]
ENSEIGNES = ("Marché Lagune", "Baobab Shop", "Comptoir Ivoire")
COLONNES_PRIX = {
    "Marché Lagune": "prix_marche_lagune_fcfa",
    "Baobab Shop": "prix_baobab_shop_fcfa",
    "Comptoir Ivoire": "prix_comptoir_ivoire_fcfa",
}
PANIER = {"P04": 1, "P12": 1, "P14": 2, "P15": 1, "P28": 1}

COLONNES_EXPORT = {
    "offres_normalisees": COLONNES_OFFRES,
    "journal_nettoyage": COLONNES_JOURNAL,
    "comparatif": [
        "produit_id", "produit", "enseignes_disponibles", *COLONNES_PRIX.values(),
        "prix_min_fcfa", "enseignes_les_moins_cheres", "ecart_max_min_fcfa",
        "gain_pct_sur_prix_max",
    ],
    "synthese": ["indicateur", "enseigne", "valeur", "unite"],
    "panier_detail": [
        "enseigne", "produit_id", "produit", "quantite", "prix_unitaire_fcfa",
        "sous_total_fcfa", "disponible",
    ],
    "panier_totaux": [
        "enseigne", "cout_fcfa", "cout_partiel_fcfa", "panier_complet", "produits_absents",
    ],
    "historique_black_friday": [
        "enseigne", "produits_comparables", "prix_moyen_annuel_fcfa",
        "prix_moyen_24_30_nov_2025_fcfa", "variation_black_friday_pct", "lecture", "note",
    ],
    "complexite": [
        "lignes_historique", "cles_indexees", "requetes", "construction_index_s",
        "recherche_lineaire_60_requetes_s", "recherche_indexee_60_requetes_s",
        "gain_vitesse_approx", "complexite",
    ],
}
