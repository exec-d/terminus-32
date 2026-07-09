<script lang="ts">
  import { reveal } from '$lib/actions/reveal';
  import SectionIllu from './SectionIllu.svelte';

  const feats = [
    {
      icon: '🚦',
      title: 'Temps réel GTFS-RT',
      text: "Retards, suppressions et arrêts non desservis, rafraîchis automatiquement (30 s à 5 min, au choix). Heure d'arrivée estimée sur chaque départ."
    },
    {
      icon: '📌',
      title: 'Trains épinglés',
      text: "Épinglez votre train du matin en récurrent : confirmation quand il apparaît dans le flux, alerte dès qu'il déraille du plan, rappel avant le départ si vous l'activez."
    },
    {
      icon: '🔔',
      title: 'Notifications utiles',
      text: 'Seuil de retard réglable, gares surveillées, silence la nuit (22 h–6 h) avec exception pour les vraies urgences. Jamais deux fois la même alerte.'
    },
    {
      icon: '⚠️',
      title: 'Perturbations décodées',
      text: 'Grève, travaux, incident : cause, effet, période et trains touchés, avec badge directement sur les départs concernés.'
    },
    {
      icon: '🗺️',
      title: 'Parcours complet',
      text: 'Un tap sur un train ouvre son parcours gare par gare, avec les horaires estimés en temps réel et les arrêts supprimés barrés.'
    },
    {
      icon: '🔄',
      title: 'Toujours à jour, toute seule',
      text: "Les horaires théoriques se mettent à jour chaque semaine sans réinstallation, et l'app vous propose ses propres mises à jour dès qu'une version sort."
    }
  ];
</script>

<section id="fonctions">
  <div class="wrap">
    <h2 class="neon-text" use:reveal>Ce qu'elle sait faire</h2>
    <SectionIllu
      src="section2.webp"
      width={1536}
      height={1024}
      alt="Schéma des fonctionnalités de TERMinus autour de l'écran de l'app : temps réel GTFS-RT, trains épinglés, notifications, perturbations, parcours complet, mise à jour automatique"
    />
    <div class="grid">
      {#each feats as feat, i}
        <div class="feat" use:reveal={i * 0.06}>
          <span class="ico">{feat.icon}</span>
          <h3>{feat.title}</h3>
          <p>{feat.text}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
  .neon-text {
    color: var(--accent);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  @media (max-width: 860px) {
    .grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (max-width: 560px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
  .feat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
    transition:
      border-color 0.3s,
      transform 0.3s;
  }
  .feat:hover {
    border-color: color-mix(in srgb, var(--accent) 25%, transparent);
    transform: translateY(-2px);
  }
  .feat .ico {
    font-size: 1.35rem;
  }
  .feat h3 {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--accent);
    margin: 12px 0 7px;
  }
  .feat p {
    font-size: 0.84rem;
    color: var(--muted);
  }
</style>
