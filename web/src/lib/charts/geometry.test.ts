import { describe, it, expect } from 'vitest';
import { linePath } from './geometry';

describe('linePath', () => {
  it('chaîne vide si moins de 2 points', () => {
    expect(linePath([], 100, 50, 0, 100)).toBe('');
    expect(linePath([10], 100, 50, 0, 100)).toBe('');
  });
  it('mappe index→x et valeur→y (y inversé)', () => {
    // 2 points, w=100 h=50, min0 max100 : x 0→100, valeur 0→y50 (bas), 100→y0 (haut).
    expect(linePath([0, 100], 100, 50, 0, 100)).toBe('M0,50 L100,0');
  });
  it('centre-clampe une plage plate (max==min) au milieu', () => {
    expect(linePath([5, 5], 100, 50, 5, 5)).toBe('M0,25 L100,25');
  });
});
