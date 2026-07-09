<script lang="ts">
  import { onMount } from 'svelte';
  import Seo from '$lib/components/Seo.svelte';
  import { reveal } from '$lib/actions/reveal';
  import { fetchLine32Stats, fetchTrend, fetchStations, fetchTrainLabels } from '$lib/data/sources';
  import type { TrendData, StationsData, TripLabel } from '$lib/data/sources';
  import { aggregatePunctuality, type Line32Stats } from '$lib/data/punctuality';
  import { rankSlots } from '$lib/charts/rank';
  import LineChart from '$lib/charts/LineChart.svelte';
  import HourlyReliability from '$lib/charts/HourlyReliability.svelte';
  import StationProfile from '$lib/charts/StationProfile.svelte';

  // Données récupérées côté client uniquement (le layout est prerenderé, aucun fetch au
  // build) : la page affiche l'état de chargement puis, pour les flux pas encore présents en
  // prod (trend/stations), les états vides gérés par chaque composant de graphe.
  let loading = $state(true);
  let line32 = $state<Line32Stats | null>(null);
  let trend = $state<TrendData | null>(null);
  let stations = $state<StationsData | null>(null);
  let labels = $state<Record<string, TripLabel>>({});

  onMount(async () => {
    const [a, b, c, l] = await Promise.all([
      fetchLine32Stats(),
      fetchTrend(),
      fetchStations(),
      fetchTrainLabels()
    ]);
    line32 = a;
    trend = b;
    stations = c;
    labels = l;
    loading = false;
  });

  // Honnêteté (principe transverse n°1) : le grand pourcentage réutilise exclusivement
  // `aggregatePunctuality` — jamais recalculé ici.
  const agg = $derived(line32 ? aggregatePunctuality(line32, 'month') : null);
  // Palmarès par créneau horaire (heure de départ + sens), pas par numéro de train.
  const slots = $derived(line32 ? rankSlots(line32, labels, 'month') : []);
  const trendValues = $derived(trend?.points.map((p) => p.onTimePct) ?? []);
  const trendLabels = $derived(trend?.points.map((p) => p.date.slice(5)) ?? []);
</script>

<Seo
  title="Statistiques — ligne 32 TER"
  description="Ponctualité de la ligne 32 : tendance, fiabilité par horaire, détail par gare. Données ouvertes SNCF."
/>

<section class="wrap page-head">
  <h1>Statistiques</h1>
</section>

<section id="global">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Ponctualité globale</h2>
      <p class="muted">
        <b>Mode de calcul :</b> la part de passages à l'heure sur <b>tous les passages prévus</b>
        des 30 derniers jours, au seuil SNCF de 5 minutes. Une
        <b>suppression compte comme non à l'heure</b>
        (jamais exclue) — d'où un chiffre honnête, où « % à l'heure + % supprimé ≤ 100 ».
      </p>
    </div>
    <div class="stat-chart stat-hero">
      <p class="stats-hero-num">{agg ? agg.onTimePct.toFixed(1) : '—'} %</p>
      <p class="muted">à l'heure · sur {agg?.totalObs ?? 0} passages</p>
      {#if loading}
        <p class="muted">Chargement…</p>
      {/if}
    </div>
  </div>
</section>

<section id="tendance">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Tendance dans le temps</h2>
      <p class="muted">
        Chaque point, c'est le pourcentage de trains à l'heure sur une journée, au seuil SNCF de 5
        minutes. Une suppression compte comme un train non à l'heure — jamais masquée. La courbe
        s'étoffe jour après jour depuis le 1<sup>er</sup> juillet 2026.
      </p>
    </div>
    <div class="stat-chart">
      <LineChart
        values={trendValues}
        labels={trendLabels}
        unit=" %"
        emptyNote="La courbe se construit un point par jour de collecte (depuis le 1ᵉʳ juillet 2026) : il faut quelques jours avant qu'une tendance se dessine."
      />
    </div>
  </div>
</section>

<section id="horaires">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Fiabilité selon l'heure</h2>
      <p class="muted">
        « Le 17h12 vers Lyon est-il souvent à l'heure ? » Une barre par horaire, selon son
        <b>heure de départ</b> et sa <b>fiabilité</b> (% à l'heure sur tous les passages, une suppression
        comptant comme non à l'heure). La ligne de tendance par-dessus montre l'allure de la journée —
        les creux, ce sont les horaires à éviter. La couleur indique le sens.
      </p>
    </div>
    <div class="stat-chart">
      <HourlyReliability
        {slots}
        emptyNote="Chaque horaire s'affiche dès que la ponctualité par train est agrégée (recalcul 3×/jour à partir du flux SNCF)."
      />
    </div>
  </div>
</section>

<section id="gares">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Le long de la ligne</h2>
      <p class="muted">
        Le retard médian gare par gare, de Bourg-en-Bresse à Lyon, pour repérer où le retard
        s'accumule sur le trajet. Les gares sans donnée restent creuses (aucun zéro inventé) ; le
        profil se précise à mesure que les mesures par gare s'accumulent.
      </p>
    </div>
    <div class="stat-chart">
      <StationProfile
        stations={stations?.stations ?? []}
        emptyNote="Le retard par gare vient d'être ajouté au collecteur et n'est pas rétroactif — le profil se dessine au fil des prochains jours de circulation."
      />
    </div>
  </div>
</section>

<p class="stats-foot muted wrap">
  Données depuis le 1<sup>er</sup> juillet 2026 — le flux SNCF ne conserve que la journée en cours.
  ·
  <a href="https://github.com/exec-d/terminus-32/blob/main/stats/line32.json">données ouvertes</a>
</p>

<style>
  .page-head {
    padding-top: var(--space-5);
  }
  h1 {
    margin: 0;
  }

  .stat-hero {
    text-align: center;
  }
  .stats-hero-num {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: clamp(3.4rem, 12vw, 6rem);
    color: var(--accent);
    line-height: 1;
    margin: 0;
  }
  .stat-hero .muted {
    margin-top: var(--space-2);
  }

  /* Chaque section stats : explication à gauche, stat/graphe à droite. */
  .stat-row {
    display: grid;
    grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.6fr);
    gap: clamp(var(--space-4), 5vw, var(--space-6));
    align-items: center;
  }
  .stat-explain h2 {
    text-align: left;
    margin: 0 0 var(--space-2);
  }
  .stat-explain p {
    margin: 0;
    font-size: 0.92rem;
  }
  @media (max-width: 760px) {
    .stat-row {
      grid-template-columns: 1fr;
      gap: var(--space-3);
    }
  }

  .stats-foot {
    padding-block: var(--space-5);
    font-size: 0.8rem;
    text-align: center;
  }
</style>
