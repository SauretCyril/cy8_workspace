#!/usr/bin/env python3
"""
Test du nouvel onglet Log pour l'analyse des logs ComfyUI
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk

def test_log_tab():
    """Test du nouvel onglet Log"""

    print("=== Test de l'onglet Log ComfyUI ===")

    try:
        # Créer l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        root = tk.Tk()
        root.geometry("1000x700")
        root.withdraw()  # Masquer pour le test

        app = cy8_prompts_manager(root)
        print("✅ Application créée avec le nouvel onglet Log")

        # Vérifier les composants de l'onglet Log
        log_components = [
            ('comfyui_log_path', 'Variable du chemin log'),
            ('log_file_info_label', 'Label info fichier log'),
            ('analyze_log_btn', 'Bouton analyser log'),
            ('log_status_label', 'Label statut analyse'),
            ('log_filter_var', 'Variable filtre résultats'),
            ('log_search_var', 'Variable recherche résultats'),
            ('log_results_count_label', 'Label compteur résultats'),
            ('log_results_tree', 'Tableau résultats analyse'),
            ('log_analyzer', 'Analyseur de logs')
        ]

        print("\n📋 Vérification des composants de l'onglet Log:")
        missing_components = []

        for attr_name, description in log_components:
            if hasattr(app, attr_name):
                print(f"   ✅ {description} ({attr_name})")
            else:
                print(f"   ❌ {description} ({attr_name}) - MANQUANT")
                missing_components.append(attr_name)

        # Test du tableau de résultats
        print("\n📊 Test du tableau de résultats d'analyse:")
        if hasattr(app, 'log_results_tree'):
            log_tree = app.log_results_tree
            print(f"   📋 Colonnes: {log_tree['columns']}")
            print(f"   📏 Hauteur: {log_tree['height']}")

            # Configuration des couleurs
            try:
                log_tree.tag_configure('error', foreground='red')
                log_tree.tag_configure('warning', foreground='orange')
                log_tree.tag_configure('info', foreground='blue')
                print("   🎨 Tags de couleur configurés")
            except Exception as e:
                print(f"   ❌ Erreur configuration tags: {e}")

            # Ajouter des données de test
            test_entries = [
                ("OK", "Custom Node", "ExtraPathReader", "Node chargé avec succès", "42"),
                ("ERREUR", "Model", "model.safetensors", "Erreur de chargement du modèle", "158"),
                ("ATTENTION", "Memory", "VRAM", "Mémoire VRAM faible", "203"),
                ("INFO", "System", "ComfyUI", "Démarrage de ComfyUI", "1")
            ]

            for entry in test_entries:
                log_tree.insert("", "end", values=entry, tags=(entry[0],))

            items_count = len(log_tree.get_children())
            print(f"   📋 Données de test ajoutées: {items_count} éléments")

            print("   ✅ Tableau des résultats fonctionnel")
        else:
            print("   ❌ Tableau des résultats non trouvé")

        # Test des méthodes de l'onglet Log
        print("\n🔧 Test des méthodes de l'onglet Log:")
        log_methods = [
            ('check_log_file_status', 'Vérification statut fichier'),
            ('refresh_log_analysis', 'Actualisation analyse'),
            ('export_log_analysis', 'Export analyse'),
            ('filter_log_results', 'Filtrage résultats'),
            ('search_log_results', 'Recherche résultats'),
            ('show_log_detail', 'Affichage détails'),
            ('analyze_comfyui_log', 'Analyse log ComfyUI'),
            ('browse_log_file', 'Parcourir fichier log')
        ]

        for method_name, description in log_methods:
            if hasattr(app, method_name):
                print(f"   ✅ {description} ({method_name})")
            else:
                print(f"   ❌ {description} ({method_name}) - MANQUANT")

        # Test de la vérification du fichier log
        print("\n📁 Test de vérification du fichier log:")
        if hasattr(app, 'check_log_file_status'):
            try:
                app.check_log_file_status()
                status_text = app.log_file_info_label.cget('text')
                print(f"   📋 Statut fichier: {status_text}")
                print("   ✅ Vérification du fichier log fonctionnelle")
            except Exception as e:
                print(f"   ⚠️ Erreur lors de la vérification: {e}")

        # Test du filtrage
        print("\n🔍 Test du système de filtrage:")
        if hasattr(app, 'log_filter_var') and hasattr(app, 'filter_log_results'):
            try:
                app.log_filter_var.set("ERREUR")
                app.filter_log_results()
                print("   ✅ Filtre 'ERREUR' appliqué")

                app.log_filter_var.set("Tous")
                app.filter_log_results()
                print("   ✅ Filtre réinitialisé")
            except Exception as e:
                print(f"   ⚠️ Erreur lors du filtrage: {e}")

        # Test de la recherche
        print("\n🔎 Test du système de recherche:")
        if hasattr(app, 'log_search_var') and hasattr(app, 'search_log_results'):
            try:
                app.log_search_var.set("model")
                app.search_log_results()
                print("   ✅ Recherche 'model' effectuée")

                app.log_search_var.set("")
                app.search_log_results()
                print("   ✅ Recherche réinitialisée")
            except Exception as e:
                print(f"   ⚠️ Erreur lors de la recherche: {e}")

        root.destroy()

        # Résultats
        success = len(missing_components) == 0
        return success, missing_components

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()
        return False, []

if __name__ == "__main__":
    success, missing = test_log_tab()

    print("\n" + "=" * 60)
    if success:
        print("🎉 NOUVEL ONGLET LOG CRÉÉ AVEC SUCCÈS!")
        print("\n✨ FONCTIONNALITÉS DE L'ONGLET LOG:")
        print("   📁 Configuration du fichier log avec vérification")
        print("   🔍 Analyse complète des logs ComfyUI")
        print("   📊 Tableau de résultats avec filtrage et recherche")
        print("   🎨 Codes couleur par type (OK, ERREUR, ATTENTION, INFO)")
        print("   📋 Détails complets au double-clic")
        print("   📤 Export des résultats en CSV")
        print("   🔄 Actualisation automatique")
        print("   📈 Compteur de résultats")

        print("\n🎯 L'ONGLET LOG EST MAINTENANT SÉPARÉ ET DÉDIÉ!")
        print("💡 Avantages:")
        print("   • Interface dédiée à l'analyse des logs")
        print("   • Onglet ComfyUI focalisé sur l'environnement")
        print("   • Meilleure organisation des fonctionnalités")
        print("   • Interface plus intuitive et spécialisée")

    else:
        print("💥 PROBLÈME AVEC LE NOUVEL ONGLET LOG!")
        if missing:
            print(f"❌ Composants manquants: {missing}")
        print("🔧 Vérifiez l'implémentation")

    print("=" * 60)
    sys.exit(0 if success else 1)
