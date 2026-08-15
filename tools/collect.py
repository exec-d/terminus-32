#!/usr/bin/env python3
"""Collecte de ponctualité de la ligne 32 depuis le GTFS-RT SNCF.

Échantillonne le flux national TripUpdates, filtre les trains de la ligne 32
(numéros extraits de line32.json, présent à la racine du dépôt), fusionne
l'observation dans history/<date>.json (clé = date de service du trip, ce qui
rend les runs idempotents), puis recalcule stats/line32.json sur trois fenêtres
glissantes (semaine, mois, année).

Le flux ne porte un train que sur une fenêtre courte (~1 h avant son départ,
jusqu'à peu après son arrivée) : il ne conserve PAS la journée de service écoulée.
Un train non échantillonné pendant cette fenêtre est donc perdu définitivement —
aucun run ultérieur ne le rattrape. D'où un échantillonnage toutes les 30 min
(cf. collect-stats.yml), qui laisse 3 passages minimum par train, et le bloc
`coverage` écrit dans chaque journée pour rendre une lacune éventuelle visible.
"""

import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.transit import gtfs_realtime_pb2

from stats_lib import (
    MIN_OBS,
    aggregate_stations,
    coverage_of,
    desserte_anomalies,
    daily_trend_point,
    merge_stops,
    percentile,
    scheduled_numbers,
    station_order,
    train_number,
    train_station_stats,
    uic_of,
)

ROOT = Path(__file__).resolve().parent.parent
FEED_URL = "https://proxy.transport.data.gouv.fr/resource/sncf-gtfs-rt-trip-updates"
ON_TIME_S = 300  # seuil SNCF : à l'heure si retard final <= 5 min
WINDOWS = {"week": 7, "month": 30, "year": 365}  # fenêtres glissantes, en jours


def load_line32():
    return json.loads((ROOT / "line32.json").read_text())


def load_line32_numbers(line32):
    return {n for t in line32["trips"] if (n := train_number(t["tripId"]))}


def fetch_feed():
    feed = gtfs_realtime_pb2.FeedMessage()
    with urllib.request.urlopen(FEED_URL, timeout=60) as r:
        feed.ParseFromString(r.read())
    return feed


def stops_from_trip_update(tu):
    """Retard par arrêt d'un trip_update : [{uic, delayS, skipped}]."""
    stops = []
    for stu in tu.stop_time_update:
        uic = uic_of(stu.stop_id)
        if not uic:
            continue
        if stu.schedule_relationship == stu.SKIPPED:
            stops.append({"uic": uic, "delayS": None, "skipped": True})
            continue
        ev = stu.arrival if stu.HasField("arrival") else stu.departure
        delay = ev.delay if ev.HasField("delay") else None
        stops.append({"uic": uic, "delayS": delay, "skipped": False})
    return stops


def observe(feed, numbers):
    """Une observation par train de la ligne, groupée par date de service."""
    obs = {}
    for e in feed.entity:
        if not e.HasField("trip_update"):
            continue
        tu = e.trip_update
        num = train_number(tu.trip.trip_id)
        if num not in numbers or not tu.trip.start_date:
            continue
        cancelled = tu.trip.schedule_relationship == tu.trip.CANCELED
        final_delay, max_delay, skipped = None, 0, 0
        for stu in tu.stop_time_update:
            if stu.schedule_relationship == stu.SKIPPED:
                skipped += 1
                continue
            ev = stu.arrival if stu.HasField("arrival") else stu.departure
            if ev.HasField("delay"):
                final_delay = ev.delay  # les STU sont ordonnés : le dernier = terminus
                max_delay = max(max_delay, ev.delay)
        obs.setdefault(tu.trip.start_date, {})[num] = {
            "finalDelayS": final_delay,
            "maxDelayS": max_delay,
            "skippedStops": skipped,
            "cancelled": cancelled,
            "stops": stops_from_trip_update(tu),
        }
    return obs


def merge_history(obs, now_iso, line32):
    hist = ROOT / "history"
    hist.mkdir(exist_ok=True)
    for date, trains in obs.items():
        iso = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        path = hist / f"{iso}.json"
        day = (
            json.loads(path.read_text())
            if path.exists()
            else {"date": iso, "samples": [], "trains": {}}
        )
        day["samples"].append(now_iso)
        for num, rec in trains.items():
            old = day["trains"].get(num)
            if old:
                # Le sample le plus tardif a vu le train plus avancé : son retard
                # final prime s'il existe ; les autres champs se cumulent.
                rec = {
                    "finalDelayS": rec["finalDelayS"] if rec["finalDelayS"] is not None else old["finalDelayS"],
                    "maxDelayS": max(old["maxDelayS"], rec["maxDelayS"]),
                    "skippedStops": max(old["skippedStops"], rec["skippedStops"]),
                    "cancelled": old["cancelled"] or rec["cancelled"],
                    "stops": merge_stops(old.get("stops", []), rec.get("stops", [])),
                }
            day["trains"][num] = rec
        day["coverage"] = coverage_of(scheduled_numbers(line32, iso), day["trains"])
        path.write_text(json.dumps(day, indent=1, sort_keys=True) + "\n")


def _aggregate(recs):
    n = len(recs)
    # Un pourcentage sur 1 ou 2 trajets n'est pas une statistique, c'est une anecdote
    # affichée comme une certitude. En deçà du seuil on ne publie que le brut ;
    # `onTimePct` étant déjà optionnel, aucun consommateur n'a à changer de schéma.
    entry = {"obs": n, "enough": n >= MIN_OBS}
    if not entry["enough"]:
        return entry
    cancelled = sum(1 for r in recs if r["cancelled"])
    ran = [r for r in recs if r["finalDelayS"] is not None and not r["cancelled"]]
    delays = sorted(r["finalDelayS"] for r in ran)
    entry["cancelledPct"] = round(100 * cancelled / n)
    # skippedStops et maxDelayS étaient collectés depuis le début sans être lus :
    # le premier dit « ce train ne s'est pas arrêté », le second permet de repérer
    # les trajets partis en retard puis rattrapés — deux vécus très différents d'un
    # même retard final.
    entry["skippedPct"] = round(100 * sum(1 for r in recs if r.get("skippedStops")) / n)
    if ran:
        recovered = sum(1 for r in ran if (r.get("maxDelayS") or 0) - r["finalDelayS"] >= 120)
        entry["recoveredPct"] = round(100 * recovered / len(ran))
    if delays:
        # onTimePct honnête, cohérent avec daily_trend_point : à l'heure rapporté à
        # TOUTES les observations de la fenêtre. Une suppression — ou un trajet sans
        # retard final publié — compte comme non-à-l'heure et n'est jamais retirée du
        # dénominateur (sinon un train supprimé un jour sur deux afficherait 100 %).
        # Les stats de retard (médiane / moyenne / cumul / max) ne portent, elles,
        # que sur les trajets ayant circulé avec un retard connu.
        on_time = sum(1 for d in delays if d <= ON_TIME_S)
        entry["onTimePct"] = round(100 * on_time / n)
        entry["medianDelayMin"] = round(delays[len(delays) // 2] / 60)
        entry["meanDelayMin"] = round(sum(delays) / len(delays) / 60)
        entry["cumDelayMin"] = round(sum(delays) / 60)
        entry["maxDelayMin"] = round(max(delays) / 60)
        # p90 plutôt que le seul max : le max est figé pour un an par un incident
        # unique, le p90 répond à « j'arrive avant quelle heure 9 fois sur 10 ? ».
        entry["p90DelayMin"] = round(percentile(delays, 90) / 60)
    return entry


_DATE_STEM = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _history_paths():
    """Fichiers d'historique journaliers, triés par date.

    Exclut history/downloads-*.json (écrits par collect_downloads.py) dont le nom
    ne parse pas en date — sinon strptime lève ValueError et le calcul plante.
    """
    return [p for p in sorted((ROOT / "history").glob("*.json")) if _DATE_STEM.match(p.stem)]


def _window_coverage(day_coverage, today, days):
    """Part des trains programmés réellement observés sur une fenêtre glissante.

    Ne comptent que les journées dont le programme est connu (cf. scheduled_numbers) :
    inclure les autres ferait passer une lacune pour une couverture parfaite.
    """
    rows = [c for d, c in day_coverage if d >= today - timedelta(days=days) and c.get("scheduled")]
    scheduled = sum(c["scheduled"] for c in rows)
    observed = sum(c["scheduled"] - len(c["missing"]) for c in rows)
    return {
        "days": len(rows),
        "scheduled": scheduled,
        "observed": observed,
        "pct": round(100 * observed / scheduled) if scheduled else None,
    }


def compute_stats(now_iso, line32):
    today = datetime.now(timezone.utc).date()
    horizon = today - timedelta(days=max(WINDOWS.values()))
    per_train, days_seen, day_coverage = {}, [], []
    for path in _history_paths():
        day = datetime.strptime(path.stem, "%Y-%m-%d").date()
        if day < horizon:
            continue
        days_seen.append(day)
        content = json.loads(path.read_text())
        if content.get("coverage"):
            day_coverage.append((day, content["coverage"]))
        for num, rec in content["trains"].items():
            per_train.setdefault(num, []).append((day, rec))

    trains = {}
    for num, dated in sorted(per_train.items()):
        entry = {}
        for name, days in WINDOWS.items():
            recs = [r for d, r in dated if d >= today - timedelta(days=days)]
            if recs:
                entry[name] = _aggregate(recs)
        trains[num] = entry

    stats_dir = ROOT / "stats"
    stats_dir.mkdir(exist_ok=True)
    (stats_dir / "line32.json").write_text(
        json.dumps(
            {
                "meta": {
                    "updatedAt": now_iso,
                    "windows": WINDOWS,
                    "daysWithData": {
                        name: sum(1 for d in days_seen if d >= today - timedelta(days=days))
                        for name, days in WINDOWS.items()
                    },
                    "onTimeThresholdMin": ON_TIME_S // 60,
                    "minObs": MIN_OBS,
                    # Couverture de la collecte : sans elle, un train jamais
                    # échantillonné sort du dénominateur sans laisser de trace et
                    # gonfle mécaniquement le % à l'heure.
                    "coverage": {
                        name: _window_coverage(day_coverage, today, days)
                        for name, days in WINDOWS.items()
                    },
                },
                "trains": trains,
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )

    station_ref = line32["stations"]
    order_by_uic = station_order(line32)
    days_records = [
        json.loads(p.read_text())
        for p in _history_paths()
        if datetime.strptime(p.stem, "%Y-%m-%d").date() >= horizon
    ]
    (stats_dir / "trend.json").write_text(
        json.dumps(
            {
                "meta": {"updatedAt": now_iso, "onTimeThresholdMin": ON_TIME_S // 60},
                "points": [daily_trend_point(d) for d in days_records],
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )
    (stats_dir / "stations.json").write_text(
        json.dumps(
            {
                "meta": {"updatedAt": now_iso},
                "stations": aggregate_stations(days_records, station_ref, order_by_uic),
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )

    # Ponctualité croisée train × gare. Fichier séparé et non fusionné dans
    # line32.json : ~120 Ko, à ne télécharger que pour une fiche train, pas à
    # chaque lancement. Le seuil de 5 min s'applique ici au passage en gare.
    (stats_dir / "train-stations.json").write_text(
        json.dumps(
            {
                "meta": {
                    "updatedAt": now_iso,
                    "windows": WINDOWS,
                    "onTimeThresholdMin": ON_TIME_S // 60,
                    "minObs": MIN_OBS,
                },
                "trains": train_station_stats(days_records, order_by_uic, WINDOWS, today),
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )

    # Dessertes réduites à venir. L'information est déductible de line32.json, mais
    # y arriver demande de croiser 168 trips et 119 dates de service : on la
    # pré-calcule ici plutôt que dans chaque client.
    (stats_dir / "desserte.json").write_text(
        json.dumps(
            {
                "meta": {"updatedAt": now_iso, "from": today.isoformat()},
                "anomalies": desserte_anomalies(line32, today.isoformat()),
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )


def main():
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    line32 = load_line32()
    numbers = load_line32_numbers(line32)
    obs = observe(fetch_feed(), numbers)
    seen = sum(len(t) for t in obs.values())
    print(f"trains ligne 32 dans le flux : {seen} (dates de service : {sorted(obs)})")

    # Hors circulation (nuit), le flux ne porte aucun train de la ligne. Écrire
    # quand même republierait des stats identiques à l'horodatage près : un commit
    # vide toutes les 30 min. On sort sans rien toucher.
    if not obs:
        print("aucun train de la ligne dans le flux — rien à écrire")
        return

    # Diagnostic : log des arrêts non mappés (validation du mapping UIC au 1er run live)
    known = {uic_of(s["id"]) for s in line32["stations"]}
    seen_uics = {s["uic"] for t in obs.values() for rec in t.values() for s in rec.get("stops", [])}
    unknown = seen_uics - known
    if unknown:
        print(f"⚠ arrêts hors référentiel (UIC non mappés) : {sorted(unknown)}")

    merge_history(obs, now_iso, line32)
    compute_stats(now_iso, line32)
    print("history/ et stats/ à jour")


if __name__ == "__main__":
    main()
