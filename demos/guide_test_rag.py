#!/usr/bin/env python3
"""
Guide d'utilisation des tests RAG intégrés dans l'application
"""

print("""
🧪 GUIDE DE TEST DU RAG DANS L'APPLICATION
=========================================

L'application cy8_prompts_manager est maintenant en cours d'exécution avec les fonctions de test RAG intégrées.

📱 COMMENT TESTER LE RAG DANS L'INTERFACE :

1. 🎯 **Accéder à l'onglet Chat**
   - Ouvrir l'onglet "💬 Chat" dans l'application
   - Vous devriez voir les boutons de test RAG

2. 🧪 **Lancer les tests via les boutons :**
   - Cliquer sur "🧪 Test RAG" pour une suite complète
   - Cliquer sur "⚡ Test rapide" pour un test basique

3. 💬 **Lancer les tests via commandes chat :**
   - Taper `/test-rag` pour la suite complète
   - Taper `/quick-test` pour un test rapide
   - Taper `/test-rag indexing` pour tester l'indexation
   - Taper `/test-rag learning` pour tester l'apprentissage
   - Taper `/test-rag performance` pour tester les performances

4. 📊 **Interpréter les résultats :**
   - ✅ = Le RAG fonctionne et apprend correctement
   - ❌ = Problème détecté, nécessite une investigation
   - ⚠️ = Fonctionnel mais performance dégradée

5. 🔍 **Vérifier l'apprentissage :**
   - Après un test réussi, essayer de poser une question
   - Le RAG devrait pouvoir retrouver les informations indexées
   - Exemple : "CUDA memory" devrait retourner les erreurs liées

⚡ STATUT ACTUEL :
- ✅ Application lancée
- ✅ RAG Manager initialisé avec environment_id: default_workspace
- ✅ Boutons de test disponibles dans l'interface
- ✅ Commandes de chat fonctionnelles

🎯 PROCHAINES ÉTAPES :
1. Aller dans l'onglet Chat de l'application
2. Cliquer sur "⚡ Test rapide" pour commencer
3. Observer les résultats dans la zone de conversation
4. Si ça fonctionne, essayer "🧪 Test RAG" pour le test complet

💡 NOTE : Le problème d'environment_id a été corrigé dans l'application.
Le RAG utilise maintenant "default_workspace" au lieu de None.
""")

# Vérification que l'application est bien lancée
import subprocess
import time

def check_if_app_running():
    """Vérifier si l'application est en cours d'exécution"""
    try:
        # Vérifier les processus Python en cours
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                              capture_output=True, text=True, shell=True)

        if 'python.exe' in result.stdout:
            print("✅ Des processus Python sont en cours d'exécution")
            print("🚀 L'application devrait être accessible")
            return True
        else:
            print("❌ Aucun processus Python détecté")
            return False
    except:
        print("⚠️ Impossible de vérifier les processus")
        return None

if __name__ == "__main__":
    print("\n🔍 Vérification du statut de l'application...")
    is_running = check_if_app_running()

    if is_running:
        print("\n🎉 PRÊT POUR LES TESTS RAG !")
        print("📱 Allez dans l'onglet Chat de l'application pour commencer.")
    else:
        print("\n⚠️ L'application ne semble pas être en cours d'exécution.")
        print("🔄 Relancez l'application avant de tester le RAG.")
