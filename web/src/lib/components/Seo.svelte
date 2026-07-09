<script lang="ts">
  import { page } from '$app/state';

  const DEFAULT_IMAGE = 'https://exec-d.github.io/terminus-32/assets/screenshot_010.png';

  interface Props {
    title: string;
    description: string;
    path?: string; // override optionnel ; par défaut dérivé de la route courante
    image?: string; // URL absolue ; par défaut le screenshot de la home
  }
  let { title, description, path, image = DEFAULT_IMAGE }: Props = $props();

  // page.url.pathname reflète l'URL réellement servie (base incluse en prod),
  // donc on ne préfixe pas nous-mêmes le base path pour éviter un doublon.
  const ORIGIN = 'https://exec-d.github.io';
  const url = $derived(ORIGIN + (path ?? page.url.pathname));
</script>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={url} />
  <meta property="og:type" content="website" />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:url" content={url} />
  <meta property="og:image" content={image} />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>
