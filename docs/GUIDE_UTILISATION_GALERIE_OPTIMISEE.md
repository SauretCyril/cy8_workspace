# 🎮 GUIDE D'UTILISATION - GALERIE OPTIMISÉE

## 🚀 DÉMARRAGE RAPIDE

### **Lancement de l'Application**
```bash
# Méthode 1: Script rapide
./start.bat                 # Windows
./start.sh                  # Linux/Mac

# Méthode 2: Direct
python src/cy8_prompts_manager_main.py

# Méthode 3: VS Code (F5)
```

### **Premier Accès à la Galerie**
1. **Aller** dans l'onglet **"Images"**
2. **Cliquer** sur le sous-onglet **"🖼️ Galerie complète"**
3. **Cliquer** sur **⚡ Recharger index** (première fois seulement)
4. **Patienter** pendant l'indexation (1-2 minutes selon le nombre d'images)
5. **Profiter** du chargement instantané pour les fois suivantes !

---

## 📋 UTILISATION QUOTIDIENNE

### **Interface de la Galerie**
```
🖼️ Galerie complète - Toutes les images du répertoire IMAGES_COLLECTE

[🔄 Actualiser] [⚡ Recharger index] [📊 Statistiques] [📁 Ouvrir dossier]

📸 Sélectionnée: image.png   [Actions contextuelles...]

[Grille 5 colonnes d'images]
```

### **Actions Rapides**

| Action | Résultat |
|--------|----------|
| **🔄 Actualiser** | Chargement instantané depuis l'index |
| **Simple clic** sur image | Sélectionne + affiche barre contextuelle |
| **Double-clic** sur image | Agrandit l'image dans popup |

---

## 🗑️ GESTION DES IMAGES

### **Suppression Intelligente**
1. **Sélectionner** une image (simple clic)
2. **Choisir** dans la barre contextuelle :
   - **🗑️ Marquer supprimée** : Cache l'image (récupérable)
   - **🗑️ Supprimer définitivement** : Supprime le fichier du disque

### **Images "Supprimées"**
- **Affichage** : Icône 🗑️ + fond gris
- **Restauration** : Bouton **♻️ Restaurer**
- **Statut** : Conservées sur le disque

---

## ⚡ OPTIMISATION PERFORMANCE

### **Statut Actuel**
L'application utilise déjà **Rust** pour une performance optimale :
```
🚀 Processeur Rust activé - Performance optimale
✅ Processeur: Rust
```

### **Temps de Chargement Typiques**
- **Première indexation** : 1-2 minutes (une seule fois)
- **Chargements suivants** : 0.2-0.5 seconde
- **Gain vs ancien système** : 50-100x plus rapide

### **Si Performance Dégradée**
1. **Vérifier** : Onglet Images > **📊 Statistiques**
2. **Backend** : Doit afficher "Rust" (optimal) ou "PIL" (standard)
3. **Cache** : Utiliser **🧹 Vider le cache** si nécessaire

---

## 📊 MONITORING ET STATISTIQUES

### **Accès aux Statistiques**
1. **Aller** dans la galerie
2. **Cliquer** sur **📊 Statistiques**
3. **Consulter** les informations détaillées

### **Informations Disponibles**
```
📸 Images totales: 1,245
✅ Images actives: 1,198
🗑️ Images supprimées: 47
💾 Taille totale: 2,156.8 MB
🧠 Cache mémoire: 150 miniatures

Backend: Rust (Optimisé)
```

---

## 🔧 MAINTENANCE

### **Nettoyage du Cache**
- **Quand** : Si l'application devient lente
- **Comment** : Statistiques > **🧹 Vider le cache**
- **Effet** : Libère la mémoire, rechargement automatique

### **Régénération de l'Index**
- **Quand** : Après ajout/suppression massive d'images
- **Comment** : **⚡ Recharger index** (force le re-scan complet)
- **Durée** : 1-2 minutes selon la taille de la collection

### **Résolution de Problèmes**
1. **Images manquantes** : ⚡ Recharger index
2. **Chargement lent** : 📊 Statistiques > 🧹 Vider le cache
3. **Erreurs d'affichage** : Fermer/relancer l'application

---

## 🎯 CONSEILS D'UTILISATION

### **Workflow Recommandé**
1. **Organisation** : Placer toutes vos images dans `IMAGES_COLLECTE`
2. **Indexation** : Lancer ⚡ Recharger index après ajouts importants
3. **Navigation** : Utiliser 🔄 Actualiser pour la navigation quotidienne
4. **Gestion** : Utiliser suppression soft (🗑️ Marquer) plutôt que définitive

### **Bonnes Pratiques**
- **Suppression soft** : Permet de récupérer une image supprimée par erreur
- **Cache** : Laisser actif pour la performance, vider si problème
- **Index** : Re-scanner seulement si nécessaire (lourd)

### **Limitations**
- **Formats supportés** : PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP
- **Taille maximale** : Limitée par la mémoire disponible
- **Répertoire** : Défini par la variable `IMAGES_COLLECTE`

---

## 🚨 DÉPANNAGE

### **Problèmes Courants**

#### **"Aucune image trouvée"**
- **Vérifier** la variable `IMAGES_COLLECTE` dans `.env`
- **S'assurer** que le répertoire existe et contient des images

#### **Chargement très lent**
- **Vérifier** le backend dans Statistiques
- **Vider** le cache si saturé
- **Re-indexer** si corruption suspectée

#### **Images dupliquées**
- **Symptôme** : Mêmes images affichées plusieurs fois
- **Solution** : ⚡ Recharger index (force le nettoyage)

#### **Erreur de base de données**
- **Localisation** : `~/cy8_images_index.db`
- **Solution** : Supprimer le fichier et re-indexer
- **Prévention** : Fermer proprement l'application

---

## 🎉 PROFITER DES AMÉLIORATIONS

### **Gains Immédiats**
- **Vitesse** : Navigation ultra-rapide dans la galerie
- **Contrôle** : Chargement manuel, pas d'attente imposée
- **Sécurité** : Suppression soft récupérable
- **Monitoring** : Statistiques détaillées

### **Fonctionnalités Avancées**
- **Index persistant** : Pas de re-scan à chaque démarrage
- **Cache intelligent** : Optimisation mémoire automatique
- **Multi-backend** : Rust optimisé avec fallback PIL
- **Gestion d'erreurs** : Récupération gracieuse des problèmes

**La galerie est maintenant optimisée pour une utilisation fluide et performante avec des milliers d'images !**
