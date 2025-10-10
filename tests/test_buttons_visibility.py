#!/usr/bin/env python3
"""
Test rapide pour vérifier la présence des boutons RAG Reset
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_buttons_presence():
    """Tester si les boutons sont bien créés"""
    print("🔍 TEST PRÉSENCE BOUTONS RAG RESET")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        print("1. 🚀 Création de l'application...")
        app = cy8_prompts_manager()

        print("2. 🔍 Vérification des méthodes...")

        # Vérifier que les méthodes existent
        required_methods = [
            'reset_rag_completely',
            'clean_custom_environments',
            'test_rag_efficiency'
        ]

        for method in required_methods:
            if hasattr(app, method):
                print(f"   ✅ {method} trouvée")
            else:
                print(f"   ❌ {method} MANQUANTE")
                return False

        print("3. 🎛️ Analyse de l'interface Chat...")

        # Vérifier que l'onglet Chat existe
        if hasattr(app, 'notebook'):
            tab_count = app.notebook.index("end")
            print(f"   📊 Nombre d'onglets: {tab_count}")

            # Lister les onglets
            for i in range(tab_count):
                tab_text = app.notebook.tab(i, "text")
                print(f"   📋 Onglet {i}: {tab_text}")

                if "Chat" in tab_text:
                    print(f"   ✅ Onglet Chat trouvé à l'index {i}")

        print("4. 🔍 Recherche du frame quick_buttons_frame...")

        # Fonction récursive pour chercher les widgets
        def find_widgets_recursive(parent, target_text="🗑️ RAG Reset", level=0):
            indent = "  " * level
            found_buttons = []

            try:
                for child in parent.winfo_children():
                    widget_class = child.__class__.__name__

                    # Si c'est un Button, vérifier son texte
                    if widget_class == "Button" and hasattr(child, 'cget'):
                        try:
                            button_text = child.cget('text')
                            if target_text in button_text:
                                found_buttons.append((button_text, child))
                                print(f"{indent}🎯 TROUVÉ: {button_text}")
                        except:
                            pass

                    # Récursion dans les enfants
                    found_buttons.extend(find_widgets_recursive(child, target_text, level + 1))

            except:
                pass

            return found_buttons

        # Chercher les boutons RAG Reset
        reset_buttons = find_widgets_recursive(app.root, "🗑️ RAG Reset")
        clean_buttons = find_widgets_recursive(app.root, "🧹 Nettoyer Custom")
        test_buttons = find_widgets_recursive(app.root, "🔬 Test Efficacité")

        print(f"\n📊 Résultats de recherche:")
        print(f"   🗑️ Boutons 'RAG Reset': {len(reset_buttons)}")
        print(f"   🧹 Boutons 'Nettoyer Custom': {len(clean_buttons)}")
        print(f"   🔬 Boutons 'Test Efficacité': {len(test_buttons)}")

        if len(reset_buttons) > 0:
            print("   ✅ Les boutons de maintenance EXISTENT dans l'interface !")

            # Vérifier s'ils sont visibles
            for text, button in reset_buttons:
                try:
                    is_visible = button.winfo_viewable()
                    is_mapped = button.winfo_ismapped()
                    print(f"   📍 {text}: Visible={is_visible}, Mapped={is_mapped}")

                    # Obtenir la position
                    x = button.winfo_x()
                    y = button.winfo_y()
                    width = button.winfo_width()
                    height = button.winfo_height()
                    print(f"   📐 Position: x={x}, y={y}, w={width}, h={height}")

                except Exception as e:
                    print(f"   ⚠️ Erreur info bouton: {e}")
        else:
            print("   ❌ AUCUN bouton de maintenance trouvé !")

            # Chercher tous les boutons pour debug
            all_buttons = find_widgets_recursive(app.root, "")
            button_texts = []
            for text, _ in all_buttons:
                if text and "🔥" in text or "🗑️" in text or "📊" in text:
                    button_texts.append(text)

            print(f"   🔍 Boutons trouvés avec emojis: {button_texts}")

        return len(reset_buttons) > 0

    except Exception as e:
        print(f"❌ Erreur test boutons: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC BOUTONS RAG RESET")
    print("=" * 60)

    success = test_buttons_presence()

    if success:
        print("\n✅ BOUTONS TROUVÉS - Problème de visibilité dans l'interface")
        print("\n💡 SOLUTIONS POSSIBLES:")
        print("1. 📏 Agrandir la fenêtre verticalement")
        print("2. 🔄 Redémarrer l'application")
        print("3. 📱 Vérifier la résolution d'écran")
        print("4. ⬇️ Scroller dans l'onglet Chat si possible")
    else:
        print("\n❌ BOUTONS NON TROUVÉS - Problème de code")
        print("\n🔧 ACTIONS NÉCESSAIRES:")
        print("1. Vérifier le code des boutons")
        print("2. Relancer l'application")
        print("3. Vérifier les imports")
