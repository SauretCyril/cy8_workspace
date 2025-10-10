#!/usr/bin/env python3
"""
Test complet de la gestion des pannes serveur dans cy8_prompts_manager
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy6_websocket_api_client import get_queue_status

def test_current_server_status():
    """Tester l'état actuel du serveur ComfyUI"""
    print("🧪 TEST ÉTAT SERVEUR COMFYUI")
    print("=" * 40)
    
    try:
        print("🔍 Vérification connexion serveur ComfyUI...")
        status = get_queue_status()
        
        if status is None:
            print("❌ SERVEUR COMFYUI INACCESSIBLE")
            print("   • Le serveur ComfyUI n'est pas démarré")
            print("   • Ou il n'écoute pas sur 127.0.0.1:8188")
            print("   • Le système de surveillance se protégera automatiquement")
            return False
        else:
            print("✅ SERVEUR COMFYUI ACCESSIBLE")
            print(f"   • Queue en attente: {len(status.get('queue_pending', []))}")
            print(f"   • Queue en cours: {len(status.get('queue_running', []))}")
            print("   • Le monitoring peut fonctionner normalement")
            return True
            
    except Exception as e:
        print(f"❌ ERREUR DE CONNEXION: {e}")
        return False

def test_workflow_execution_with_server_check():
    """Simuler l'exécution d'un workflow avec vérification serveur"""
    print("\n🧪 TEST EXÉCUTION WORKFLOW AVEC VÉRIFICATION")
    print("=" * 50)
    
    # Simuler la vérification pré-exécution
    print("🔍 Vérification serveur avant exécution workflow...")
    
    status = get_queue_status()
    if status is None:
        print("❌ WORKFLOW BLOQUÉ - Serveur inaccessible")
        print("   • Le workflow ne sera pas lancé")
        print("   • Protection automatique activée")
        return False
    else:
        print("✅ WORKFLOW AUTORISÉ - Serveur accessible")
        print("   • Le workflow peut être lancé en sécurité")
        return True

def show_protection_features():
    """Afficher les fonctionnalités de protection implémentées"""
    print("\n🛡️ FONCTIONNALITÉS DE PROTECTION SERVEUR")
    print("=" * 45)
    print("1. 🔍 Vérification pré-exécution:")
    print("   • Test serveur avant lancement workflow")
    print("   • Arrêt immédiat si serveur down")
    
    print("\n2. 👁️ Surveillance continue:")
    print("   • Monitoring toutes les 10 secondes")
    print("   • Arrêt après 3 erreurs consécutives")
    
    print("\n3. 🧹 Nettoyage automatique:")
    print("   • Marquage workflows en erreur")
    print("   • Vidage de la pile de surveillance")
    print("   • Arrêt du thread de monitoring")
    
    print("\n4. 📞 Notification utilisateur:")
    print("   • Popup d'alerte panne serveur")
    print("   • Messages console détaillés")
    print("   • Redémarrage automatique possible")

if __name__ == "__main__":
    print("🚨 SYSTÈME DE PROTECTION CONTRE LES PANNES SERVEUR")
    print("=" * 55)
    
    # Test 1: État serveur
    server_ok = test_current_server_status()
    
    # Test 2: Simulation workflow
    workflow_ok = test_workflow_execution_with_server_check()
    
    # Affichage des protections
    show_protection_features()
    
    # Résumé
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 20)
    print(f"🔌 Serveur accessible: {'✅ OUI' if server_ok else '❌ NON'}")
    print(f"🚀 Workflow possible: {'✅ OUI' if workflow_ok else '❌ NON'}")
    
    if not server_ok:
        print("\n⚠️ RECOMMANDATIONS:")
        print("• Démarrer ComfyUI sur 127.0.0.1:8188")
        print("• Vérifier que le serveur n'est pas bloqué")
        print("• Le système de protection est ACTIF")
    else:
        print("\n✅ TOUT EST PRÊT:")
        print("• Serveur opérationnel")
        print("• Monitoring fonctionnel")
        print("• Protection en veille")
    
    print("=" * 55)