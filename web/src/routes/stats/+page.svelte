<script lang="ts">
  import { onMount } from 'svelte';
  import Seo from '$lib/components/Seo.svelte';
  import { reveal } from '$lib/actions/reveal';
  import { fetchLine32Stats, fetchTrend, fetchStations } from '$lib/data/sources';
  import type { TrendData, StationsData } from '$lib/data/sources';
  import { aggregatePunctuality, type Line32Stats } from '$lib/data/punctuality';
  import { rankTrains } from '$lib/charts/rank';
  import LineChart from '$lib/charts/LineChart.svelte';
  import BarChart from '$lib/charts/BarChart.svelte';
  import StationProfile from '$lib/charts/StationProfile.svelte';

  // Données récupérées côté client uniquement (le layout est prerenderé,
  // aucun fetch n'a lieu au build) : la page affiche l'état de chargement
  // puis, gare aux flux qui n'existent pas encore en prod (trend/stations),
  // les états vides gérés par chaque composant de graphe.
  let loading = $state(true);
  let line32 = $state<Line32Stats | null>(null);
  let trend = $state<TrendData | null>(null);
  let stations = $state<StationsData | null>(null);

  onMount(async () => {
    const [a, b, c] = await Promise.all([fetchLine32Stats(), fetchTrend(), fetchStations()]);
    line32 = a;
    trend = b;
    stations = c;
    loading = false;
  });

  // Honnêteté (principe transverse n°1) : le grand pourcentage réutilise
  // exclusivement `aggregatePunctuality` — jamais recalculé ici.
  const agg = $derived(line32 ? aggregatePunctuality(line32, 'month') : null);
  const rows = $derived(line32 ? rankTrains(line32, 'month') : []);
  const trendValues = $derived(trend?.points.map((p) => p.onTimePct) ?? []);
  const trendLabels = $derived(trend?.points.map((p) => p.date.slice(5)) ?? []);
</script>

<Seo
  title="Statistiques — ligne 32 TER"
  description="Ponctualité de la ligne 32 : tendance, palmarès des trains, détail par gare. Données ouvertes SNCF."
/>

<section>
  <div class="wrap">
    <h1>Statistiques</h1>
    <p class="stats-big"><span class="stats-num">{agg ? agg.onTimePct.toFixed(1) : '—'}</span> %</p>
    <p class="muted">à l'heure</p>
    <p class="muted">sur {agg?.totalObs ?? 0} passages · seuil 5 min</p>
    {#if loading}
      <p class="muted">Chargement des statistiques…</p>
    {/if}
  </div>
</section>

<section id="tendance">
  <div class="wrap">
    <h2 use:reveal>Tendance dans le temps</h2>
    <LineChart values={trendValues} labels={trendLabels} unit=" %" />
  </div>
</section>

<section id="palmares">
  <div class="wrap">
    <h2 use:reveal>Palmarès des trains</h2>
    <BarChart {rows} />
  </div>
</section>

<section id="gares">
  <div class="wrap">
    <h2 use:reveal>Le long de la ligne</h2>
    <StationProfile stations={stations?.stations ?? []} />
  </div>
</section>

<p class="stats-foot muted wrap">
  Données depuis le 1<sup>er</sup> juillet 2026 — le flux SNCF ne conserve que la journée en cours.
  ·
  <a href="https://github.com/exec-d/terminus-32/blob/main/stats/line32.json">données ouvertes</a>
</p>

<style>
  .stats-big {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin: var(--space-3) 0 0;
    font-family: var(--font-mono);
    font-weight: 700;
  }
  .stats-num {
    font-size: clamp(3.4rem, 12vw, 6rem);
    color: var(--accent);
    line-height: 1;
  }
  .stats-foot {
    padding-block: var(--space-5);
    font-size: 0.8rem;
    text-align: center;
  }
</style>
