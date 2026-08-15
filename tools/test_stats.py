from datetime import date

from stats_lib import (
    aggregate_stations,
    desserte_anomalies,
    percentile,
    train_station_stats,
    coverage_of,
    daily_trend_point,
    merge_stops,
    scheduled_numbers,
    station_order,
    train_number,
    uic_of,
)


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


def test_aggregate_stations_mean_median_skip_and_geo_order():
    days = [
        _day_with_stops({
            "T1": [{"uic": "1111111", "delayS": 0, "skipped": False}, {"uic": "2222222", "delayS": 120, "skipped": False}],
            "T2": [{"uic": "1111111", "delayS": 60, "skipped": False}, {"uic": "2222222", "delayS": None, "skipped": True}],
        })
    ]
    # Ordre géographique VOLONTAIREMENT différent de l'ordre du _ref : Beta, Gamma, Alpha.
    order = {"2222222": 0, "3333333": 1, "1111111": 2}
    out = aggregate_stations(days, _ref(), order)
    assert [s["name"] for s in out] == ["Beta", "Gamma", "Alpha"]  # rangé par order_by_uic
    assert [s["order"] for s in out] == [0, 1, 2]  # order final = index géographique
    by = {s["name"]: s for s in out}
    # Alpha : delays [0, 60] → médiane 60 (élément haut), moyenne 30.
    assert by["Alpha"]["obs"] == 2 and by["Alpha"]["medianDelayS"] == 60 and by["Alpha"]["meanDelayS"] == 30
    assert by["Alpha"]["skippedPct"] == 0
    assert by["Beta"]["obs"] == 2 and by["Beta"]["medianDelayS"] == 120 and by["Beta"]["meanDelayS"] == 120
    assert by["Beta"]["skippedPct"] == 50  # 1 skip sur 2
    assert by["Gamma"]["obs"] == 0 and by["Gamma"]["medianDelayS"] is None and by["Gamma"]["meanDelayS"] is None


def test_station_order_from_beb_to_lyon_trip():
    line32 = {
        "trips": [
            {"direction": "lyonToBeb", "stops": [  # sens retour : ordre inverse, ignoré
                {"stationId": "StopArea:OCE3333333", "seq": 0},
                {"stationId": "StopArea:OCE2222222", "seq": 1},
                {"stationId": "StopArea:OCE1111111", "seq": 2},
            ]},
            {"direction": "bebToLyon", "stops": [
                {"stationId": "StopArea:OCE1111111", "seq": 0},
                {"stationId": "StopArea:OCE2222222", "seq": 1},
                {"stationId": "StopArea:OCE3333333", "seq": 2},
            ]},
        ]
    }
    assert station_order(line32) == {"1111111": 0, "2222222": 1, "3333333": 2}


def test_train_number_extrait_le_numero_commercial():
    assert train_number("OCESN889439F1187_F:TER:FR:Line::ABC::87743005:87722025:12:2100:20260813") == "889439"
    assert train_number("sans-numero") is None
    assert train_number(None) is None


_LINE32 = {
    "trips": [
        {"tripId": "OCESN889439F1187_x", "serviceId": "A"},
        {"tripId": "OCESN889485F1187_x", "serviceId": "A"},
        {"tripId": "OCESN889441F1187_x", "serviceId": "B"},
    ],
    "calendarDates": [
        {"serviceId": "A", "date": "2026-08-16", "exception": "added"},
        {"serviceId": "B", "date": "2026-08-17", "exception": "added"},
        {"serviceId": "B", "date": "2026-08-16", "exception": "removed"},
    ],
}


def test_scheduled_numbers_ne_retient_que_les_services_actifs_du_jour():
    # Le service B est explicitement retiré le 16 : son train ne doit pas être attendu.
    assert scheduled_numbers(_LINE32, "2026-08-16") == {"889439", "889485"}
    assert scheduled_numbers(_LINE32, "2026-08-17") == {"889441"}


def test_scheduled_numbers_hors_calendrier_vaut_none():
    # Journée antérieure au référentiel : programme inconnu, surtout pas « 0 attendu ».
    assert scheduled_numbers(_LINE32, "2026-07-04") is None


def test_coverage_of_signale_les_trains_jamais_vus():
    cov = coverage_of({"1", "2", "3", "4"}, {"1": {}, "3": {}})
    assert cov == {"scheduled": 4, "observed": 2, "pct": 50, "missing": ["2", "4"]}


def test_coverage_of_ignore_les_trains_hors_programme():
    # Un train observé mais non programmé (renfort, erreur de calendrier) ne doit pas
    # faire dépasser 100 % : la couverture mesure le programme, pas le volume vu.
    cov = coverage_of({"1", "2"}, {"1": {}, "2": {}, "999": {}})
    assert cov["pct"] == 100
    assert cov["scheduled"] == 2
    assert cov["missing"] == []


def test_coverage_of_sans_programme_connu_reste_indetermine():
    cov = coverage_of(None, {"1": {}})
    assert cov == {"scheduled": None, "observed": 1, "pct": None, "missing": None}


def test_percentile_plus_proche_rang():
    assert percentile([0, 0, 0, 0, 0, 0, 0, 0, 0, 2700], 90) == 0
    assert percentile([0, 0, 0, 0, 0, 0, 0, 0, 2700, 2700], 90) == 2700
    assert percentile([], 90) is None
    assert percentile([42], 90) == 42


def _stop(uic, delay=0, skipped=False):
    return {"uic": uic, "delayS": None if skipped else delay, "skipped": skipped}


def _day_stops(date, trains):
    return {"date": date, "samples": [], "trains": trains}


def test_train_station_stats_ne_melange_pas_les_circulations():
    # Le 06:13 à l'heure et le 20:13 en retard passent par la même gare : les agréger
    # ensemble (ce que fait aggregate_stations) noie le train du soir. Ici on sépare.
    days = [
        _day_stops(
            f"2026-08-{d:02d}",
            {
                "889411": {"stops": [_stop("87723759", 0)]},
                "889439": {"stops": [_stop("87723759", 900)]},
            },
        )
        for d in range(10, 16)
    ]
    out = train_station_stats(days, {"87723759": 0}, {"week": 7}, date(2026, 8, 16))
    assert out["889411"]["87723759"]["week"]["onTimePct"] == 100
    assert out["889439"]["87723759"]["week"]["onTimePct"] == 0
    assert out["889439"]["87723759"]["week"]["p90DelayS"] == 900


def test_train_station_stats_applique_le_seuil():
    days = [_day_stops("2026-08-15", {"889411": {"stops": [_stop("87723759", 0)]}})]
    out = train_station_stats(days, {"87723759": 0}, {"week": 7}, date(2026, 8, 16))
    assert out["889411"]["87723759"]["week"] == {"obs": 1, "enough": False}


_DESSERTE = {
    "stations": [
        {"id": "A", "name": "Bourg-en-Bresse"},
        {"id": "B", "name": "Villars-les-Dombes"},
        {"id": "C", "name": "Lyon Perrache"},
    ],
    "trips": [
        {"tripId": "OCESN889441_complet", "serviceId": "PLEIN", "stops": [
            {"stationId": "A"}, {"stationId": "B"}, {"stationId": "C"}]},
        {"tripId": "OCESN889441_court", "serviceId": "COURT", "stops": [
            {"stationId": "A"}, {"stationId": "B"}]},
    ],
    "calendarDates": (
        # 3 lundis complets, 1 lundi raccourci → seul le dernier est une anomalie.
        [{"serviceId": "PLEIN", "date": d, "exception": "added"}
         for d in ("2026-08-17", "2026-08-24", "2026-08-31")]
        + [{"serviceId": "COURT", "date": "2026-09-07", "exception": "added"}]
        # Le dimanche a son propre schéma : jamais Perrache, ce n'est pas une anomalie.
        + [{"serviceId": "COURT", "date": d, "exception": "added"}
           for d in ("2026-08-16", "2026-08-23", "2026-08-30")]
    ),
}


def test_desserte_anomalies_repere_le_terminus_raccourci():
    out = desserte_anomalies(_DESSERTE, "2026-08-15")
    assert [(a["date"], a["train"], a["missing"]) for a in out] == [
        ("2026-09-07", "889441", ["Lyon Perrache"])
    ]


def test_desserte_anomalies_ignore_le_schema_propre_au_week_end():
    # Aucun dimanche ne doit sortir : la référence est calculée par jour de semaine.
    assert not [a for a in desserte_anomalies(_DESSERTE, "2026-08-15") if a["date"] == "2026-08-16"]


def test_desserte_anomalies_ne_regarde_pas_le_passe():
    assert desserte_anomalies(_DESSERTE, "2026-09-08") == []
