<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
</script>

<Seo
  title="Confidentialité — TERMinus"
  description="TERMinus ne collecte aucune donnée personnelle : pas de compte, pas de tracking, pas de cookie."
/>

<article class="doc">
  <h1>Politique de confidentialité</h1>
  <p class="updated">Dernière mise à jour : 7 juillet 2026</p>

  <p class="lead">
    TERMinus est conçue pour fonctionner sans vous connaître : <b
      >aucune donnée personnelle n'est collectée</b
    >, aucun compte n'est requis, et rien n'est envoyé à un serveur nous appartenant — parce qu'il
    n'y en a pas.
  </p>

  <h2>Aucune collecte, aucun tracking</h2>
  <ul>
    <li>Pas de compte, pas d'inscription, pas d'identifiant.</li>
    <li>Pas de traceur publicitaire, pas de mesure d'audience, aucun cookie sur ce site.</li>
    <li>
      Vos préférences (gares Domicile/Travail, réglages de notifications, trains épinglés) restent
      <b>stockées uniquement sur votre appareil</b>.
    </li>
  </ul>

  <h2>Requêtes réseau de l'application</h2>
  <p>
    Pour afficher les horaires en temps réel et se mettre à jour, l'application contacte directement
    des services tiers depuis votre téléphone :
  </p>
  <ul>
    <li><b>transport.data.gouv.fr / SNCF</b> — flux temps réel et théoriques de la ligne 32.</li>
    <li>
      <b>GitHub</b> — téléchargement des fichiers de données et des mises à jour de l'application.
    </li>
  </ul>
  <p>
    Lors de ces requêtes, l'adresse IP de votre appareil est techniquement transmise à ces services,
    qui appliquent leurs propres politiques de confidentialité. TERMinus n'enregistre ni ne
    retransmet ces informations.
  </p>

  <h2>Site web</h2>
  <p>
    Ce site est statique et ne dépose aucun cookie. Son hébergeur, GitHub Pages, peut conserver des
    journaux techniques de connexion (dont l'adresse IP) à des fins de fonctionnement et de
    sécurité, conformément à la politique de confidentialité de GitHub.
  </p>

  <h2>Vos droits</h2>
  <p>
    Le règlement général sur la protection des données (RGPD) vous ouvre un droit d'accès, de
    rectification et d'effacement. L'éditeur ne détenant aucune donnée personnelle vous concernant,
    ces demandes sont sans objet ; vous pouvez néanmoins écrire à
    <a href="mailto:kevin@delfour.co">kevin@delfour.co</a> pour toute question.
  </p>

  <h2>Responsable de traitement</h2>
  <p>Kevin Delfour — <a href="mailto:kevin@delfour.co">kevin@delfour.co</a>.</p>
</article>
