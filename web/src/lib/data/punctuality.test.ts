import { describe, it, expect } from 'vitest';
import { aggregatePunctuality, type Line32Stats } from './punctuality';

function stats(trains: Line32Stats['trains']): Line32Stats {
  return { meta: {}, trains };
}

describe('aggregatePunctuality', () => {
  it('retourne des zéros quand il n’y a aucune observation', () => {
    const out = aggregatePunctuality(stats({}), 'month');
    expect(out).toEqual({ onTimePct: 0, cancelledPct: 0, totalObs: 0, trains: 0 });
  });

  it('compte une suppression comme non-à-l’heure (jamais exclue)', () => {
    // Train entièrement supprimé sur 10 passages, sans onTimePct.
    const out = aggregatePunctuality(
      stats({ '1': mkTrain({ obs: 10, cancelledPct: 100 }) }),
      'month'
    );
    expect(out.onTimePct).toBe(0);
    expect(out.cancelledPct).toBe(100);
    expect(out.totalObs).toBe(10);
    expect(out.trains).toBe(1);
  });

  it('garde l’invariant à-l’heure + supprimé ≤ 100 (cas 97,7 + 2,3)', () => {
    // 100 passages, 2,3% supprimés ; onTimePct=100 est mesuré sur les 97,7 ayant circulé.
    const out = aggregatePunctuality(
      stats({ '1': mkTrain({ obs: 100, cancelledPct: 2.3, onTimePct: 100 }) }),
      'month'
    );
    expect(out.onTimePct).toBeCloseTo(97.7, 5);
    expect(out.cancelledPct).toBeCloseTo(2.3, 5);
    expect(out.onTimePct + out.cancelledPct).toBeLessThanOrEqual(100);
  });

  it('pondère par le nombre d’observations entre trains', () => {
    const out = aggregatePunctuality(
      stats({
        '1': mkTrain({ obs: 90, cancelledPct: 0, onTimePct: 100 }),
        '2': mkTrain({ obs: 10, cancelledPct: 0, onTimePct: 0 })
      }),
      'month'
    );
    // 90 à l'heure + 0 = 90 sur 100.
    expect(out.onTimePct).toBeCloseTo(90, 5);
    expect(out.trains).toBe(2);
  });

  it('ignore les fenêtres sans observation pour le compte de trains', () => {
    const out = aggregatePunctuality(
      stats({
        '1': mkTrain({ obs: 10, cancelledPct: 0, onTimePct: 100 }),
        '2': mkTrain({ obs: 0 })
      }),
      'month'
    );
    expect(out.trains).toBe(1);
    expect(out.totalObs).toBe(10);
  });

  it('sélectionne bien la fenêtre demandée (week ≠ month ≠ year)', () => {
    const s = stats({
      '1': {
        week: { obs: 10, cancelledPct: 0, onTimePct: 50 },
        month: { obs: 10, cancelledPct: 0, onTimePct: 80 },
        year: { obs: 10, cancelledPct: 0, onTimePct: 100 }
      }
    });
    expect(aggregatePunctuality(s, 'week').onTimePct).toBeCloseTo(50, 5);
    expect(aggregatePunctuality(s, 'month').onTimePct).toBeCloseTo(80, 5);
    expect(aggregatePunctuality(s, 'year').onTimePct).toBeCloseTo(100, 5);
  });
});

function mkTrain(w: { obs: number; cancelledPct?: number; onTimePct?: number }): Record<
  'week' | 'month' | 'year',
  {
    obs: number;
    cancelledPct?: number;
    onTimePct?: number;
  }
> {
  return { week: w, month: w, year: w };
}
