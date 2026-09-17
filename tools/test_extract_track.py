"""Tests de `extract_track.py` — tout sauf l'appel réseau.

`fetch_ways` est la seule fonction non couverte : elle ne fait qu'un POST et un
`json.load`. Tout le reste — graphe, plus court chemin, garde-fous, encodage —
tourne ici sur des voies fabriquées à la main, donc sans Overpass.
"""

import math

import pytest

from extract_track import (
    MAX_SEGMENT_RATIO,
    MAX_SNAP_M,
    QUERY,
    build,
    candidate_nodes,
    build_graph,
    encode_polyline,
    haversine,
    nearest_node,
    ordered_stations,
    path_length,
    shortest_path,
    simplify,
    simplify_indices,
    stitch,
)


# --------------------------------------------------------------------------
# Fabrique de voies : une « ligne » nord-sud de nœuds régulièrement espacés.
# --------------------------------------------------------------------------

def way(node_ids, coords):
    """Une voie Overpass : ids et géométrie, index par index."""
    return {
        "type": "way",
        "nodes": list(node_ids),
        "geometry": [{"lat": coords[n][0], "lon": coords[n][1]} for n in node_ids],
    }


def straight_line(n=11, lat0=46.0, lon=5.0, step=0.01, first_id=1):
    """`n` nœuds alignés sur un méridien, du nord vers le sud."""
    return {first_id + i: (lat0 - i * step, lon) for i in range(n)}


# --------------------------------------------------------------------------
# Géométrie
# --------------------------------------------------------------------------

def test_haversine_sur_une_distance_connue():
    # Un degré de latitude vaut ~111,2 km sur une sphère de rayon moyen.
    d = haversine((45.0, 5.0), (46.0, 5.0))
    assert 111_000 < d < 111_400


def test_encode_polyline_donne_la_sortie_de_reference_de_google():
    # Exemple canonique de la spécification : si notre encodeur en diverge, il
    # diverge aussi de tout décodeur — dont celui de l'app.
    points = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    assert encode_polyline(points) == r"_p~iF~ps|U_ulLnnqC_mqNvxq`@"


def test_simplify_retire_les_points_alignes_et_garde_les_extremites():
    points = [(46.0, 5.0), (45.99, 5.0), (45.98, 5.0), (45.97, 5.0)]
    out = simplify(points)
    assert out == [points[0], points[-1]]


def test_simplify_garde_un_point_qui_s_ecarte_plus_que_la_tolerance():
    # ~0,001° de longitude ≈ 77 m à cette latitude : bien au-delà des 8 m.
    points = [(46.0, 5.0), (45.99, 5.001), (45.98, 5.0)]
    out = simplify(points)
    assert len(out) == 3


def test_simplify_tient_une_ligne_longue_sans_deborder_la_pile():
    # La version récursive de Douglas-Peucker meurt sur ce cas ; l'itérative non.
    points = [(46.0 - i * 0.00001, 5.0 + (i % 2) * 0.0001) for i in range(20_000)]
    out = simplify(points)
    assert out[0] == points[0] and out[-1] == points[-1]


# --------------------------------------------------------------------------
# Graphe
# --------------------------------------------------------------------------

def test_build_graph_relie_deux_voies_qui_partagent_un_noeud():
    coords = straight_line(5)
    ways = [way([1, 2, 3], coords), way([3, 4, 5], coords)]
    adj, got = build_graph(ways)
    assert set(got) == {1, 2, 3, 4, 5}
    assert shortest_path(adj, 1, 5) == [1, 2, 3, 4, 5]


def test_build_graph_ne_relie_pas_deux_voies_qui_se_croisent_sans_aiguille():
    # Deux rails au même endroit mais sans nœud commun : dans la réalité, un
    # saut-de-mouton ou un passage supérieur. Les relier inventerait un
    # itinéraire qu'aucun train ne peut prendre.
    coords = {**straight_line(3, first_id=1), **straight_line(3, first_id=10)}
    ways = [way([1, 2, 3], coords), way([10, 11, 12], coords)]
    adj, _ = build_graph(ways)
    assert shortest_path(adj, 1, 12) is None


def test_build_graph_ignore_une_voie_a_la_geometrie_tronquee():
    # Overpass rend parfois des ids sans la géométrie correspondante (voie
    # coupée par la bbox). Mieux vaut l'écarter que d'apparier ids et points au
    # petit bonheur.
    coords = straight_line(3)
    tronquee = {"type": "way", "nodes": [1, 2, 3], "geometry": [{"lat": 46.0, "lon": 5.0}]}
    adj, got = build_graph([tronquee])
    assert got == {} and adj == {}


def test_shortest_path_prend_le_chemin_le_plus_court_pas_le_premier_trouve():
    # Un détour de trois nœuds et une liaison directe entre les mêmes bouts.
    coords = {
        1: (46.0, 5.0),
        2: (45.99, 5.0),      # direct
        3: (46.0, 5.05),      # détour, nettement plus long
        4: (45.99, 5.05),
    }
    ways = [way([1, 2], coords), way([1, 3, 4, 2], coords)]
    adj, _ = build_graph(ways)
    assert shortest_path(adj, 1, 2) == [1, 2]


def test_nearest_node_rend_le_noeud_et_sa_distance():
    coords = straight_line(3)
    nid, d = nearest_node(coords, (45.9901, 5.0))
    assert nid == 2 and d < 20


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

def test_stitch_ne_duplique_pas_le_point_de_jonction():
    coords = straight_line(5)
    adj, got = build_graph([way([1, 2, 3, 4, 5], coords)])
    points, at = stitch(adj, got, [coords[1], coords[3], coords[5]])
    assert points == [coords[i] for i in (1, 2, 3, 4, 5)]
    # Et les gares sont repérées à leur place dans le tracé, pas retrouvées après.
    assert [points[i] for i in at] == [coords[1], coords[3], coords[5]]


def test_stitch_suit_l_ordre_donne_meme_s_il_revient_sur_ses_pas():
    # Le cas lyonnais : Part-Dieu, puis Perrache plus au sud, puis Vaise au
    # nord. Un tracé qui « optimiserait » cet ordre couperait le terminus.
    coords = straight_line(5)
    adj, got = build_graph([way([1, 2, 3, 4, 5], coords)])
    points, _ = stitch(adj, got, [coords[1], coords[5], coords[3]])
    assert points[0] == coords[1]
    assert points[-1] == coords[3]
    # Le point le plus au sud est bien traversé avant de remonter.
    assert coords[5] in points


def test_stitch_refuse_une_gare_trop_loin_du_rail():
    coords = straight_line(3)
    adj, got = build_graph([way([1, 2, 3], coords)])
    loin = (46.0, 5.5)  # ~38 km à l'est de la voie
    with pytest.raises(SystemExit, match="du rail le plus proche"):
        stitch(adj, got, [coords[1], loin])


def test_stitch_refuse_deux_gares_non_reliees():
    coords = {**straight_line(3, first_id=1), **straight_line(3, lat0=45.9, first_id=10)}
    adj, got = build_graph([way([1, 2, 3], coords), way([10, 11, 12], coords)])
    with pytest.raises(SystemExit, match="aucun chemin ferroviaire"):
        stitch(adj, got, [coords[1], coords[12]])


# --------------------------------------------------------------------------
# Référentiel
# --------------------------------------------------------------------------

def _line32(stop_ids, extra_trip_len=2):
    stations = [
        {"id": sid, "name": sid, "lat": 46.0 - i * 0.01, "lon": 5.0}
        for i, sid in enumerate(stop_ids)
    ]
    long_trip = {
        "tripId": "LONG",
        "stops": [{"stationId": sid, "seq": i + 1} for i, sid in enumerate(stop_ids)],
    }
    court = {
        "tripId": "COURT",
        "stops": [
            {"stationId": sid, "seq": i + 1}
            for i, sid in enumerate(stop_ids[:extra_trip_len])
        ],
    }
    return {"stations": stations, "trips": [court, long_trip]}


def test_ordered_stations_prend_le_trajet_le_plus_long_et_suit_les_seq():
    data = _line32(["A", "B", "C", "D"])
    # `seq` fait foi, pas l'ordre du tableau : on le mélange pour le prouver.
    data["trips"][1]["stops"].reverse()
    out = ordered_stations(data)
    assert [s["id"] for s in out] == ["A", "B", "C", "D"]
    assert [(s["lat"], s["lon"]) for s in out] == [
        (46.0, 5.0), (45.99, 5.0), (45.98, 5.0), (45.97, 5.0)
    ]


def test_ordered_stations_refuse_une_gare_absente_du_referentiel():
    data = _line32(["A", "B"])
    data["trips"][1]["stops"].append({"stationId": "FANTOME", "seq": 3})
    with pytest.raises(SystemExit, match="absente du référentiel"):
        ordered_stations(data)


# --------------------------------------------------------------------------
# build() : le contrat de sortie et son dernier garde-fou
# --------------------------------------------------------------------------

def test_build_produit_une_polyligne_et_ses_chiffres():
    coords = straight_line(11)
    ways = [way(list(coords), coords)]
    data = _line32(["A", "B"])
    # Les gares du référentiel synthétique tombent sur les nœuds 1 et 2.
    track, stats = build(data, ways)
    assert track["version"] == 1
    assert track["precision"] == 5
    assert "OpenStreetMap" in track["attribution"]
    assert track["polyline"]
    assert stats["rapport"] == pytest.approx(1.0, abs=0.01)
    # Chaque gare porte son abscisse sur le tracé publié : la première à 0, la
    # suivante à la distance qui les sépare.
    assert [s["id"] for s in track["stations"]] == ["A", "B"]
    assert track["stations"][0]["offset"] == 0
    assert track["stations"][1]["offset"] == pytest.approx(
        haversine((46.0, 5.0), (45.99, 5.0)), abs=2
    )


def test_build_refuse_un_trace_trop_long_pour_la_distance_a_vol_d_oiseau():
    # Deux gares voisines, mais le seul rail qui les relie fait un grand détour :
    # un plus court chemin qui part par ailleurs reste un plus court chemin, et
    # c'est ce contrôle-là qui l'attrape.
    coords = {
        1: (46.0, 5.0),
        2: (46.0, 5.3),
        3: (45.7, 5.3),
        4: (45.99, 5.0),
    }
    ways = [way([1, 2, 3, 4], coords)]
    data = {
        "stations": [
            {"id": "A", "name": "A", "lat": 46.0, "lon": 5.0},
            {"id": "B", "name": "B", "lat": 45.99, "lon": 5.0},
        ],
        "trips": [{"tripId": "T", "stops": [
            {"stationId": "A", "seq": 1}, {"stationId": "B", "seq": 2},
        ]}],
    }
    with pytest.raises(SystemExit, match="rapport"):
        build(data, ways)


def test_build_refuse_une_reponse_overpass_vide():
    with pytest.raises(SystemExit, match="aucune voie ferrée"):
        build(_line32(["A", "B"]), [])


def test_path_length_somme_les_segments():
    points = [(46.0, 5.0), (45.99, 5.0), (45.98, 5.0)]
    assert path_length(points) == pytest.approx(
        haversine(points[0], points[1]) * 2, rel=1e-6
    )


def test_max_snap_reste_sous_le_demi_kilometre():
    # Garde-fou sur le garde-fou : desserré, il laisserait une gare s'accrocher
    # à la ligne d'à côté, et le tracé passerait par une voie que le train 32
    # n'emprunte pas.
    assert MAX_SNAP_M <= 500
    assert not math.isinf(MAX_SNAP_M)


# --------------------------------------------------------------------------
# Les gares restent des sommets, et le détour d'un seul tronçon se voit
# --------------------------------------------------------------------------

def test_simplify_garde_les_points_imposes_meme_alignes():
    # Sans `pinned`, ces trois points du milieu disparaissent : ils sont alignés.
    points = [(46.0 - i * 0.01, 5.0) for i in range(6)]
    assert simplify(points) == [points[0], points[-1]]
    assert simplify(points, pinned=[2]) == [points[0], points[2], points[-1]]


def test_simplify_indices_rend_des_index_exploitables():
    points = [(46.0 - i * 0.01, 5.0) for i in range(6)]
    idx = simplify_indices(points, pinned=[3])
    assert idx == [0, 3, 5]
    assert [points[i] for i in idx] == simplify(points, pinned=[3])


def test_simplify_ne_laisse_pas_un_segment_de_reference_enjamber_une_gare():
    # Le point 2 s'écarte franchement ; le point 4 est une gare sur la droite.
    # Si l'intervalle de référence enjambait la gare, elle pourrait disparaître.
    points = [(46.0, 5.0), (45.99, 5.0), (45.98, 5.01), (45.97, 5.0), (45.96, 5.0)]
    out = simplify(points, pinned=[3])
    assert points[3] in out


def test_build_refuse_un_troncon_qui_part_ailleurs_meme_si_le_total_tient():
    # Onze gares alignées ; entre les deux dernières, le seul rail fait un
    # crochet de plusieurs dizaines de kilomètres. Noyé dans le total, il passe
    # sous le rapport global — c'est le contrôle par tronçon qui l'attrape.
    coords = {i + 1: (46.0 - i * 0.02, 5.0) for i in range(11)}
    coords[100] = (45.82, 5.4)  # le crochet
    ids = list(range(1, 11))
    ways = [way(ids, coords), way([10, 100, 11], coords)]
    stations = [
        {"id": f"S{i}", "name": f"S{i}", "lat": coords[i + 1][0], "lon": coords[i + 1][1]}
        for i in range(11)
    ]
    data = {
        "stations": stations,
        "trips": [{"tripId": "T", "stops": [
            {"stationId": s["id"], "seq": i + 1} for i, s in enumerate(stations)
        ]}],
    }
    with pytest.raises(SystemExit, match="passe ailleurs que par la ligne"):
        build(data, ways)


def test_max_segment_ratio_reste_serre():
    # Desserré, il ne distinguerait plus un tronçon lyonnais sinueux d'un
    # détour par une autre ligne.
    assert 1.5 <= MAX_SEGMENT_RATIO <= 2.5


# --------------------------------------------------------------------------
# Double voie : la panne qui a coûté 18,8 km entre deux gares distantes de 3,5
# --------------------------------------------------------------------------

def double_track():
    """Deux voies parallèles à 23 m, reliées à leurs seules extrémités.

    C'est le dessin OSM d'une ligne à double voie : deux chemins distincts, qui
    ne se rejoignent qu'aux communications.
    """
    coords = {}
    for i in range(5):
        coords[1 + i] = (46.0 - i * 0.001, 5.0000)      # voie A
        coords[11 + i] = (46.0 - i * 0.001, 5.0003)     # voie B
    ways = [
        way([1, 2, 3, 4, 5], coords),
        way([11, 12, 13, 14, 15], coords),
        way([1, 11], coords),   # communication nord
        way([5, 15], coords),   # communication sud
    ]
    return coords, ways


def test_candidate_nodes_rend_une_voie_puis_l_autre_pas_trois_traverses():
    coords, ways = double_track()
    _, got = build_graph(ways)
    picked = candidate_nodes(got, (45.998, 5.0))
    # Le nœud le plus proche est sur la voie A ; son vis-à-vis sur la voie B
    # doit figurer, sinon l'assemblage n'a pas le choix.
    assert picked[0] == 3
    assert 13 in picked
    # Et deux candidats ne sont jamais le même rail à 5 m près.
    for a in picked:
        for b in picked:
            if a != b:
                assert haversine(got[a], got[b]) >= 20


def test_stitch_ne_change_pas_de_voie_entre_deux_gares_voisines():
    # Deux gares à 111 m, l'une collée à la voie A, l'autre à la voie B. En
    # prenant le nœud le plus proche de chacune, le chemin doit courir jusqu'à
    # une communication et revenir. En choisissant la chaîne d'un coup, il reste
    # sur une voie. C'est la panne mesurée sur la ligne 32, en miniature.
    coords, ways = double_track()
    adj, got = build_graph(ways)
    points, at = stitch(adj, got, [(45.998, 5.00000), (45.997, 5.00030)])

    assert path_length(points) < 200, "le tracé fait un détour par une communication"
    # Une seule voie empruntée : toutes les longitudes sont les mêmes.
    assert len({lon for _, lon in points}) == 1
    assert at == [0, len(points) - 1]


def test_la_requete_garde_les_communications_entre_voies():
    # Les exclure était la cause du détour : sur une ligne à double voie, ce
    # sont souvent les seuls points de jonction.
    assert "crossover" not in QUERY
    assert "yard|siding|spur" in QUERY
