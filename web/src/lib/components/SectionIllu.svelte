<script lang="ts">
  import { base } from '$app/paths';
  import { reveal } from '$lib/actions/reveal';

  let { src, width, height, alt }: { src: string; width: number; height: number; alt: string } =
    $props();
</script>

<figure class="section-illu" use:reveal>
  <img src="{base}/assets/{src}" {width} {height} {alt} loading="lazy" data-parallax />
</figure>

<style>
  .section-illu {
    max-width: 900px;
    margin: 0 auto 48px;
  }
  .section-illu img {
    display: block;
    width: 100%;
    height: auto;
    -webkit-mask-image:
      linear-gradient(to right, transparent, #000 8%, #000 92%, transparent),
      linear-gradient(to bottom, transparent, #000 8%, #000 92%, transparent);
    -webkit-mask-composite: source-in;
    mask-image:
      linear-gradient(to right, transparent, #000 8%, #000 92%, transparent),
      linear-gradient(to bottom, transparent, #000 8%, #000 92%, transparent);
    mask-composite: intersect;
  }
</style>
