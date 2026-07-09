<script lang="ts">
  import type { SlotRow } from './rank';

  // Diagramme en barres SVG maison : une barre par créneau horaire (hauteur = fiabilité
  // honnête, % à l'heure sur tous les passages), rangées par heure de départ, colorées par
  // sens, avec une ligne de tendance (moyenne mobile) par-dessus. Statique → safe vis-à-vis
  // de prefers-reduced-motion.
  let { slots, emptyNote = '' }: { slots: SlotRow[]; emptyNote?: string } = $props();

  const W = 640;
  const H = 240;
  const PAD_L = 26;
  const PAD_R = 8;
  const PAD_T = 8;
  const PAD_B = 22;
  const PLOT_W = W - PAD_L - PAD_R;
  const PLOT_H = H - PAD_T - PAD_B;
  const baseY = PAD_T + PLOT_H;

  // Seuls les créneaux horodatés (les replis « TER {num} » ont depMin -1 → hors diagramme).
  const pts = $derived(slots.filter((s) => s.depMin >= 0).sort((a, b) => a.depMin - b.depMin));
  const band = $derived(pts.length ? PLOT_W / pts.length : PLOT_W);
  const barW = $derived(Math.min(18, band * 0.68));

  const cx = (i: number) => PAD_L + band * (i + 0.5);
  const yTop = (rel: number) => PAD_T + (1 - rel / 100) * PLOT_H;

  // Ligne de tendance : moyenne mobile centrée (fenêtre 5) de la fiabilité, dans l'ordre horaire.
  const trendPath = $derived.by(() => {
    const v = pts.map((p) => p.reliability);
    const n = v.length;
    const win = 2;
    return v
      .map((_, i) => {
        let sum = 0;
        let c = 0;
        for (let j = Math.max(0, i - win); j <= Math.min(n - 1, i + win); j++) {
          sum += v[j];
          c++;
        }
        return `${i === 0 ? 'M' : 'L'}${cx(i).toFixed(1)},${yTop(sum / c).toFixed(1)}`;
      })
      .join(' ');
  });

  // Un libellé d'heure à chaque changement d'heure.
  const hourTicks = $derived.by(() => {
    const t: { x: number; label: string }[] = [];
    let last = -1;
    pts.forEach((p, i) => {
      const h = Math.floor(p.depMin / 60);
      if (h !== last) {
        t.push({ x: cx(i), label: `${h}h` });
        last = h;
      }
    });
    return t;
  });

  const yLines = [0, 50, 100];
  // Feu tricolore selon la fiabilité : vert ≥ 90 %, orange 75–90 %, rouge < 75 %.
  const relColor = (r: number) =>
    r >= 90 ? 'var(--rel-good)' : r >= 75 ? 'var(--rel-mid)' : 'var(--rel-bad)';
</script>

{#if pts.length === 0}
  <p class="hr-empty muted">Données horaires bientôt disponibles.</p>
  {#if emptyNote}<p class="hr-note muted">{emptyNote}</p>{/if}
{:else}
  <svg
    class="hr"
    viewBox="0 0 {W} {H}"
    role="img"
    aria-label="Fiabilité de chaque horaire de la ligne 32 selon l'heure de départ"
  >
    {#each yLines as yv (yv)}
      <line class="grid" x1={PAD_L} y1={yTop(yv)} x2={W - PAD_R} y2={yTop(yv)} />
      <text class="lbl" x="2" y={yTop(yv) + 3}>{yv}</text>
    {/each}
    {#each pts as p, i (p.key)}
      <rect
        x={cx(i) - barW / 2}
        y={yTop(p.reliability)}
        width={barW}
        height={baseY - yTop(p.reliability)}
        rx="1.5"
        fill={relColor(p.reliability)}
      >
        <title
          >Départ {p.dep} · {p.reliability} % à l'heure · {p.cancelledPct} % suppr. · {p.obs} passages</title
        >
      </rect>
    {/each}
    <path class="trend" d={trendPath} />
    {#each hourTicks as t (t.x)}
      <text class="lbl" x={t.x} y={H - 6} text-anchor="middle">{t.label}</text>
    {/each}
  </svg>
  <div class="hr-legend muted">
    <span><i style="background: var(--rel-good)"></i> ≥ 90 %</span>
    <span><i style="background: var(--rel-mid)"></i> 75–90 %</span>
    <span><i style="background: var(--rel-bad)"></i> &lt; 75 %</span>
    <span class="hr-axis">— tendance · ↑ % à l'heure · → heure de départ</span>
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
    stroke: var(--fg);
    stroke-width: 1.5;
    opacity: 0.7;
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
  .hr-note {
    font-size: 0.8rem;
    margin-top: var(--space-2);
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
