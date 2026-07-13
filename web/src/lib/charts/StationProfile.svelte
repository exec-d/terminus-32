<script lang="ts">
  import type { StationStat } from '../data/sources';

  // Retard MOYEN par gare (en minutes) le long de la ligne, en barres, dans l'ordre
  // géographique Bourg-en-Bresse → Lyon, avec la valeur au-dessus de chaque barre. La
  // moyenne (et non la médiane, souvent à 0 car la majorité des passages sont à l'heure)
  // capte les à-coups. Gares sans donnée (meanDelayS null) : pas de barre. Statique
  // (pas d'animation) → safe vis-à-vis de prefers-reduced-motion.
  let { stations, emptyNote = '' }: { stations: StationStat[]; emptyNote?: string } = $props();

  const W = 640;
  const H = 172; // zone des barres
  const LABEL_H = 82; // noms de gares (pivotés) sous les barres
  const TOTAL_H = H + LABEL_H;
  const PAD_L = 30;
  const PAD_R = 8;
  const PAD_T = 16; // place pour la valeur au-dessus de la plus haute barre

  const sorted = $derived([...stations].sort((a, b) => a.order - b.order));
  const withData = $derived(sorted.filter((s) => s.meanDelayS != null));
  const mins = $derived(sorted.map((s) => (s.meanDelayS != null ? s.meanDelayS / 60 : null)));
  const max = $derived.by(() => {
    const vals = mins.filter((m): m is number => m != null);
    return vals.length ? Math.max(1, ...vals) : 1;
  });

  const band = $derived(sorted.length ? (W - PAD_L - PAD_R) / sorted.length : W);
  const barW = $derived(Math.min(28, band * 0.62));
  const cx = (i: number) => PAD_L + band * (i + 0.5);
  const barTop = (m: number) => PAD_T + (1 - m / max) * (H - PAD_T);

  function truncate(name: string, maxLen = 12): string {
    return name.length > maxLen ? `${name.slice(0, maxLen - 1)}…` : name;
  }
  function title(s: StationStat): string {
    const d =
      s.meanDelayS != null ? `retard moyen ${(s.meanDelayS / 60).toFixed(1)} min` : 'pas de donnée';
    const skip = s.skippedPct > 0 ? ` · ${s.skippedPct.toFixed(0)} % suppr.` : '';
    return `${s.name} — ${d}${skip} · ${s.obs} passages`;
  }
</script>

{#if withData.length === 0}
  <p class="chart-empty muted">Données par gare à venir.</p>
  {#if emptyNote}<p class="chart-note muted">{emptyNote}</p>{/if}
{:else}
  <figure class="stationprofile">
    <svg
      viewBox="0 0 {W} {TOTAL_H}"
      role="img"
      aria-label="Retard moyen par gare (en minutes), de Bourg-en-Bresse à Lyon"
    >
      <!-- repères : 0 en bas, max en haut -->
      <line class="grid" x1={PAD_L} y1={barTop(max)} x2={W - PAD_R} y2={barTop(max)} />
      <text class="grid-label" x="2" y={barTop(max) + 3}>{max.toFixed(1)} min</text>
      <line class="grid" x1={PAD_L} y1={H} x2={W - PAD_R} y2={H} />
      <text class="grid-label" x="2" y={H - 3}>0</text>
      {#each sorted as s, i (s.order)}
        {@const m = mins[i]}
        {#if m != null}
          <rect
            class="bar"
            class:skipped={s.skippedPct > 0}
            x={cx(i) - barW / 2}
            y={barTop(m)}
            width={barW}
            height={H - barTop(m)}
            rx="2"
          >
            <title>{title(s)}</title>
          </rect>
          <text class="val" x={cx(i)} y={barTop(m) - 4} text-anchor="middle">{m.toFixed(1)}</text>
        {/if}
        <g transform="translate({cx(i)},{H + 8})">
          <text class="station-label" transform="rotate(-45)" text-anchor="end" x="-2" y="4"
            >{truncate(s.name)}</text
          >
        </g>
      {/each}
    </svg>
  </figure>
{/if}

<style>
  .chart-empty {
    font-family: var(--font-mono);
    font-size: 0.85rem;
  }
  .chart-note {
    font-size: 0.8rem;
    margin-top: var(--space-2);
  }
  .stationprofile {
    margin: 0;
    width: 100%;
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
  .grid {
    stroke: var(--border);
    stroke-width: 1;
  }
  .grid-label {
    fill: var(--muted);
    font-family: var(--font-mono);
    font-size: 10px;
  }
  .bar {
    fill: var(--accent);
  }
  /* Gare où des trains sont souvent supprimés : liseré orange (détail au survol). */
  .bar.skipped {
    stroke: var(--warning);
    stroke-width: 1.5;
  }
  .val {
    fill: var(--fg);
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
  }
  .station-label {
    fill: var(--muted);
    font-family: var(--font-mono);
    font-size: 8px;
  }
</style>
