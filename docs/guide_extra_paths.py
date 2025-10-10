#!/usr/bin/env python3
"""
Guide d'utilisation du tableau des extra paths dans cy8_prompts_manager

Ce script explique comment utiliser la fonctionnalité d'affichage des extra paths
dans l'onglet ComfyUI de l'application cy8_prompts_manager.
"""

print("""
🌟 GUIDE D'UTILISATION - Tableau des Extra Paths ComfyUI
========================================================

Le tableau des extra paths est intégré dans l'onglet "ComfyUI" de l'application.

📍 LOCALISATION :
- Onglet : "ComfyUI"
- Section : "🌍 Environnement ComfyUI - Extra Paths"
- Position : En bas de l'onglet ComfyUI

🔧 COMPOSANTS DISPONIBLES :
1. Informations de configuration (ID + Racine ComfyUI)
2. Bouton "🔄 Actualiser Extra Paths"
3. Zone de recherche (🔍 Rechercher)
4. Filtre par type (🏷️ Type: checkpoints, loras, etc.)
5. Bouton "📋 Copier chemin"
6. Tableau avec colonnes : Clé | Type | Chemin | Section

⚙️ ÉTAPES D'UTILISATION :

Étape 1: Démarrer ComfyUI
-------------------------
• Assurez-vous que ComfyUI est démarré sur 127.0.0.1:8188
• Vérifiez que le custom node ExtraPathReader est installé

Étape 2: Lancer l'application
-----------------------------
• Exécutez: python src/cy8_prompts_manager_main.py
• Ou utilisez: start.bat

Étape 3: Aller dans l'onglet ComfyUI
------------------------------------
• Cliquez sur l'onglet "ComfyUI"
• Faites défiler vers le bas jusqu'à la section "Environnement ComfyUI"

Étape 4: Identifier l'environnement
-----------------------------------
• Cliquez sur "🔍 Identifier l'environnement"
• Attendez que l'identification se termine
• Le tableau se remplira automatiquement

📊 FONCTIONNALITÉS DU TABLEAU :

Recherche:
• Tapez dans le champ "🔍 Rechercher" pour filtrer les chemins
• La recherche fonctionne sur les clés et les chemins

Filtrage:
• Utilisez le menu "🏷️ Type" pour filtrer par type d'extra path
• Types disponibles: checkpoints, loras, embeddings, vae, custom_nodes, controlnet

Copie:
• Sélectionnez une ligne dans le tableau
• Cliquez "📋 Copier chemin" pour copier le chemin dans le presse-papiers

Actualisation:
• Cliquez "🔄 Actualiser Extra Paths" pour recharger les données

🎨 COULEURS DU TABLEAU :
• checkpoints : Fond vert clair
• loras : Fond bleu clair
• embeddings : Fond jaune clair
• custom_nodes : Fond violet clair
• vae : Fond rose clair

❗ DÉPANNAGE :

Si le tableau est vide:
• Vérifiez que ComfyUI est démarré
• Cliquez sur "Identifier l'environnement"
• Vérifiez que le fichier extra_model_paths.yaml existe dans ComfyUI

Si l'identification échoue:
• Vérifiez la connexion à ComfyUI (bouton "🔗 Tester la connexion")
• Assurez-vous que le custom node ExtraPathReader est installé
• Consultez les logs dans la section "Détails techniques"

💡 ASTUCES :
• Le tableau se met à jour automatiquement après identification
• Les données sont stockées et persistent entre les sessions
• Vous pouvez combiner recherche et filtrage par type
• Double-cliquez sur une ligne pour sélectionner tout le texte

🚀 Pour une démonstration complète, lancez l'application et suivez ces étapes !
""")

# Optionnel: Lancer l'application directement
import sys
import os

if len(sys.argv) > 1 and sys.argv[1] == "--launch":
    print("\n🚀 Lancement de l'application...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from cy8_prompts_manager_main import main
        main()
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Essayez: python src/cy8_prompts_manager_main.py")
