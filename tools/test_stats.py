from stats_lib import uic_of, daily_trend_point, merge_stops, aggregate_stations


def test_uic_of_extracts_code():
    assert uic_of("StopPoint:OCE87743005") == "87743005"
    assert uic_of("StopArea:OCE87723783") == "87723783"
    assert uic_of("87721001") == "87721001"
    assert uic_of(None) is None
    assert uic_of("no-digits-here") is None


def _day(trains):
    return {"date": "2026-07-08", "samples": [], "trains": trains}


def test_trend_counts_cancelled_as_not_on_time():
    # 1 à l'heure, 1 en retard, 1 supprimé → obs 3, onTime 1/3, cancelled 1/3.
    day = _day(
        {
            "1": {"finalDelayS": 0, "cancelled": False, "skippedStops": 0, "maxDelayS": 0},
            "2": {"finalDelayS": 600, "cancelled": False, "skippedStops": 0, "maxDelayS": 600},
            "3": {"finalDelayS": None, "cancelled": True, "skippedStops": 0, "maxDelayS": 0},
        }
    )
    out = daily_trend_point(day)
    assert out["date"] == "2026-07-08"
    assert out["obs"] == 3
    assert out["onTimePct"] == 33  # round(100*1/3)
    assert out["cancelledPct"] == 33  # round(100*1/3)
    assert out["onTimePct"] + out["cancelledPct"] <= 100


def test_trend_on_time_threshold_is_300s():
    day = _day(
        {
            "1": {"finalDelayS": 300, "cancelled": False, "skippedStops": 0, "maxDelayS": 300},
            "2": {"finalDelayS": 301, "cancelled": False, "skippedStops": 0, "maxDelayS": 301},
        }
    )
    out = daily_trend_point(day)
    assert out["onTimePct"] == 50  # 300s à l'heure, 301s non


def test_trend_empty_day():
    out = daily_trend_point(_day({}))
    assert out == {"date": "2026-07-08", "obs": 0, "onTimePct": 0, "cancelledPct": 0}


def test_merge_stops_prefers_non_null_and_ors_skipped():
    a = [{"uic": "1", "delayS": None, "skipped": False}, {"uic": "2", "delayS": 60, "skipped": False}]
    b = [{"uic": "1", "delayS": 120, "skipped": True}, {"uic": "3", "delayS": 0, "skipped": False}]
    out = merge_stops(a, b)
    by = {s["uic"]: s for s in out}
    assert by["1"] == {"uic": "1", "delayS": 120, "skipped": True}  # b remplit le None + OR skipped
    assert by["2"] == {"uic": "2", "delayS": 60, "skipped": False}  # a seul
    assert by["3"] == {"uic": "3", "delayS": 0, "skipped": False}  # b seul
    assert [s["uic"] for s in out] == ["1", "2", "3"]  # trié


def test_merge_stops_is_order_independent():
    a = [{"uic": "1", "delayS": 60, "skipped": False}]
    b = [{"uic": "1", "delayS": None, "skipped": True}]
    # b n'écrase pas le delay non-None de a par un None ; skipped OR.
    assert merge_stops(a, b) == merge_stops(b, a)
    assert merge_stops(a, b)[0] == {"uic": "1", "delayS": 60, "skipped": True}


def _ref():
    return [
        {"id": "StopArea:OCE1111111", "name": "Alpha"},
        {"id": "StopArea:OCE2222222", "name": "Beta"},
        {"id": "StopArea:OCE3333333", "name": "Gamma"},
    ]


def _day_with_stops(stops_by_train):
    return {"date": "2026-07-08", "samples": [], "trains": {
        num: {"cancelled": False, "finalDelayS": 0, "maxDelayS": 0, "skippedStops": 0, "stops": stops}
        for num, stops in stops_by_train.items()
    }}


def test_aggregate_stations_median_and_skip():
    days = [
        _day_with_stops({
            "T1": [{"uic": "1111111", "delayS": 0, "skipped": False}, {"uic": "2222222", "delayS": 120, "skipped": False}],
            "T2": [{"uic": "1111111", "delayS": 60, "skipped": False}, {"uic": "2222222", "delayS": None, "skipped": True}],
        })
    ]
    out = aggregate_stations(days, _ref())
    assert [s["name"] for s in out] == ["Alpha", "Beta", "Gamma"]  # ordre du ref
    alpha, beta, gamma = out
    assert alpha["uic"] == "1111111" and alpha["order"] == 0 and alpha["obs"] == 2
    assert alpha["medianDelayS"] == 60  # median(0, 60) -> élément haut
    assert alpha["skippedPct"] == 0
    assert beta["obs"] == 2 and beta["medianDelayS"] == 120 and beta["skippedPct"] == 50
    assert gamma["obs"] == 0 and gamma["medianDelayS"] is None and gamma["skippedPct"] == 0
