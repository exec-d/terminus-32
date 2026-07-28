# Licences et attribution des données publiées dans ce dépôt

Ce dépôt redistribue des données dérivées de jeux de données publics. Chaque jeu conserve la licence
de sa source.

## `line32.json` — référentiel de la ligne 32

Extrait du jeu **GTFS SNCF** diffusé sur le Point d'Accès National
[transport.data.gouv.fr](https://transport.data.gouv.fr), sous licence
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).

Ce fichier est une **base de données dérivée** au sens de l'ODbL. Il est publié **sous la même
licence ODbL 1.0**. Toute réutilisation doit conserver cette licence, en citer la source et
indiquer les modifications apportées (ici : filtrage sur la ligne 32 Bourg-en-Bresse ⇄ Lyon et
restructuration des champs).

> Contient des données de la SNCF diffusées via transport.data.gouv.fr, sous licence ODbL 1.0.
> Base dérivée publiée sous licence ODbL 1.0.

## `stats/` et `history/` — statistiques de ponctualité

Calculés à partir des flux **GTFS-RT** de la SNCF diffusés via
[transport.data.gouv.fr](https://transport.data.gouv.fr), sous licence
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).

> Statistiques calculées à partir des données temps réel de la SNCF diffusées via
> transport.data.gouv.fr, sous licence ODbL 1.0.

## Autres jeux utilisés par l'application

L'application TERMinus interroge en direct, sans les redistribuer, deux jeux supplémentaires. Ils
n'entrent donc pas dans le champ du partage à l'identique, mais leur attribution est due :

- **Équipements d'élévatique en gare** (ascenseurs, escaliers mécaniques) — SNCF Gares & Connexions,
  via [ressources.data.sncf.com](https://ressources.data.sncf.com), sous licence
  [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/) ; conditions détaillées
  sur [data.sncf.com/pages/licence](https://data.sncf.com/pages/licence).
- **Vélo'v** — Métropole de Lyon / JCDecaux, flux GBFS. Le flux déclare lui-même sa licence : la
  [Licence Ouverte de JCDecaux](https://developer.jcdecaux.com/files/Open-Licence-fr.pdf). Les
  conditions d'usage du service figurent dans les
  [conditions générales d'accès et d'utilisation Vélo'v](https://velov.grandlyon.com/fr/documents/cgau/vls).
  L'accès au flux ne requiert aucune clé d'API.

## Indépendance

TERMinus est un projet indépendant, **non officiel** et **non affilié** à la SNCF ni à SNCF
Voyageurs. « TER » et « SNCF » sont des marques déposées de leurs titulaires respectifs.
