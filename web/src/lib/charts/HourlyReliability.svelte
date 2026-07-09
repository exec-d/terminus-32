<script lang="ts">
  import type { SlotRow } from './rank';

  // Diagramme SVG maison : chaque créneau horaire de la ligne 32 placé selon son heure
  // de départ (X) et sa fiabilité honnête (Y, % à l'heure sur tous les passages), avec une
  // sparkline reliant les créneaux dans l'ordre horaire pour donner la tendance de la journée.
  let { slots }: { slots: SlotRow[] } = $props();

  const W = 640;
  const H = 260;
  const PAD_L = 30;
  const PAD_R = 10;
  const PAD_T = 10;
  const PAD_B = 26;

  // Seuls les créneaux horodatés apparaissent (les replis « TER {num} » ont depMin -1).
  const pts = $derived(slots.filter((s) => s.depMin >= 0).sort((a, b) => a.depMin - b.depMin));
  const minX = $derived(pts.length ? Math.min(...pts.map((p) => p.depMin)) : 0);
  const maxX = $derived(pts.length ? Math.max(...pts.map((p) => p.depMin)) : 1);

  function sx(depMin: number): number {
    const span = maxX - minX || 1;
    return PAD_L + ((depMin - minX) / span) * (W - PAD_L - PAD_R);
  }
  function sy(rel: number): number {
    return PAD_T + (1 - rel / 100) * (H - PAD_T - PAD_B);
  }

  const trendPath = $derived(
    pts
      .map(
        (p, i) => `${i === 0 ? 'M' : 'L'}${sx(p.depMin).toFixed(1)},${sy(p.reliability).toFixed(1)}`
      )
      .join(' ')
  );

  // Graduations horaires toutes les 2 h.
  const ticks = $derived.by(() => {
    const t: number[] = [];
    if (!pts.length) return t;
    for (let m = Math.ceil(minX / 120) * 120; m <= maxX; m += 120) t.push(m);
    return t;
  });
  const hh = (m: number) => `${Math.floor(m / 60)}h`;
  const yLines = [0, 50, 100];
  const dirColor = (dir: string) => (dir === 'lyonToBeb' ? 'var(--accent-dim)' : 'var(--accent)');
</script>

{#if pts.length === 0}
  <p class="hr-empty muted">Données horaires bientôt disponibles.</p>
{:else}
  <svg
    class="hr"
    viewBox="0 0 {W} {H}"
    role="img"
    aria-label="Fiabilité de chaque horaire de la ligne 32 selon l'heure de départ"
  >
    {#each yLines as y (y)}
      <line class="grid" x1={PAD_L} y1={sy(y)} x2={W - PAD_R} y2={sy(y)} />
      <text class="lbl" x="2" y={sy(y) + 3}>{y}</text>
    {/each}
    {#each ticks as m (m)}
      <text class="lbl" x={sx(m)} y={H - 8} text-anchor="middle">{hh(m)}</text>
    {/each}
    <path class="trend" d={trendPath} />
    {#each pts as p (p.key)}
      <circle cx={sx(p.depMin)} cy={sy(p.reliability)} r="4" fill={dirColor(p.dir)}>
        <title
          >{p.label} · {p.reliability} % à l'heure · {p.cancelledPct} % suppr. · {p.obs} passages</title
        >
      </circle>
    {/each}
  </svg>
  <div class="hr-legend muted">
    <span><i style="background: var(--accent)"></i> Bourg → Lyon</span>
    <span><i style="background: var(--accent-dim)"></i> Lyon → Bourg</span>
    <span class="hr-axis">↑ % à l'heure · → heure de départ</span>
  </div>
{/if}

<style>
  .hr {
    width: 100%;
    height: auto;
    display: block;
  }
  .grid {
    stroke: var(--border);
    stroke-width: 1;
  }
  .trend {
    fill: none;
    stroke: color-mix(in srgb, var(--accent) 45%, transparent);
    stroke-width: 1.5;
  }
  .lbl {
    fill: var(--muted);
    font-family: var(--font-mono);
    font-size: 10px;
  }
  .hr-empty {
    font-family: var(--font-mono);
    font-size: 0.85rem;
  }
  .hr-legend {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2) var(--space-4);
    margin-top: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.72rem;
  }
  .hr-legend i {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 4px;
    vertical-align: middle;
  }
  .hr-axis {
    opacity: 0.8;
  }
</style>
