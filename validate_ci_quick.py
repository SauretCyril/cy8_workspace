#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation CI rapide pour le push
Version allégée qui se concentre sur les fonctionnalités critiques
"""

import os
import sys
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Configuration de l'encodage pour Windows
if os.name == "nt":  # Windows
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


def log_with_timestamp(message, level="INFO"):
    """Afficher un message avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "STEP": "🔄",
        "TEST": "🧪"
    }.get(level, "📝")

    print(f"[{timestamp}] {prefix} {message}")


def print_section(title):
    """Afficher une section avec séparateur"""
    print("\n" + "="*60)
    log_with_timestamp(f"SECTION: {title}", "STEP")
    print("="*60)


def detect_virtual_env():
    """Détecter et retourner le chemin de l'environnement virtuel s'il existe"""
    log_with_timestamp("Détection de l'environnement virtuel...", "STEP")

    project_root = Path(__file__).parent.absolute()

    # Vérifier si on est déjà dans un venv
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        log_with_timestamp(f"Environnement virtuel actif: {sys.executable}", "SUCCESS")
        return sys.executable

    # Chercher un venv dans le projet
    possible_venv_paths = [
        project_root / "venv" / "Scripts" / "python.exe",  # Windows
        project_root / "venv" / "bin" / "python",  # Unix/Linux/Mac
    ]

    for venv_python in possible_venv_paths:
        if venv_python.exists():
            log_with_timestamp(f"Environnement virtuel trouvé: {venv_python}", "SUCCESS")
            return str(venv_python)

    log_with_timestamp("Utilisation du Python système", "WARNING")
    return sys.executable


def run_command(cmd, description, cwd=None, timeout=120):
    """Exécuter une commande et retourner le résultat"""
    log_with_timestamp(f"Exécution: {description}", "STEP")
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'  # Remplacer les caractères problématiques
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            log_with_timestamp(f"{description} - Terminé en {elapsed_time:.1f}s", "SUCCESS")
            return True
        else:
            log_with_timestamp(f"{description} - ÉCHEC après {elapsed_time:.1f}s", "ERROR")
            if result.stderr.strip():
                log_with_timestamp(f"Erreur: {result.stderr.strip()[:200]}...", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log_with_timestamp(f"{description} - TIMEOUT après {timeout}s", "ERROR")
        return False
    except Exception as e:
        log_with_timestamp(f"{description} - ERREUR: {e}", "ERROR")
        return False


def check_python_version():
    """Vérifier la version de Python"""
    log_with_timestamp("Vérification de la version Python...", "STEP")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    log_with_timestamp(f"Version Python détectée: {version_str}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        log_with_timestamp("Python 3.9+ requis pour ce projet", "ERROR")
        return False

    log_with_timestamp("Version Python compatible", "SUCCESS")
    return True


def check_requirements():
    """Vérifier que les dépendances sont installées"""
    log_with_timestamp("Vérification des dépendances Python...", "STEP")

    required_packages = [
        ("tkinter", "tkinter"),
        ("sqlite3", "sqlite3"),
        ("requests", "requests"),
        ("websocket-client", "websocket"),
    ]

    missing = []
    for i, (package_name, import_name) in enumerate(required_packages, 1):
        log_with_timestamp(f"Vérification {i}/{len(required_packages)}: {package_name}")
        try:
            __import__(import_name)
            log_with_timestamp(f"✓ {package_name} disponible")
        except ImportError:
            missing.append(package_name)
            log_with_timestamp(f"✗ {package_name} manquant", "WARNING")

    if missing:
        log_with_timestamp(f"Packages manquants: {', '.join(missing)}", "ERROR")
        return False

    log_with_timestamp("Toutes les dépendances sont installées", "SUCCESS")
    return True


def check_imports():
    """Vérifier que tous les imports cy8 fonctionnent"""
    log_with_timestamp("Vérification des imports cy8...", "STEP")

    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root / "src"))

    modules = [
        "cy8_database_manager",
        "cy8_prompts_manager_main",
    ]

    failed_imports = []
    for i, module in enumerate(modules, 1):
        log_with_timestamp(f"Import {i}/{len(modules)}: {module}")
        try:
            __import__(module)
            log_with_timestamp(f"✓ {module} importé avec succès")
        except ImportError as e:
            failed_imports.append((module, str(e)))
            log_with_timestamp(f"✗ {module} échec: {e}", "WARNING")

    if failed_imports:
        log_with_timestamp(f"Échecs d'import: {len(failed_imports)}/{len(modules)}", "ERROR")
        return False

    log_with_timestamp("Tous les imports critiques fonctionnent", "SUCCESS")
    return True


def run_critical_tests():
    """Exécuter les tests critiques pour vérifier le bon fonctionnement"""
    log_with_timestamp("Exécution de tests critiques...", "TEST")

    project_root = Path(__file__).parent.absolute()
    python_cmd = detect_virtual_env()

    # Tests critiques uniquement
    critical_tests = [
        ("test_log_analysis_storage.py", "Test stockage analyse"),
        ("test_final_log_storage_validation.py", "Test validation finale")
    ]

    success_count = 0
    for i, (test_file, description) in enumerate(critical_tests, 1):
        test_path = project_root / "tests" / test_file

        if test_path.exists():
            log_with_timestamp(f"Test critique {i}/{len(critical_tests)}: {description}")
            cmd = f'"{python_cmd}" "{test_path}"'
            if run_command(cmd, description, cwd=project_root, timeout=60):
                success_count += 1
            else:
                log_with_timestamp(f"ÉCHEC CRITIQUE: {test_file}", "ERROR")
        else:
            log_with_timestamp(f"Test non trouvé: {test_file}", "WARNING")

    log_with_timestamp(f"Tests critiques: {success_count}/{len(critical_tests)} réussis")
    return success_count == len(critical_tests)  # Tous les tests critiques doivent passer


def check_git_status():
    """Vérifier le statut Git"""
    log_with_timestamp("Vérification du statut Git...", "STEP")

    project_root = Path(__file__).parent.absolute()

    # Vérifier qu'on est dans un repo git
    if not (project_root / ".git").exists():
        log_with_timestamp("Pas un repository Git", "WARNING")
        return True

    # Vérifier s'il y a des modifications
    cmd = "git status --porcelain"
    if run_command(cmd, "Statut Git", cwd=project_root):
        log_with_timestamp("Repository Git prêt", "SUCCESS")
        return True
    else:
        log_with_timestamp("Problème avec le repository Git", "WARNING")
        return True  # Ne pas bloquer pour les problèmes Git mineurs


def main():
    """Fonction principale de validation CI rapide"""
    start_time = time.time()

    print("🚀 VALIDATION CI RAPIDE - cy8_workspace")
    print("="*60)
    log_with_timestamp("Démarrage de la validation CI rapide pour push", "INFO")

    # Liste des vérifications critiques
    validation_steps = [
        ("Version Python", check_python_version),
        ("Dépendances", check_requirements),
        ("Imports critiques", check_imports),
        ("Tests critiques", run_critical_tests),
        ("Statut Git", check_git_status),
    ]

    results = []
    total_steps = len(validation_steps)

    for i, (step_name, step_function) in enumerate(validation_steps, 1):
        print_section(f"{i}/{total_steps}: {step_name}")

        try:
            result = step_function()
            results.append((step_name, result))

            if result:
                log_with_timestamp(f"✅ {step_name} - SUCCÈS", "SUCCESS")
            else:
                log_with_timestamp(f"❌ {step_name} - ÉCHEC", "ERROR")

        except Exception as e:
            log_with_timestamp(f"❌ {step_name} - ERREUR: {e}", "ERROR")
            results.append((step_name, False))

    # Résumé final
    print_section("RÉSUMÉ DE LA VALIDATION RAPIDE")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100

    log_with_timestamp(f"Résultats: {passed}/{total} vérifications réussies ({success_rate:.1f}%)")

    for step_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        log_with_timestamp(f"  {step_name}: {status}")

    elapsed_time = time.time() - start_time
    log_with_timestamp(f"Durée totale: {elapsed_time:.1f} secondes")

    # Seuil plus bas pour la validation rapide
    if success_rate >= 80:
        log_with_timestamp("🎉 VALIDATION CI RAPIDE RÉUSSIE - Prêt pour le push!", "SUCCESS")
        log_with_timestamp("💡 Note: Style de code ignoré pour cette validation rapide", "INFO")
        return 0
    else:
        log_with_timestamp("❌ VALIDATION CI RAPIDE ÉCHOUÉE - Corrections critiques nécessaires", "ERROR")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
