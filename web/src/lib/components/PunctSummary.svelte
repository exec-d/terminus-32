<script lang="ts">
  import { aggregatePunctuality, type Line32Stats } from '$lib/data/punctuality';
  import { base } from '$app/paths';
  import { onMount } from 'svelte';
  import { reveal } from '$lib/actions/reveal';

  // Effet ponctualité en direct : agrège les vraies stats et anime les
  // compteurs à l'apparition. Honnêteté (principe transverse n°1) : le calcul
  // vient exclusivement de `aggregatePunctuality` (une suppression compte
  // comme non-à-l'heure, jamais exclue) — on ne recalcule rien ici.
  interface Line32Meta {
    daysWithData?: { month?: number };
    updatedAt?: string;
  }

  let show = $state(true);
  let onTimePct = $state(0);
  let cancelledPct = $state(0);
  let trains = $state(0);
  let days = $state(0);
  let totalObs = $state(0);
  let updated = $state('');

  function animateCount(
    target: number,
    decimals: number,
    set: (v: number) => void,
    reduce: boolean
  ) {
    if (reduce) {
      set(Number(target.toFixed(decimals)));
      return;
    }
    const dur = 1300;
    let start: number | null = null;
    function step(ts: number) {
      if (start === null) start = ts;
      const p = Math.min((ts - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      set(Number((target * eased).toFixed(decimals)));
      if (p < 1) {
        requestAnimationFrame(step);
      } else {
        set(Number(target.toFixed(decimals)));
      }
    }
    requestAnimationFrame(step);
  }

  function relTime(iso: string | undefined): string {
    if (!iso) return '';
    const then = new Date(iso).getTime();
    if (Number.isNaN(then)) return '';
    const mins = Math.max(0, Math.round((Date.now() - then) / 60000));
    if (mins < 60) return `il y a ${mins} min`;
    const h = Math.round(mins / 60);
    if (h < 24) return `il y a ${h} h`;
    return `il y a ${Math.round(h / 24)} j`;
  }

  onMount(async () => {
    try {
      const res = await fetch(
        'https://raw.githubusercontent.com/exec-d/terminus-32/main/stats/line32.json'
      );
      const d = (res.ok ? await res.json() : null) as Line32Stats | null;
      if (!d || !d.trains) {
        show = false;
        return;
      }
      const agg = aggregatePunctuality(d, 'month');
      if (agg.totalObs === 0) {
        show = false;
        return;
      }

      const meta = d.meta as Line32Meta;
      totalObs = agg.totalObs;
      updated = relTime(meta.updatedAt);

      const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
      animateCount(agg.onTimePct, 1, (v) => (onTimePct = v), reduce);
      animateCount(agg.cancelledPct, 1, (v) => (cancelledPct = v), reduce);
      animateCount(Object.keys(d.trains).length, 0, (v) => (trains = v), reduce);
      animateCount(meta.daysWithData?.month ?? 0, 0, (v) => (days = v), reduce);
    } catch {
      show = false;
    }
  });
</script>

{#if show}
  <section id="ponctualite">
    <div class="wrap">
      <h2 class="neon-text" use:reveal>La ligne 32, sans langue de bois</h2>
      <div class="punct" use:reveal>
        <div class="punct-hero">
          <div class="punct-big">
            <span class="punct-num">{onTimePct.toFixed(1)}</span><span class="punct-pct">%</span>
          </div>
          <p class="punct-label">à l'heure <span class="muted">· seuil SNCF 5 min</span></p>
        </div>
        <div class="punct-kpis">
          <div class="kpi">
            <span class="kpi-num">{trains.toFixed(0)}</span><span class="kpi-lbl"
              >trains suivis</span
            >
          </div>
          <div class="kpi">
            <span class="kpi-num">{cancelledPct.toFixed(1)} %</span><span class="kpi-lbl"
              >supprimés</span
            >
          </div>
          <div class="kpi">
            <span class="kpi-num">{days.toFixed(0)}</span><span class="kpi-lbl"
              >jours de données</span
            >
          </div>
        </div>
        <p class="punct-foot muted">
          Données collectées depuis le 1<sup>er</sup> juillet 2026 — le flux SNCF ne conserve que la
          journée en cours, sans historique antérieur. <b>{totalObs}</b> passages observés · mis à
          jour <span>{updated}</span> ·
          <a href="https://github.com/exec-d/terminus-32/blob/main/stats/line32.json"
            >données ouvertes</a
          >
          · <a href="{base}/stats/">Voir le détail des statistiques →</a>
        </p>
      </div>
    </div>
  </section>
{/if}

<style>
  .neon-text {
    color: var(--accent);
  }
  .punct {
    max-width: 760px;
    margin: 0 auto;
    text-align: center;
  }
  .punct-big {
    display: flex;
    align-items: baseline;
    justify-content: center;
    font-family: var(--font-mono);
    font-weight: 700;
  }
  .punct-num {
    font-size: clamp(3.4rem, 12vw, 6rem);
    color: var(--accent);
    line-height: 1;
  }
  .punct-pct {
    font-size: clamp(1.4rem, 4vw, 2.2rem);
    color: var(--accent-dim);
    margin-left: 4px;
  }
  .punct-label {
    margin-top: 10px;
    font-family: var(--font-mono);
    font-size: 0.95rem;
    color: var(--fg);
  }
  .punct-kpis {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 40px;
  }
  .kpi {
    min-width: 150px;
    flex: 1 1 150px;
    max-width: 220px;
    padding: 22px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .kpi-num {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 1.7rem;
    color: var(--fg);
  }
  .kpi-lbl {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
  }
  .punct-foot {
    margin-top: 34px;
    font-size: 0.8rem;
  }
</style>
