<script lang="ts">
  import { base } from '$app/paths';
</script>

<footer class="site-footer">
  <div class="container">
    TERMinus est une application <b>non officielle</b>, non affiliée à la SNCF.<br />
    Données SNCF · <a href="https://transport.data.gouv.fr">transport.data.gouv.fr</a> · licence
    ODbL ·
    <a href="https://github.com/exec-d/terminus-32">GitHub</a> ·
    <a href="https://github.com/sponsors/kdelfour">Soutenir le projet</a><br />
    © 2026 Kevin Delfour
    <div class="footer-legal">
      <a href="{base}/mentions-legales/">Mentions légales</a> ·
      <a href="{base}/confidentialite/">Confidentialité</a> ·
      <a href="{base}/cgu/">CGU</a> ·
      <a href="{base}/contact/">Contact</a>
    </div>
  </div>
</footer>

<style>
  .site-footer {
    border-top: 1px solid var(--border);
    margin-top: var(--space-6);
    padding: 44px 0 56px;
    text-align: center;
    color: #555;
    font-size: 0.78rem;
    line-height: 2.1;
  }
  .site-footer b {
    color: var(--muted);
  }
  .footer-legal {
    margin-top: 6px;
  }
  .footer-legal a {
    color: var(--muted);
  }
  .footer-legal a:hover {
    color: var(--accent);
  }
</style>
