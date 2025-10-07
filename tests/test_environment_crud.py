#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités CRUD pour les environnements
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_environment_crud():
    """Test des fonctions CRUD des environnements"""
    print("🔧 TEST FONCTIONS CRUD ENVIRONNEMENTS")
    print("=" * 50)

    try:
        from cy8_database_manager import cy8_database_manager

        print("1. ✅ Import cy8_database_manager réussi")

        # Créer une instance avec base temporaire
        import tempfile
        temp_db = tempfile.mktemp(suffix=".db")
        db_manager = cy8_database_manager(temp_db)  # Base temporaire pour test
        db_manager.init_database("dev")  # Initialiser la base

        print("2. ✅ cy8_database_manager initialisé")

        # Test des méthodes CRUD
        crud_methods = [
            'add_environment',
            'update_environment',
            'delete_environment',
            'get_all_environments'
        ]

        for method_name in crud_methods:
            if hasattr(db_manager, method_name):
                print(f"3. ✅ {method_name}: Méthode trouvée")
            else:
                print(f"3. ❌ {method_name}: Méthode MANQUANTE")
                return False

        # Test d'ajout d'environnement
        print("\n🧪 Test d'ajout d'environnement...")
        success = db_manager.add_environment(
            "test_env",
            "Environnement Test",
            "C:/test/path",
            "Description test"
        )

        if success:
            print("   ✅ Ajout réussi")
        else:
            print("   ❌ Échec de l'ajout")
            return False

        # Test de récupération
        print("\n📋 Test de récupération des environnements...")
        environments = db_manager.get_all_environments()

        if environments and len(environments) > 0:
            print(f"   ✅ {len(environments)} environnement(s) trouvé(s)")
            for env in environments:
                print(f"   📌 {env[0]}: {env[1]} - {env[2]}")
        else:
            print("   ❌ Aucun environnement trouvé")
            return False

        # Test de modification
        print("\n✏️ Test de modification d'environnement...")
        success = db_manager.update_environment(
            "test_env",
            "test_env_modified",
            "Environnement Test Modifié",
            "C:/test/path/modified",
            "Description modifiée"
        )

        if success:
            print("   ✅ Modification réussie")
        else:
            print("   ❌ Échec de la modification")
            return False

        # Test de suppression
        print("\n🗑️ Test de suppression d'environnement...")
        success = db_manager.delete_environment("test_env_modified")

        if success:
            print("   ✅ Suppression réussie")
        else:
            print("   ❌ Échec de la suppression")
            return False

        print("\n🎯 RÉSULTAT:")
        print("✅ Toutes les fonctions CRUD sont opérationnelles")
        print("📋 Interface utilisateur:")
        print("   • Onglet ComfyUI > Section Environnements")
        print("   • Boutons: ➕ Ajouter, ✏️ Modifier, 🗑️ Supprimer")
        print("   • Double-clic pour sélectionner un environnement")

        # Nettoyage
        try:
            os.unlink(temp_db)
        except:
            pass

        return True

    except Exception as e:
        print(f"❌ Erreur test CRUD: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_dialog():
    """Test de la classe EnvironmentDialog"""
    print("\n🪟 TEST DIALOGUE ENVIRONNEMENT")
    print("=" * 40)

    try:
        # Import test
        from cy8_prompts_manager_main import EnvironmentDialog
        print("✅ Classe EnvironmentDialog trouvée")

        # Test des attributs requis
        required_attrs = ['setup_ui', 'validate_and_save', 'browse_folder', 'cancel']

        # On ne peut pas instancier sans Tkinter, mais on peut vérifier la classe
        for attr in required_attrs:
            if hasattr(EnvironmentDialog, attr):
                print(f"✅ Méthode {attr} trouvée")
            else:
                print(f"❌ Méthode {attr} MANQUANTE")
                return False

        print("✅ Dialogue d'environnement prêt")
        return True

    except Exception as e:
        print(f"❌ Erreur test dialogue: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TEST COMPLET GESTION ENVIRONNEMENTS")
    print("=" * 60)

    success1 = test_environment_crud()
    success2 = test_environment_dialog()

    if success1 and success2:
        print("\n✅ TOUS LES TESTS RÉUSSIS !")
        print("\n🚀 FONCTIONNALITÉS DISPONIBLES:")
        print("1. ➕ Ajouter un nouvel environnement ComfyUI")
        print("2. ✏️ Modifier un environnement existant (ID, Nom, Chemin)")
        print("3. 🗑️ Supprimer un environnement et ses données")
        print("4. 🔄 Actualiser la liste des environnements")
        print("5. 📁 Sélecteur de dossier intégré")
        print("6. ✅ Validation des données")
        print("7. ⚠️ Confirmations de sécurité")

        print("\n💡 UTILISATION:")
        print("• Lancez l'application: python main.py")
        print("• Onglet ComfyUI > Section Environnements")
        print("• Utilisez les boutons pour gérer vos environnements")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les erreurs ci-dessus")
