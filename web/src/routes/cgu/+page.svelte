<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
  import { base } from '$app/paths';
</script>

<Seo
  title="Conditions d'utilisation — TERMinus"
  description="Conditions générales d'utilisation de l'application TERMinus et du site."
/>

<article class="doc">
  <h1>Conditions générales d'utilisation</h1>
  <p class="updated">Dernière mise à jour : 28 juillet 2026</p>

  <h2>1. Objet</h2>
  <p>
    Les présentes conditions régissent l'utilisation de l'application mobile TERMinus et du présent
    site. L'application vous les présente en substance à son premier lancement et vous demande de
    les accepter avant de vous en donner l'usage ; utiliser le site vaut également acceptation.
  </p>

  <h2>2. Description du service</h2>
  <p>
    TERMinus affiche des informations sur les circulations de la
    <b>ligne 32 TER (Bourg-en-Bresse ⇄ Lyon)</b> : horaires, retards, suppressions, perturbations,
    ainsi que quelques informations annexes sur les gares desservies. Le service est fourni
    <b>gratuitement</b>
    et <b>« en l'état »</b>, sans garantie de disponibilité continue. Il n'existe ni compte, ni
    abonnement, ni paiement d'aucune sorte.
  </p>

  <h2>3. Nature des informations</h2>
  <p>
    Les informations affichées sont <b>indicatives et non contractuelles</b>. Elles proviennent des
    flux de données publiés par la SNCF et ses partenaires, et peuvent être incomplètes, retardées,
    erronées ou indisponibles — l'application n'a aucun moyen de les vérifier.
  </p>
  <p>
    Quand une donnée manque, l'application ne l'affiche pas plutôt que de la deviner. Cela signifie
    aussi qu'une absence d'alerte ne garantit pas qu'il n'y a pas de perturbation.
    <b>Seuls les canaux officiels de la SNCF font foi</b> : vérifiez toujours une information critique
    à la source, et l'affichage en gare en cas de doute.
  </p>

  <h2>4. Données et licences</h2>
  <p>L'application agrège trois jeux de données publiques :</p>
  <ul>
    <li>
      <b>horaires et temps réel</b> — SNCF, via
      <a href="https://transport.data.gouv.fr">transport.data.gouv.fr</a>, sous licence
      <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a>, redistribués avec attribution
      conformément à cette licence ;
    </li>
    <li>
      <b>équipements en gare</b> — SNCF Gares &amp; Connexions,
      <a href="https://ressources.data.sncf.com">ressources.data.sncf.com</a>, sous licence
      <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a> ;
    </li>
    <li>
      <b>Vélo'v</b> — Métropole de Lyon / JCDecaux, sous
      <a href="https://developer.jcdecaux.com/files/Open-Licence-fr.pdf">Licence Ouverte JCDecaux</a
      >.
    </li>
  </ul>
  <p>
    Ces données restent soumises à leur licence d'origine. L'application ne fait que les afficher :
    elle ne les modifie pas et n'en produit aucune.
  </p>

  <h2>5. Responsabilité</h2>
  <p>
    L'application est un projet personnel offert gratuitement, sans garantie. L'éditeur ne peut être
    tenu responsable d'un train manqué, d'un retard, ou d'un préjudice résultant de l'utilisation de
    l'application ou d'une information inexacte affichée par elle — <b
      >dans les limites permises par la loi</b
    >, et sous réserve des cas où celle-ci interdit toute exclusion, notamment la faute lourde ou
    dolosive et le dommage corporel.
  </p>
  <p>
    Autrement dit : ne prenez pas cette application pour une source officielle, et ne lui reprochez
    pas ce que la SNCF ne publie pas.
  </p>

  <h2>6. Distribution et mises à jour</h2>
  <p>
    TERMinus est distribuée <b>hors magasin d'applications</b>, par téléchargement direct du fichier
    d'installation depuis le dépôt du projet. Android vous demandera d'autoriser l'installation
    depuis cette source ; c'est également la raison de la permission « installer des applications
    inconnues ».
  </p>
  <p>
    L'application vérifie à chaque lancement si une version plus récente existe et vous la signale.
    <b>Le téléchargement et l'installation ne se déclenchent que si vous les demandez</b> : rien ne s'installe
    dans votre dos. Les versions sont signées avec la même clé, ce qui garantit qu'une mise à jour provient
    bien du même auteur que la version déjà installée.
  </p>
  <p>
    Vous n'avez pas de version modifiée à craindre tant que vous installez depuis le dépôt officiel
    du projet. À l'inverse, une copie obtenue ailleurs n'engage en rien l'éditeur.
  </p>

  <h2>7. Usage acceptable</h2>
  <p>
    Vous pouvez utiliser l'application librement, la partager et en consulter le code. Vous ne
    pouvez pas en diffuser une version modifiée en la présentant comme officielle, ni laisser
    entendre qu'elle émane de la SNCF ou de l'éditeur.
  </p>

  <h2>8. Propriété intellectuelle</h2>
  <p>
    Les contenus originaux de TERMinus — textes, illustrations, logo — sont l'œuvre de leur auteur
    et ne peuvent être repris sans son autorisation. « TER » et « SNCF » sont des marques déposées
    de SNCF et de SNCF Voyageurs ; elles ne sont employées ici que pour désigner la ligne dont
    l'application donne les horaires. Les données restent soumises à leurs licences respectives
    (section 4).
  </p>

  <h2>9. Indépendance</h2>
  <p>
    TERMinus est une application <b>non officielle</b>, non affiliée à la SNCF ni à SNCF Voyageurs.
  </p>

  <h2>10. Vie privée</h2>
  <p>
    L'application ne collecte aucune donnée et n'en transmet aucune à son éditeur. Le détail figure
    dans la <a href="{base}/confidentialite/">politique de confidentialité</a>.
  </p>

  <h2>11. Évolution des conditions</h2>
  <p>
    Ces conditions peuvent être modifiées ; la date de dernière mise à jour figure en haut de cette
    page.
  </p>

  <h2>12. Droit applicable</h2>
  <p>Les présentes conditions sont soumises au droit français.</p>
</article>
