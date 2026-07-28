<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
  import { base } from '$app/paths';
</script>

<Seo
  title="Mentions légales — TERMinus"
  description="Mentions légales de TERMinus : éditeur, hébergement, sources de données, propriété intellectuelle."
/>

<article class="doc">
  <h1>Mentions légales</h1>
  <p class="updated">Dernière mise à jour : 28 juillet 2026</p>

  <h2>Éditeur</h2>
  <p>
    Le présent site et l'application TERMinus sont édités par <b>Kevin Delfour</b>, personne
    physique agissant à titre non professionnel dans le cadre d'un projet personnel non commercial.
  </p>
  <p>Contact : <a href="mailto:kevin@delfour.co">kevin@delfour.co</a></p>

  <h2>Directeur de la publication</h2>
  <p>Kevin Delfour.</p>

  <h2>Hébergement</h2>
  <p>
    Le site est hébergé par <b>GitHub Pages</b> — GitHub, Inc., 88 Colin P. Kelly Jr. Street, San
    Francisco, CA 94107, États-Unis — <a href="https://github.com">github.com</a>.
  </p>

  <h2>Application mobile</h2>
  <p>
    TERMinus est une application Android distribuée <b>hors magasin d'applications</b> : le fichier
    d'installation est téléchargé depuis le dépôt du projet sur GitHub. L'application vérifie à
    chaque lancement si une version plus récente existe et vous la propose ;
    <b>le téléchargement et l'installation n'ont lieu que si vous les demandez</b>. C'est ce
    mécanisme qui explique la permission « installer des applications inconnues » qu'Android vous
    signale.
  </p>

  <h2>Propriété intellectuelle</h2>
  <p>
    Les contenus originaux du site et de l'application — textes, illustrations, logo — sont l'œuvre
    de leur auteur et ne peuvent être repris sans son autorisation. « TER » et « SNCF » sont des
    marques déposées de SNCF et de SNCF Voyageurs ; elles ne sont employées ici que pour désigner la
    ligne dont l'application donne les horaires, sans aucun lien économique avec leurs titulaires.
  </p>
  <p>
    Le code du site et des données publiées est ouvert :
    <a href="https://github.com/exec-d/terminus-32">github.com/exec-d/terminus-32</a>. Le code de
    l'application mobile est hébergé séparément :
    <a href="https://github.com/exec-d/terminus">github.com/exec-d/terminus</a>.
  </p>

  <h2>Données</h2>
  <p>L'application agrège trois jeux de données publiques, de trois producteurs différents :</p>
  <ul>
    <li>
      <b>Horaires et temps réel</b> — SNCF, via
      <a href="https://transport.data.gouv.fr">transport.data.gouv.fr</a>, sous licence
      <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a>.
    </li>
    <li>
      <b>Équipements en gare</b> (ascenseurs, escaliers mécaniques) — SNCF Gares &amp; Connexions,
      <a href="https://ressources.data.sncf.com">ressources.data.sncf.com</a>, sous licence
      <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a> (détail sur
      <a href="https://data.sncf.com/pages/licence">data.sncf.com</a>).
    </li>
    <li>
      <b>Vélo'v</b> — Métropole de Lyon / JCDecaux, sous
      <a href="https://developer.jcdecaux.com/files/Open-Licence-fr.pdf">Licence Ouverte JCDecaux</a
      >.
    </li>
  </ul>
  <p>
    Voir aussi la <a href="{base}/confidentialite/">politique de confidentialité</a> et les
    <a href="{base}/cgu/">conditions d'utilisation</a>.
  </p>

  <h2>Indépendance</h2>
  <p>
    TERMinus est une application <b>non officielle</b>, indépendante et <b>non affiliée</b> à la SNCF
    ni à SNCF Voyageurs.
  </p>

  <p class="muted">
    En application de l'article 6 III 2 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans
    l'économie numérique (LCEN), l'éditeur, personne physique non professionnelle, ne publie pas son
    adresse personnelle ; celle-ci est tenue à la disposition de l'hébergeur.
  </p>
</article>
