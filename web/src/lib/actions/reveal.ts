import type { Action } from 'svelte/action';

/**
 * Révèle un élément à l'entrée dans le viewport (fade-in au scroll).
 * L'élément doit être visible par défaut (SSR/prerender sans JS) ; l'action
 * pose la classe `fade-in` (état initial masqué) au montage côté client puis
 * `visible` à l'intersection. Si `prefers-reduced-motion`, no-op (pas de masque).
 * `param` optionnel : délai de transition en secondes (effet cascade).
 */
export const reveal: Action<HTMLElement, number | undefined> = (node, delay) => {
  if (typeof window === 'undefined') return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  if (delay) node.style.transitionDelay = `${delay}s`;
  node.classList.add('fade-in');

  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          node.classList.add('visible');
          io.unobserve(node);
        }
      }
    },
    { threshold: 0.12 }
  );
  io.observe(node);

  return { destroy: () => io.disconnect() };
};
