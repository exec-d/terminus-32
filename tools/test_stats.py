from stats_lib import uic_of, daily_trend_point


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
