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
