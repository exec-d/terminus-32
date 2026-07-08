<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import WhySection from '$lib/components/WhySection.svelte';
  import FeaturesSection from '$lib/components/FeaturesSection.svelte';
  import PunctSummary from '$lib/components/PunctSummary.svelte';
  import Gallery from '$lib/components/Gallery.svelte';
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
