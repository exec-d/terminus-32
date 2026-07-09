<script lang="ts">
  import { base } from '$app/paths';

  const links = [
    { href: `${base}/`, label: 'Accueil' },
    { href: `${base}/stats/`, label: 'Stats' },
    { href: `${base}/docs/`, label: 'Doc' }
  ];
</script>

<header class="site-header">
  <div class="container inner">
    <a class="brand" href="{base}/">
      <span class="w-ter">TER</span><span class="w-minus">Minus</span>
    </a>
    <nav aria-label="Navigation principale">
      {#each links as link (link.href)}
        <a href={link.href}>{link.label}</a>
      {/each}
    </nav>
  </div>
</header>

<style>
  .site-header {
    border-bottom: 1px solid var(--border);
    background: var(--bg);
  }
  .inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-block: var(--space-3);
  }
  .brand {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 1.25rem;
    text-decoration: none;
  }
  nav {
    display: flex;
    gap: var(--space-4);
  }
  nav a {
    color: var(--muted);
  }
  nav a:hover {
    color: var(--fg);
    text-decoration: none;
  }
</style>
