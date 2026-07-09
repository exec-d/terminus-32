import { describe, it, expect } from 'vitest';
import { rankTrains } from './rank';
import type { Line32Stats } from '$lib/data/punctuality';

function stats(trains: Line32Stats['trains']): Line32Stats {
  return { meta: {}, trains };
}

describe('rankTrains', () => {
  it('classe par onTimePct décroissant, exclut obs=0, labellise', () => {
    const rows = rankTrains(
      stats({
        '111': {
          week: { obs: 0 },
          month: { obs: 10, onTimePct: 80, cancelledPct: 0, medianDelayMin: 2 },
          year: { obs: 0 }
        },
        '222': {
          week: { obs: 0 },
          month: { obs: 5, onTimePct: 100, cancelledPct: 0, medianDelayMin: 0 },
          year: { obs: 0 }
        },
        '333': { week: { obs: 0 }, month: { obs: 0 }, year: { obs: 0 } }
      }),
      'month'
    );
    expect(rows.map((r) => r.label)).toEqual(['TER 222', 'TER 111']);
    expect(rows[0]).toEqual({
      label: 'TER 222',
      onTimePct: 100,
      medianDelayMin: 0,
      cancelledPct: 0,
      obs: 5
    });
  });

  it('départage à onTimePct égal par cancelledPct croissant', () => {
    const rows = rankTrains(
      stats({
        A: {
          week: { obs: 0 },
          month: { obs: 4, onTimePct: 90, cancelledPct: 10 },
          year: { obs: 0 }
        },
        B: { week: { obs: 0 }, month: { obs: 4, onTimePct: 90, cancelledPct: 0 }, year: { obs: 0 } }
      }),
      'month'
    );
    expect(rows.map((r) => r.label)).toEqual(['TER B', 'TER A']);
  });
});
