<script lang="ts">
  import { reveal } from '$lib/actions/reveal';
  import SectionIllu from './SectionIllu.svelte';
</script>

<section id="pourquoi">
  <div class="wrap">
    <h2 class="neon-text" use:reveal>Pourquoi une app pour une seule ligne ?</h2>
    <SectionIllu
      src="section1.webp"
      width={1536}
      height={1024}
      alt="Train TER 32 la nuit entre un clocher de village et la skyline de Lyon, avec l'application affichant les prochains départs"
    />
    <div class="why">
      <div class="card" use:reveal={0}>
        <h3>Faite par un navetteur, pour les navetteurs</h3>
        <p>
          TERMinus ne cherche pas à couvrir toute la France : elle connaît <em>votre</em> ligne par cœur.
          Les 13 gares de la ligne 32 sont embarquées, l'app démarre directement sur votre trajet Domicile
          ⇄ Travail, et chaque écran répond à la question du quotidien : « mon train est-il à l'heure
          ? »
        </p>
        <p class="stations">
          <b>Bourg-en-Bresse</b> · Servas-Lent · Saint-Paul-de-Varax · Marlieux-Châtillon ·
          Villars-les-Dombes · Saint-Marcel-en-Dombes · Saint-André-de-Corcy · Mionnay · Les Échets
          · Sathonay-Rillieux · <b>Lyon Part-Dieu</b> · Lyon Vaise · Lyon Perrache
        </p>
      </div>
      <div class="card" use:reveal={0.09}>
        <h3>Zéro serveur, zéro compte, zéro tracking</h3>
        <p>
          L'app interroge directement les flux temps réel publics de la SNCF (<a
            href="https://transport.data.gouv.fr">transport.data.gouv.fr</a
          >) depuis votre téléphone. Aucun backend, aucune donnée personnelle ne quitte l'appareil,
          aucun compte à créer. Les données publiées (horaires, statistiques de ponctualité) sont
          <a href="https://github.com/exec-d/terminus-32">ouvertes et vérifiables</a>.
        </p>
        <p>
          Et si l'expérience fait ses preuves, la même mécanique pourra un jour être déclinée à
          d'autres lignes — chaque ligne son app, légère et sur mesure.
        </p>
      </div>
    </div>
  </div>
</section>

<style>
  .neon-text {
    color: var(--accent);
  }
  .why {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  @media (max-width: 760px) {
    .why {
      grid-template-columns: 1fr;
    }
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 26px;
    transition: border-color 0.3s;
  }
  .card:hover {
    border-color: color-mix(in srgb, var(--accent) 25%, transparent);
  }
  .card h3 {
    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 12px;
  }
  .card p {
    color: var(--muted);
    font-size: 0.92rem;
  }
  .card p + p {
    margin-top: 10px;
  }
  .stations {
    margin-top: 16px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: #555;
    line-height: 2;
  }
  .stations b {
    color: var(--accent-dim);
    font-weight: 400;
  }
</style>
