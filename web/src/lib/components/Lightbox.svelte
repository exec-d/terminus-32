<script lang="ts">
  // Overlay plein écran pour agrandir une capture de la galerie. Piloté par le
  // parent via `src` (null = fermé). Fermeture : clic hors de l'image, bouton
  // ✕, touche Échap. Le scroll du body est bloqué tant que l'overlay est
  // ouvert, et le focus part sur le bouton de fermeture (piège clavier simple,
  // porté depuis `site/index.html:247-273`).
  let { src, alt, onClose }: { src: string | null; alt: string; onClose: () => void } = $props();

  let closeBtn = $state<HTMLButtonElement>();

  $effect(() => {
    if (!src) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeBtn?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  });

  function handleOverlayClick(e: MouseEvent) {
    // Ne ferme que si le clic touche le fond de l'overlay, pas l'image.
    if (e.target === e.currentTarget) onClose();
  }

  function handleWindowKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && src) onClose();
  }
</script>

<svelte:window onkeydown={handleWindowKeydown} />

{#if src}
  <!-- Le clic sur le fond est une commodité souris ; la fermeture reste accessible
       au clavier via le bouton ✕ (focus posé à l'ouverture) et la touche Échap
       (svelte:window ci-dessus). -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="lightbox" onclick={handleOverlayClick}>
    <button
      class="lightbox__close"
      type="button"
      aria-label="Fermer la vue agrandie"
      bind:this={closeBtn}
      onclick={onClose}
    >
      ✕
    </button>
    <img class="lightbox__img" {src} {alt} />
  </div>
{/if}

<style>
  .lightbox {
    position: fixed;
    inset: 0;
    z-index: 50;
    padding: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.92);
    cursor: zoom-out;
  }
  .lightbox__img {
    max-width: 92vw;
    max-height: 92vh;
    width: auto;
    height: auto;
    border-radius: 16px;
    border: 1px solid var(--border);
    cursor: default;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  }
  .lightbox__close {
    position: absolute;
    top: 18px;
    right: 22px;
    width: 42px;
    height: 42px;
    background: var(--surface);
    color: var(--fg);
    border: 1px solid var(--border);
    border-radius: 50%;
    font-size: 1.05rem;
    line-height: 1;
    cursor: pointer;
    transition:
      color 0.2s,
      border-color 0.2s;
  }
  .lightbox__close:hover {
    color: var(--accent);
    border-color: color-mix(in srgb, var(--accent) 40%, transparent);
  }
</style>
