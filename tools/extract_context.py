#!/usr/bin/env python3
"""Extrait d'OpenStreetMap le décor de la carte, pour `context/line32.json`.

Le tracé seul ne fait pas une carte. Un trait et des pastilles, même nommées,
répètent ce que la liste des arrêts dit déjà mieux ; ce qui manque est ce à quoi
rattacher la ligne — l'eau, d'abord. La Saône et le Rhône placent Lyon en une
seconde, et les étangs disent la Dombes sans qu'on ait à l'écrire.

## Pourquoi l'eau, et presque rien d'autre

C'est le repère le plus lisible à petite échelle, et le plus stable : un cours
d'eau ne déménage pas, là où un lotissement ou une rocade changent d'année en
année. C'est aussi ce qui coûte le moins de traits pour le plus de sens.

Ce qu'on n'extrait **pas**, et pourquoi :

- les routes — elles rempliraient le cadre d'un maillage dont aucune ligne n'a
  de rapport avec un train ;
- les zones urbaines — leur contour OSM est un patchwork de `landuse` qui rend
  mal à cette échelle, et les noms de communes sont déjà là, en face de leurs
  gares ;
- les limites administratives — invisibles sur le terrain, donc sans valeur de
  repère pour un voyageur qui regarde par la fenêtre.

## Ce que le script refuse de produire

Comme pour le tracé : un run qui échoue vaut mieux qu'un décor faux. Sans cours
d'eau dans la réponse, on n'écrit rien — une carte sans la Saône ni le Rhône
n'est pas un décor appauvri, c'est un bug silencieux.

Usage : `python tools/extract_context.py` (écrit `context/line32.json`).
Données © les contributeurs OpenStreetMap, ODbL.
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

from extract_track import (
    ATTRIBUTION,
    BBOX,
    OVERPASS_URL,
    PRECISION,
    encode_polyline,
    haversine,
    simplify,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "context" / "line32.json"

# Tolérance de simplification du décor, plus lâche que celle du tracé : on ne
# situe pas un train sur une berge, on la reconnaît. À 40 m, une boucle de la
# Saône reste une boucle pour dix fois moins de points.
SIMPLIFY_M = 40.0

# Surface minimale d'un plan d'eau retenu, en mètres carrés — mesurée sur son
# encadrement. La Dombes compte un millier d'étangs ; les dessiner tous ferait
# un semis de confettis illisible et lourd. Au-delà de quinze hectares, ils se
# voient encore à l'échelle du cadre et disent la région.
MIN_WATER_M2 = 150_000.0

# Le plus petit nombre de cours d'eau en deçà duquel on considère que la
# réponse est incomplète plutôt que la région sèche. Le corridor traverse la
# Saône, le Rhône, l'Ain et la Veyle : quelques dizaines de segments au minimum.
MIN_RIVERS = 10

QUERY = """[out:json][timeout:300];
(
  way["waterway"="river"]({s},{w},{n},{e});
  way["natural"="water"]({s},{w},{n},{e});
);
out body geom;
"""


def fetch_elements(url=OVERPASS_URL, bbox=BBOX, timeout=600):
    """Interroge Overpass et rend les chemins de la réponse."""
    query = QUERY.format(s=bbox[0], w=bbox[1], n=bbox[2], e=bbox[3])
    data = urllib.parse.urlencode({"data": query}).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "terminus-32/extract_context (github.com/exec-d/terminus-32)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    return [e for e in payload.get("elements", []) if e.get("type") == "way"]


def points_of(way):
    """Géométrie d'un chemin, en couples (lat, lon)."""
    return [(p["lat"], p["lon"]) for p in way.get("geometry") or []]


def bbox_area_m2(points):
    """Surface de l'encadrement d'un contour, en mètres carrés.

    Approximation volontaire : la vraie surface d'un polygone coûterait plus
    cher pour trancher la même chose. On ne cherche qu'à distinguer un étang
    d'une mare.
    """
    if len(points) < 3:
        return 0.0
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    height = haversine((min(lats), lons[0]), (max(lats), lons[0]))
    width = haversine((lats[0], min(lons)), (lats[0], max(lons)))
    return height * width


def is_closed(points):
    """Un contour fermé revient à son point de départ, à quelques mètres près."""
    return len(points) > 3 and haversine(points[0], points[-1]) < 5


def build(elements):
    """Assemble le contenu de `context/line32.json`. Pur : ni réseau, ni I/O."""
    rivers, water = [], []
    for way in elements:
        tags = way.get("tags") or {}
        points = points_of(way)
        if len(points) < 2:
            continue
        if tags.get("waterway") == "river":
            rivers.append(simplify(points, SIMPLIFY_M))
        elif tags.get("natural") == "water":
            # Un plan d'eau se dessine rempli : il doit être fermé, et assez
            # grand pour se voir.
            if not is_closed(points) or bbox_area_m2(points) < MIN_WATER_M2:
                continue
            water.append(simplify(points, SIMPLIFY_M))

    if len(rivers) < MIN_RIVERS:
        raise SystemExit(
            f"{len(rivers)} cours d'eau seulement (minimum {MIN_RIVERS}) — la "
            f"réponse Overpass est incomplète, ou la requête a changé de sens. "
            f"Un décor sans la Saône ni le Rhône n'est pas un décor appauvri, "
            f"c'est un bug silencieux."
        )

    return {
        "version": 1,
        "precision": PRECISION,
        "attribution": ATTRIBUTION,
        "rivers": [encode_polyline(p) for p in rivers],
        "water": [encode_polyline(p) for p in water],
    }, {
        "cours_d_eau": len(rivers),
        "plans_d_eau": len(water),
        "points": sum(len(p) for p in rivers) + sum(len(p) for p in water),
    }


def main():
    elements = fetch_elements()
    print(f"chemins reçus : {len(elements)}")
    context, stats = build(elements)
    for key, value in stats.items():
        print(f"{key} : {value}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {OUT.relative_to(ROOT)} ({OUT.stat().st_size} octets)")


if __name__ == "__main__":
    main()
