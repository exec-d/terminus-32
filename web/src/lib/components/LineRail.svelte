<script lang="ts">
  import { onMount } from 'svelte';

  // Effet ligne 32 : rail vertical piloté par le scroll — le train descend de
  // Bourg-en-Bresse (haut) vers Lyon (bas), les gares s'allument au passage.
  const STOPS = [
    'Bourg-en-Bresse',
    'Servas-Lent',
    'Saint-Paul-de-Varax',
    'Marlieux-Châtillon',
    'Villars-les-Dombes',
    'Saint-Marcel-en-Dombes',
    'Saint-André-de-Corcy',
    'Mionnay',
    'Les Échets',
    'Sathonay-Rillieux',
    'Lyon Part-Dieu',
    'Lyon Vaise',
    'Lyon Perrache'
  ];
  const n = STOPS.length;

  let p = $state(0);
  let currentName = $state('');
  let showName = $state(false);

  onMount(() => {
    let ticking = false;
    let cur = -1;

    function frame() {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      p = max > 0 ? Math.min(Math.max(window.scrollY / max, 0), 1) : 0;
      const idx = Math.round(p * (n - 1));
      if (idx !== cur) {
        cur = idx;
        if (idx === 0 || idx === n - 1) {
          showName = false;
        } else {
          currentName = STOPS[idx];
          showName = true;
        }
      }
      ticking = false;
    }

    function onScroll() {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(frame);
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    frame();

    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    };
  });
</script>

<div class="linerail" aria-hidden="true" style="--p:{p.toFixed(4)}">
  <div class="linerail__track">
    <div class="linerail__fill"></div>
    {#each STOPS as _, i}
      <div
        class="linerail__stop"
        class:reached={i / (n - 1) <= p + 0.0001}
        style="--f:{(i / (n - 1)).toFixed(4)}"
      ></div>
    {/each}
    <div class="linerail__train"></div>
    <div class="linerail__name" class:show={showName}>{currentName}</div>
  </div>
  <div class="linerail__end linerail__end--top">{STOPS[0]}</div>
  <div class="linerail__end linerail__end--bottom">Lyon</div>
</div>

<style>
  /* ---------- Effet : ligne 32 pilotée par le scroll ---------- */
  /* --p = progression (0→1) mise à jour au scroll ; --f = fraction fixe de chaque gare. */
  .linerail {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 30;
    pointer-events: none;
    --p: 0;
  }
  .linerail__track {
    position: absolute;
    left: 22px;
    top: 6vh;
    height: 88vh;
    width: 2px;
    background: #1c1c1c;
  }
  .linerail__fill {
    position: absolute;
    left: 0;
    top: 0;
    width: 2px;
    height: calc(var(--p) * 100%);
    background: var(--accent);
    box-shadow: 0 0 8px color-mix(in srgb, var(--accent) 60%, transparent);
  }
  .linerail__stop {
    position: absolute;
    left: -4px;
    top: calc(var(--f) * 100%);
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--bg);
    border: 2px solid #2a2a2a;
    transform: translateY(-50%);
    transition:
      border-color 0.3s,
      background 0.3s;
  }
  .linerail__stop.reached {
    border-color: var(--accent);
    background: var(--accent-dim);
  }
  .linerail__end {
    position: absolute;
    left: 20px;
    white-space: nowrap;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .linerail__end--top {
    top: calc(6vh - 22px);
  }
  .linerail__end--bottom {
    top: calc(94vh + 10px);
  }
  .linerail__train {
    position: absolute;
    left: -6px;
    top: calc(var(--p) * 100%);
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow:
      0 0 6px var(--accent),
      0 0 16px color-mix(in srgb, var(--accent) 50%, transparent);
    transform: translateY(-50%);
  }
  .linerail__name {
    position: absolute;
    left: 18px;
    top: calc(var(--p) * 100%);
    transform: translateY(-50%);
    white-space: nowrap;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--fg);
    background: rgba(0, 0, 0, 0.72);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 9px;
    opacity: 0;
    transition: opacity 0.25s;
  }
  .linerail__name.show {
    opacity: 1;
  }

  /* Mobile : pas de gouttière → on masque complètement le rail. */
  @media (max-width: 767px) {
    .linerail {
      display: none;
    }
  }

  /* Laptops étroits (768–1299px) : le contenu centré (.wrap, max 1020px) n'a
     pas de gouttière gauche assez large pour un libellé de gare → on masque les
     libellés (le rail fin, les points et le train restent). Au-delà de 1300px,
     la gouttière dégage le texte et les libellés réapparaissent. */
  @media (min-width: 768px) and (max-width: 1299px) {
    .linerail__name,
    .linerail__end {
      display: none;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .linerail__stop,
    .linerail__fill,
    .linerail__train,
    .linerail__name {
      transition: none;
    }
  }
</style>
