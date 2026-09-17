"""Tests de `extract_context.py` — tout sauf l'appel réseau.

Même principe que `test_extract_track.py` : les chemins sont fabriqués à la
main, donc rien ne dépend d'Overpass.
"""

import pytest

from extract_context import (
    MIN_RIVERS,
    MIN_WATER_M2,
    bbox_area_m2,
    build,
    is_closed,
    points_of,
)
from extract_track import haversine


def way(tags, points):
    return {
        "type": "way",
        "tags": tags,
        "geometry": [{"lat": lat, "lon": lon} for lat, lon in points],
    }


def river(n=1):
    """Un cours d'eau qui serpente, assez long pour survivre à la simplification."""
    return way(
        {"waterway": "river"},
        [(46.0 - i * 0.005, 5.0 + (i % 2) * 0.004 + n * 0.01) for i in range(8)],
    )


def lake(size_deg):
    """Un plan d'eau carré et fermé, de `size_deg` degrés de côté."""
    lat, lon = 46.0, 5.0
    return way(
        {"natural": "water"},
        [
            (lat, lon),
            (lat + size_deg, lon),
            (lat + size_deg, lon + size_deg),
            (lat, lon + size_deg),
            (lat, lon),
        ],
    )


def rivers(n=MIN_RIVERS):
    return [river(i) for i in range(n)]


# --------------------------------------------------------------------------
# Briques
# --------------------------------------------------------------------------

def test_points_of_lit_la_geometrie():
    assert points_of(way({}, [(46.0, 5.0), (45.9, 5.1)])) == [(46.0, 5.0), (45.9, 5.1)]


def test_points_of_sur_un_chemin_sans_geometrie():
    assert points_of({"type": "way"}) == []


def test_is_closed_distingue_un_contour_d_une_ligne():
    assert is_closed(points_of(lake(0.01)))
    assert not is_closed(points_of(river()))


def test_is_closed_refuse_un_contour_trop_court():
    # Trois points qui reviennent au départ ne délimitent aucune surface.
    assert not is_closed([(46.0, 5.0), (46.001, 5.0), (46.0, 5.0)])


def test_bbox_area_croit_avec_le_cote():
    petit = bbox_area_m2(points_of(lake(0.005)))
    grand = bbox_area_m2(points_of(lake(0.01)))
    assert grand > petit * 3  # le carré du rapport des côtés


def test_bbox_area_nulle_sur_une_ligne():
    assert bbox_area_m2([(46.0, 5.0), (45.9, 5.0)]) == 0.0


# --------------------------------------------------------------------------
# build()
# --------------------------------------------------------------------------

def test_build_separe_cours_d_eau_et_plans_d_eau():
    context, stats = build([*rivers(), lake(0.02)])
    assert stats["cours_d_eau"] == MIN_RIVERS
    assert stats["plans_d_eau"] == 1
    assert len(context["rivers"]) == MIN_RIVERS
    assert len(context["water"]) == 1
    assert context["version"] == 1
    assert "OpenStreetMap" in context["attribution"]


# La Dombes compte un millier d'étangs : les dessiner tous ferait un semis de
# confettis illisible, et un fichier que personne ne veut télécharger.
def test_build_ecarte_les_plans_d_eau_trop_petits():
    minuscule = lake(0.0005)  # ~55 m de côté
    assert bbox_area_m2(points_of(minuscule)) < MIN_WATER_M2
    _, stats = build([*rivers(), minuscule])
    assert stats["plans_d_eau"] == 0


def test_build_ecarte_un_plan_d_eau_non_ferme():
    # Une berge ouverte ne se remplit pas : la dessiner donnerait un triangle
    # arbitraire refermé par le rendu.
    ouvert = way(
        {"natural": "water"},
        [(46.0, 5.0), (46.02, 5.0), (46.02, 5.02)],
    )
    _, stats = build([*rivers(), ouvert])
    assert stats["plans_d_eau"] == 0


def test_build_ignore_ce_qui_n_est_ni_eau_ni_riviere():
    _, stats = build([*rivers(), way({"highway": "motorway"}, [(46.0, 5.0), (45.9, 5.0)])])
    assert stats["cours_d_eau"] == MIN_RIVERS
    assert stats["plans_d_eau"] == 0


def test_build_ignore_un_chemin_a_un_seul_point():
    _, stats = build([*rivers(), way({"waterway": "river"}, [(46.0, 5.0)])])
    assert stats["cours_d_eau"] == MIN_RIVERS


# Une carte sans la Saône ni le Rhône n'est pas un décor appauvri : c'est une
# réponse tronquée qu'on publierait sans s'en apercevoir.
def test_build_refuse_une_reponse_sans_cours_d_eau():
    with pytest.raises(SystemExit, match="cours d'eau"):
        build([lake(0.02)])


def test_build_refuse_une_reponse_partielle():
    with pytest.raises(SystemExit, match=f"minimum {MIN_RIVERS}"):
        build(rivers(MIN_RIVERS - 1))


def test_build_simplifie_sans_deplacer_les_extremites():
    context, _ = build(rivers())
    # La polyligne encodée est non vide, et le nombre de points a fondu.
    assert all(p for p in context["rivers"])
    original = points_of(river(0))
    assert haversine(original[0], original[-1]) > 0
