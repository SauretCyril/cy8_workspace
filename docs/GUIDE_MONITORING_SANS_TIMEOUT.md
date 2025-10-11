# Guide d'utilisation - Monitoring des Workflows sans Timeout

## Vue d'ensemble

Le système de monitoring des workflows a été amélioré pour supprimer les timeouts et fournir une surveillance continue. Le tableau de suivi des exécutions fait maintenant office de composant de visualisation du monitoring.

## Fonctionnalités

### 1. Suppression du Timeout
- **Avant** : Les workflows étaient marqués en échec après 10 minutes
- **Maintenant** : Surveillance continue tant que le serveur ComfyUI répond
- **Avantage** : Les workflows longs ne sont plus interrompus artificiellement

### 2. Colonne Monitoring dans le tableau des exécutions
Le tableau des exécutions affiche maintenant une colonne "Monitoring" avec :
- `✅ Actif` : Le monitoring fonctionne normalement
- `🔄 Actif (n)` : Le monitoring est actif avec n tâches en cours
- `🚨 Panne` : Panne serveur ComfyUI détectée
- `⏹️ Arrêté` : Le monitoring est arrêté
- `❓ Non init.` : Le monitoring n'est pas initialisé
- `❌ Erreur` : Erreur dans le monitoring

### 3. Informations détaillées du monitoring
Quand vous sélectionnez une exécution dans le tableau, les détails affichent :
- Statut du monitoring
- État du thread de surveillance
- Nombre de tâches actives
- Nombre de workflows traités
- Nombre d'images récupérées
- Compteur d'erreurs serveur
- Dernière activité

## Fonctionnement automatique

### Démarrage automatique
- Le monitoring démarre automatiquement au lancement de l'application
- Pas besoin d'intervention manuelle

### Gestion des pannes serveur
- Détection automatique des pannes serveur ComfyUI
- Arrêt automatique du monitoring en cas de panne persistante
- Notification à l'utilisateur via popup
- Marquage des workflows en cours comme échoués

### Surveillance continue
- Vérification toutes les 3 secondes
- Pas de timeout sur les workflows individuels
- Surveillance tant que le serveur répond

## Utilisation

### Visualiser l'état du monitoring
1. Ouvrez l'onglet "🔄 Exécutions" dans l'application
2. Regardez la colonne "Monitoring" pour voir l'état actuel
3. Sélectionnez une exécution pour voir les détails complets

### Interpréter les statuts
- **Actif** : Tout fonctionne normalement
- **Actif (n)** : n workflows sont en cours de traitement
- **Panne** : Le serveur ComfyUI n'est pas accessible
- **Arrêté** : Le monitoring a été arrêté (redémarrage nécessaire)

### En cas de panne serveur
1. Vérifiez que ComfyUI est démarré
2. Redémarrez l'application si nécessaire
3. Le monitoring reprendra automatiquement

## Avantages

1. **Pas de limitation temporelle** : Les workflows complexes peuvent s'exécuter sans limite
2. **Surveillance en temps réel** : Visualisation continue de l'état du monitoring
3. **Gestion robuste des pannes** : Détection et gestion automatique des problèmes serveur
4. **Interface intégrée** : Le tableau des exécutions sert de console de monitoring

## Statistiques disponibles

Le système collecte et affiche :
- Nombre total de workflows traités
- Nombre total d'images récupérées
- Temps de dernière activité
- Compteur d'erreurs serveur
- Nombre de tâches actives

Ces informations sont disponibles dans les détails d'exécution et permettent de surveiller la performance globale du système.
