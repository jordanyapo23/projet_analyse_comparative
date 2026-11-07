# Synthèse de l’analyse comparative

Les données de l’exercice sont fictives. Les offres en rupture, sans stock ou sans prix exploitable sont exclues du choix de l’enseigne la moins chère.

## Couverture et qualité des données

Le programme a rapproché **76 offres sur 76** du catalogue, dont **63 disponibles**. Le comparatif couvre **23 produits** disponibles dans au moins deux enseignes. Le journal contient **17 entrées**, dont **4 alertes**.

Le prix de **779 000 FCFA** affiché par Marché Lagune pour le Tecno Spark 20 est très supérieur à son ancien prix de 88 700 FCFA. La valeur source a été conservée et signalée; les comparaisons qui la concernent sont à lire avec prudence.

## Résultats par enseigne

| Enseigne | Produits au prix le plus bas | Écart moyen au prix le plus bas | Surcoût moyen |
|---|---:|---:|---:|
| Marché Lagune | 6 | 44 671,05 FCFA | 52,99 % |
| Baobab Shop | 9 | 2 702,25 FCFA | 4,67 % |
| Comptoir Ivoire | 10 | 6 666,67 FCFA | 2,81 % |

Les égalités sont comptées pour chaque enseigne gagnante; le total des victoires peut donc dépasser le nombre de produits comparés. L’écart moyen est calculé uniquement sur les produits disponibles chez l’enseigne concernée.

### Trois produits où comparer rapporte le plus

| Produit | Écart entre le prix le plus bas et le plus haut |
|---|---:|
| Tecno Spark 20 128 Go | 704 000 FCFA |
| HP 250 G9 Core i5 8 Go 512 Go | 52 800 FCFA |
| Apple iPhone 13 128 Go | 26 500 FCFA |

## Panier de rentrée

| Option | Total | Panier complet | Articles absents |
|---|---:|:---:|---|
| Marché Lagune | 1 205 400 FCFA | oui | — |
| Baobab Shop | 491 500 FCFA | oui | — |
| Comptoir Ivoire | 484 075 FCFA | oui | — |
| Panier mixte au moins cher | 477 575 FCFA | oui | — |

## Semaine du Black Friday

Les moyennes annuelles et celles du 24 au 30 novembre 2025 sont calculées par produit, puis moyennées entre produits. L’historique du Comptoir Ivoire contient le prix catalogue, sans remise.

| Enseigne | Moyenne annuelle | Moyenne du 24 au 30 novembre | Variation | Lecture |
|---|---:|---:|---:|---|
| Marché Lagune | 161 977,91 FCFA | 143 894,39 FCFA | -11,32 % | moins cher que la moyenne annuelle |
| Baobab Shop | 140 913,40 FCFA | 124 579,12 FCFA | -11,68 % | moins cher que la moyenne annuelle |
| Comptoir Ivoire | 154 842,88 FCFA | 160 604,55 FCFA | 3,75 % | plus cher que la moyenne annuelle |

## Temps de recherche et complexité

L’historique contient **20 876 lignes**. Pour 60 recherches, un balayage séquentiel a pris en moyenne **0,024246 s**; le dictionnaire indexé a pris **0,000012 s**, après **0,003688 s** de construction de l’index.

Le balayage coûte O(n) par recherche. Le dictionnaire demande O(n) à construire, puis O(1) en moyenne par recherche grâce à une clé composée de l’enseigne, du produit et de la date. Les temps sont ceux de cette exécution et peuvent varier selon l’ordinateur.
