<script lang="ts">
  import { onMount } from 'svelte';
  import Seo from '$lib/components/Seo.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import WhySection from '$lib/components/WhySection.svelte';
  import FeaturesSection from '$lib/components/FeaturesSection.svelte';
  import PunctSummary from '$lib/components/PunctSummary.svelte';
  import Gallery from '$lib/components/Gallery.svelte';

  // Effet scroll cinématique : parallaxe des illustrations + inclinaison 3D du
  // screenshot hero au survol (desktop pointer fin). Porté depuis site/index.html:320-357.
  onMount(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const cleanups: Array<() => void> = [];

    // (a) Parallaxe des illustrations `[data-parallax]`.
    const pxEls = Array.from(document.querySelectorAll<HTMLElement>('[data-parallax]'));
    let ticking = false;
    function frame() {
      const vh = window.innerHeight;
      for (const el of pxEls) {
        const r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) continue;
        const mid = r.top + r.height / 2 - vh / 2;
        el.style.transform = `translateY(${(mid * -0.04).toFixed(1)}px)`;
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
    onScroll();
    cleanups.push(() => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    });

    // (b) Inclinaison 3D du screenshot hero au survol (desktop pointer fin uniquement).
    const shot = document.querySelector<HTMLElement>('.hero-shot img');
    const hero = document.querySelector<HTMLElement>('.hero');
    if (shot && hero && window.matchMedia('(min-width: 821px) and (pointer: fine)').matches) {
      const onMouseMove = (e: MouseEvent) => {
        const rx = (e.clientY / window.innerHeight - 0.5) * -5;
        const ry = (e.clientX / window.innerWidth - 0.5) * 9;
        shot.style.transform = `perspective(1000px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
      };
      const onMouseLeave = () => {
        shot.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
      };
      hero.addEventListener('mousemove', onMouseMove);
      hero.addEventListener('mouseleave', onMouseLeave);
      cleanups.push(() => {
        hero.removeEventListener('mousemove', onMouseMove);
        hero.removeEventListener('mouseleave', onMouseLeave);
      });
    }

    return () => {
      for (const cleanup of cleanups) cleanup();
    };
  });
</script>

<Seo
  title="TERMinus — ligne 32 TER Bourg-en-Bresse ⇄ Lyon"
  description="Application non officielle de suivi de la ligne 32 TER : ponctualité, horaires et données ouvertes."
/>

<Hero />
<WhySection />
<FeaturesSection />
<PunctSummary />
<Gallery />
