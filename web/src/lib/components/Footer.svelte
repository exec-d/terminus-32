<script lang="ts">
  import { base } from '$app/paths';
</script>

<footer class="site-footer">
  <div class="container">
    <p class="muted">
      Application non officielle, non affiliée à la SNCF. Données SNCF (ODbL) via
      <a href="https://transport.data.gouv.fr">transport.data.gouv.fr</a>.
    </p>
    <p class="muted links">
      <a href="{base}/mentions-legales/">Mentions légales</a> ·
      <a href="{base}/confidentialite/">Confidentialité</a> ·
      <a href="{base}/cgu/">CGU</a> ·
      <a href="{base}/contact/">Contact</a> ·
      <a href="https://github.com/exec-d/terminus-32">GitHub</a>
    </p>
  </div>
</footer>

<style>
  .site-footer {
    border-top: 1px solid var(--border);
    margin-top: var(--space-6);
    padding-block: var(--space-5);
    font-size: 0.9rem;
  }
  .links {
    margin-top: var(--space-2);
  }
</style>
