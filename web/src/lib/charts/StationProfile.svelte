<script lang="ts">
  import type { StationStat } from '../data/sources';

  // Profil du retard médian (en minutes) le long de la ligne, gare par gare
  // (ordre Bourg-en-Bresse → Lyon). Le pipeline vient de démarrer la collecte
  // par gare : beaucoup de gares n'ont encore aucune donnée (medianDelayS
  // null). On les affiche quand même (point creux) plutôt que de les
  // masquer — la ligne ne doit pas mentir sur ce qu'on sait vs. ce qu'on ne
  // sait pas encore. Noms de gares tronqués + tracé sans animation (safe
  // vis-à-vis de prefers-reduced-motion).
  let { stations }: { stations: StationStat[] } = $props();

  const W = 640;
  const H = 200;
  const LABEL_H = 70;
  const TOTAL_H = H + LABEL_H;

  const sorted = $derived([...stations].sort((a, b) => a.order - b.order));
  const withData = $derived(sorted.filter((s) => s.medianDelayS != null));
  const mins = $derived(sorted.map((s) => (s.medianDelayS ?? 0) / 60));
  const max = $derived(Math.max(2, ...mins));

  // Le tracé ne relie que les gares consécutives qui ont une donnée : une
  // gare sans donnée (medianDelayS null) coupe la ligne plutôt que d'y
  // injecter un faux 0 (honnêteté — cf. commentaire en tête de fichier).
  const linePathSegmented = $derived.by(() => {
    const n = sorted.length;
    let d = '';
    let pen = false; // pen down = la gare précédente avait une donnée
    sorted.forEach((s, i) => {
      if (s.medianDelayS == null) {
        pen = false;
        return;
      }
      const px = n > 1 ? (i / (n - 1)) * W : W / 2;
      const py = max === 0 ? H / 2 : H - (s.medianDelayS / 60 / max) * H;
      d += `${pen ? 'L' : 'M'}${px.toFixed(2)},${py.toFixed(2)} `;
      pen = true;
    });
    return d.trim();
  });

  function x(i: number): number {
    return sorted.length < 2 ? W / 2 : (i / (sorted.length - 1)) * W;
  }
  function y(v: number): number {
    return H - (v / max) * H;
  }
  function truncate(name: string, maxLen = 12): string {
    return name.length > maxLen ? `${name.slice(0, maxLen - 1)}…` : name;
  }
  function pointTitle(s: StationStat): string {
    const delay =
      s.medianDelayS != null ? `méd. ${(s.medianDelayS / 60).toFixed(1)} min` : 'pas de donnée';
    const skip = s.skippedPct > 0 ? ` · ${s.skippedPct.toFixed(0)} % suppr.` : '';
    return `${s.name} — ${delay}${skip} · ${s.obs} obs`;
  }
</script>

{#if withData.length === 0}
  <p class="chart-empty muted">Données par gare à venir.</p>
{:else}
  <figure class="stationprofile">
    <svg
      viewBox="0 0 {W} {TOTAL_H}"
      role="img"
      aria-label="Retard médian par gare, de Bourg-en-Bresse à Lyon"
    >
      <line class="grid" x1="0" y1="1" x2={W} y2="1" />
      <text class="grid-label" x="0" y="14">{max.toFixed(0)} min</text>
      <line class="grid" x1="0" y1={H - 1} x2={W} y2={H - 1} />
      <text class="grid-label" x="0" y={H - 6}>0 min</text>
      <path class="line" d={linePathSegmented} />
      {#each sorted as s, i (s.order)}
        <circle
          class="point"
          class:has-data={s.medianDelayS != null}
          class:skipped={s.skippedPct > 0}
          cx={x(i)}
          cy={y(mins[i])}
          r="3.5"
        >
          <title>{pointTitle(s)}</title>
        </circle>
        {#if s.skippedPct > 0}
          <text class="skip-marker" x={x(i)} y={y(mins[i]) - 8} text-anchor="middle">!</text>
        {/if}
        <g transform="translate({x(i)},{H + 8})">
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
  .stationprofile {
    margin: 0;
    width: 100%;
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
  .line {
    fill: none;
    stroke: var(--accent);
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
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
  .point {
    fill: var(--surface);
    stroke: var(--accent);
    stroke-width: 2;
  }
  .point.has-data {
    fill: var(--accent);
  }
  .point.skipped {
    stroke: var(--warning);
  }
  .point.skipped.has-data {
    fill: var(--warning);
  }
  .skip-marker {
    fill: var(--warning);
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
