import type { Line32Stats } from './punctuality';

export const RAW_BASE = 'https://raw.githubusercontent.com/exec-d/terminus-32/main';

/** GET JSON depuis le dépôt brut ; null sur !ok / JSON invalide / erreur réseau (jamais de throw). */
export async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${RAW_BASE}/${path}`);
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export function isHttpsUrl(u: unknown): u is string {
  return typeof u === 'string' && /^https:\/\//i.test(u);
}

export interface LatestApp {
  version: string;
  apkUrl: string;
}

export async function fetchLatestApp(): Promise<LatestApp | null> {
  const info = await fetchJson<{ version?: unknown; apkUrl?: unknown }>('app/latest.json');
  if (!info || !isHttpsUrl(info.apkUrl)) return null;
  return { version: typeof info.version === 'string' ? info.version : '', apkUrl: info.apkUrl };
}

export function fetchLine32Stats(): Promise<Line32Stats | null> {
  return fetchJson<Line32Stats>('stats/line32.json');
}

export interface TripLabel {
  dep: string; // heure de départ "HH:MM"
  dir: string; // "bebToLyon" | "lyonToBeb"
}

/** Table numéro de train → heure de départ + sens, extraite du référentiel line32.json
 *  (permet d'étiqueter les stats par horaire plutôt que par numéro de train). */
export async function fetchTrainLabels(): Promise<Record<string, TripLabel>> {
  const ref = await fetchJson<{
    trips?: Array<{
      tripId?: string;
      direction?: string;
      stops?: Array<{ dep?: string; arr?: string }>;
    }>;
  }>('line32.json');
  const map: Record<string, TripLabel> = {};
  if (!ref?.trips) return map;
  for (const t of ref.trips) {
    const m = t.tripId ? /OCESN(\d+)/.exec(t.tripId) : null;
    if (!m || map[m[1]]) continue; // premier trip rencontré pour ce numéro
    const first = t.stops?.[0];
    const dep = (first?.dep ?? first?.arr ?? '').slice(0, 5); // "05:17:00" → "05:17"
    map[m[1]] = { dep, dir: t.direction ?? '' };
  }
  return map;
}

export interface TrendPoint {
  date: string;
  obs: number;
  onTimePct: number;
  cancelledPct: number;
}
export interface TrendData {
  meta: { updatedAt: string; onTimeThresholdMin: number };
  points: TrendPoint[];
}
export async function fetchTrend(): Promise<TrendData | null> {
  const data = await fetchJson<TrendData>('stats/trend.json');
  return data && Array.isArray(data.points) ? data : null;
}

export interface StationStat {
  uic: string | null;
  name: string;
  order: number;
  obs: number;
  medianDelayS: number | null;
  skippedPct: number;
}
export interface StationsData {
  meta: { updatedAt: string };
  stations: StationStat[];
}
export async function fetchStations(): Promise<StationsData | null> {
  const data = await fetchJson<StationsData>('stats/stations.json');
  return data && Array.isArray(data.stations) ? data : null;
}
