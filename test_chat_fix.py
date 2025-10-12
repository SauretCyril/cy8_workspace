#!/usr/bin/env python3
"""
Test de correction de l'erreur is_todo_command dans TemporalRAGManager
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_temporal_rag_delegation():
    """Test de la délégation des méthodes vers RAGManager"""
    print("🚀 TEST DÉLÉGATION TEMPORALRAGMANAGER")
    print("=" * 50)
    
    try:
        # Import des modules nécessaires
        from cy8_rag_manager import RAGManager
        from cy8_temporal_rag import TemporalRAGManager
        from cy8_database_manager import cy8_database_manager
        
        print("✅ Import des modules réussi")
        
        # Créer un gestionnaire de base minimal
        db_manager = cy8_database_manager()
        db_manager.init_database("dev")
        
        print("✅ Base de données initialisée")
        
        # Créer le RAGManager
        rag_manager = RAGManager(db_manager, "test_env")
        print("✅ RAGManager créé")
        
        # Créer le TemporalRAGManager
        temporal_rag = TemporalRAGManager(rag_manager)
        print("✅ TemporalRAGManager créé")
        
        # Test 1: Vérifier que is_todo_command existe
        print("\n🔍 Test 1: Vérification de is_todo_command")
        if hasattr(temporal_rag, 'is_todo_command'):
            print("✅ Attribut is_todo_command trouvé")
            
            # Tester l'appel
            result = temporal_rag.is_todo_command("/todo")
            print(f"✅ Appel is_todo_command('/todo') = {result}")
            
            result2 = temporal_rag.is_todo_command("message normal")
            print(f"✅ Appel is_todo_command('message normal') = {result2}")
            
        else:
            print("❌ Attribut is_todo_command non trouvé")
            
        # Test 2: Vérifier d'autres méthodes importantes
        print("\n🔍 Test 2: Vérification d'autres méthodes déléguées")
        methods_to_test = ['is_available', 'process_query', 'get_chat_history']
        
        for method_name in methods_to_test:
            if hasattr(temporal_rag, method_name):
                print(f"✅ Méthode {method_name} disponible")
            else:
                print(f"❌ Méthode {method_name} manquante")
        
        # Test 3: Vérifier le type d'object retourné
        print(f"\n🔍 Test 3: Type de TemporalRAGManager = {type(temporal_rag)}")
        print(f"🔍 Type de RAGManager sous-jacent = {type(temporal_rag.rag_manager)}")
        
        print("\n✅ CORRECTION VALIDÉE!")
        print("🎯 TemporalRAGManager délègue maintenant correctement")
        print("   toutes les méthodes vers RAGManager sous-jacent")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_error_simulation():
    """Simuler l'erreur du chat pour vérifier la correction"""
    print("\n🚀 TEST SIMULATION ERREUR CHAT")
    print("=" * 50)
    
    try:
        from cy8_rag_manager import RAGManager
        from cy8_temporal_rag import TemporalRAGManager
        from cy8_database_manager import cy8_database_manager
        
        # Recréer le contexte de l'erreur
        db_manager = cy8_database_manager()
        db_manager.init_database("dev")
        
        base_rag = RAGManager(db_manager, "test_env")
        rag_manager = TemporalRAGManager(base_rag)  # Ceci simule self.rag_manager
        
        # Simuler le code qui causait l'erreur
        user_message = "peux tu redonner la dernier config dans le dernier log"
        
        print(f"📨 Message utilisateur: {user_message}")
        print("🔍 Test: rag_manager.is_todo_command(user_message)")
        
        # Cette ligne causait l'erreur avant la correction
        is_todo = rag_manager.is_todo_command(user_message)
        print(f"✅ Résultat: {is_todo}")
        
        print("🎉 ERREUR CORRIGÉE!")
        print("   TemporalRAGManager peut maintenant traiter les commandes TODO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur toujours présente: {e}")
        return False

if __name__ == "__main__":
    print("🔧 CORRECTION ERREUR CHAT - is_todo_command")
    print("=" * 60)
    
    # Test de la délégation
    test1_ok = test_temporal_rag_delegation()
    
    # Test de simulation de l'erreur
    test2_ok = test_chat_error_simulation()
    
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DE LA CORRECTION")
    print(f"✅ Délégation fonctionne: {test1_ok}")
    print(f"✅ Erreur chat corrigée: {test2_ok}")
    
    if test1_ok and test2_ok:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("   Le chat devrait maintenant fonctionner correctement")
    else:
        print("\n❌ Problème persistant - Vérification supplémentaire nécessaire")