/** Chemin SVG d'une polyligne : index→x sur [0,w], valeur→y sur [0,h] (inversé). */
export function linePath(values: number[], w: number, h: number, min: number, max: number): string {
  if (values.length < 2) return '';
  const span = max - min;
  const x = (i: number) => (i / (values.length - 1)) * w;
  const y = (v: number) => (span === 0 ? h / 2 : h - ((v - min) / span) * h);
  return values.map((v, i) => `${i === 0 ? 'M' : 'L'}${round(x(i))},${round(y(v))}`).join(' ');
}

function round(n: number): number {
  return Math.round(n * 100) / 100;
}
