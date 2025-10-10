#!/usr/bin/env python3
"""
Test de diagnostic du terminal - Vérification de l'exécution des commandes
"""

import subprocess
import sys
import os
import time

def test_echo_command():
    """Test direct de la commande echo"""
    print("🧪 Test de diagnostic du terminal")
    print("=" * 50)

    print("1. Test direct avec subprocess...")
    try:
        # Test 1: Subprocess simple
        result = subprocess.run(
            ["echo", "test"],
            capture_output=True,
            text=True,
            shell=True
        )
        print(f"   Sortie: '{result.stdout}'")
        print(f"   Erreur: '{result.stderr}'")
        print(f"   Code: {result.returncode}")

    except Exception as e:
        print(f"   ❌ Erreur: {e}")

    print("\n2. Test avec Popen (comme dans l'app)...")
    try:
        # Test 2: Popen comme dans l'application
        process = subprocess.Popen(
            "echo test",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )

        stdout, stderr = process.communicate()
        print(f"   Sortie: '{stdout}'")
        print(f"   Erreur: '{stderr}'")
        print(f"   Code: {process.returncode}")

    except Exception as e:
        print(f"   ❌ Erreur: {e}")

    print("\n3. Test avec lecture ligne par ligne...")
    try:
        # Test 3: Lecture ligne par ligne
        process = subprocess.Popen(
            "echo test ligne par ligne",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )

        print("   Lecture stdout:")
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"   -> '{line.strip()}'")
            else:
                break

        process.wait()
        print(f"   Code final: {process.returncode}")

    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_command_variations():
    """Test différentes variations de commandes"""
    print("\n4. Test de variations de commandes...")

    commands = [
        "echo Hello",
        "echo Hello World",
        "dir /b | findstr test",  # Windows
        "python --version",
        "ping 127.0.0.1 -n 1"    # Test avec sortie multiple
    ]

    for cmd in commands:
        print(f"\n   Test: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"   ✅ Sortie: '{result.stdout.strip()}'")
            if result.stderr:
                print(f"   ⚠️  Erreur: '{result.stderr.strip()}'")

        except subprocess.TimeoutExpired:
            print("   ⏱️ Timeout")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    test_echo_command()
    test_command_variations()

    print("\n" + "=" * 50)
    print("🎯 Diagnostic terminé")
    print("Si les tests ci-dessus fonctionnent, le problème")
    print("est dans la gestion des threads de l'application.")
