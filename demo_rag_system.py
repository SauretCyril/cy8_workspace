#!/usr/bin/env python3
"""
Démonstration des fonctionnalités RAG pour ComfyUI
Script de test et d'initialisation avec des données d'exemple
"""

import sys
import os

# Ajouter le répertoire src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from datetime import datetime, timedelta
import random

# Import des classes
try:
    from cy8_rag_manager import RAGManager
    from cy8_database_manager import cy8_database_manager
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def setup_demo_environment():
    """Configurer un environnement de démonstration avec données réalistes"""
    
    print("🎬 DÉMONSTRATION RAG COMFYUI")
    print("=" * 60)
    
    # Initialiser avec la base principale
    db_path = "G:/tmp/prompts_manager.db"
    print(f"📊 Base de données: {db_path}")
    
    db_manager = cy8_database_manager(db_path)
    db_manager.init_database("dev")  # Initialiser en mode dev
    
    # Environnement de démonstration
    env_id = "G11_01"  # Utiliser un environnement existant
    print(f"🖥️ Environnement: {env_id}")
    
    # Initialiser le RAG
    rag = RAGManager(db_manager, env_id)
    
    if not rag.is_available():
        print("❌ RAG non disponible - vérifiez les dépendances")
        return None, None
    
    print("✅ RAG initialisé")
    
    return db_manager, rag


def add_realistic_constraints(rag):
    """Ajouter des contraintes système réalistes"""
    print("\n🚫 Ajout de contraintes système réalistes...")
    
    constraints = [
        ("numpy_version", "1.24.4", "Ne peut pas passer à numpy 2.x - incompatibilité avec custom nodes existants"),
        ("vram_limit", "12GB", "RTX 3060 Ti - limitation pour les gros modèles SDXL"),
        ("python_version", "3.10.11", "Version stable recommandée pour ComfyUI"),
        ("torch_version", "2.0.1+cu118", "Version CUDA compatible avec le système"),
        ("batch_size_limit", "2", "Limitation batch size pour éviter OOM"),
        ("model_size_limit", "7GB", "Modèles trop volumineux causent des erreurs mémoire"),
        ("custom_node_conflict", "was-node-suite-comfyui", "Incompatibilité avec certains nodes d'inpainting"),
    ]
    
    for constraint_type, value, description in constraints:
        rag.add_constraint(constraint_type, value, description)
        print(f"  ✅ {constraint_type}: {value}")
    
    print(f"📋 {len(constraints)} contraintes ajoutées")


def add_realistic_analyses(rag):
    """Ajouter des analyses de logs réalistes"""
    print("\n📝 Indexation d'analyses de logs réalistes...")
    
    # Analyses variées sur plusieurs jours
    base_time = datetime.now() - timedelta(days=7)
    
    analyses = [
        {
            "timestamp": (base_time + timedelta(hours=1)).isoformat(),
            "type": "startup_error",
            "summary": "Échec de démarrage ComfyUI - conflit numpy",
            "errors": [
                {
                    "type": "dependency_conflict",
                    "message": "AttributeError: module 'numpy' has no attribute 'bool'",
                    "solution": "Downgrade numpy de 2.1.0 vers 1.24.4"
                }
            ],
            "successes": [],
            "recommendations": ["Fixer numpy à 1.24.4 dans requirements.txt"]
        },
        {
            "timestamp": (base_time + timedelta(hours=8)).isoformat(),
            "type": "memory_error",
            "summary": "VRAM insuffisante pour SDXL",
            "errors": [
                {
                    "type": "cuda_oom",
                    "message": "RuntimeError: CUDA out of memory. Tried to allocate 2.73 GiB",
                    "solution": "Réduire batch_size à 1 ou utiliser model offloading"
                }
            ],
            "successes": ["Custom nodes chargés correctement"],
            "recommendations": ["Activer attention offloading", "Utiliser SDXL Lightning pour réduire VRAM"]
        },
        {
            "timestamp": (base_time + timedelta(days=1, hours=2)).isoformat(),
            "type": "optimization_success",
            "summary": "Optimisation pipeline réussie",
            "errors": [],
            "successes": [
                "Temps de génération réduit de 40%",
                "VRAM stabilisée à 11.2GB",
                "Pipeline stable sur 50 générations"
            ],
            "recommendations": ["Documenter cette configuration", "Créer un preset optimisé"]
        },
        {
            "timestamp": (base_time + timedelta(days=2, hours=5)).isoformat(),
            "type": "custom_node_error",
            "summary": "Erreur installation WAS Node Suite",
            "errors": [
                {
                    "type": "installation_error",
                    "message": "ModuleNotFoundError: No module named 'segment_anything'",
                    "solution": "Installer manuellement: pip install segment-anything"
                }
            ],
            "successes": ["80% des custom nodes installés"],
            "recommendations": ["Vérifier requirements de chaque custom node avant installation"]
        },
        {
            "timestamp": (base_time + timedelta(days=3, hours=10)).isoformat(),
            "type": "workflow_success", 
            "summary": "Workflow inpainting fonctionnel",
            "errors": [],
            "successes": [
                "Inpainting haute qualité atteint",
                "ControlNet + IP-Adapter compatibles",
                "Temps de traitement acceptable (45s)"
            ],
            "recommendations": ["Sauvegarder ce workflow comme template", "Tester sur différents types d'images"]
        },
        {
            "timestamp": (base_time + timedelta(days=4, hours=3)).isoformat(),
            "type": "performance_issue",
            "summary": "Ralentissement après mise à jour",
            "errors": [
                {
                    "type": "performance_degradation",
                    "message": "Génération 3x plus lente après update ComfyUI",
                    "solution": "Revenir à la version précédente ou réinstaller"
                }
            ],
            "successes": [],
            "recommendations": ["Toujours backup avant mise à jour", "Tester sur workflow simple d'abord"]
        },
        {
            "timestamp": (base_time + timedelta(days=5, hours=7)).isoformat(),
            "type": "config_optimization",
            "summary": "Configuration ControlNet optimisée",
            "errors": [],
            "successes": [
                "ControlNet Depth fonctionnel",
                "Pas de conflit avec IP-Adapter", 
                "Résultats cohérents"
            ],
            "recommendations": ["Documenter les paramètres ControlNet", "Créer presets par type de contrôle"]
        }
    ]
    
    indexed_count = 0
    for analysis in analyses:
        if rag.index_analysis_result(analysis):
            indexed_count += 1
    
    print(f"✅ {indexed_count}/{len(analyses)} analyses indexées")


def demonstrate_search_capabilities(rag):
    """Démontrer les capacités de recherche"""
    print("\n🔍 Démonstration des capacités de recherche...")
    
    test_queries = [
        "problème mémoire VRAM",
        "erreur numpy AttributeError",
        "optimisation performance",
        "installation custom nodes",
        "conflit ControlNet IP-Adapter",
        "ComfyUI ralentissement",
        "SDXL batch size",
    ]
    
    for query in test_queries:
        print(f"\n🔎 Recherche: '{query}'")
        results = rag.search_similar_issues(query, limit=2)
        
        if results:
            for i, result in enumerate(results, 1):
                similarity = max(0, int(result['similarity'] * 100))
                print(f"  {i}. Pertinence: {similarity}%")
                print(f"     {result['content'][:150]}...")
        else:
            print("  ❌ Aucun résultat")


def demonstrate_server_status(rag):
    """Démontrer le résumé de statut du serveur"""
    print("\n📊 État du serveur ComfyUI...")
    
    status = rag.get_server_status_summary()
    
    print(f"🖥️  Environnement: {status['environment_id']}")
    print(f"📈 État actuel: {status['current_state']['value']}")
    
    if status['constraints']:
        print(f"\n🚫 Contraintes système ({len(status['constraints'])}):")
        for constraint in status['constraints'][:5]:
            print(f"  • {constraint['type']}: {constraint['value']}")
            if constraint['description']:
                print(f"    💬 {constraint['description']}")
    
    if status['recurring_errors']:
        print(f"\n⚠️  Erreurs récurrentes ({len(status['recurring_errors'])}):")
        for error in status['recurring_errors']:
            print(f"  • {error['message']} (x{error['frequency']})")
            if error['solution']:
                print(f"    💡 {error['solution']}")


def demonstrate_chat_context(rag):
    """Démontrer la génération de contexte pour chat"""
    print("\n💬 Exemples de contexte pour chat...")
    
    queries = [
        "J'ai une erreur de mémoire",
        "Comment optimiser mon workflow",
        "Problème avec custom nodes",
    ]
    
    for query in queries:
        print(f"\n👤 Question: '{query}'")
        context = rag.generate_chat_context(query)
        print("🤖 Contexte généré:")
        print("-" * 40)
        # Afficher les premières lignes du contexte
        lines = context.split('\n')[:8]
        for line in lines:
            print(f"   {line}")
        if len(context.split('\n')) > 8:
            print("   ...")


def main():
    """Fonction principale de démonstration"""
    try:
        # Configuration
        db_manager, rag = setup_demo_environment()
        if not rag:
            return
        
        # Étapes de démonstration
        add_realistic_constraints(rag)
        add_realistic_analyses(rag)
        demonstrate_search_capabilities(rag)
        demonstrate_server_status(rag)
        demonstrate_chat_context(rag)
        
        print("\n" + "=" * 60)
        print("🎉 DÉMONSTRATION RAG TERMINÉE AVEC SUCCÈS !")
        print(f"📁 Base vectorielle: {rag.vector_db_path}")
        print(f"🗃️ Base contraintes: {rag.constraints_db_path}")
        print("\n💡 Le système RAG est maintenant prêt à utiliser dans l'onglet Chat !")
        print("🚀 Lancez l'application et testez l'onglet '💬 Chat'")
        
    except Exception as e:
        print(f"💥 Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()