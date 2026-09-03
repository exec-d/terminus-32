<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
</script>

<Seo
  title="Confidentialité — TERMinus"
  description="Ce que TERMinus enregistre sur votre téléphone, ce qu'elle va chercher sur Internet, et ce qui ne nous parvient jamais."
/>

<article class="doc">
  <h1>Politique de confidentialité</h1>
  <p class="updated">Dernière mise à jour : 3 septembre 2026</p>

  <p class="lead">
    TERMinus fonctionne sans vous connaître. Il n'y a pas de compte, pas d'inscription, pas
    d'identifiant, pas de traceur, et rien n'est envoyé à un serveur nous appartenant — parce qu'il
    n'y en a pas. Cette page dit précisément ce que cela veut dire, et aussi ce que cela ne veut pas
    dire.
  </p>

  <h2>Ce que nous ne faisons pas</h2>
  <ul>
    <li>Aucun compte, aucune inscription, aucun identifiant d'appareil ou de publicité.</li>
    <li>
      Aucun outil de mesure d'audience, aucun outil publicitaire, aucun rapport de plantage.
      L'application n'embarque aucune bibliothèque de ce type — c'est vérifiable, le code est
      ouvert.
    </li>
    <li>
      Aucune donnée ne nous est envoyée <b>par l'application elle-même</b>. Nous n'avons pas de
      serveur, donc pas de base de données, donc rien à consulter, à revendre ou à perdre. La seule
      exception est un signalement que <b>vous</b> décidez d'envoyer : voir « Signaler un problème » ci-dessous.
    </li>
  </ul>

  <h2>Ce qui reste sur votre téléphone</h2>
  <p>
    Tout ce que vous réglez dans l'application est enregistré <b>sur votre appareil uniquement</b> :
  </p>
  <ul>
    <li>
      vos gares <b>Domicile</b> et <b>Travail</b>, vos gares surveillées et vos gares favorites ;
    </li>
    <li>vos <b>trains épinglés</b> (gare, heure, sens, jours ou date) ;</li>
    <li>
      vos réglages de notifications : seuil de retard, heures de silence, alertes critiques la nuit,
      résumé matinal, rappel avant départ ;
    </li>
    <li>
      vos réglages d'affichage et d'accessibilité : thème, taille du texte, contraste, animations,
      icônes d'état, cadence de rafraîchissement ;
    </li>
    <li>
      une trace des alertes déjà envoyées, pour ne pas vous notifier deux fois la même chose ;
    </li>
    <li>
      le numéro de la dernière version dont vous avez vu les nouveautés, pour ne pas vous les
      représenter ;
    </li>
    <li>
      une copie des données publiques déjà téléchargées (horaires, ponctualité, équipements en gare,
      Vélo'v), pour que l'application reste utilisable hors ligne et n'interroge pas les serveurs en
      boucle.
    </li>
  </ul>
  <p>
    Nous n'avons accès à rien de tout cela. Ces informations sont conservées tant que l'application
    est installée ; la trace des alertes envoyées, elle, est élaguée à la fin de chaque cycle de
    notification — l'application n'en garde que les événements encore en cours. Effacer les données
    de l'application, ou la désinstaller, supprime l'ensemble immédiatement et définitivement.
  </p>
  <p>
    Une précision utile : vos gares Domicile et Travail, associées aux jours de vos trains épinglés,
    dessinent un trajet quotidien. C'est une donnée personnelle, même si elle ne quitte jamais votre
    téléphone — et c'est justement pour cela qu'elle n'en sort pas.
  </p>

  <h2>Le widget d'écran d'accueil</h2>
  <p>
    Si vous posez le widget TERMinus sur votre écran d'accueil, il affiche vos trois prochains
    départs : depuis votre gare Domicile en direction du Travail, ou, si ces deux gares ne sont pas
    renseignées, depuis la première gare que vous surveillez. Ces informations sont alors visibles
    par quiconque regarde votre écran, y compris verrouillé selon les réglages de votre téléphone.
    Rien n'est transmis nulle part, mais c'est à savoir avant de le poser.
  </p>

  <h2>Ce que l'application va chercher sur Internet</h2>
  <p>
    Pour afficher des horaires, l'application interroge directement les serveurs de données
    publiques, depuis votre téléphone. Il n'y a aucun intermédiaire :
  </p>
  <ul>
    <li>
      <b>proxy.transport.data.gouv.fr</b> — flux temps réel SNCF (retards, suppressions,
      perturbations). Interrogé pendant que vous consultez l'application, et toutes les 15 minutes
      en tâche de fond même quand l'application est fermée : c'est ce qui permet aux alertes
      d'arriver à temps et au widget de rester à jour. Ce cycle de fond ne travaille que s'il a une
      raison de le faire :
      <b
        >si vous n'avez ni activé les notifications ni posé le widget sur votre écran d'accueil, il
        s'interrompt aussitôt, avant la moindre requête réseau</b
      >.
    </li>
    <li>
      <b>raw.githubusercontent.com</b> — horaires de la ligne, statistiques de ponctualité, et vérification
      de l'existence d'une nouvelle version de l'application.
    </li>
    <li>
      <b>ressources.data.sncf.com</b> — état des ascenseurs et escaliers mécaniques en gare.
    </li>
    <li>
      <b>api.cyclocity.fr</b> — disponibilité des Vélo'v, <b>uniquement</b> quand vous consultez un train
      arrivant à Lyon Part-Dieu, Perrache ou Vaise.
    </li>
    <li>
      <b>github.com</b> — le fichier d'installation d'une mise à jour, à l'adresse annoncée par le manifeste
      de version, et seulement si vous en demandez le téléchargement.
    </li>
  </ul>
  <p>
    Ces requêtes ne transportent <b>aucune information vous concernant</b> : pas d'identifiant, pas de
    contenu, pas même vos gares. L'application télécharge les données de toute la ligne — et pour le temps
    réel, celles de tout le réseau — puis fait le tri sur votre téléphone. Aucun de ces serveurs ne peut
    donc savoir quelle gare vous surveillez. La vérification de mise à jour, elle, ne transmet pas non
    plus la version que vous avez installée : la comparaison se fait localement.
  </p>
  <p>
    Ce que ces serveurs voient malgré tout, comme n'importe quel site que vous visitez : votre
    <b>adresse IP</b>, le type de logiciel qui se connecte, et l'heure de la requête. C'est
    inévitable dès qu'un appareil se connecte à un serveur. Nous ne l'enregistrons pas et nous n'y
    avons pas accès, mais nous avons choisi ces serveurs, alors nous vous le disons. Chacun applique
    sa propre politique de confidentialité.
  </p>
  <p>
    Enfin, certains liens vous font sortir de l'application. « Plus d'infos » sur une perturbation
    ouvre dans votre navigateur une adresse fournie par la SNCF dans son flux d'alertes ; l'écran À
    propos renvoie vers les sources de données et vers ce site. L'application ne va rien chercher à
    ces adresses : c'est votre navigateur qui s'y connecte, et à partir de là vous êtes sur un site
    tiers, soumis à ses propres règles.
  </p>

  <h2>Transferts hors Union européenne</h2>
  <p>
    <b>raw.githubusercontent.com</b> et <b>github.com</b> appartiennent à GitHub, Inc., société de
    droit américain, qui héberge également ce site. Lorsque l'application ou votre navigateur
    contacte ces adresses, votre adresse IP est transmise aux États-Unis. Ce transfert repose sur
    deux fondements : GitHub, Inc. déclare adhérer au <b>EU-U.S. Data Privacy Framework</b>, dans le
    cadre de la certification tenue par le Département du commerce des États-Unis, et s'appuie par
    ailleurs sur les
    <b>clauses contractuelles types</b> adoptées par la Commission européenne (décision d'exécution (UE)
    2021/914).
  </p>
  <p>
    Les autres serveurs contactés — <b>transport.data.gouv.fr</b>,
    <b>ressources.data.sncf.com</b>, <b>api.cyclocity.fr</b> — sont opérés depuis l'Union européenne.
  </p>

  <h2>Pourquoi il n'y a pas de bandeau de consentement</h2>
  <p>
    L'article 82 de la loi Informatique et Libertés impose de recueillir votre consentement avant
    d'écrire ou de lire des informations sur votre appareil — sauf lorsque ces opérations sont
    strictement nécessaires au service que vous avez demandé.
  </p>
  <p>
    C'est exactement le cas ici : l'application n'enregistre que ce que vous avez vous-même réglé,
    plus les caches techniques dont elle a besoin pour fonctionner. Aucune écriture n'a de finalité
    publicitaire ou statistique, et aucun identifiant n'est créé. Il n'y a donc rien à consentir, et
    pas de bandeau. Ce site, de son côté, ne dépose aucun cookie, ni le moindre équivalent.
  </p>

  <h2>Les permissions Android</h2>
  <p>
    L'application déclare <b>neuf permissions</b>. Aucune n'est là par confort ; voici à quoi
    chacune sert.
  </p>
  <p>Trois concernent directement ce que vous faites de l'application :</p>
  <ul>
    <li>
      <b>Accès à Internet</b>, pour aller chercher les horaires — sans elle, l'application n'aurait
      rien à afficher.
    </li>
    <li>
      <b>Envoyer des notifications</b>, demandée après la configuration initiale, et refusable :
      l'application reste utilisable sans, vous n'aurez simplement pas d'alerte.
    </li>
    <li>
      <b>Installer des applications inconnues</b>, parce que TERMinus n'est pas distribuée par un
      magasin d'applications : c'est le seul moyen de vous proposer ses mises à jour, et rien ne
      s'installe sans que vous le demandiez.
    </li>
  </ul>
  <p>Six autres sont techniques : elles font vivre le rafraîchissement de fond et les alertes.</p>
  <ul>
    <li>
      <b>Connaître l'état de la connexion</b>, pour ne pas tenter d'aller chercher des données quand
      le téléphone est hors ligne.
    </li>
    <li>
      <b>Faire vibrer le téléphone</b>, pour qu'une alerte de retard puisse se signaler autrement
      qu'en silence.
    </li>
    <li>
      <b>Empêcher la mise en veille</b>, le temps très court d'un rafraîchissement, pour qu'il aille
      à son terme.
    </li>
    <li>
      <b>Se relancer au démarrage du téléphone</b>, pour que le cycle reprenne après un redémarrage
      sans que vous ayez à rouvrir l'application.
    </li>
    <li>
      <b>Exécuter une tâche en arrière-plan</b>, qui est la permission qu'Android exige pour ce
      cycle.
    </li>
    <li>
      <b>Une permission propre à l'application</b>, créée automatiquement par une bibliothèque
      Android : elle sert uniquement à ce que les composants internes de TERMinus se parlent entre
      eux sans être accessibles aux autres applications du téléphone.
    </li>
  </ul>
  <p>
    Quatre permissions figuraient auparavant dans la fiche de l'application sans que nous nous en
    servions : la bibliothèque de mise à jour les ajoutait automatiquement. Elles ont été retirées —
    accès au stockage partagé en lecture et en écriture, état du Wi-Fi, et une installation de
    paquets réservée aux applications du système. Le fichier de mise à jour est d'ailleurs
    téléchargé dans l'espace privé de l'application, jamais dans votre stockage partagé.
  </p>
  <p>
    <b>Aucune permission de localisation n'est demandée.</b> L'application ne sait pas où vous êtes :
    elle sait seulement quelles gares vous avez choisies, et elle est la seule à le savoir.
  </p>

  <h2>Signaler un problème</h2>
  <p>
    Depuis l'écran « À propos », l'application propose de nous signaler un dysfonctionnement. C'est
    le <b>seul</b> cas où une information quitte votre téléphone à destination de l'éditeur, et il
    ne se produit <b>que si vous le déclenchez</b>.
  </p>
  <p>
    Ce que le rapport contient : la version de l'application, la date et la taille du référentiel
    horaire installé, l'état du flux temps réel, vos réglages d'affichage (thème, taille du texte,
    contraste), la version de votre système, l'écran d'où part le signalement, et le texte que vous
    écrivez. <b
      >La gare et le sens que vous consultiez n'y figurent que si vous cochez la case prévue</b
    > — elle est décochée par défaut, parce que ces deux informations dessinent un trajet.
  </p>
  <p>
    Le rapport complet vous est <b>affiché avant tout envoi</b> : rien ne part que vous n'ayez pu lire,
    et vous pouvez modifier votre texte ou renoncer. Deux sorties vous sont proposées : ouvrir votre application
    de messagerie sur un courriel prérempli, ou copier le rapport pour en faire ce que vous voulez. L'application
    n'envoie rien elle-même — c'est votre client de messagerie qui envoie, et votre adresse d'expéditeur
    nous parvient donc avec le message.
  </p>
  <p>
    Ces courriels sont conservés le temps de traiter le signalement, puis supprimés. Ils ne sont ni
    recoupés, ni transmis, ni utilisés pour autre chose.
  </p>

  <h2>Vos droits</h2>
  <p>
    Le RGPD vous ouvre un droit d'accès, de rectification, d'effacement, de limitation et
    d'opposition.
  </p>
  <p>
    <b>Tant que vous ne nous avez pas écrit</b>, nous ne détenons aucune donnée vous concernant et
    nous ne pouvons vous identifier d'aucune manière. Dans cette situation, l'article 11 du RGPD
    prévoit que les droits d'accès, de rectification, d'effacement, de limitation et de portabilité
    ne s'exercent pas auprès du responsable de traitement : il n'aurait rien à vous montrer, ni rien
    à corriger.
  </p>
  <p>
    En pratique, vous exercez ces droits <b>directement sur votre appareil</b>, et sans nous
    demander la permission :
  </p>
  <ul>
    <li>consulter et modifier vos données : les Réglages de l'application ;</li>
    <li>
      tout effacer : effacer les données de l'application dans les réglages Android, ou la
      désinstaller ;
    </li>
    <li>
      couper les notifications : le réglage dédié dans l'application, ou la permission Android.
    </li>
  </ul>
  <p>
    Si vous nous avez envoyé un signalement, ces droits s'exercent alors normalement sur ce courriel
    : écrivez-nous et nous le supprimons.
  </p>
  <p>
    Vous pouvez écrire à <a href="mailto:kevin@delfour.co">kevin@delfour.co</a> pour toute question,
    et vous avez le droit d'introduire une réclamation auprès de la <b>CNIL</b> (3 place de
    Fontenoy, TSA 80715, 75334 Paris Cedex 07 — <a href="https://www.cnil.fr">cnil.fr</a>).
  </p>

  <h2>Ce site</h2>
  <p>
    Ce site est constitué de pages statiques hébergées par GitHub Pages. Il ne dépose aucun cookie
    et ne conserve rien dans votre navigateur.
  </p>
  <p>
    Deux pages — l'accueil et la page des statistiques — vont chercher des fichiers de données sur
    <b>raw.githubusercontent.com</b> au moment où vous les affichez. Votre navigateur contacte donc cette
    adresse en plus de celle du site ; il s'agit du même hébergeur.
  </p>
  <p>
    GitHub, en tant qu'hébergeur, peut conserver des journaux techniques de connexion, dont votre
    adresse IP, à des fins de fonctionnement et de sécurité, conformément à sa propre politique de
    confidentialité. Nous n'y avons pas accès.
  </p>

  <h2>Responsable de traitement</h2>
  <p>Kevin Delfour — <a href="mailto:kevin@delfour.co">kevin@delfour.co</a>.</p>
  <p>
    Hors signalement que vous choisissez de nous envoyer, nous ne recevons aucune de vos données,
    mais c'est bien nous qui décidons de ce que l'application enregistre sur votre téléphone et des
    serveurs qu'elle contacte. À ce titre, la responsabilité de ces choix nous revient, et cette
    page est là pour en rendre compte.
  </p>
</article>
