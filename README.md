# projet_analyse_comparative
## Analyse comparative de marché

Application console qui rapproche les prix de trois enseignes au catalogue commun et produit les comparatifs, le calcul du panier et une analyse de l'historique. Elle utilise seulement la bibliothèque standard de Python, y compris pour lire le fichier Excel.

## Organisation du code

Le projet suit une architecture MVC adaptée à une application console : `main.py` lance le contrôleur; les modèles chargent et calculent les données; les vues gèrent les entrées, affichent les résultats et produisent les exports.

| Fichier | Rôle |
|---|---|
| `main.py` | Point d’entrée du programme |
| `controllers/analyse_controller.py` | Coordination des opérations entre modèles et vues |
| `models/constantes.py` | Chemins, enseignes, colonnes et contenu du panier |
| `models/rapprochement.py` | Normalisation des libellés et alias vers les identifiants produits |
| `models/chargement.py` | Lecture des CSV, du JSON, du classeur Excel et nettoyage |
| `models/analyse.py` | Comparatif, synthèse, panier, historique et mesure de complexité |
| `models/service_analyse.py` | Exécution complète du cas d’usage et assemblage des résultats |
| `models/resultats.py` | Lecture des résultats générés pour les rendre consultables |
| `views/console_view.py` | Menu, saisie et affichage des résultats dans le terminal |
| `views/rapport_view.py` | Présentation et export des tableaux CSV et du rapport commenté |
| `donnees/` | Fichiers fournis pour l’exercice |
| `sorties/` | Résultats produits par l’analyse |

## Utiliser l’application dans VS Code

Dans le terminal intégré, créez l’environnement virtuel et lancez l’application :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python main.py
```

Le menu permet de lancer l’analyse et de consulter le comparatif, le panier, l’historique Black Friday, la mesure de complexité, le journal, la synthèse ou le rapport complet. Vous pouvez aussi appuyer sur F5 après avoir créé `.venv`.

## Fichiers créés dans `sorties/`

- `offres_normalisees.csv` : offres rapprochées et prix réellement payés.
- `journal_nettoyage.csv` : doublons ignorés, prix manquants, prix suspects, ruptures et autres problèmes détectés.
- `comparatif.csv` : prix par enseigne, enseigne la moins chère et économies possibles.
- `synthese.csv` : nombre de produits remportés, écart moyen par rapport au prix le plus bas et trois meilleures économies.
- `panier_detail.csv` et `panier_totaux.csv` : détail et total complet ou partiel du panier dans chaque enseigne et en achat mixte.
- `historique_black_friday.csv` : comparaison du 24 au 30 novembre 2025 à la moyenne annuelle.
- `complexite.csv` : temps mesurés pour rechercher des prix par balayage et par dictionnaire indexé.
- `rapport_synthese.md` : lecture commentée des résultats, limites et principaux constats.

Les offres en rupture, sans stock ou sans prix exploitable sont exclues du choix de l’enseigne la moins chère. Le prix payé au Comptoir Ivoire tient compte de la remise; son historique conserve le prix catalogue, comme l’indiquent les consignes.

## Calcul du pourcentage d’économie

Dans `comparatif.csv`, le pourcentage est calculé ainsi : `(prix le plus élevé - prix le plus bas) / prix le plus élevé × 100`. Il indique la part du prix le plus élevé économisée en choisissant l’offre la moins chère.

