<script lang="ts">
  import type { RankRow } from './rank';

  // Palmarès des trains : une barre horizontale par train, largeur ∝
  // onTimePct. Honnêteté (principe transverse n°1) : la sous-ligne affiche
  // toujours le taux de suppression et le nombre d'observations — un train
  // très supprimé n'est jamais masqué faute d'onTimePct.
  let { rows }: { rows: RankRow[] } = $props();
</script>

{#if rows.length === 0}
  <p class="bar-empty muted">Pas encore assez de données.</p>
{:else}
  <ul class="barchart">
    {#each rows as row (row.label)}
      <li class="bar-row">
        <span class="bar-label">{row.label}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:{row.onTimePct}%"></div>
        </div>
        <span class="bar-val">{row.onTimePct.toFixed(0)} %</span>
        <span class="bar-sub muted"
          >· méd. {row.medianDelayMin} min · {row.cancelledPct.toFixed(0)} % suppr. · {row.obs} obs</span
        >
      </li>
    {/each}
  </ul>
{/if}

<style>
  .bar-empty {
    font-family: var(--font-mono);
    font-size: 0.85rem;
  }
  .barchart {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  .bar-row {
    display: grid;
    grid-template-columns: 6.5em 1fr 3.5em;
    align-items: center;
    gap: var(--space-2);
  }
  .bar-label {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--fg);
    white-space: nowrap;
  }
  .bar-track {
    height: 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 999px;
  }
  .bar-val {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--fg);
    text-align: right;
    font-weight: 700;
  }
  .bar-sub {
    grid-column: 1 / -1;
    font-family: var(--font-mono);
    font-size: 0.7rem;
  }
</style>
