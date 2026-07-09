<script lang="ts">
  import { base } from '$app/paths';
  import { onMount } from 'svelte';
  import { fetchLatestApp } from '$lib/data/sources';

  let version = $state<string | null>(null);
  let apkUrl = $state('https://github.com/exec-d/terminus-32/releases/latest');

  onMount(async () => {
    // Version + lien direct depuis le manifeste publié par la CI à chaque release.
    // Si la récupération échoue ou que l'URL n'est pas https, le bouton
    // retombe silencieusement sur la page des releases (cf. fetchLatestApp).
    const app = await fetchLatestApp();
    if (app) {
      apkUrl = app.apkUrl;
      version = app.version || null;
    }
  });
</script>

<header class="hero">
  <div class="hero-inner">
    <div class="hero-copy">
      <h1><span class="w-ter">TER</span><span class="w-minus">Minus</span></h1>
      <p class="tagline">L'heure de votre train, en temps réel.</p>
      <p class="subline">Ligne <b>32</b> · Bourg-en-Bresse ⇄ Lyon · Android</p>
      <div class="cta">
        <a class="apk-download" href={apkUrl}>
          <img
            class="apk-download__logo"
            src="{base}/assets/logo-terminus.png"
            alt="Logo TERMinus"
            width="36"
            height="36"
          />
          <span class="apk-download__text">
            <span class="apk-download__label">Télécharger l'APK</span>
            <span class="apk-download__sub"
              >{version ? `v${version} — Android` : 'Android · hors Play Store'}</span
            >
          </span>
        </a>
        <a class="ghost-btn" href="#pourquoi">Découvrir ↓</a>
      </div>
      <div class="badges">
        <span class="badge">Open data · ODbL</span>
        <span class="badge">100 % sur l'appareil</span>
        <span class="badge">Sans compte · sans pub</span>
      </div>
    </div>
    <figure class="hero-shot">
      <img
        src="{base}/assets/screenshot_010.png"
        width="884"
        height="1964"
        alt="Écran principal de TERMinus : liste des prochains départs vers Lyon avec heures, numéros de train et statut temps réel"
      />
    </figure>
  </div>
  <span class="scroll-hint">↧</span>
</header>

<style>
  .hero {
    position: relative;
    min-height: 100vh;
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 48px 20px;
  }
  .hero h1 {
    margin-top: 18px;
    font-family: var(--font-mono);
    font-weight: 700;
    letter-spacing: -0.02em;
    font-size: clamp(2.6rem, 8vw, 4.2rem);
  }
  .hero .tagline {
    margin-top: 14px;
    font-size: clamp(1.02rem, 2.8vw, 1.25rem);
    color: var(--fg);
  }
  .hero .subline {
    margin-top: 6px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.04em;
  }
  .hero .subline b {
    color: var(--accent-dim);
    font-weight: 400;
  }

  .cta {
    margin-top: 38px;
    display: flex;
    gap: 16px;
    justify-content: center;
    align-items: stretch;
    flex-wrap: wrap;
  }
  .apk-download {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1.35rem;
    border-radius: 0.5rem;
    background: color-mix(in srgb, var(--accent) 5%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
    transition:
      background 0.3s,
      border-color 0.3s,
      transform 0.3s;
  }
  .apk-download:hover {
    background: color-mix(in srgb, var(--accent) 12%, transparent);
    transform: scale(1.03);
    text-decoration: none;
  }
  .apk-download__logo {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    flex: 0 0 auto;
  }
  .apk-download__text {
    display: flex;
    flex-direction: column;
    line-height: 1.25;
    text-align: left;
  }
  .apk-download__label {
    font-family: var(--font-mono);
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--accent);
  }
  .apk-download__sub {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: color-mix(in srgb, var(--accent) 50%, transparent);
  }
  .ghost-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.7rem 1.35rem;
    border-radius: 0.5rem;
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.9rem;
    transition:
      color 0.3s,
      border-color 0.3s;
  }
  .ghost-btn:hover {
    color: var(--fg);
    border-color: #333;
    text-decoration: none;
  }

  .hero .badges {
    margin-top: 34px;
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }
  .badge {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 13px;
    background: var(--surface);
  }

  /* Hero deux colonnes */
  .hero-inner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: clamp(28px, 5vw, 68px);
    width: 100%;
    max-width: 1020px;
  }
  .hero-copy {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  .hero-copy .tagline,
  .hero-copy .subline {
    text-align: left;
  }
  .hero-copy .cta,
  .hero-copy .badges {
    justify-content: flex-start;
  }
  .hero-shot {
    margin: 0;
    flex: 0 0 auto;
  }
  .hero-shot img {
    display: block;
    width: auto;
    max-height: 76vh;
    max-width: 40vw;
    border-radius: 30px;
    border: 1px solid var(--border);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.8);
    will-change: transform;
    transition: transform 0.25s ease-out;
  }
  @media (max-width: 820px) {
    .hero-inner {
      flex-direction: column;
      gap: 36px;
    }
    .hero-copy {
      align-items: center;
      text-align: center;
    }
    .hero-copy .tagline,
    .hero-copy .subline {
      text-align: center;
    }
    .hero-copy .cta,
    .hero-copy .badges {
      justify-content: center;
    }
    .hero-shot img {
      max-height: 52vh;
      max-width: 78vw;
    }
  }
  .hero .scroll-hint {
    position: absolute;
    bottom: 26px;
    left: 50%;
    transform: translateX(-50%);
    color: color-mix(in srgb, var(--accent) 40%, transparent);
    font-size: 1.2rem;
    animation: bob 2.2s ease-in-out infinite;
  }
  @keyframes bob {
    0%,
    100% {
      transform: translate(-50%, 0);
    }
    50% {
      transform: translate(-50%, 8px);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .hero .scroll-hint {
      animation: none;
    }
  }
</style>
