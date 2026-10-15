# 🐚 20km de la Côte de Granit Rose · Statistiques

Tableau de bord interactif des résultats chronométriques du **20 km – Trophée Intermarché** et du **10 km – Trophée Intersport** (éditions 2022 à 2026), réalisé avec [Streamlit](https://streamlit.io).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://statistiques-20kmcotegranitrose-app.streamlit.app/)

## Origine des données

Les résultats ne sont pas fournis par l'organisation : ils ont été **récupérés (scrapés) par mes soins** sur le site du chronométreur [sportinnovation.fr](https://sportinnovation.fr).

- **Éditions 2022 à 2025** : pages HTML des résultats, collectées avec [Selenium](https://www.selenium.dev) (navigation page par page) et [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) / pandas pour lire le tableau.
- **Édition 2026** : le site expose les résultats via une API JSON, interrogée avec `requests` puis remise au même format que les années précédentes.
- Les résultats sont enregistrés dans deux classeurs Excel, `results_10km.xlsx` et `results_20km.xlsx` (une feuille par édition), puis transformés en un unique `data/resultats.csv` par `prepare_data.py`.

Ces données sont publiques mais peuvent contenir des erreurs, et les noms peuvent être écrits de façon différente d'une édition à l'autre (l'application les harmonise).

## Fonctionnalités

Un sélecteur **20 km / 10 km** permet de choisir la course. Toutes les statistiques ci-dessous portent sur la course sélectionnée.

L'application comporte trois onglets : **Général** (vue d'ensemble de toutes les éditions), **Édition** (détail d'une édition au choix) et **Individuel** (suivi d'un coureur).

### 📊 Général

Vue d'ensemble sur toutes les éditions et toutes les catégories confondues.

- **Records** féminin et masculin avec le nom du détenteur et l'année, et **plus grand nombre de participations**.
- **Podiums des participations** : les 3 coureuses et les 3 coureurs les plus fidèles, classés par nombre d'éditions.
- **Évolution entre les éditions**, au choix :
  - *Nombre* : nombre de coureurs par édition, hommes et femmes ;
  - *Densité* : part des arrivants par tranche de temps, année après année (barres empilées à 100 %).

### 👟 Édition

Détail d'une édition, à choisir parmi toutes les éditions disponibles.

- **Sélecteur d'édition**, à droite des onglets : liste déroulante avec recherche et flèches ‹ › pour passer à l'édition précédente ou suivante.
- **Indicateurs clés** : nombre de participants, d'hommes et de femmes, avec le temps moyen de chacun.
- **Filtre par catégorie** (Scratch, CA, JU, ES, SE, M0 à M9), propre à l'édition choisie, appliqué aux podiums et aux graphiques de distribution.
- **Podiums** hommes et femmes, avec gestion des ex æquo.
- **Distribution des temps officiels**, au choix :
  - *Courbe* : densité de coureurs par sexe, sur les temps pistolet ;
  - *Tranches* : nombre de coureurs par tranche de performance. Les tranches s'adaptent à la distance : 10min pour le 20 km (de « < 1h10 » à « ≥ 2h10 »), 5min pour le 10 km (de « < 35min » à « ≥ 1h05 »).
- **Répartition hommes / femmes** sous forme d'anneau.

### 🏃 Individuel

- **Recherche d'un coureur** par nom ou prénom, dans n'importe quel ordre, sans tenir compte des accents ni des majuscules. En cas d'homonymes, une liste permet de choisir le bon coureur.
- **Indicateurs personnels** : nombre d'éditions courues, meilleur temps (avec son année) et nombre de médailles (or, argent, bronze) obtenues sur les podiums au scratch.
- **Évolution des performances** : graphique du temps de chaque édition, avec le meilleur temps mis en évidence.
- **Détail par édition** : temps, place au scratch, place chez les hommes ou les femmes, catégorie et médaille éventuelle.
- **Carte récap en PDF** : chaque coureur peut télécharger une carte (format A5) avec son nom, le logo de la course, ses chiffres clés et l'évolution de ses temps sur les éditions courues.

Les couleurs suivent partout la même règle : **rouge pour les hommes, bleu pour les femmes**.

## Structure du dépôt

```
.
├── streamlit_app.py            # application Streamlit
├── carte_pdf.py                # génération de la carte récap (PDF, reportlab)
├── prepare_data.py             # xlsx scrapés -> data/resultats.csv
├── assets/                     # images utiles (fond et logo)
├── data/                       # résultats chronométriques (une ligne par coureur)
├── pyproject.toml              # dépendances (uv)
└── README.md
```
### Format des données

`data/resultats.csv` contient une ligne par coureur, avec les colonnes :

| Colonne          | Description                                                                |
|------------------|----------------------------------------------------------------------------|
| `Annee`          | Édition de la course                                                       |
| `Course`         | Distance : `10km` ou `20km`                                                |
| `Dossard`        | Numéro de dossard                                                          |
| `Place`          | Classement au scratch                                                      |
| `Nom`            | Nom puis prénom du coureur (ex. `NOM Prénom`)                              |
| `Sexe`           | `H` ou `F`                                                                 |
| `Club`           | Club ou association (peut être vide)                                       |
| `Catégorie`      | Catégorie telle qu'affichée sur le site (ex. `SH`, `EH - U23H`), ramenée à un code court (`SE`, `ES`, `M0`…) dans l'application |
| `Classement_Cat` | Classement dans la catégorie                                               |
| `Nat`            | Nationalité                                                                |
| `Temps_s`        | Temps officiel (pistolet) en secondes ; vide en cas d'abandon              |
| `Temps_reel_s`   | Temps réel (puce) en secondes                                              |

Les coureurs sans temps (abandons) sont comptés parmi les participants mais exclus des moyennes, des courbes, des tranches et des podiums.

## Crédits

- Résultats chronométriques : [sportinnovation.fr](https://sportinnovation.fr), collectés par scraping (voir "Origine des données").
- Construit avec [Streamlit](https://streamlit.io), [pandas](https://pandas.pydata.org), [Plotly](https://plotly.com/python/), [ReportLab](https://docs.reportlab.com/) pour la carte PDF, et [Selenium](https://www.selenium.dev) pour la collecte.
- Image de fond : Jean-claude EMILY - 20km (Photos 2025)