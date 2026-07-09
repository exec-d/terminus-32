<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
  import { reveal } from '$lib/actions/reveal';
  import { base } from '$app/paths';

  const steps = [
    {
      title: "Téléchargez l'APK",
      text: "Avec le bouton en haut de la page d'accueil — de préférence en Wi-Fi (~56 Mo)."
    },
    {
      title: 'Ouvrez le fichier téléchargé',
      text: "Autorisez l'installation depuis cette source quand Android le demande (une seule fois)."
    },
    {
      title: 'Lancez TERMinus',
      text: 'Choisissez vos gares Domicile et Travail. Pas de compte, pas de configuration.'
    },
    {
      title: 'Les mises à jour viennent à vous',
      text: "L'app vérifie à chaque lancement si une nouvelle version existe et l'installe en un tap, données conservées."
    }
  ];
</script>

<Seo
  title="Documentation — TERMinus"
  description="Installer et utiliser TERMinus : installation de l'APK, guide pas à pas, FAQ, dépannage."
/>

<article class="doc">
  <h1>Documentation</h1>

  <nav class="toc" aria-label="Sommaire">
    <a href="#installation">Installation</a>
    <a href="#utilisation">Guide d'utilisation</a>
    <a href="#faq">FAQ</a>
    <a href="#depannage">Dépannage</a>
  </nav>

  <h2 id="installation" use:reveal>Installation</h2>
  <div class="steps">
    {#each steps as step, i (step.title)}
      <div class="step" use:reveal={i * 0.05}>
        <span class="step__num">{i + 1}</span>
        <span class="step__body">
          <b>{step.title}</b>
          <span>{step.text}</span>
        </span>
      </div>
    {/each}
  </div>
  <div class="callout">
    <b>Play Protect peut afficher un avertissement générique</b> : c'est le message standard pour toute
    application installée hors Play Store. L'APK est signé, construit et publié automatiquement par une
    chaîne d'intégration continue GitHub — aucun binaire modifié à la main.
  </div>

  <h2 id="utilisation" use:reveal>Guide d'utilisation</h2>
  <p class="note">
    Une prise en main pas à pas des situations du quotidien. Ce guide sera affiné au fil des usages
    réels, en le relisant à l'aune de l'app.
  </p>
  <div class="guide">
    <h3>Au premier lancement</h3>
    <p>
      Choisissez votre gare <b>Domicile</b> et votre gare <b>Travail</b> parmi les 13 gares de la ligne
      32. L'app s'ouvre ensuite directement sur votre trajet — sans compte ni configuration à rallonge.
    </p>

    <h3>Voir mon prochain train</h3>
    <p>
      L'écran d'accueil liste les prochains départs dans votre sens : heure, numéro de train et
      statut temps réel (à l'heure, en retard, supprimé, arrêt non desservi). La liste se rafraîchit
      toute seule, à une fréquence que vous réglez (de 30 s à 5 min).
    </p>

    <h3>Suivre mon train du quotidien</h3>
    <p>
      Depuis la liste des départs, <b>épinglez</b> le train que vous prenez chaque jour : il reste en
      tête d'écran, confirmé dès qu'il apparaît dans le flux, avec une alerte s'il déraille du plan.
    </p>

    <h3>Être prévenu au bon moment</h3>
    <p>
      Dans les réglages, définissez le seuil de retard qui déclenche une notification, les gares à
      surveiller, et activez le silence nocturne (22 h–6 h) — sauf vraie urgence.
    </p>

    <h3>Comprendre un retard ou une perturbation</h3>
    <p>
      Touchez un train pour ouvrir son parcours gare par gare, avec les horaires estimés en temps
      réel et les arrêts supprimés barrés. Un badge sur les départs concernés signale grève, travaux
      ou incident : touchez-le pour la cause, l'effet, la période et les trains impactés.
    </p>

    <h3>Ne rien avoir à maintenir</h3>
    <p>
      Les horaires théoriques se resynchronisent seuls chaque semaine, et l'app propose elle-même
      ses mises à jour au lancement (cf. <a href="#installation">Installation</a>).
    </p>
  </div>

  <h2 id="faq" use:reveal>FAQ</h2>
  <div class="qa">
    <h3>Pourquoi l'application n'est-elle pas sur le Play Store ?</h3>
    <p>
      TERMinus est un projet personnel non commercial, distribué en APK signé via GitHub Releases.
      Cela demande d'autoriser l'installation depuis « sources inconnues » (cf.
      <a href="#installation">Installation</a>).
    </p>
    <h3>L'application est-elle officielle ?</h3>
    <p>
      Non — TERMinus est <b>non officielle</b>, indépendante, non affiliée à la SNCF. Seuls les
      canaux officiels SNCF font foi.
    </p>
    <h3>Quelles permissions demande l'app ? Est-ce sûr ?</h3>
    <p>
      Pas de compte, pas de tracking : l'application interroge directement les flux publics SNCF et
      GitHub depuis votre téléphone, et aucune donnée personnelle ne quitte l'appareil (cf.
      <a href="{base}/confidentialite/">Confidentialité</a>). L'APK est construit et publié
      automatiquement par une CI GitHub, donc auditable.
    </p>
    <h3>D'où viennent les données ?</h3>
    <p>
      De la SNCF, via <a href="https://transport.data.gouv.fr">transport.data.gouv.fr</a>, sous
      licence <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a>, redistribuées avec
      attribution.
    </p>
    <h3>Combien ça coûte ?</h3>
    <p>
      Rien : l'application est gratuite et sans publicité. Vous pouvez soutenir le projet via
      <a href="https://github.com/sponsors/kdelfour">GitHub Sponsors</a>.
    </p>
  </div>

  <h2 id="depannage" use:reveal>Dépannage</h2>
  <div class="qa">
    <h3>L'installation est bloquée</h3>
    <p>
      Autorisez l'installation depuis cette source dans les réglages Android quand le système le
      demande ; un avertissement Play Protect générique est normal hors Play Store (cf.
      <a href="#installation">Installation</a>).
    </p>
    <h3>L'app ne se met pas à jour</h3>
    <p>
      Elle vérifie à chaque lancement : relancez l'application et vérifiez votre connexion — la mise
      à jour se télécharge depuis GitHub.
    </p>
    <h3>Aucune donnée, pas d'horaires affichés</h3>
    <p>
      Le flux SNCF peut être momentanément indisponible ou incomplet ; les données de ponctualité ne
      démarrent qu'au 1ᵉʳ juillet 2026. Réessayez plus tard.
    </p>
    <h3>Signaler un bug</h3>
    <p>
      Ouvrez un ticket sur
      <a href="https://github.com/exec-d/terminus-32/issues">github.com/exec-d/terminus-32</a>
      ou passez par la page <a href="{base}/contact/">Contact</a>.
    </p>
  </div>
</article>

<style>
  .toc {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2) var(--space-4);
    margin: 0 0 var(--space-5);
    padding: var(--space-3) var(--space-4);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-family: var(--font-mono);
    font-size: 0.85rem;
  }
  .toc a {
    color: var(--fg);
  }
  .toc a:hover {
    color: var(--accent);
  }

  .note {
    font-size: 0.82rem;
    font-style: italic;
    border-left: 2px solid var(--border);
    padding-left: var(--space-3);
  }

  .steps {
    display: grid;
    gap: var(--space-3);
    margin: 0 0 var(--space-4);
  }
  .step {
    display: flex;
    gap: var(--space-3);
    align-items: flex-start;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-3) var(--space-4);
  }
  .step__num {
    flex: 0 0 auto;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--accent);
    border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
  }
  .step__body {
    display: block;
  }
  .step__body b {
    display: block;
    font-family: var(--font-mono);
    font-size: 0.92rem;
    color: var(--fg);
    margin-bottom: 4px;
  }
  .step__body span {
    font-size: 0.85rem;
    color: var(--muted);
  }

  .callout {
    margin: 0 0 var(--space-4);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius);
    font-size: 0.84rem;
    border: 1px solid color-mix(in srgb, var(--warning) 30%, transparent);
    background: color-mix(in srgb, var(--warning) 6%, transparent);
    color: var(--muted);
  }
  .callout b {
    color: var(--warning);
  }

  /* Guide « pas à pas » : sous-sections orientées tâches (prose, pas de grille de cartes
     — pour ne pas dupliquer la vitrine de fonctions de l'accueil). */
  .guide h3 {
    font-family: var(--font-mono);
    font-size: 0.95rem;
    color: var(--accent);
    margin: var(--space-4) 0 6px;
  }

  .qa h3 {
    font-family: var(--font-mono);
    font-size: 0.95rem;
    color: var(--fg);
    margin: var(--space-3) 0 6px;
  }
</style>
