#!/usr/bin/env python3
"""Audit de complétude de l'historique de la ligne 32.

Compare, journée par journée, les trains programmés (calendrier de line32.json)
aux trains réellement observés dans history/<date>.json. Le flux GTFS-RT ne
retient un train que le temps de son passage : une lacune n'est pas rattrapable,
seulement constatable — d'où cet audit.

    python tools/audit.py                 # tableau de couverture
    python tools/audit.py --restamp       # (ré)écrit le bloc coverage des journées
    python tools/audit.py --fail-under 95 # code retour 1 si un jour passe sous le seuil
    python tools/audit.py --days 14       # ne regarde que les N derniers jours

Les journées antérieures au calendrier publié (référentiel régénéré chaque
semaine) sont marquées « ? » : programme inconnu, ni succès ni lacune.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from stats_lib import coverage_of, scheduled_numbers

ROOT = Path(__file__).resolve().parent.parent
_DATE_STEM = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def history_paths():
    return [p for p in sorted((ROOT / "history").glob("*.json")) if _DATE_STEM.match(p.stem)]


def audit(days=None, restamp=False):
    """Couverture par journée, la plus récente en dernier."""
    line32 = json.loads((ROOT / "line32.json").read_text())
    paths = history_paths()
    if days:
        paths = paths[-days:]
    rows = []
    for path in paths:
        content = json.loads(path.read_text())
        cov = coverage_of(scheduled_numbers(line32, path.stem), content.get("trains", {}))
        if restamp and content.get("coverage") != cov:
            content["coverage"] = cov
            path.write_text(json.dumps(content, indent=1, sort_keys=True) + "\n")
        rows.append((path.stem, len(content.get("samples", [])), cov))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--restamp", action="store_true", help="réécrit le bloc coverage")
    ap.add_argument("--fail-under", type=int, metavar="PCT", help="seuil de couverture")
    ap.add_argument("--days", type=int, metavar="N", help="derniers N jours seulement")
    args = ap.parse_args()

    rows = audit(days=args.days, restamp=args.restamp)
    print(f"{'date':12} {'samples':>7} {'observés':>8} {'prévus':>7} {'couv.':>6}  manquants")
    known, faulty = [], []
    for date, samples, cov in rows:
        if cov["scheduled"] is None:
            print(f"{date:12} {samples:7} {cov['observed']:8} {'?':>7} {'?':>6}")
            continue
        known.append(cov)
        missing = ", ".join(cov["missing"][:8]) + (" …" if len(cov["missing"]) > 8 else "")
        print(
            f"{date:12} {samples:7} {cov['observed']:8} {cov['scheduled']:7} "
            f"{cov['pct']:5}%  {missing}"
        )
        if args.fail_under is not None and cov["pct"] < args.fail_under:
            faulty.append((date, cov["pct"]))

    scheduled = sum(c["scheduled"] for c in known)
    observed = sum(c["scheduled"] - len(c["missing"]) for c in known)
    if scheduled:
        print(
            f"\n{len(known)} journées au programme connu : {observed}/{scheduled} trains "
            f"observés ({round(100 * observed / scheduled)} %)"
        )
    if faulty:
        print(f"\n✗ {len(faulty)} journée(s) sous {args.fail_under} % : " + ", ".join(
            f"{d} ({p} %)" for d, p in faulty
        ))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
