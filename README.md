# Proxy Desk — ZZZ

Tableau de bord de routines Zenless Zone Zero.

## Déploiement
Dans **Settings → Pages → Build and deployment**, sélectionner **GitHub Actions**. Le déploiement s'effectue sur les commits de la branche main.

## Données des événements
Le site charge `feed/events.json` depuis son propre domaine. Le flux initial est volontairement vide : aucune échéance d'événement non vérifiée n'est publiée comme actuelle.

**Attention** : le déploiement automatique du JSON ne signifie pas qu'il est alimenté automatiquement. Un processus fiable de collecte/validation des annonces reste à installer.

## Données personnelles
Cases et préférences conservées dans le navigateur ; pas de synchronisation multi-appareils.
