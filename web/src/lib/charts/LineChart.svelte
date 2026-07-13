<script lang="ts">
  import { linePath } from './geometry';

  // Graphe de tendance SVG pur (aucune dépendance de charting) : ligne + aire,
  // graduations min/max, 1re/dernière étiquette d'axe X. Statique (pas de
  // tracé animé) pour rester safe vis-à-vis de prefers-reduced-motion.
  let {
    values,
    labels,
    min = 0,
    max = 100,
    unit = '',
    emptyNote = '',
    values2 = [],
    label = '',
    label2 = ''
  }: {
    values: number[];
    labels: string[];
    min?: number;
    max?: number;
    unit?: string;
    emptyNote?: string;
    // Série secondaire optionnelle (ex. % de suppressions) : simple ligne, sans aire.
    values2?: number[];
    label?: string; // légende de la série principale
    label2?: string; // légende de la série secondaire
  } = $props();

  const W = 600;
  const H = 200;

  const path = $derived(linePath(values, W, H, min, max));
  const area = $derived(path ? `${path} L${W},${H} L0,${H} Z` : '');
  const path2 = $derived(values2.length >= 2 ? linePath(values2, W, H, min, max) : '');
  const hasLegend = $derived(!!path2 && !!label && !!label2);
</script>

{#if values.length < 2}
  <p class="chart-empty muted">Pas encore assez de données.</p>
  {#if emptyNote}<p class="chart-note muted">{emptyNote}</p>{/if}
{:else}
  <figure class="linechart">
    <svg
      viewBox="0 0 {W} {H}"
      role="img"
      aria-label="Évolution : de {labels[0]} à {labels[labels.length - 1]}"
    >
      <path class="area" d={area} />
      <path class="line" d={path} />
      {#if path2}<path class="line2" d={path2} />{/if}
      <line class="grid" x1="0" y1="1" x2={W} y2="1" />
      <text class="grid-label" x="0" y="14">{max}{unit}</text>
      <line class="grid" x1="0" y1={H - 1} x2={W} y2={H - 1} />
      <text class="grid-label" x="0" y={H - 6}>{min}{unit}</text>
    </svg>
    <div class="axis">
      <span>{labels[0]}</span>
      <span>{labels[labels.length - 1]}</span>
    </div>
    {#if hasLegend}
      <div class="legend">
        <span class="key"><i class="swatch swatch-main"></i>{label}</span>
        <span class="key"><i class="swatch swatch-alt"></i>{label2}</span>
      </div>
    {/if}
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
  .linechart {
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
  .area {
    fill: color-mix(in srgb, var(--accent) 14%, transparent);
    stroke: none;
  }
  /* Série secondaire (suppressions) : ligne fine pointillée, couleur d'alerte. */
  .line2 {
    fill: none;
    stroke: var(--warning);
    stroke-width: 1.75;
    stroke-dasharray: 4 3;
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
  .axis {
    display: flex;
    justify-content: space-between;
    margin-top: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--muted);
  }
  .legend {
    display: flex;
    gap: var(--space-4);
    margin-top: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--muted);
  }
  .key {
    display: inline-flex;
    align-items: center;
    gap: 0.4em;
  }
  .swatch {
    width: 1.4em;
    height: 0;
    border-top-width: 2px;
    border-top-style: solid;
  }
  .swatch-main {
    border-top-color: var(--accent);
  }
  .swatch-alt {
    border-top-style: dashed;
    border-top-color: var(--warning);
  }
</style>
