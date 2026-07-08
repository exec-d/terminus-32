<script lang="ts">
  import '$lib/styles/tokens.css';
  import '$lib/styles/global.css';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';

  let { children } = $props();
</script>

<Header />
<main>
  {@render children()}
</main>
<Footer />
