import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reveal } from './reveal';

beforeEach(() => {
  vi.stubGlobal(
    'IntersectionObserver',
    class {
      observe = vi.fn();
      unobserve = vi.fn();
      disconnect = vi.fn();
    }
  );
});

function mm(matches: boolean) {
  vi.stubGlobal('matchMedia', () => ({
    matches,
    media: '',
    addEventListener() {},
    removeEventListener() {}
  }));
}

describe('reveal action', () => {
  it('ajoute la classe fade-in quand le mouvement est autorisé', () => {
    mm(false);
    const el = document.createElement('div');
    reveal(el, undefined);
    expect(el.classList.contains('fade-in')).toBe(true);
  });

  it('applique le délai de cascade en secondes', () => {
    mm(false);
    const el = document.createElement('div');
    reveal(el, 0.18);
    expect(el.style.transitionDelay).toBe('0.18s');
  });

  it('ne touche pas au DOM si reduced-motion (no-op)', () => {
    mm(true);
    const el = document.createElement('div');
    const ret = reveal(el, 0.2);
    expect(el.classList.contains('fade-in')).toBe(false);
    expect(el.style.transitionDelay).toBe('');
    expect(ret).toBeUndefined();
  });
});
