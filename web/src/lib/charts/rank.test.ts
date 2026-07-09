import { describe, it, expect } from 'vitest';
import { rankSlots } from './rank';
import type { Line32Stats } from '$lib/data/punctuality';
import type { TripLabel } from '$lib/data/sources';

function stats(trains: Line32Stats['trains']): Line32Stats {
  return { meta: {}, trains };
}

describe('rankSlots', () => {
  it('agrège les numéros d’un même créneau et classe les moins fiables d’abord', () => {
    const labels: Record<string, TripLabel> = {
      '1': { dep: '17:12', dir: 'bebToLyon' },
      '2': { dep: '17:12', dir: 'bebToLyon' }, // même créneau que 1 (autre jour)
      '3': { dep: '08:00', dir: 'bebToLyon' }
    };
    const rows = rankSlots(
      stats({
        '1': {
          week: { obs: 0 },
          month: { obs: 10, onTimePct: 100, cancelledPct: 0 },
          year: { obs: 0 }
        },
        '2': {
          week: { obs: 0 },
          month: { obs: 10, onTimePct: 50, cancelledPct: 0 },
          year: { obs: 0 }
        },
        '3': {
          week: { obs: 0 },
          month: { obs: 10, onTimePct: 100, cancelledPct: 0 },
          year: { obs: 0 }
        }
      }),
      labels,
      'month'
    );
    // créneau 17:12 : obs 20, à l'heure 10+5 = 15 → 75 % ; 08:00 : 100 %
    expect(rows.map((r) => r.label)).toEqual(['17:12 → Lyon', '08:00 → Lyon']);
    const slot = rows[0];
    expect(slot.reliability).toBe(75);
    expect(slot.obs).toBe(20);
    expect(slot.trains).toBe(2);
    expect(slot.depMin).toBe(17 * 60 + 12);
  });

  it('une suppression compte : créneau 100 % supprimé → fiabilité 0, en tête', () => {
    const rows = rankSlots(
      stats({
        '1': { week: { obs: 0 }, month: { obs: 8, cancelledPct: 100 }, year: { obs: 0 } },
        '2': {
          week: { obs: 0 },
          month: { obs: 8, onTimePct: 100, cancelledPct: 0 },
          year: { obs: 0 }
        }
      }),
      { '1': { dep: '06:30', dir: 'lyonToBeb' }, '2': { dep: '07:00', dir: 'lyonToBeb' } },
      'month'
    );
    expect(rows[0].label).toBe('06:30 → Bourg');
    expect(rows[0].reliability).toBe(0);
  });

  it('repli sur le numéro (hors diagramme, depMin -1) si horaire inconnu ; exclut obs=0', () => {
    const rows = rankSlots(
      stats({
        '999': {
          week: { obs: 0 },
          month: { obs: 5, onTimePct: 60, cancelledPct: 0 },
          year: { obs: 0 }
        },
        '000': { week: { obs: 0 }, month: { obs: 0 }, year: { obs: 0 } }
      }),
      {},
      'month'
    );
    expect(rows).toHaveLength(1);
    expect(rows[0].label).toBe('TER 999');
    expect(rows[0].depMin).toBe(-1);
  });
});
