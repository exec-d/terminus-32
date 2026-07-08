<script lang="ts">
  // Bande de captures défilante (scroll-snap horizontal) ; clic ou Entrée/Espace
  // sur une capture l'agrandit dans la Lightbox. Portée depuis
  // `site/index.html:142-172` (markup) + `:247-273` (JS lightbox).
  import { base } from '$app/paths';
  import { reveal } from '$lib/actions/reveal';
  import Lightbox from './Lightbox.svelte';

  interface Shot {
    src: string;
    alt: string;
    caption: string;
  }

  const shots: Shot[] = [
    {
      src: 'screenshot_010.png',
      alt: 'Écran principal : liste des prochains départs vers Lyon avec heures, numéros de train et statut temps réel',
      caption: "Les prochains départs, en un coup d'œil"
    },
    {
      src: 'screenshot_007.png',
      alt: "Détail d'un train : parcours complet gare par gare avec horaires",
      caption: 'Le parcours complet de chaque train'
    },
    {
      src: 'screenshot_004.png',
      alt: "Épinglage d'un train récurrent avec choix des jours de la semaine",
      caption: 'Épinglez votre train du quotidien'
    },
    {
      src: 'screenshot_006.png',
      alt: 'Écran des trains épinglés',
      caption: 'Vos trains suivis, notifiés au moindre écart'
    },
    {
      src: 'screenshot_002.png',
      alt: 'Réglages des notifications : seuil de retard, sens surveillé, gares surveillées',
      caption: 'Des notifications sur mesure'
    },
    {
      src: 'screenshot_001.png',
      alt: 'Réglages des données : fraîcheur des horaires et vérification manuelle',
      caption: 'Des horaires qui se mettent à jour seuls'
    }
  ];

  let lightbox = $state<{ src: string; alt: string } | null>(null);

  function open(shot: Shot) {
    lightbox = { src: `${base}/assets/${shot.src}`, alt: shot.alt };
  }

  function handleKeydown(e: KeyboardEvent, shot: Shot) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      open(shot);
    }
  }
</script>

<section id="captures">
  <div class="wrap">
    <h2 class="neon-text" use:reveal>En images</h2>
    <div class="shots">
      {#each shots as shot (shot.src)}
        <figure class="shot">
          <!-- L'image agrandissable est son propre déclencheur (role="button" du JS
               source, site/index.html:263), avec gestion clavier via onkeydown. -->
          <!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
          <img
            src="{base}/assets/{shot.src}"
            alt={shot.alt}
            loading="lazy"
            use:reveal
            role="button"
            tabindex="0"
            onclick={() => open(shot)}
            onkeydown={(e) => handleKeydown(e, shot)}
          />
          <figcaption>{shot.caption}</figcaption>
        </figure>
      {/each}
    </div>
  </div>
</section>

<Lightbox src={lightbox?.src ?? null} alt={lightbox?.alt ?? ''} onClose={() => (lightbox = null)} />

<style>
  .neon-text {
    color: var(--accent);
  }
  .shots {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding: 6px 4px 20px;
    scroll-snap-type: x mandatory;
  }
  .shots::-webkit-scrollbar {
    height: 6px;
  }
  .shots::-webkit-scrollbar-thumb {
    background: color-mix(in srgb, var(--accent) 25%, transparent);
    border-radius: 3px;
  }
  .shots::-webkit-scrollbar-track {
    background: var(--surface);
  }
  .shot {
    flex: 0 0 auto;
    width: 300px;
    scroll-snap-align: start;
    text-align: center;
  }
  .shot img {
    width: 100%;
    height: auto;
    border-radius: 20px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 34px rgba(0, 0, 0, 0.7);
    transition:
      border-color 0.3s,
      transform 0.3s;
    cursor: zoom-in;
  }
  .shot:hover img {
    border-color: color-mix(in srgb, var(--accent) 35%, transparent);
    transform: translateY(-3px);
  }
  .shot figcaption {
    margin-top: 12px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--muted);
  }
</style>
