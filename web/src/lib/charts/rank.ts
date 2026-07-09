import type { Line32Stats, Windows } from '$lib/data/punctuality';
import type { TripLabel } from '$lib/data/sources';

/** Un CRÉNEAU horaire (heure de départ + sens), pas un numéro de train : ce qui intéresse
 *  l'usager c'est « le 17h12 vers Lyon est-il souvent à l'heure ? ». Plusieurs numéros couvrant
 *  le même créneau (jours différents) sont agrégés. */
export interface SlotRow {
  key: string;
  label: string;
  dep: string; // "HH:MM" ('' si inconnu)
  depMin: number; // minutes depuis minuit (-1 si inconnu → hors diagramme)
  dir: string;
  /** Fiabilité honnête : % à l'heure sur TOUS les passages du créneau (suppression = non à l'heure). */
  reliability: number;
  medianDelayMin: number;
  cancelledPct: number;
  obs: number;
  trains: number;
}

function destOf(dir: string): string {
  return dir === 'lyonToBeb' ? 'Bourg' : dir === 'bebToLyon' ? 'Lyon' : '';
}

function toMin(dep: string): number {
  const m = /^(\d{1,2}):(\d{2})/.exec(dep);
  return m ? Number(m[1]) * 60 + Number(m[2]) : -1;
}

export function rankSlots(
  stats: Line32Stats,
  labels: Record<string, TripLabel>,
  win: Windows
): SlotRow[] {
  const acc = new Map<
    string,
    {
      label: string;
      dep: string;
      dir: string;
      obs: number;
      cancelled: number;
      onTime: number;
      medW: number;
      trains: Set<string>;
    }
  >();

  for (const num of Object.keys(stats.trains)) {
    const w = stats.trains[num]?.[win];
    const obs = w?.obs ?? 0;
    if (!w || obs <= 0) continue;

    const l = labels[num];
    const dep = l?.dep ?? '';
    const dir = l?.dir ?? '';
    const key = dep ? `${dep}|${dir}` : num;
    const label = dep ? (destOf(dir) ? `${dep} → ${destOf(dir)}` : dep) : `TER ${num}`;

    const cancelledPct = w.cancelledPct ?? 0;
    const onTimePct = w.onTimePct ?? 0;
    const ran = obs * (1 - cancelledPct / 100); // passages ayant circulé

    let a = acc.get(key);
    if (!a) {
      a = { label, dep, dir, obs: 0, cancelled: 0, onTime: 0, medW: 0, trains: new Set() };
      acc.set(key, a);
    }
    a.obs += obs;
    a.cancelled += obs * (cancelledPct / 100);
    a.onTime += (ran * onTimePct) / 100; // à l'heure = part ayant circulé × ponctualité
    a.medW += obs * (w.medianDelayMin ?? 0);
    a.trains.add(num);
  }

  const rows: SlotRow[] = [];
  for (const [key, a] of acc) {
    rows.push({
      key,
      label: a.label,
      dep: a.dep,
      depMin: toMin(a.dep),
      dir: a.dir,
      reliability: Math.round((100 * a.onTime) / a.obs),
      medianDelayMin: Math.round(a.medW / a.obs),
      cancelledPct: Math.round((100 * a.cancelled) / a.obs),
      obs: a.obs,
      trains: a.trains.size
    });
  }
  // Les créneaux les MOINS fiables d'abord ; à égalité, plus de suppressions d'abord.
  return rows.sort((x, y) => x.reliability - y.reliability || y.cancelledPct - x.cancelledPct);
}
