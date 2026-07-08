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
