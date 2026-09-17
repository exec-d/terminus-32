#!/usr/bin/env python3
"""Extrait le tracé de la ligne 32 depuis OpenStreetMap, pour `track/line32.json`.

Le GTFS national SNCF **ne publie pas de `shapes.txt`** : l'app ne dispose donc
d'aucune géométrie de voie, et sa jauge de progression interpole à vol d'oiseau
entre deux gares. Sur une jauge, invisible ; sur une carte, le point coupe à
travers la campagne. Ce script produit la géométrie qui manque.

## Pourquoi un plus court chemin plutôt qu'une relation OSM

On pourrait chercher la relation `type=route` de la ligne et lire ses membres.
C'est plus direct, et c'est justement le problème : cela fait dépendre le
résultat d'un étiquetage que personne ici ne contrôle, sur un objet qu'un
contributeur peut scinder, renommer ou retagger un mardi soir. Le jour où la
relation change de forme, le script rend un tracé faux sans rien signaler.

À la place : on charge **toutes** les voies ferrées du corridor, on en fait un
graphe, et on cherche le plus court chemin d'une gare à la suivante. La seule
hypothèse est qu'un train relie deux gares par les rails, et que le chemin le
plus court entre elles est celui qu'il emprunte — vrai sur une ligne comme la
32, qui n'a pas d'itinéraire alternatif entre deux arrêts consécutifs. Les voies
de service (garages, faisceaux) sont écartées à la source : elles créeraient des
raccourcis qui n'en sont pas.

## Ce que le script refuse de produire

Un tracé faux est pire que pas de tracé : l'app dégrade proprement quand le
fichier est absent, alors qu'une géométrie erronée placerait le train dans un
champ avec le même aplomb qu'ailleurs. D'où trois garde-fous, qui font échouer
le run plutôt que d'écrire :

- chaque gare doit tomber à moins de `MAX_SNAP_M` d'un nœud ferroviaire ;
- chaque couple de gares consécutives doit être relié dans le graphe ;
- la longueur totale doit rester dans un rapport plausible à la distance à vol
  d'oiseau — un plus court chemin qui part par Genève reste un plus court
  chemin, et c'est ce contrôle-là qui l'attrape.

L'ordre des gares vient du trajet le plus long de `line32.json`, pas d'un tri
géographique : la ligne 32 passe par Part-Dieu **puis** Perrache **puis** Vaise,
donc elle revient sur ses pas, et un tri nord-sud la couperait de son terminus.

Usage : `python tools/extract_track.py` (écrit `track/line32.json`).
Données © les contributeurs OpenStreetMap, ODbL — compatible avec le reste du
dépôt.
"""

import heapq
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "track" / "line32.json"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Corridor Bourg-en-Bresse ⇄ Lyon, avec de la marge de part et d'autre : le plus
# court chemin doit pouvoir contourner, pas seulement suivre une ligne droite.
# Ordre Overpass : sud, ouest, nord, est.
BBOX = (45.68, 4.72, 46.28, 5.32)

# Rayon terrestre moyen (m). Aux 60 km de la ligne, l'écart entre sphère et
# ellipsoïde est sans effet sur un tracé simplifié à 8 m près.
EARTH_R = 6_371_000.0

# Une gare doit tomber près d'un rail. 300 m couvre l'écart entre le point
# « StopArea » du GTFS (souvent le bâtiment voyageurs) et la voie elle-même,
# sans laisser passer une gare rattachée à une autre ligne.
MAX_SNAP_M = 300.0

# Tolérance de simplification. À 8 m, l'écart au tracé réel est plus petit que
# l'épaisseur d'un trait à l'écran, à tous les zooms que l'app propose.
SIMPLIFY_M = 8.0

# Rapport longueur du tracé / distance à vol d'oiseau, bornes d'acceptation.
# Une voie ferrée est toujours plus longue que la corde ; au-delà de 1,8 on ne
# suit plus la ligne mais un détour par ailleurs.
MIN_RATIO, MAX_RATIO = 1.0, 1.8

# Même contrôle, tronçon par tronçon. Un détour de 20 km entre deux gares
# voisines se noie dans le total d'une ligne de 60 km ; ici, non. La borne est
# haute parce que les tronçons lyonnais le sont réellement — Part-Dieu →
# Perrache emprunte une boucle sans rapport avec la corde.
MAX_SEGMENT_RATIO = 2.0

PRECISION = 5
ATTRIBUTION = "© les contributeurs OpenStreetMap (ODbL)"

# On écarte les garages, faisceaux et antennes de dépôt : ils relient des points
# que nul train de voyageurs ne parcourt, et offriraient au plus court chemin des
# raccourcis imaginaires. Les **communications** entre voies (`service=crossover`),
# elles, restent : ce sont de vraies voies, empruntées par de vrais trains, et ce
# sont souvent les seuls points où les deux voies d'une ligne à double voie se
# rejoignent. Les exclure force le chemin à courir jusqu'au prochain aiguillage.
QUERY = """[out:json][timeout:300];
way["railway"="rail"]["service"!~"^(yard|siding|spur)$"]({s},{w},{n},{e});
out body geom;
"""


# --------------------------------------------------------------------------
# Géométrie
# --------------------------------------------------------------------------

def haversine(a, b):
    """Distance en mètres entre deux couples (lat, lon)."""
    lat1, lon1 = a
    lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(h))


def _plane(points):
    """Projette des (lat, lon) en mètres sur un plan local.

    Équirectangulaire centrée sur le premier point : sur 60 km de long et 40 de
    large, la déformation reste très en deçà de la tolérance de simplification.
    Sert uniquement à mesurer des écarts perpendiculaires, jamais à produire des
    coordonnées publiées.
    """
    lat0 = math.radians(points[0][0])
    k = math.cos(lat0)
    return [
        (math.radians(lon) * k * EARTH_R, math.radians(lat) * EARTH_R)
        for lat, lon in points
    ]


def _perp(p, a, b):
    """Distance du point `p` au segment `ab`, tous en mètres planaires."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def simplify_indices(points, epsilon_m=SIMPLIFY_M, pinned=()):
    """Index des points retenus par Douglas-Peucker, dans l'ordre.

    Itératif et non récursif : la version récursive dépasse la pile de Python
    sur une ligne de 60 km.

    Conserve toujours les deux extrémités et les index de `pinned` — les gares.
    Une gare doit rester un **sommet** du tracé : sinon son abscisse curviligne
    devrait être retrouvée par projection à l'exécution, et une projection sur un
    tracé qui revient sur ses pas, comme celui-ci dans Lyon, n'a pas de réponse
    unique.
    """
    if len(points) < 3:
        return list(range(len(points)))
    flat = _plane(points)
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    for i in pinned:
        keep[i] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        # Un point imposé dans l'intervalle le scinde d'office : le segment de
        # référence du Douglas-Peucker ne doit jamais enjamber une gare.
        forced = next((k for k in range(i + 1, j) if keep[k]), None)
        if forced is not None:
            stack.append((i, forced))
            stack.append((forced, j))
            continue
        worst, at = -1.0, None
        for k in range(i + 1, j):
            d = _perp(flat[k], flat[i], flat[j])
            if d > worst:
                worst, at = d, k
        if worst > epsilon_m:
            keep[at] = True
            stack.append((i, at))
            stack.append((at, j))
    return [i for i, k in enumerate(keep) if k]


def simplify(points, epsilon_m=SIMPLIFY_M, pinned=()):
    """Les points retenus par [simplify_indices]."""
    return [points[i] for i in simplify_indices(points, epsilon_m, pinned)]


def encode_polyline(points, precision=PRECISION):
    """Encodage polyligne de Google — le même que celui d'OSRM.

    ~10 octets par point contre ~40 pour un couple de flottants JSON, ce qui
    fait la différence entre un asset embarquable et un fichier qu'on renonce à
    télécharger sur un réseau de train.
    """
    factor = 10 ** precision
    out = []
    prev_lat = prev_lon = 0
    for lat, lon in points:
        lat_i = int(round(lat * factor))
        lon_i = int(round(lon * factor))
        for delta in (lat_i - prev_lat, lon_i - prev_lon):
            v = ~(delta << 1) if delta < 0 else (delta << 1)
            while v >= 0x20:
                out.append(chr((0x20 | (v & 0x1F)) + 63))
                v >>= 5
            out.append(chr(v + 63))
        prev_lat, prev_lon = lat_i, lon_i
    return "".join(out)


# --------------------------------------------------------------------------
# Graphe ferroviaire
# --------------------------------------------------------------------------

def build_graph(ways):
    """Construit (adjacence, coordonnées) à partir des voies Overpass.

    Les nœuds sont identifiés par leur **id OSM**, et non par leurs coordonnées
    arrondies : c'est ce qui fait qu'une bifurcation est un vrai embranchement
    du graphe et non deux voies qui se frôlent. Deux rails qui se croisent sans
    aiguille ne partagent pas de nœud, et le graphe ne les relie donc pas — ce
    qui est exactement le comportement voulu.
    """
    adj, coords = {}, {}
    for way in ways:
        ids = way.get("nodes") or []
        geom = way.get("geometry") or []
        if len(ids) != len(geom) or len(ids) < 2:
            # Géométrie tronquée (voie coupée par la bbox) : inexploitable comme
            # arête, mais ses nœuds connus restent utiles au reste du graphe.
            continue
        for nid, pt in zip(ids, geom):
            coords[nid] = (pt["lat"], pt["lon"])
        for a, b in zip(ids, ids[1:]):
            d = haversine(coords[a], coords[b])
            adj.setdefault(a, []).append((b, d))
            adj.setdefault(b, []).append((a, d))
    return adj, coords


def nearest_node(coords, point):
    """Nœud du graphe le plus proche de `point`, et sa distance en mètres."""
    best, best_d = None, float("inf")
    for nid, c in coords.items():
        d = haversine(c, point)
        if d < best_d:
            best, best_d = nid, d
    return best, best_d


def costs_to(adj, start, targets):
    """Coût du plus court chemin de `start` vers chacune des `targets`.

    S'arrête dès que toutes les cibles sont atteintes : sur un graphe de cette
    taille, la différence entre « jusqu'à la gare suivante » et « jusqu'au bout
    du corridor » n'est pas négligeable, et on lance cette fonction des dizaines
    de fois.
    """
    remaining = set(targets)
    out = {}
    dist = {start: 0.0}
    seen = set()
    queue = [(0.0, start)]
    while queue and remaining:
        d, node = heapq.heappop(queue)
        if node in seen:
            continue
        seen.add(node)
        if node in remaining:
            out[node] = d
            remaining.discard(node)
        for nxt, w in adj.get(node, ()):
            if nxt in seen:
                continue
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(queue, (nd, nxt))
    return out


def candidate_nodes(coords, point, max_m=None, limit=4, min_sep_m=20.0):
    """Nœuds plausibles pour une gare : un par voie, pas quatre sur la même.

    Une ligne à double voie est, dans OSM, deux chemins parallèles distincts. Le
    nœud le plus proche d'une gare tombe donc sur l'une **ou** l'autre, au hasard
    du dessin — et si deux gares voisines tirent chacune la leur, le plus court
    chemin doit courir jusqu'à la communication suivante et revenir. Mesuré sur
    la ligne 32 : 18,8 km de rail pour 3,5 km à vol d'oiseau entre Saint-Marcel
    et Saint-André.

    On rend donc plusieurs candidats, séparés d'au moins `min_sep_m` pour qu'ils
    représentent des voies différentes et non trois traverses du même rail ;
    c'est l'assemblage qui choisira la combinaison cohérente.
    """
    max_m = MAX_SNAP_M if max_m is None else max_m
    near = sorted(
        ((haversine(c, point), nid, c) for nid, c in coords.items() if haversine(c, point) <= max_m),
        key=lambda t: t[0],
    )
    picked = []
    for _, nid, c in near:
        if all(haversine(c, coords[other]) >= min_sep_m for other in picked):
            picked.append(nid)
            if len(picked) == limit:
                break
    return picked


def shortest_path(adj, start, goal):
    """Dijkstra. Rend la liste des nœuds traversés, ou `None` si non relié."""
    if start == goal:
        return [start]
    dist = {start: 0.0}
    prev = {}
    seen = set()
    queue = [(0.0, start)]
    while queue:
        d, node = heapq.heappop(queue)
        if node in seen:
            continue
        seen.add(node)
        if node == goal:
            break
        for nxt, w in adj.get(node, ()):
            if nxt in seen:
                continue
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                prev[nxt] = node
                heapq.heappush(queue, (nd, nxt))
    if goal not in dist:
        return None
    path, node = [goal], goal
    while node != start:
        node = prev[node]
        path.append(node)
    path.reverse()
    return path


def stitch(adj, coords, stations):
    """Tracé complet : les plus courts chemins de gare à gare, bout à bout.

    `stations` est la liste ordonnée des (lat, lon) des arrêts, dans l'ordre du
    trajet — pas dans un ordre géographique.

    Chaque gare a **plusieurs** nœuds candidats (une ligne à double voie est
    deux chemins parallèles dans OSM), et le choix ne peut pas se faire gare par
    gare : le nœud par lequel on quitte une gare doit être celui par lequel on y
    est entré, sinon le tracé saute. On résout donc la chaîne entière d'un coup,
    par programmation dynamique — le coût d'arriver à un candidat de la gare `i`
    est le meilleur coût d'arriver à un candidat de la gare `i-1`, plus le plus
    court chemin entre les deux.

    Rend `(points, index_des_gares)` : les gares sont des sommets du tracé brut,
    et leur position y est connue exactement plutôt que retrouvée après coup.
    """
    candidates = []
    for lat, lon in stations:
        picked = candidate_nodes(coords, (lat, lon))
        if not picked:
            nid, d = nearest_node(coords, (lat, lon))
            raise SystemExit(
                f"gare ({lat}, {lon}) à {d:.0f} m du rail le plus proche "
                f"(maximum {MAX_SNAP_M:.0f} m) — corridor trop étroit, ou "
                f"étiquetage OSM changé"
            )
        candidates.append(picked)

    # Aller : le meilleur coût pour atteindre chaque candidat de chaque gare,
    # et de quel candidat de la gare précédente il vient.
    best = {node: (0.0, None) for node in candidates[0]}
    back = []
    for previous, current in zip(candidates, candidates[1:]):
        reached, came_from = {}, {}
        for node in previous:
            if node not in best:
                continue
            for target, leg in costs_to(adj, node, current).items():
                total = best[node][0] + leg
                if total < reached.get(target, float("inf")):
                    reached[target] = total
                    came_from[target] = node
        if not reached:
            raise SystemExit(
                "aucun chemin ferroviaire entre deux gares consécutives : "
                "le corridor coupe la ligne, ou une voie manque dans OSM"
            )
        best = {node: (cost, came_from[node]) for node, cost in reached.items()}
        back.append(came_from)

    # Retour : on déroule la chaîne depuis le meilleur candidat de la dernière
    # gare, puis on reconstruit les chemins eux-mêmes — une seule fois chacun.
    end = min(best, key=lambda node: best[node][0])
    chain = [end]
    for came_from in reversed(back):
        chain.append(came_from[chain[-1]])
    chain.reverse()

    points = []
    at = [0]  # index, dans `points`, de chaque gare
    for a, b in zip(chain, chain[1:]):
        path = shortest_path(adj, a, b)
        if path is None:
            raise SystemExit(
                f"aucun chemin ferroviaire entre les nœuds {a} et {b} : "
                f"le corridor coupe la ligne, ou une voie manque dans OSM"
            )
        segment = [coords[n] for n in path]
        # Le premier point d'un segment est le dernier du précédent.
        points.extend(segment if not points else segment[1:])
        at.append(len(points) - 1)
    return points, at


def path_length(points):
    return sum(haversine(a, b) for a, b in zip(points, points[1:]))


# --------------------------------------------------------------------------
# Entrées / sorties
# --------------------------------------------------------------------------

def ordered_stations(line32):
    """Coordonnées des gares, dans l'ordre du trajet le plus long.

    Le trajet le plus long dessert toute la ligne ; sa séquence d'arrêts est
    donc l'ordre réel des gares le long des voies, aller-retour lyonnais
    compris.
    """
    by_id = {s["id"]: s for s in line32["stations"]}
    trip = max(line32["trips"], key=lambda t: len(t["stops"]))
    stops = sorted(trip["stops"], key=lambda s: s["seq"])
    out = []
    for stop in stops:
        station = by_id.get(stop["stationId"])
        if station is None:
            raise SystemExit(
                f"gare {stop['stationId']} absente du référentiel : "
                f"line32.json est incohérent"
            )
        out.append(station)
    return out


def fetch_ways(url=OVERPASS_URL, bbox=BBOX, timeout=600):
    """Interroge Overpass et rend les voies (`elements` de type `way`)."""
    query = QUERY.format(s=bbox[0], w=bbox[1], n=bbox[2], e=bbox[3])
    data = urllib.parse.urlencode({"data": query}).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "terminus-32/extract_track (github.com/exec-d/terminus-32)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    return [e for e in payload.get("elements", []) if e.get("type") == "way"]


def build(line32, ways):
    """Assemble le contenu de `track/line32.json`. Pur : aucun réseau, aucun I/O."""
    stations = ordered_stations(line32)
    adj, coords = build_graph(ways)
    if not coords:
        raise SystemExit("aucune voie ferrée dans la réponse Overpass")

    points, at = stitch(adj, coords, [(s["lat"], s["lon"]) for s in stations])

    # Garde-fou par tronçon, et non seulement sur le total : un détour de 20 km
    # entre deux gares voisines se noie dans une ligne de 60 km, alors qu'il
    # saute aux yeux ici. C'est le contrôle qui attrape un plus court chemin
    # passé par une autre ligne.
    for (i, a), (j, b) in zip(zip(at, stations), zip(at[1:], stations[1:])):
        rail = path_length(points[i : j + 1])
        straight = haversine((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        ratio = rail / straight if straight else 0.0
        if ratio > MAX_SEGMENT_RATIO:
            raise SystemExit(
                f"{a['name']} → {b['name']} : {rail / 1000:.1f} km de rail pour "
                f"{straight / 1000:.1f} km à vol d'oiseau (rapport {ratio:.2f}, "
                f"maximum {MAX_SEGMENT_RATIO}) — le plus court chemin passe "
                f"ailleurs que par la ligne"
            )

    length = path_length(points)
    straight = sum(
        haversine((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        for a, b in zip(stations, stations[1:])
    )
    ratio = length / straight if straight else 0.0
    if not (MIN_RATIO <= ratio <= MAX_RATIO):
        raise SystemExit(
            f"tracé de {length / 1000:.1f} km pour {straight / 1000:.1f} km à vol "
            f"d'oiseau (rapport {ratio:.2f}, attendu entre {MIN_RATIO} et "
            f"{MAX_RATIO}) — le plus court chemin passe probablement ailleurs"
        )

    kept = simplify_indices(points, pinned=at)
    simplified = [points[i] for i in kept]

    # Abscisse curviligne de chaque gare **sur le tracé publié**, en mètres.
    # C'est ce qui dispense l'app de projeter une gare sur la polyligne à
    # l'exécution : dans Lyon, le tracé passe deux fois au même endroit, et une
    # projection y aurait deux réponses aussi défendables l'une que l'autre.
    rank = {index: position for position, index in enumerate(kept)}
    cumulative = [0.0]
    for a, b in zip(simplified, simplified[1:]):
        cumulative.append(cumulative[-1] + haversine(a, b))

    return {
        "version": 1,
        "precision": PRECISION,
        "attribution": ATTRIBUTION,
        "polyline": encode_polyline(simplified),
        "stations": [
            {"id": station["id"], "offset": round(cumulative[rank[index]])}
            for station, index in zip(stations, at)
        ],
    }, {
        "points_bruts": len(points),
        "points_simplifiés": len(simplified),
        "longueur_km": round(length / 1000, 1),
        "vol_d_oiseau_km": round(straight / 1000, 1),
        "rapport": round(ratio, 2),
        "pire_tronçon": max(
            (
                round(path_length(points[i : j + 1]) / haversine(
                    (a["lat"], a["lon"]), (b["lat"], b["lon"])
                ), 2),
                f"{a['name']} → {b['name']}",
            )
            for (i, a), (j, b) in zip(
                zip(at, stations), zip(at[1:], stations[1:])
            )
        ),
    }


def main():
    line32 = json.loads((ROOT / "line32.json").read_text())
    ways = fetch_ways()
    print(f"voies ferrées reçues : {len(ways)}")
    track, stats = build(line32, ways)
    for key, value in stats.items():
        print(f"{key} : {value}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(track, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {OUT.relative_to(ROOT)} ({OUT.stat().st_size} octets)")


if __name__ == "__main__":
    main()
