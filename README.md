# terminus-32

La partie **publique** du projet [TERMinus](https://github.com/exec-d/terminus) : les données de la
**ligne 32 TER (Bourg-en-Bresse ⇄ Lyon)**, la distribution de l'application Android, et sa
[**landing page**](https://exec-d.github.io/terminus-32/).

## Contenu

- **`line32.json`** — référentiel de la ligne (gares, trips, calendrier de service), extrait du
  GTFS national SNCF et **mis à jour automatiquement chaque semaine** par la CI du repo app.
- **`stats/line32.json`** — statistiques de ponctualité par train (% à l'heure au seuil SNCF de
  5 min, retard médian, % suppression) sur **trois fenêtres glissantes** (semaine, mois, année),
  recalculées **3 fois par jour** par le workflow `collect-stats.yml` de ce dépôt
  (`tools/collect.py` échantillonne le flux GTFS-RT).
- **`stats/downloads.json`** — téléchargements de l'APK par version (`download_count` des assets
  GitHub Releases), recalculés quotidiennement par le workflow `collect-downloads.yml`
  (`tools/collect_downloads.py`).
- **`history/AAAA-MM-JJ.json`** — observations brutes par journée de service (retard final,
  retard max, arrêts sautés, suppression), auditables dans l'historique git.
- **`history/downloads-AAAA-MM-JJ.json`** — snapshot quotidien des téléchargements APK par version,
  pour garder un historique temporel.
- **`app/latest.json`** — manifeste de la dernière version de l'application (version, URL de
  l'APK), publié par la CI du repo app à chaque tag ; c'est lui que l'app consulte pour proposer
  ses mises à jour in-app.
- **[Releases](https://github.com/exec-d/terminus-32/releases)** — les APK signés de chaque
  version, téléchargeables anonymement (le repo app est privé).
- **`site/`** — la landing page, déployée sur GitHub Pages par `.github/workflows/pages.yml` :
  <https://exec-d.github.io/terminus-32/>

L'app télécharge ces fichiers à la volée (mise à jour OTA, sans réinstallation).

## Données & licence

Données : **SNCF** via [transport.data.gouv.fr](https://transport.data.gouv.fr) — licence
**ODbL** (Open Database License). Ce dépôt redistribue un extrait de ces données avec attribution,
conformément à la licence. Application non officielle, non affiliée à la SNCF.
