# terminus-32

La partie **publique** du projet [TERMinus](https://github.com/exec-d/terminus) : les données de la
**ligne 32 TER (Bourg-en-Bresse ⇄ Lyon)**, la distribution de l'application Android, et sa
[**landing page**](https://exec-d.github.io/terminus-32/).

## Contenu

- **`line32.json`** — référentiel de la ligne (gares, trips, calendrier de service), extrait du
  GTFS national SNCF et **mis à jour automatiquement chaque semaine** par la CI du repo app.
- **`stats/line32.json`** — statistiques de ponctualité par train (% à l'heure au seuil SNCF de
  5 min, retard médian, % suppression) sur **trois fenêtres glissantes** (semaine, mois, année),
  recalculées **toutes les 30 min** par le workflow `collect-stats.yml` de ce dépôt
  (`tools/collect.py` échantillonne le flux GTFS-RT). Le `% à l'heure` rapporte les
  trajets ponctuels à **toutes** les observations de la fenêtre : une suppression y
  compte comme non-à-l'heure (jamais retirée du dénominateur). `meta.coverage`
  indique quelle part du programme a effectivement été observée sur chaque fenêtre —
  un `% à l'heure` ne se lit pas sans lui. En deçà de `meta.minObs` observations, la
  fenêtre porte `enough: false` et **aucun pourcentage** : un taux calculé sur un
  trajet n'est pas une statistique. Outre la médiane et le max, chaque fenêtre publie
  un `p90DelayMin` (« j'arrive avant quelle heure 9 fois sur 10 ? », insensible à
  l'incident unique qui fige le max pendant un an), un `skippedPct` (trajets ayant
  sauté au moins un arrêt) et un `recoveredPct` (trajets partis en retard puis
  rattrapés d'au moins 2 min avant le terminus).
- **`stats/train-stations.json`** — ponctualité croisée **train × gare**, par fenêtre.
  La régularité SNCF se mesure au terminus ; l'usager, lui, monte et descend en gare
  intermédiaire. Le profil d'arrêts était déjà collecté, il n'était qu'écrasé en une
  médiane par gare toutes circulations confondues. Fichier séparé (~170 Ko) : à
  charger pour une fiche train, pas à chaque lancement.
- **`stats/desserte.json`** — journées à venir où un train **ne dessert pas ses gares
  habituelles** (terminus raccourci, arrêt supprimé au calendrier). La référence est
  calculée par (train, jour de semaine), pour que le schéma propre au samedi ne sorte
  pas en anomalie. Déductible de `line32.json`, mais au prix d'un croisement de tous
  les trips et de toutes les dates de service : pré-calculé ici plutôt que dans chaque
  client.
- **`stats/downloads.json`** — téléchargements de l'APK par version (`download_count` des assets
  GitHub Releases), recalculés quotidiennement par le workflow `collect-downloads.yml`
  (`tools/collect_downloads.py`).
- **`history/AAAA-MM-JJ.json`** — observations brutes par journée de service (retard final,
  retard max, arrêts sautés, suppression), auditables dans l'historique git. Chaque journée
  porte un bloc `coverage` (trains programmés, observés, manquants) : le flux GTFS-RT ne
  retient un train qu'environ 1 h avant son départ et jusqu'à peu après son arrivée, un
  train manqué est donc **définitivement** perdu. D'où l'échantillonnage toutes les 30 min,
  qui laisse au moins 3 passages par train, et ce bloc qui rend toute lacune visible plutôt
  que de la laisser sortir silencieusement du dénominateur. `python tools/audit.py` affiche
  la couverture journée par journée (`--fail-under 95` pour un contrôle automatisé).
- **`history/downloads-AAAA-MM-JJ.json`** — snapshot quotidien des téléchargements APK par version,
  pour garder un historique temporel.
- **`app/latest.json`** — manifeste de la dernière version de l'application (version, URL de
  l'APK), publié par la CI du repo app à chaque tag ; c'est lui que l'app consulte pour proposer
  ses mises à jour in-app.
- **[Releases](https://github.com/exec-d/terminus-32/releases)** — les APK signés de chaque
  version, téléchargeables anonymement (le repo app est privé).
- **`web/`** — le site (application **SvelteKit**), construit puis déployé sur GitHub Pages par
  `.github/workflows/pages.yml` : <https://exec-d.github.io/terminus-32/>

L'app télécharge ces fichiers à la volée (mise à jour OTA, sans réinstallation).

## Données & licence

Données : **SNCF** via [transport.data.gouv.fr](https://transport.data.gouv.fr) — licence
**ODbL** (Open Database License). Ce dépôt redistribue un extrait de ces données avec attribution,
conformément à la licence ; `line32.json` étant une **base dérivée**, il est lui-même publié sous
ODbL 1.0. Application non officielle, non affiliée à la SNCF.

Le détail des licences et des mentions d'attribution, jeu par jeu, figure dans
**[`DATA-LICENSE.md`](DATA-LICENSE.md)**.
