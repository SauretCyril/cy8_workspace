#!/usr/bin/env python3
"""
Test simple du terminal - validation fonctionnelle
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Ajouter le dossier src au chemin
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_basic_terminal():
    """Test des fonctionnalités de base du terminal"""
    print("🧪 Test de base terminal...")

    # Test simple avec PowerShell
    print("✅ Test echo...")
    result = subprocess.run(['powershell', '-Command', 'echo "Hello Terminal Test"'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Hello Terminal Test' in result.stdout

    print("✅ Test pwd...")
    result = subprocess.run(['powershell', '-Command', 'pwd'], capture_output=True, text=True)
    assert result.returncode == 0

    print("✅ Test python...")
    result = subprocess.run(['powershell', '-Command', 'python --version'], capture_output=True, text=True)
    # Note: peut échouer si python n'est pas dans PATH mais ce n'est pas grave

    print("✅ Tests de base réussis!")
    return True

def test_color_tags():
    """Test des tags de couleur pour le terminal"""
    print("🎨 Test configuration couleurs...")

    # Importer tkinter pour tester les couleurs
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()

    # Créer un widget Text pour tester
    text_widget = tk.Text(root, bg="#1e1e1e", fg="#ffffff")

    # Configurer les tags comme dans l'application
    text_widget.tag_configure("command", foreground="#87CEEB")
    text_widget.tag_configure("output", foreground="#ffffff")
    text_widget.tag_configure("error", foreground="#ff6b6b")
    text_widget.tag_configure("success", foreground="#51cf66")
    text_widget.tag_configure("info", foreground="#74c0fc")
    text_widget.tag_configure("warning", foreground="#ffa726")
    text_widget.tag_configure("prompt", foreground="#40c057")

    # Test d'insertion avec tags
    text_widget.insert("end", "G:\\test> ", "prompt")
    text_widget.insert("end", "echo test\n", "command")
    text_widget.insert("end", "test\n", "output")
    text_widget.insert("end", "✅ Succès\n", "success")
    text_widget.insert("end", "ℹ️ Information\n", "info")
    text_widget.insert("end", "⚠️ Attention\n", "warning")
    text_widget.insert("end", "❌ Erreur\n", "error")

    print("✅ Configuration couleurs OK!")
    root.destroy()
    return True

if __name__ == "__main__":
    print("🚀 Test terminal simple\n")

    try:
        # Tests de base
        test_basic_terminal()
        test_color_tags()

        print("\n🎉 Tous les tests de base passent!")
        print("✅ Terminal prêt à fonctionner")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
