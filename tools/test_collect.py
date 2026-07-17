import pytest

pytest.importorskip("google.transit")  # skip si la lib GTFS-RT n'est pas installée
from google.transit import gtfs_realtime_pb2  # noqa: E402
from collect import _aggregate, stops_from_trip_update  # noqa: E402


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
    # côté app), cancelledPct = 100.
    recs = [{"cancelled": True, "finalDelayS": None, "skippedStops": 0}] * 3
    out = _aggregate(recs)
    assert out["obs"] == 3
    assert out["cancelledPct"] == 100
    assert "onTimePct" not in out
    assert "medianDelayMin" not in out
