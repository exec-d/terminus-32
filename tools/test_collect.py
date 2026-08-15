import pytest

pytest.importorskip("google.transit")  # skip si la lib GTFS-RT n'est pas installée
from google.transit import gtfs_realtime_pb2  # noqa: E402
import json  # noqa: E402

import collect  # noqa: E402
from collect import _aggregate, merge_history, stops_from_trip_update  # noqa: E402


def _tu():
    tu = gtfs_realtime_pb2.TripUpdate()
    a = tu.stop_time_update.add()
    a.stop_id = "StopPoint:OCE87743005"
    a.arrival.delay = 60
    b = tu.stop_time_update.add()
    b.stop_id = "StopPoint:OCE87721001"
    b.schedule_relationship = b.SKIPPED
    return tu


def test_stops_from_trip_update_extracts_uic_delay_skip():
    stops = stops_from_trip_update(_tu())
    by = {s["uic"]: s for s in stops}
    assert by["87743005"] == {"uic": "87743005", "delayS": 60, "skipped": False}
    assert by["87721001"]["skipped"] is True
    assert by["87721001"]["delayS"] is None


def test_aggregate_mean_et_median():
    # Cas réel (train 889431) : 5 trajets à 0 s + 1 à 1200 s → 83 % à l'heure,
    # médiane insensible à l'accroc (0 min) mais moyenne à 3 min (200 s).
    recs = [{"cancelled": False, "finalDelayS": 0, "skippedStops": 0}] * 5 + [
        {"cancelled": False, "finalDelayS": 1200, "skippedStops": 0}
    ]
    out = _aggregate(recs)
    assert out["obs"] == 6
    assert out["onTimePct"] == 83
    assert out["medianDelayMin"] == 0
    assert out["meanDelayMin"] == 3
    assert out["cumDelayMin"] == 20


def test_aggregate_cancellations_count_against_on_time():
    # onTimePct honnête (cohérent avec daily_trend_point) : 5 trajets à l'heure +
    # 5 supprimés → 50 % à l'heure, pas 100 %. Les suppressions restent au
    # dénominateur ; les stats de retard ne portent que sur les trajets circulés.
    recs = [{"cancelled": False, "finalDelayS": 0, "skippedStops": 0}] * 5 + [
        {"cancelled": True, "finalDelayS": None, "skippedStops": 0}
    ] * 5
    out = _aggregate(recs)
    assert out["obs"] == 10
    assert out["cancelledPct"] == 50
    assert out["onTimePct"] == 50  # 5 à l'heure / 10 observations, pas 5/5
    assert out["medianDelayMin"] == 0
    assert out["maxDelayMin"] == 0


def test_aggregate_all_cancelled_has_no_delay_stats():
    # Que des suppressions : aucune stat de retard, onTimePct absent (fenêtre null
    # côté app), cancelledPct = 100. 5 observations pour passer le seuil de publication.
    recs = [{"cancelled": True, "finalDelayS": None, "skippedStops": 0}] * 5
    out = _aggregate(recs)
    assert out["obs"] == 5
    assert out["cancelledPct"] == 100
    assert "onTimePct" not in out
    assert "medianDelayMin" not in out


def test_aggregate_sous_le_seuil_ne_publie_aucun_pourcentage():
    # 100 % à l'heure sur 1 trajet, c'est une anecdote affichée comme une certitude.
    # Sous le seuil on ne publie que le brut — et surtout pas un pourcentage.
    out = _aggregate([{"cancelled": False, "finalDelayS": 0, "skippedStops": 0}])
    assert out == {"obs": 1, "enough": False}
    assert _aggregate([{"cancelled": False, "finalDelayS": 0, "skippedStops": 0}] * 5)["enough"]


def test_aggregate_p90_ignore_l_incident_unique():
    # 9 trajets à l'heure + 1 incident à 45 min : le max reste à 45 (et le restera un
    # an), le p90 dit ce que vit l'usager 9 fois sur 10.
    recs = [{"cancelled": False, "finalDelayS": 0, "skippedStops": 0}] * 9 + [
        {"cancelled": False, "finalDelayS": 2700, "skippedStops": 0}
    ]
    out = _aggregate(recs)
    assert out["maxDelayMin"] == 45
    assert out["p90DelayMin"] == 0


def test_aggregate_exploite_maxdelay_et_skipped():
    # maxDelayS et skippedStops étaient collectés sans être lus : un trajet parti à
    # +10 et arrivé à l'heure a rattrapé, un trajet qui saute un arrêt s'est allégé.
    recs = [
        {"cancelled": False, "finalDelayS": 0, "maxDelayS": 600, "skippedStops": 1},
        {"cancelled": False, "finalDelayS": 60, "maxDelayS": 60, "skippedStops": 0},
        {"cancelled": False, "finalDelayS": 0, "maxDelayS": 0, "skippedStops": 0},
        {"cancelled": False, "finalDelayS": 0, "maxDelayS": 0, "skippedStops": 0},
        {"cancelled": False, "finalDelayS": 0, "maxDelayS": 0, "skippedStops": 0},
    ]
    out = _aggregate(recs)
    assert out["recoveredPct"] == 20  # 1 trajet sur 5 a rattrapé >= 2 min
    assert out["skippedPct"] == 20


_LINE32 = {
    "trips": [
        {"tripId": "OCESN889439_x", "serviceId": "A"},
        {"tripId": "OCESN889485_x", "serviceId": "A"},
    ],
    "calendarDates": [{"serviceId": "A", "date": "2026-08-16", "exception": "added"}],
}


def _rec(delay):
    return {
        "finalDelayS": delay,
        "maxDelayS": delay or 0,
        "skippedStops": 0,
        "cancelled": False,
        "stops": [],
    }


def test_merge_history_stampe_la_couverture_et_reste_idempotent(tmp_path, monkeypatch):
    # Le flux ne garde pas la journée écoulée : un train jamais échantillonné doit
    # rester visible comme manquant, pas disparaître du dénominateur.
    monkeypatch.setattr(collect, "ROOT", tmp_path)
    (tmp_path / "history").mkdir()

    merge_history({"20260816": {"889439": _rec(0)}}, "2026-08-16T10:00:00+00:00", _LINE32)
    day = json.loads((tmp_path / "history" / "2026-08-16.json").read_text())
    assert day["coverage"] == {
        "scheduled": 2,
        "observed": 1,
        "pct": 50,
        "missing": ["889485"],
    }

    # Second passage : le train manquant est vu, la couverture se referme et le
    # retard final le plus tardif prime (fusion idempotente par date de service).
    merge_history({"20260816": {"889485": _rec(120)}}, "2026-08-16T10:30:00+00:00", _LINE32)
    day = json.loads((tmp_path / "history" / "2026-08-16.json").read_text())
    assert day["coverage"]["pct"] == 100
    assert day["coverage"]["missing"] == []
    assert len(day["samples"]) == 2
    assert day["trains"]["889485"]["finalDelayS"] == 120
