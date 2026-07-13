export type Windows = 'week' | 'month' | 'year';

export interface WindowStats {
  obs: number;
  onTimePct?: number;
  cancelledPct?: number;
  medianDelayMin?: number;
  meanDelayMin?: number;
  maxDelayMin?: number;
  cumDelayMin?: number;
}

export interface Line32Stats {
  meta: Record<string, unknown>;
  trains: Record<string, Record<Windows, WindowStats>>;
}

export interface Aggregate {
  onTimePct: number;
  cancelledPct: number;
  totalObs: number;
  trains: number;
}

export interface DelayTotals {
  cumDelayMin: number; // total des minutes de retard accumulées sur la fenêtre
  maxDelayMin: number; // pire retard observé
}

/** Totaux de retard sur tous les trains (fenêtre donnée) : cumul et maximum. */
export function delayTotals(stats: Line32Stats, win: Windows): DelayTotals {
  let cum = 0;
  let max = 0;
  for (const key of Object.keys(stats.trains)) {
    const w = stats.trains[key]?.[win];
    if (!w || (w.obs ?? 0) <= 0) continue;
    cum += w.cumDelayMin ?? 0;
    max = Math.max(max, w.maxDelayMin ?? 0);
  }
  return { cumDelayMin: cum, maxDelayMin: max };
}

/**
 * Agrège la ponctualité sur tous les trains, pour une fenêtre donnée.
 *
 * Honnêteté (principe transverse n°1) : une suppression compte comme
 * non-à-l'heure et n'est jamais exclue du dénominateur. `onTimePct` par train
 * étant mesuré sur les seuls passages ayant circulé, on le repondère par la
 * part réellement circulée avant de sommer.
 */
export function aggregatePunctuality(stats: Line32Stats, win: Windows): Aggregate {
  let totalObs = 0;
  let cancelled = 0;
  let onTime = 0;
  let trains = 0;

  for (const key of Object.keys(stats.trains)) {
    const w = stats.trains[key]?.[win];
    const obs = w?.obs ?? 0;
    if (!w || obs <= 0) continue;

    trains += 1;
    const cancelledPct = w.cancelledPct ?? 0;
    const ran = obs * (1 - cancelledPct / 100);
    totalObs += obs;
    cancelled += obs * (cancelledPct / 100);
    if (typeof w.onTimePct === 'number') {
      onTime += (ran * w.onTimePct) / 100;
    }
  }

  if (totalObs === 0) {
    return { onTimePct: 0, cancelledPct: 0, totalObs: 0, trains: 0 };
  }

  return {
    onTimePct: (100 * onTime) / totalObs,
    cancelledPct: (100 * cancelled) / totalObs,
    totalObs,
    trains
  };
}
