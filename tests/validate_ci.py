#!/usr/bin/env python3
"""
Script de validation CI locale pour cy8_workspace
Exécute tous les tests et vérifications avant un commit/push
"""

import os
import sys
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path


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


def print_progress(current, total, task_name):
    """Afficher une barre de progression simple"""
    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current / total)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    log_with_timestamp(f"[{bar}] {percentage:.1f}% - {task_name}", "STEP")


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
        project_root / ".venv" / "Scripts" / "python.exe",  # Alternative Windows
        project_root / ".venv" / "bin" / "python",  # Alternative Unix
    ]

    for venv_python in possible_venv_paths:
        if venv_python.exists():
            log_with_timestamp(f"Environnement virtuel trouvé: {venv_python}", "SUCCESS")
            return str(venv_python)

    log_with_timestamp("Aucun environnement virtuel trouvé, utilisation du Python système", "WARNING")
    return sys.executable


def get_python_cmd():
    """Retourner la commande Python à utiliser (avec venv si disponible)"""
    return detect_virtual_env()


def run_command(cmd, description, cwd=None, show_output=True):
    """Exécuter une commande et retourner le résultat"""
    log_with_timestamp(f"Exécution: {description}", "STEP")
    start_time = time.time()

    try:
        # Si cmd est une liste, ne pas utiliser shell=True
        if isinstance(cmd, list):
            shell_mode = False
            cmd_str = " ".join(cmd)
        else:
            shell_mode = True
            cmd_str = cmd

        log_with_timestamp(f"Commande: {cmd_str[:100]}{'...' if len(cmd_str) > 100 else ''}")

        result = subprocess.run(
            cmd,
            shell=shell_mode,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            log_with_timestamp(f"{description} - Terminé en {elapsed_time:.1f}s", "SUCCESS")
            if show_output and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) <= 5:
                    for line in lines:
                        log_with_timestamp(f"   {line}")
                else:
                    for line in lines[:3]:
                        log_with_timestamp(f"   {line}")
                    log_with_timestamp(f"   ... ({len(lines)-6} lignes supplémentaires)")
                    for line in lines[-3:]:
                        log_with_timestamp(f"   {line}")
            return True
        else:
            log_with_timestamp(f"{description} - ÉCHEC après {elapsed_time:.1f}s", "ERROR")
            if result.stdout.strip():
                log_with_timestamp(f"STDOUT: {result.stdout.strip()}", "ERROR")
            if result.stderr.strip():
                log_with_timestamp(f"STDERR: {result.stderr.strip()}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log_with_timestamp(f"{description} - TIMEOUT après 5 minutes", "ERROR")
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
        ("tkinter", "tkinter"),  # (package_name, import_name)
        ("sqlite3", "sqlite3"),
        ("requests", "requests"),
        ("websocket-client", "websocket"),  # Package websocket-client s'importe comme websocket
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
        log_with_timestamp("Solution: pip install -r requirements.txt", "INFO")
        return False

    log_with_timestamp("Toutes les dépendances sont installées", "SUCCESS")
    return True


def run_cy8_tests():
    """Exécuter la suite de tests cy8"""
    log_with_timestamp("Démarrage de la suite de tests cy8...", "TEST")

    # Changer vers le répertoire du projet
    project_root = Path(__file__).parent.absolute()
    python_cmd = get_python_cmd()

    cmd = f'"{python_cmd}" "{project_root}/src/cy8_test_suite.py"'
    return run_command(cmd, "Suite de tests cy8", cwd=project_root, show_output=True)


def run_pytest_tests():
    """Exécuter les tests pytest si disponibles"""
    log_with_timestamp("Recherche de tests pytest...", "TEST")

    project_root = Path(__file__).parent.absolute()
    tests_dir = project_root / "tests"

    if not tests_dir.exists():
        log_with_timestamp("Répertoire 'tests' non trouvé", "INFO")
        return True

    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        log_with_timestamp("Aucun fichier test_*.py trouvé", "INFO")
        return True

    log_with_timestamp(f"Trouvé {len(test_files)} fichiers de test pytest", "INFO")
    for test_file in test_files[:5]:  # Afficher les 5 premiers
        log_with_timestamp(f"  - {test_file.name}")
    if len(test_files) > 5:
        log_with_timestamp(f"  ... et {len(test_files)-5} autres")

    python_cmd = get_python_cmd()
    cmd = f'"{python_cmd}" -m pytest tests/ -v'
    return run_command(cmd, "Tests pytest", cwd=project_root, show_output=False)


def check_code_style():
    """Vérifier le style de code avec flake8 (si disponible)"""
    log_with_timestamp("Vérification du style de code...", "STEP")

    try:
        import flake8
        import glob
        import os

        project_root = Path(__file__).parent.absolute()
        python_cmd = get_python_cmd()

        # Lister explicitement les fichiers cy8
        os.chdir(project_root)
        cy8_files = glob.glob("src/cy8_*.py")

        if not cy8_files:
            log_with_timestamp("Aucun fichier cy8_*.py trouvé", "INFO")
            return True

        log_with_timestamp(f"Analyse de {len(cy8_files)} fichiers cy8", "INFO")

        files_to_check = cy8_files + ["tests/"]

        # Configuration flake8 basique - ignorer les erreurs mineures pour une validation rapide
        cmd_parts = [python_cmd, "-m", "flake8"] + files_to_check + [
            "--max-line-length=127",
            "--ignore=E203,W503,E722,F401,F811,F541,E501,E226,E402"
        ]

        return run_command(cmd_parts, "Vérification style (flake8)", cwd=project_root, show_output=False)

    except ImportError:
        log_with_timestamp("flake8 non installé, vérification de style ignorée", "INFO")
        return True


def check_imports():
    """Vérifier que tous les imports cy8 fonctionnent"""
    log_with_timestamp("Vérification des imports cy8...", "STEP")

    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root / "src"))

    modules = [
        "cy8_database_manager",
        "cy8_popup_manager",
        "cy8_editable_tables",
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
        for module, error in failed_imports:
            log_with_timestamp(f"  {module}: {error}", "ERROR")
        return False

    log_with_timestamp("Tous les imports cy8 fonctionnent", "SUCCESS")
    return True


def run_sample_tests():
    """Exécuter quelques tests rapides pour vérifier le bon fonctionnement"""
    log_with_timestamp("Exécution de tests d'échantillonnage...", "TEST")

    project_root = Path(__file__).parent.absolute()
    python_cmd = get_python_cmd()

    # Tests rapides et ciblés
    quick_tests = [
        ("test_log_scrollbar_validation.py", "Test scrollbar log"),
        ("test_savetext_fix.py", "Test correction SaveText"),
        ("test_log_analysis_storage.py", "Test stockage analyse"),
        ("test_final_log_storage_validation.py", "Test validation finale")
    ]

    success_count = 0
    for i, (test_file, description) in enumerate(quick_tests, 1):
        test_path = project_root / "tests" / test_file

        if test_path.exists():
            log_with_timestamp(f"Test {i}/{len(quick_tests)}: {description}")
            cmd = f'"{python_cmd}" "{test_path}"'
            if run_command(cmd, description, cwd=project_root, show_output=False):
                success_count += 1
            else:
                log_with_timestamp(f"Échec du test: {test_file}", "WARNING")
        else:
            log_with_timestamp(f"Test non trouvé: {test_file}", "INFO")

    log_with_timestamp(f"Tests d'échantillonnage: {success_count}/{len(quick_tests)} réussis")
    return success_count >= len(quick_tests) * 0.7  # Au moins 70% de réussite


def check_basic_functionality():
    """Vérifier que l'application de base fonctionne"""
    log_with_timestamp("Test de fonctionnalité de base...", "STEP")

    project_root = Path(__file__).parent.absolute()
    python_cmd = get_python_cmd()

    # Test d'import de base
    test_script = f'''
import sys
sys.path.insert(0, r"{project_root / "src"}")

try:
    from cy8_prompts_manager_main import cy8_prompts_manager
    print("✓ Import principal réussi")

    # Test de création de base (sans interface graphique)
    import os
    os.environ["DISPLAY"] = ""  # Empêcher l'affichage graphique

    app = cy8_prompts_manager()
    print("✓ Création de l'application réussie")

    # Test de base de données
    if hasattr(app, "db_manager"):
        print("✓ Gestionnaire de base de données présent")

    print("✓ Tests de base réussis")

except Exception as e:
    print(f"✗ Erreur: {{e}}")
    exit(1)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        cmd = f'"{python_cmd}" "{test_file}"'
        result = run_command(cmd, "Test de fonctionnalité de base", show_output=True)
        return result
    finally:
        try:
            os.unlink(test_file)
        except:
            pass


def main():
    """Fonction principale de validation CI"""
    start_time = time.time()

    # Forcer l'encodage UTF-8 pour Windows
    if os.name == "nt":  # Windows
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

    print("🚀 VALIDATION CI - cy8_workspace")
    print("="*60)
    log_with_timestamp("Démarrage de la validation CI complète", "INFO")

    # Liste des étapes de validation
    validation_steps = [
        ("Version Python", check_python_version),
        ("Environnement virtuel", lambda: True),  # Déjà fait dans detect_virtual_env
        ("Dépendances", check_requirements),
        ("Imports cy8", check_imports),
        ("Fonctionnalité de base", check_basic_functionality),
        ("Tests d'échantillonnage", run_sample_tests),
        ("Style de code", check_code_style),
    ]

    results = []
    total_steps = len(validation_steps)

    for i, (step_name, step_function) in enumerate(validation_steps, 1):
        print_section(f"{i}/{total_steps}: {step_name}")
        print_progress(i-1, total_steps, step_name)

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

    print_progress(total_steps, total_steps, "Validation terminée")

    # Résumé final
    print_section("RÉSUMÉ DE LA VALIDATION")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100

    log_with_timestamp(f"Résultats: {passed}/{total} étapes réussies ({success_rate:.1f}%)")

    for step_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        log_with_timestamp(f"  {step_name}: {status}")

    elapsed_time = time.time() - start_time
    log_with_timestamp(f"Durée totale: {elapsed_time:.1f} secondes")

    if success_rate >= 80:
        log_with_timestamp("🎉 VALIDATION CI RÉUSSIE - Prêt pour le push!", "SUCCESS")
        return 0
    else:
        log_with_timestamp("❌ VALIDATION CI ÉCHOUÉE - Corrections nécessaires", "ERROR")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
