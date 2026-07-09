import { describe, it, expect, vi, afterEach } from 'vitest';
import { isHttpsUrl, fetchJson, fetchLatestApp, fetchTrend } from './sources';

afterEach(() => vi.unstubAllGlobals());

function stubFetch(impl: () => Promise<Response> | Response) {
  vi.stubGlobal('fetch', vi.fn(impl));
}

describe('isHttpsUrl', () => {
  it('n’accepte que les URL https', () => {
    expect(isHttpsUrl('https://example.com/a.apk')).toBe(true);
    expect(isHttpsUrl('http://example.com')).toBe(false);
    expect(isHttpsUrl('javascript:alert(1)')).toBe(false);
    expect(isHttpsUrl(null)).toBe(false);
    expect(isHttpsUrl(42)).toBe(false);
  });
});

describe('fetchJson', () => {
  it('renvoie les données quand ok', async () => {
    stubFetch(() => new Response(JSON.stringify({ a: 1 }), { status: 200 }));
    expect(await fetchJson('x.json')).toEqual({ a: 1 });
  });
  it('renvoie null sur !ok', async () => {
    stubFetch(() => new Response('nope', { status: 404 }));
    expect(await fetchJson('x.json')).toBeNull();
  });
  it('renvoie null sur erreur réseau', async () => {
    stubFetch(() => Promise.reject(new Error('offline')));
    expect(await fetchJson('x.json')).toBeNull();
  });
});

describe('fetchLatestApp', () => {
  it('rejette une apkUrl non-https (sécurité)', async () => {
    stubFetch(
      () =>
        new Response(JSON.stringify({ version: '1', apkUrl: 'javascript:alert(1)' }), {
          status: 200
        })
    );
    expect(await fetchLatestApp()).toBeNull();
  });
  it('accepte une apkUrl https', async () => {
    stubFetch(
      () =>
        new Response(JSON.stringify({ version: '1.2', apkUrl: 'https://x/y.apk' }), { status: 200 })
    );
    expect(await fetchLatestApp()).toEqual({ version: '1.2', apkUrl: 'https://x/y.apk' });
  });
});

describe('fetchTrend', () => {
  it('renvoie null si trend.json est mal formé (pas de points)', async () => {
    stubFetch(() => new Response(JSON.stringify({}), { status: 200 }));
    expect(await fetchTrend()).toBeNull();
  });
  it('renvoie les données quand trend.json est valide', async () => {
    const data = {
      meta: { updatedAt: '2026-07-08', onTimeThresholdMin: 5 },
      points: [{ date: '2026-07-01', obs: 10, onTimePct: 95, cancelledPct: 1 }]
    };
    stubFetch(() => new Response(JSON.stringify(data), { status: 200 }));
    expect(await fetchTrend()).toEqual(data);
  });
});
