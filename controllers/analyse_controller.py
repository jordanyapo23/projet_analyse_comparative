"""Orchestre le chargement des données et les calculs du projet."""

from models.constantes import COLONNES_EXPORT, DOSSIER_SORTIES, ENSEIGNES
from models.resultats import charger_rapport, charger_resultats
from models.service_analyse import executer_analyse
from views.console_view import (
    MENUS,
    afficher_bilan_analyse,
    afficher_menu,
    afficher_message,
    afficher_resultat,
    attendre_retour,
)
from views.rapport_view import exporter_resultats


def lancer_analyse() -> None:
    donnees = executer_analyse()
    exporter_resultats(donnees, DOSSIER_SORTIES, COLONNES_EXPORT, ENSEIGNES)
    afficher_bilan_analyse(
        len(donnees["catalogue"]),
        donnees["statistiques_rapport"],
        donnees["analyse_historique"],
        DOSSIER_SORTIES,
    )


def lancer_application() -> None:
    """Affiche le menu console et appelle l'action choisie."""
    resultats = charger_resultats()
    rapport = charger_rapport()
    while True:
        try:
            choix = afficher_menu()
        except (EOFError, KeyboardInterrupt):
            afficher_message("\nFin de l’application.")
            return

        if choix == "0":
            afficher_message("Au revoir.")
            return
        if choix == "1":
            lancer_analyse()
            resultats = charger_resultats()
            rapport = charger_rapport()
            attendre_retour()
        elif choix in MENUS or choix == "8":
            afficher_resultat(choix, resultats, rapport)
            attendre_retour()
        else:
            afficher_message("Choix invalide. Sélectionnez une option de 0 à 8.")
