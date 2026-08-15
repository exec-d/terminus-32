"""Agrégations pures de ponctualité (sans dépendance GTFS-RT/protobuf).

Isolé de collect.py pour être testable sans le flux : trend quotidien honnête,
agrégat par gare, fusion des arrêts, extraction du code UIC.
"""

import re

ON_TIME_S = 300  # seuil SNCF : à l'heure si retard final <= 5 min

_UIC_RE = re.compile(r"(\d{7,8})")


def uic_of(raw_id):
    """Code UIC (7-8 chiffres) d'un identifiant d'arrêt/gare, ou None."""
    if not raw_id:
        return None
    m = _UIC_RE.search(raw_id)
    return m.group(1) if m else None


_TRAIN_RE = re.compile(r"OCESN(\d+)")


def train_number(trip_id):
    """Numéro de train commercial d'un tripId GTFS SNCF, ou None."""
    if not trip_id:
        return None
    m = _TRAIN_RE.search(trip_id)
    return m.group(1) if m else None


def scheduled_numbers(line32, date):
    """Numéros programmés une date de service donnée (AAAA-MM-JJ), ou None.

    None quand la date sort du calendrier publié : le référentiel est régénéré
    chaque semaine et ne couvre pas le passé lointain. On ne peut alors ni
    affirmer ni infirmer une lacune — mieux vaut l'avouer que compter 0 attendu.
    """
    if not any(c["date"] == date for c in line32.get("calendarDates", [])):
        return None
    services = {
        c["serviceId"]
        for c in line32["calendarDates"]
        if c["date"] == date and c["exception"] == "added"
    }
    return {
        n
        for t in line32.get("trips", [])
        if t.get("serviceId") in services and (n := train_number(t.get("tripId")))
    }


def coverage_of(scheduled, observed):
    """Couverture d'une journée : ce qui était programmé vs ce qu'on a vraiment vu.

    Le flux GTFS-RT ne porte un train que sur une fenêtre courte autour de son
    passage : un train manqué est perdu définitivement, jamais rattrapable. D'où
    ce bloc, qui rend la lacune visible dans la donnée au lieu de la laisser
    disparaître silencieusement du dénominateur des stats.
    """
    seen = set(observed)
    if scheduled is None:
        return {"scheduled": None, "observed": len(seen), "pct": None, "missing": None}
    missing = sorted(set(scheduled) - seen)
    total = len(scheduled)
    return {
        "scheduled": total,
        "observed": len(seen),
        "pct": round(100 * (total - len(missing)) / total) if total else None,
        "missing": missing,
    }


def daily_trend_point(day):
    """Point de tendance honnête pour une journée d'historique.

    Une suppression compte comme non-à-l'heure (jamais exclue du dénominateur).
    onTimePct = trains ayant circulé avec finalDelayS <= 300, sur TOUS les trains.
    """
    trains = day.get("trains", {})
    obs = len(trains)
    if not obs:
        return {"date": day["date"], "obs": 0, "onTimePct": 0, "cancelledPct": 0}
    cancelled = sum(1 for r in trains.values() if r.get("cancelled"))
    on_time = sum(
        1
        for r in trains.values()
        if not r.get("cancelled")
        and r.get("finalDelayS") is not None
        and r["finalDelayS"] <= ON_TIME_S
    )
    return {
        "date": day["date"],
        "obs": obs,
        "onTimePct": round(100 * on_time / obs),
        "cancelledPct": round(100 * cancelled / obs),
    }


def merge_stops(a, b):
    """Fusionne deux listes d'arrêts {uic, delayS, skipped} par uic (idempotent)."""
    merged = {}
    for s in list(a) + list(b):
        cur = merged.get(s["uic"])
        if cur is None:
            merged[s["uic"]] = {"uic": s["uic"], "delayS": s.get("delayS"), "skipped": bool(s.get("skipped"))}
        else:
            if s.get("delayS") is not None:
                cur["delayS"] = s["delayS"]
            cur["skipped"] = cur["skipped"] or bool(s.get("skipped"))
    return [merged[k] for k in sorted(merged)]


def _median(values):
    vs = sorted(values)
    return vs[len(vs) // 2] if vs else None


def _mean(values):
    return round(sum(values) / len(values)) if values else None


def station_order(line32):
    """Ordre géographique {uic: index} le long de la ligne, d'après le trajet ALLER
    (bebToLyon) le plus complet de line32.json — ses arrêts sont dans l'ordre `seq`.
    Le tableau `stations` de line32.json n'est PAS trié géographiquement, d'où ce calcul."""
    best = []
    for t in line32.get("trips", []):
        if t.get("direction") == "bebToLyon":
            stops = sorted(t.get("stops", []), key=lambda s: s.get("seq", 0))
            if len(stops) > len(best):
                best = stops
    order = {}
    for s in best:
        u = uic_of(s.get("stationId"))
        if u and u not in order:
            order[u] = len(order)
    return order


def aggregate_stations(days, station_ref, order_by_uic):
    """Agrège le retard par gare, rangé par ordre géographique (`order_by_uic`, cf.
    station_order). Retard médian ET moyen : la médiane reste souvent à 0 (majorité de
    passages à l'heure) alors que la moyenne capte les à-coups (retards de la queue)."""
    delays, skips, obs = {}, {}, {}
    for day in days:
        for rec in day.get("trains", {}).values():
            for s in rec.get("stops", []):
                u = s["uic"]
                obs[u] = obs.get(u, 0) + 1
                if s.get("skipped"):
                    skips[u] = skips.get(u, 0) + 1
                elif s.get("delayS") is not None:
                    delays.setdefault(u, []).append(s["delayS"])
    end = len(order_by_uic)
    rows = []
    for station in station_ref:
        u = uic_of(station["id"])
        n = obs.get(u, 0)
        rows.append({
            "uic": u,
            "name": station["name"],
            "order": order_by_uic.get(u, end),  # gares hors trajet retenu → en fin
            "obs": n,
            "medianDelayS": _median(delays.get(u, [])),
            "meanDelayS": _mean(delays.get(u, [])),
            "skippedPct": round(100 * skips.get(u, 0) / n) if n else 0,
        })
    rows.sort(key=lambda r: (r["order"], r["name"]))
    for i, r in enumerate(rows):  # ordre final propre 0..N après tri géographique
        r["order"] = i
    return rows


MIN_OBS = 5  # en deçà, un pourcentage ne veut rien dire — on publie le brut et rien d'autre


def percentile(values, q):
    """Quantile (méthode du plus proche rang) d'une liste de valeurs, ou None.

    p90 plutôt que max : le max est fixé pour un an par un incident unique, alors
    que le p90 répond à la question de l'usager — « j'arrive avant quelle heure
    9 fois sur 10 ? ».
    """
    vs = sorted(values)
    if not vs:
        return None
    rank = max(1, min(len(vs), -(-len(vs) * q // 100)))  # ceil(n*q/100), borné
    return vs[rank - 1]


def train_station_stats(days, order_by_uic, windows, today, min_obs=MIN_OBS):
    """Ponctualité croisée train × gare, par fenêtre glissante.

    La régularité SNCF se mesure au terminus ; l'usager, lui, monte et descend en
    gare intermédiaire. Le profil d'arrêts est déjà collecté : il suffit de ne PAS
    l'écraser en une médiane par gare toutes circulations confondues.
    """
    from datetime import datetime, timedelta

    per_key = {}
    for day in days:
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        for num, rec in day.get("trains", {}).items():
            for stop in rec.get("stops", []):
                per_key.setdefault((num, stop["uic"]), []).append((date, stop))

    out = {}
    for (num, uic), dated in sorted(per_key.items()):
        by_window = {}
        for name, days_back in windows.items():
            stops = [s for d, s in dated if d >= today - timedelta(days=days_back)]
            if not stops:
                continue
            by_window[name] = _stop_window(stops, min_obs)
        if by_window:
            out.setdefault(num, {})[uic] = by_window
    return {
        num: {u: w for u, w in sorted(stations.items(), key=lambda kv: order_by_uic.get(kv[0], 99))}
        for num, stations in out.items()
    }


def _stop_window(stops, min_obs):
    """Agrégat d'une gare sur une fenêtre : suppressions au dénominateur, comme ailleurs."""
    n = len(stops)
    skipped = sum(1 for s in stops if s.get("skipped"))
    entry = {"obs": n, "enough": n >= min_obs}
    if not entry["enough"]:
        return entry
    delays = [s["delayS"] for s in stops if not s.get("skipped") and s.get("delayS") is not None]
    entry["skippedPct"] = round(100 * skipped / n)
    if delays:
        entry["onTimePct"] = round(100 * sum(1 for d in delays if d <= ON_TIME_S) / n)
        entry["medianDelayS"] = _median(delays)
        entry["p90DelayS"] = percentile(delays, 90)
    return entry


def desserte_anomalies(line32, from_date, horizon_days=120):
    """Journées où un train ne dessert pas ses gares habituelles, à venir.

    La desserte de référence est calculée par (train, jour de semaine) : le samedi
    a son propre schéma, le signaler comme anomalie serait du bruit. Ne reste que
    le vrai cas gênant — le train qui, tel jour, s'arrête avant son terminus
    habituel alors que l'app en affiche le nom.
    """
    from collections import Counter, defaultdict
    from datetime import datetime, timedelta

    name_of = {s["id"]: s["name"] for s in line32.get("stations", [])}
    active = defaultdict(set)
    for c in line32.get("calendarDates", []):
        if c["exception"] == "added":
            active[c["serviceId"]].add(c["date"])

    served = defaultdict(dict)  # train -> date -> frozenset(stationId)
    for trip in line32.get("trips", []):
        stops = frozenset(s["stationId"] for s in trip["stops"])
        num = train_number(trip.get("tripId"))
        for date in active.get(trip.get("serviceId"), ()):
            if num:
                served[num][date] = stops

    start = datetime.strptime(from_date, "%Y-%m-%d").date()
    end = start + timedelta(days=horizon_days)
    out = []
    for num, by_date in served.items():
        usual = {}  # jour de semaine -> desserte modale
        for date, stops in by_date.items():
            wd = datetime.strptime(date, "%Y-%m-%d").date().weekday()
            usual.setdefault(wd, Counter())[stops] += 1
        for date, stops in sorted(by_date.items()):
            day = datetime.strptime(date, "%Y-%m-%d").date()
            if not (start <= day <= end):
                continue
            ref = usual[day.weekday()].most_common(1)[0][0]
            missing = ref - stops
            if not missing:
                continue
            out.append({
                "date": date,
                "train": num,
                "missing": sorted(name_of.get(s, s) for s in missing),
                "servedCount": len(stops),
                "usualCount": len(ref),
            })
    return sorted(out, key=lambda a: (a["date"], a["train"]))
