import type { Line32Stats, Windows } from '$lib/data/punctuality';

export interface RankRow {
  label: string;
  onTimePct: number;
  medianDelayMin: number;
  cancelledPct: number;
  obs: number;
}

export function rankTrains(stats: Line32Stats, win: Windows): RankRow[] {
  const rows: RankRow[] = [];
  for (const num of Object.keys(stats.trains)) {
    const w = stats.trains[num]?.[win];
    if (!w || (w.obs ?? 0) <= 0) continue;
    rows.push({
      label: `TER ${num}`,
      onTimePct: w.onTimePct ?? 0,
      medianDelayMin: w.medianDelayMin ?? 0,
      cancelledPct: w.cancelledPct ?? 0,
      obs: w.obs
    });
  }
  return rows.sort((a, b) => b.onTimePct - a.onTimePct || a.cancelledPct - b.cancelledPct);
}
