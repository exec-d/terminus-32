<script lang="ts">
  import { onMount } from 'svelte';
  import Seo from '$lib/components/Seo.svelte';
  import { reveal } from '$lib/actions/reveal';
  import { fetchLine32Stats, fetchTrend, fetchStations, fetchTrainLabels } from '$lib/data/sources';
  import type { TrendData, StationsData, TripLabel } from '$lib/data/sources';
  import {
    aggregatePunctuality,
    delayTotals,
    type Line32Stats,
    type Windows
  } from '$lib/data/punctuality';
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

  // Fenêtre d'analyse pour les métriques agrégées (ponctualité globale, retards, horaires).
  // La tendance (une valeur par jour) et le profil par gare (sur toutes les données) n'en
  // dépendent pas.
  const WINDOWS = [
    { key: 'week', label: '7 jours', period: 'des 7 derniers jours', horizon: 7 },
    { key: 'month', label: '30 jours', period: 'des 30 derniers jours', horizon: 30 },
    { key: 'year', label: '1 an', period: 'des 12 derniers mois', horizon: 365 }
  ] as const;
  let win = $state<Windows>('month');
  const winMeta = $derived(WINDOWS.find((w) => w.key === win) ?? WINDOWS[1]);

  // On ne propose une fenêtre que lorsqu'on a de quoi la remplir (nombre de jours de
  // données ≥ son horizon). Sans ça, « 1 an » afficherait la même chose que « 30 jours »
  // avec un libellé trompeur tant qu'on n'a pas un an de recul. « 30 jours » (défaut)
  // reste toujours proposé, et le sélecteur disparaît s'il ne reste qu'une fenêtre.
  const coverage = $derived((line32?.meta?.daysWithData ?? {}) as Partial<Record<Windows, number>>);
  const visibleWindows = $derived(
    WINDOWS.filter((w) => w.key === 'month' || (coverage[w.key] ?? 0) >= w.horizon)
  );

  // Honnêteté (principe transverse n°1) : le grand pourcentage réutilise exclusivement
  // `aggregatePunctuality` — jamais recalculé ici.
  const agg = $derived(line32 ? aggregatePunctuality(line32, win) : null);
  // Retard cumulé (temps total perdu) et pire retard, toutes circulations confondues.
  const totals = $derived(line32 ? delayTotals(line32, win) : null);
  const hasData = $derived((agg?.totalObs ?? 0) > 0);
  // Palmarès par créneau horaire (heure de départ + sens), pas par numéro de train.
  const slots = $derived(line32 ? rankSlots(line32, labels, win) : []);
  // Aller (Bourg → Lyon) et retour (Lyon → Bourg) sur deux diagrammes distincts.
  const slotsAller = $derived(slots.filter((s) => s.dir === 'bebToLyon'));
  const slotsRetour = $derived(slots.filter((s) => s.dir === 'lyonToBeb'));
  const trendValues = $derived(trend?.points.map((p) => p.onTimePct) ?? []);
  const trendCancelled = $derived(trend?.points.map((p) => p.cancelledPct) ?? []);
  const trendLabels = $derived(trend?.points.map((p) => p.date.slice(5)) ?? []);

  // Retard cumulé en minutes → « 2 h 15 min » lisible (les grosses fenêtres dépassent l'heure).
  function fmtDuration(min: number): string {
    const m = Math.round(min);
    if (m < 60) return `${m} min`;
    const h = Math.floor(m / 60);
    const r = m % 60;
    return r ? `${h} h ${r} min` : `${h} h`;
  }
</script>

<Seo
  title="Statistiques — ligne 32 TER"
  description="Ponctualité de la ligne 32 : tendance, fiabilité par horaire, détail par gare. Données ouvertes SNCF."
/>

<section class="wrap page-head">
  <h1>Statistiques</h1>
  {#if visibleWindows.length > 1}
    <div class="win-select" role="group" aria-label="Fenêtre d'analyse">
      {#each visibleWindows as w (w.key)}
        <button
          type="button"
          class="win-btn"
          class:active={win === w.key}
          aria-pressed={win === w.key}
          onclick={() => (win = w.key)}>{w.label}</button
        >
      {/each}
    </div>
    <p class="win-hint muted">
      Fenêtre appliquée à la ponctualité globale, aux retards et à la fiabilité par horaire.
    </p>
  {/if}
</section>

<section id="global">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Ponctualité globale</h2>
      <p class="muted">
        <b>Mode de calcul :</b> la part de passages à l'heure sur <b>tous les passages prévus</b>
        {winMeta.period}, au seuil SNCF de 5 minutes. Une
        <b>suppression compte comme non à l'heure</b>
        (jamais exclue) — d'où un chiffre honnête, où « % à l'heure + % supprimé ≤ 100 ». Le
        <b>retard cumulé</b> additionne toutes les minutes de retard sur la fenêtre ; le
        <b>pire retard</b>, c'est le plus gros écart observé.
      </p>
    </div>
    <div class="stat-chart stat-hero">
      <p class="stats-hero-num">{agg ? agg.onTimePct.toFixed(1) : '—'} %</p>
      <p class="muted">à l'heure · sur {agg?.totalObs ?? 0} passages</p>
      <div class="kpi-row">
        <div class="kpi">
          <span class="kpi-num">{hasData && totals ? fmtDuration(totals.cumDelayMin) : '—'}</span>
          <span class="kpi-lbl">de retard cumulé</span>
        </div>
        <div class="kpi">
          <span class="kpi-num"
            >{hasData && totals && totals.maxDelayMin > 0 ? `${totals.maxDelayMin} min` : '—'}</span
          >
          <span class="kpi-lbl">pire retard</span>
        </div>
      </div>
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
        minutes. La courbe pointillée suit en parallèle la <b>part de trains supprimés</b> le même
        jour. Une suppression compte comme un train non à l'heure — jamais masquée. La courbe
        s'étoffe jour après jour depuis le 1<sup>er</sup> juillet 2026.
      </p>
    </div>
    <div class="stat-chart">
      <LineChart
        values={trendValues}
        labels={trendLabels}
        values2={trendCancelled}
        label="% à l'heure"
        label2="% supprimés"
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
        les creux, ce sont les horaires à éviter. La couleur code la fiabilité : vert au-dessus de 90
        %, orange puis rouge en dessous.
      </p>
    </div>
    <div class="stat-chart">
      <div class="dir-block">
        <h3 class="dir-title">Aller · Bourg → Lyon</h3>
        <HourlyReliability
          slots={slotsAller}
          emptyNote="Chaque horaire s'affiche dès que la ponctualité par train est agrégée (recalcul 3×/jour à partir du flux SNCF)."
        />
      </div>
      <div class="dir-block">
        <h3 class="dir-title">Retour · Lyon → Bourg</h3>
        <HourlyReliability
          slots={slotsRetour}
          emptyNote="Chaque horaire s'affiche dès que la ponctualité par train est agrégée (recalcul 3×/jour à partir du flux SNCF)."
        />
      </div>
    </div>
  </div>
</section>

<section id="gares">
  <div class="wrap stat-row">
    <div class="stat-explain">
      <h2 use:reveal>Le long de la ligne</h2>
      <p class="muted">
        Le retard moyen gare par gare, de Bourg-en-Bresse à Lyon, pour repérer où le retard
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

  /* Sélecteur de fenêtre : pastilles segmentées 7 j / 30 j / 1 an. */
  .win-select {
    display: inline-flex;
    margin-top: var(--space-3);
    padding: 3px;
    gap: 2px;
    border: 1px solid var(--border);
    border-radius: 999px;
  }
  .win-btn {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    padding: 0.3em 0.9em;
    border: 0;
    border-radius: 999px;
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    transition:
      color 0.2s,
      background 0.2s;
  }
  .win-btn:hover {
    color: var(--fg);
  }
  .win-btn.active {
    background: var(--accent);
    color: var(--bg);
  }
  .win-hint {
    margin: var(--space-2) 0 0;
    font-size: 0.8rem;
  }

  .stat-hero {
    text-align: center;
  }

  /* Deux KPI (retard cumulé, pire retard) sous le grand pourcentage. */
  .kpi-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    margin-top: var(--space-4);
    text-align: center;
  }
  .kpi {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding-top: var(--space-2);
    border-top: 1px solid var(--border);
  }
  .kpi-num {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: clamp(1.1rem, 4vw, 1.5rem);
    color: var(--fg);
    line-height: 1.1;
  }
  .kpi-lbl {
    font-size: 0.75rem;
    color: var(--muted);
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

  /* Deux diagrammes horaires (aller / retour) empilés dans la colonne de droite. */
  .dir-block + .dir-block {
    margin-top: var(--space-4);
  }
  .dir-title {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    color: var(--fg);
    margin: 0 0 var(--space-2);
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
