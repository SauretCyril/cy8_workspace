# 📖 GUIDE UTILISATION - NOUVEAU SYSTÈME DE MONITORING

## 🎯 Comment utiliser le nouveau système de monitoring temps réel

### 🚀 **Lancement de l'application**
```bash
python main.py
# ou
start.bat
```

## 📊 **Onglet "Exécutions" - Tableau temps réel**

### Ce que vous verrez maintenant :

#### ✅ **Colonnes améliorées :**
- **Message** : Progression détaillée avec pourcentage et temps écoulé
- **Progression** : Barre de progression mise à jour en temps réel
- **Monitoring** : Statut individuel par exécution

#### 📈 **Exemples d'affichage temps réel :**
```
Message: Workflow en attente... (⏱️ 2.1s)
Monitoring: 🔄 En attente

Message: Génération en cours 25% (⏱️ 15.3s) - Node: VAE Encode
Monitoring: ⚡ En cours

Message: Génération en cours 67% (⏱️ 32.7s) - Node: KSampler
Monitoring: ⚡ En cours

Message: Workflow terminé ! Images récupérées (⏱️ 58.2s)
Monitoring: ✅ Terminé
```

### 🔄 **Mise à jour automatique :**
- Le **temps écoulé** se met à jour **toutes les secondes**
- La **progression** vient directement de **ComfyUI** (pas d'estimation)
- Les **statuts** sont **individuels** par exécution

## 🔍 **Nouvel Onglet "Monitoring"**

### 📝 **Logs en temps réel :**
Cliquez sur l'onglet **"🔍 Monitoring"** pour voir :

#### Logs détaillés :
```
[19:03:24] 🔌 Démarrage surveillance WebSocket pour abc123
[19:03:25] 🔄 Progression temps réel: abc123 - 15% (node: VAE Encode)
[19:03:28] 🔄 Progression temps réel: abc123 - 45% (node: KSampler)
[19:03:30] 🔄 Progression temps réel: abc123 - 67% (node: KSampler)
[19:03:45] ✅ Workflow abc123 terminé, récupération des images...
[19:03:47] 📁 Images récupérées pour abc123: 4 fichiers
```

#### Contrôles disponibles :
- **🧹 Clear** : Efface les logs affichés
- **⏸️ Pause/▶️ Resume** : Met en pause/reprend la surveillance
- **📊 Statistiques** : Affiche l'état du système

### 📊 **Statistiques système :**
Cliquez sur **"📊 Statistiques"** pour voir :
```
=== STATISTIQUES WORKFLOW MONITOR ===
Workflows surveillés: 3
Surveillance active: Oui
Connexions WebSocket: 2
Dernière activité: il y a 5 secondes
Logs générés: 47
```

## 🎯 **Workflow d'utilisation typique**

### 1. **Lancer un workflow :**
1. Allez dans l'onglet **"Prompts"**
2. Sélectionnez un prompt
3. Cliquez **"Exécuter"**

### 2. **Suivre la progression :**
1. Allez dans l'onglet **"Exécutions"**
2. Observez la ligne de votre workflow :
   - **Message** : Progression avec % et temps
   - **Progression** : Barre visuelle
   - **Monitoring** : Statut en temps réel

### 3. **Voir les détails :**
1. Allez dans l'onglet **"🔍 Monitoring"**
2. Observez les logs détaillés en temps réel
3. Utilisez les contrôles si nécessaire

## 🚨 **Résolution de problèmes**

### ❌ **Plus d'erreur "main thread is not in main loop"**
- **Avant** : L'application plantait lors de la récupération d'images
- **Maintenant** : Correction automatique avec fallback

### 🔄 **Si la progression ne s'affiche pas :**
1. Vérifiez que **ComfyUI est démarré**
2. Allez dans l'onglet **"🔍 Monitoring"**
3. Regardez s'il y a des messages d'erreur WebSocket
4. La progression fonctionne uniquement avec ComfyUI **en cours d'exécution**

### 📊 **Si le tableau ne se met pas à jour :**
1. La mise à jour se fait **automatiquement toutes les secondes**
2. En cas de problème, redémarrez l'application
3. Vérifiez les logs dans l'onglet **"🔍 Monitoring"**

## 💡 **Fonctionnalités avancées**

### ⏱️ **Temps précis :**
- Affiché avec **1 décimale** : `(⏱️ 45.3s)`
- Mis à jour **en temps réel** toutes les secondes
- **Même si ComfyUI ne répond pas**

### 🔌 **WebSocket avancé :**
- **Connexion automatique** pour chaque workflow
- **Surveillance en parallèle** de plusieurs workflows
- **Reconnexion automatique** en cas de perte

### 📈 **Progression exacte :**
- **Pourcentages réels** de ComfyUI (pas d'estimation)
- **Nom du node** en cours d'exécution
- **Temps restant estimé** (si disponible dans ComfyUI)

## 🎉 **Avantages du nouveau système**

### ✅ **Pour l'utilisateur :**
- **Visibilité complète** sur l'état des workflows
- **Temps de traitement** visible en temps réel
- **Debugging facilité** avec logs détaillés
- **Interface responsive** et moderne

### ✅ **Pour le développement :**
- **Thread-safety** garantie
- **Logs structurés** pour debugging
- **Architecture modulaire** et extensible
- **Tests automatisés** pour la stabilité

## 🚀 **Prochaines étapes suggérées**

1. **Testez différents workflows** pour voir la progression
2. **Explorez l'onglet monitoring** pour comprendre le système
3. **Utilisez les statistiques** pour optimiser vos workflows
4. **Rapportez tout problème** pour amélioration continue

---

**Le système de monitoring est maintenant complètement opérationnel ! 🎯**

Plus besoin de deviner ce qui se passe - tout est visible en temps réel ! ✨
