#!/usr/bin/env python3
"""
Script utilitaire pour vérifier et utiliser l'environnement virtuel
"""

import os
import sys
import subprocess

def check_virtual_env():
    """Vérifie si l'environnement virtuel est activé"""
    venv_path = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
    current_executable = sys.executable.replace('\\', '/')
    venv_path = venv_path.replace('\\', '/')

    print(f"🐍 Python actuel: {current_executable}")
    print(f"🎯 Python venv attendu: {venv_path}")

    is_venv = venv_path.lower() in current_executable.lower()

    if is_venv:
        print("✅ Environnement virtuel ACTIVÉ")
        print(f"📊 Version: {sys.version}")
        return True
    else:
        print("❌ Environnement virtuel NON ACTIVÉ")
        print("🔧 Pour l'activer:")
        print("   PowerShell: .\\venv\\Scripts\\Activate.ps1")
        print("   CMD: .\\venv\\Scripts\\activate.bat")
        return False

def run_in_venv(command):
    """Exécute une commande dans l'environnement virtuel"""
    venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')

    if not os.path.exists(venv_python):
        print(f"❌ Environnement virtuel introuvable: {venv_python}")
        return False

    print(f"🚀 Exécution dans venv: {command}")

    try:
        # Remplacer 'python' par le chemin complet du venv
        if command.startswith('python '):
            command = command.replace('python ', f'"{venv_python}" ', 1)

        result = subprocess.run(command, shell=True, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur d'exécution: {e}")
        return False

def main():
    print("🔍 Vérification de l'environnement virtuel cy8_workspace")
    print("=" * 60)

    # Vérifier l'environnement
    is_venv_active = check_virtual_env()

    print("\n📋 Informations sur l'environnement:")
    print(f"   Répertoire: {os.getcwd()}")
    print(f"   Système: {sys.platform}")

    # Lister les packages installés si venv actif
    if is_venv_active:
        print("\n📦 Packages principaux installés:")
        try:
            import tkinter
            print("   ✅ tkinter (GUI)")
        except ImportError:
            print("   ❌ tkinter")

        try:
            import sqlite3
            print("   ✅ sqlite3 (Base de données)")
        except ImportError:
            print("   ❌ sqlite3")

        try:
            import websocket
            print("   ✅ websocket-client (ComfyUI)")
        except ImportError:
            print("   ❌ websocket-client")

        try:
            import requests
            print("   ✅ requests (HTTP)")
        except ImportError:
            print("   ❌ requests")

    print(f"\n🎯 Recommandations:")
    if is_venv_active:
        print("   ✅ Vous pouvez exécuter l'application:")
        print("      python main.py")
        print("      python src/cy8_prompts_manager_main.py")
        print("      python src/cy8_test_suite.py")
    else:
        print("   🔧 Activez d'abord l'environnement virtuel:")
        print("      .\\venv\\Scripts\\Activate.ps1")
        print("   📝 Ou utilisez les scripts fournis:")
        print("      .\\start.bat")
        print("      .\\activate.bat")

if __name__ == "__main__":
    main()
