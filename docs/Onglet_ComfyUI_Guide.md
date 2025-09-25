# Onglet ComfyUI - Test de Connexion

## 🎯 Vue d'ensemble

L'application `cy8_prompts_manager` dispose maintenant d'un **onglet ComfyUI dédié** dans le panneau de détails des prompts pour tester la connexion avec ComfyUI de manière contrôlée.

## 📍 Localisation

L'onglet **"ComfyUI"** se trouve dans le panneau de détails des prompts, entre les onglets :
- Informations ← **ComfyUI** → Data

## 🎨 Interface

### Section principale : "Test de Connexion ComfyUI"

#### Informations serveur
- **Serveur** : Affiche l'adresse configurée (par défaut : `127.0.0.1:8188`)
- Source : Variable d'environnement `COMFYUI_SERVER` du fichier `.env`

#### Bouton de test
- **🔗 Tester la connexion** : Lance le test de connexion
- État pendant le test : **🔄 Test en cours...** (bouton désactivé)

#### Indicateur de statut
Icône dynamique + texte descriptif :

| État | Icône | Texte | Couleur |
|------|-------|-------|---------|
| Initial | ⚪ | "Cliquez sur 'Tester la connexion' pour vérifier" | Gris |
| En cours | 🟡 | "Test de connexion en cours..." | Orange |
| Succès | ✅ | "Connexion ComfyUI réussie" | Vert |
| Échec | ❌ | "ComfyUI non accessible" / "Erreur: ..." | Rouge |
| Timeout | ⏱️ | "ComfyUI : Timeout" | Orange |

### Section détails techniques (affichage dynamique)

Apparaît après le premier test avec :
- Informations de connexion HTTP
- Statistiques système ComfyUI (version, Python, etc.)
- Test WebSocket (si disponible)
- Messages d'erreur détaillés le cas échéant

## 🔧 Fonctionnalités du test

### Tests effectués
1. **Connexion HTTP** : Requête GET vers `/system_stats`
2. **Validation de réponse** : Vérification du code de statut 200
3. **Parsing des statistiques** : Extraction des informations système
4. **Test WebSocket** (optionnel) : Vérification de la connexion temps réel

### Informations récupérées
- **Version ComfyUI** : Version du serveur ComfyUI
- **Version Python** : Version Python du serveur
- **Statistiques système** : RAM, CPU, etc. (si disponibles)
- **État WebSocket** : Connexion temps réel active ou non

### Gestion des erreurs
- **ConnectionError** : Serveur non accessible
- **Timeout** : Délai d'attente dépassé (5 secondes)
- **HTTP non-200** : Erreurs serveur ComfyUI
- **Exceptions générales** : Autres erreurs techniques

## 🚨 Changements importants

### ❌ Tests automatiques supprimés
- **Avant** : Les tests d'exécution de workflow étaient inclus dans la validation automatique
- **Maintenant** : Les tests d'exécution sont uniquement accessibles via l'interface

### ✅ Contrôle utilisateur
- **Avantages** :
  - L'utilisateur contrôle quand tester la connexion
  - Pas d'interférence avec ComfyUI en production
  - Feedback visuel immédiat
  - Détails techniques disponibles à la demande

### 📝 Fichier `tests/test_comfyui_connection.py` modifié
- **Test d'exécution supprimé** : `test_workflow_execution()` retiré
- **Connexion uniquement** : Seul `test_comfyui_connection()` reste
- **Guide utilisateur** : Redirection vers l'onglet ComfyUI pour les tests complets

## 🎯 Utilisation

### Procédure de test
1. **Lancer l'application** : `python src/cy8_prompts_manager_main.py`
2. **Sélectionner un prompt** : Cliquer sur un prompt dans la liste
3. **Aller à l'onglet ComfyUI** : Cliquer sur l'onglet "ComfyUI"
4. **Tester la connexion** : Cliquer sur "🔗 Tester la connexion"
5. **Consulter les résultats** : Lire l'indicateur et les détails techniques

### Interprétation des résultats

#### ✅ Connexion réussie
```
✅ Connexion ComfyUI réussie
```
- ComfyUI est accessible et fonctionnel
- Les statistiques système sont affichées
- Prêt pour l'exécution de workflows

#### ❌ Connexion échouée
```
❌ ComfyUI non accessible
```
**Actions à effectuer :**
- Vérifier que ComfyUI est démarré
- Vérifier l'adresse dans le fichier `.env`
- Vérifier qu'aucun firewall ne bloque

#### ⏱️ Timeout
```
⏱️ ComfyUI : Timeout
```
**Causes possibles :**
- Serveur ComfyUI surchargé
- Connexion réseau lente
- ComfyUI en cours de traitement d'un gros workflow

## 🔧 Configuration

### Variables d'environnement
```env
# Fichier .env
COMFYUI_SERVER=127.0.0.1:8188
```

### Personnalisation
- **Timeout** : Modifiable dans `test_comfyui_connection()` (défaut : 5 secondes)
- **URL de test** : `/system_stats` endpoint de ComfyUI
- **Affichage** : Icônes et couleurs modifiables dans le code

## 💡 Avantages de cette approche

1. **Contrôle utilisateur** : Tests à la demande uniquement
2. **Feedback visuel** : Indicateurs clairs et colorés
3. **Informations détaillées** : Diagnostics techniques disponibles
4. **Sécurité** : Pas d'exécution automatique de workflows
5. **Intégration** : Directement dans l'interface principale
6. **Simplicité** : Un seul bouton pour tout tester
