import { describe, it, expect } from 'vitest';
import {
  aggregatePunctuality,
  delayTotals,
  type Line32Stats,
  type WindowStats
} from './punctuality';

function stats(trains: Line32Stats['trains']): Line32Stats {
  return { meta: {}, trains };
}

describe('aggregatePunctuality', () => {
  it('retourne des zéros quand il n’y a aucune observation', () => {
    const out = aggregatePunctuality(stats({}), 'month');
    expect(out).toEqual({ onTimePct: 0, cancelledPct: 0, totalObs: 0, trains: 0 });
  });

  it('exclut une fenêtre sous le seuil de publication au lieu de la compter en échec', () => {
    // `enough: false` = trop peu d'observations pour conclure. Sans exclusion, ses
    // passages entreraient au dénominateur sans jamais créditer onTime : une lacune
    // de mesure se lirait comme un train jamais à l'heure.
    const out = aggregatePunctuality(
      stats({
        '1': mkTrain({ obs: 100, onTimePct: 90, cancelledPct: 0 }),
        '2': mkTrain({ obs: 1, enough: false })
      }),
      'month'
    );
    expect(out.onTimePct).toBe(90);
    expect(out.totalObs).toBe(100);
    expect(out.trains).toBe(1);
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

describe('seuil de publication', () => {
  it('delayTotals ignore les fenêtres sous le seuil', () => {
    const out = delayTotals(
      stats({
        '1': mkTrain({ obs: 10, cumDelayMin: 30, maxDelayMin: 12 }),
        '2': mkTrain({ obs: 1, enough: false, cumDelayMin: 99, maxDelayMin: 99 })
      }),
      'month'
    );
    expect(out).toEqual({ cumDelayMin: 30, maxDelayMin: 12 });
  });
});

describe('delayTotals', () => {
  it('retourne des zéros quand il n’y a aucune observation', () => {
    expect(delayTotals(stats({}), 'month')).toEqual({ cumDelayMin: 0, maxDelayMin: 0 });
  });

  it('somme les retards cumulés et prend le maximum des pires retards', () => {
    const s = stats({
      '1': { month: { obs: 30, cumDelayMin: 120, maxDelayMin: 18 } },
      '2': { month: { obs: 20, cumDelayMin: 45, maxDelayMin: 32 } }
    } as unknown as Line32Stats['trains']);
    expect(delayTotals(s, 'month')).toEqual({ cumDelayMin: 165, maxDelayMin: 32 });
  });

  it('ignore les trains sans observation sur la fenêtre', () => {
    const s = stats({
      '1': { month: { obs: 0, cumDelayMin: 999, maxDelayMin: 999 } },
      '2': { month: { obs: 5, cumDelayMin: 10, maxDelayMin: 7 } }
    } as unknown as Line32Stats['trains']);
    expect(delayTotals(s, 'month')).toEqual({ cumDelayMin: 10, maxDelayMin: 7 });
  });
});

function mkTrain(w: WindowStats): Record<'week' | 'month' | 'year', WindowStats> {
  return { week: w, month: w, year: w };
}
