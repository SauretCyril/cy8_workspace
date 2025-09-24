#!/usr/bin/env python3
"""
Script de validation CI locale pour cy8_workspace
Exécute tous les tests et vérifications avant un commit/push
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def detect_virtual_env():
    """Détecter et retourner le chemin de l'environnement virtuel s'il existe"""
    project_root = Path(__file__).parent.absolute()

    # Vérifier si on est déjà dans un venv
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print(f"[VENV] Environnement virtuel actif: {sys.executable}")
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
            print(f"[FOUND] Environnement virtuel trouvé: {venv_python}")
            return str(venv_python)

    print("[WARN] Aucun environnement virtuel trouvé, utilisation du Python système")
    return sys.executable


def get_python_cmd():
    """Retourner la commande Python à utiliser (avec venv si disponible)"""
    return detect_virtual_env()


def run_command(cmd, description, cwd=None):
    """Exécuter une commande et retourner le résultat"""
    print(f"🔍 {description}...")
    try:
        # Si cmd est une liste, ne pas utiliser shell=True
        if isinstance(cmd, list):
            shell_mode = False
        else:
            shell_mode = True

        result = subprocess.run(
            cmd,
            shell=shell_mode,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode == 0:
            print(f"[OK] {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            print(f"[FAIL] {description}")
            if result.stdout.strip():
                print(f"   STDOUT: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"   STDERR: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description}")
        return False
    except Exception as e:
        print(f"[ERROR] {description}: {e}")
        return False


def check_python_version():
    """Vérifier la version de Python"""
    version = sys.version_info
    print(f"[PYTHON] {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("[ERROR] Python 3.9+ requis")
        return False

    print("[OK] Version Python compatible")
    return True


def check_requirements():
    """Vérifier que les dépendances sont installées"""
    print("[DEPS] Vérification des dépendances...")

    required_packages = [
        ("tkinter", "tkinter"),  # (package_name, import_name)
        ("sqlite3", "sqlite3"),
        ("requests", "requests"),
        ("websocket-client", "websocket"),  # Package websocket-client s'importe comme websocket
    ]

    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"[ERROR] Packages manquants: {', '.join(missing)}")
        print("[INFO] Exécutez: pip install -r requirements.txt")
        return False

    print("[OK] Toutes les dépendances sont installées")
    return True


def run_cy8_tests():
    """Exécuter la suite de tests cy8"""
    print("🧪 Exécution des tests cy8...")

    # Changer vers le répertoire du projet
    project_root = Path(__file__).parent.absolute()
    python_cmd = get_python_cmd()

    cmd = f'"{python_cmd}" "{project_root}/src/cy8_test_suite.py"'
    return run_command(cmd, "Tests cy8", cwd=project_root)


def run_pytest_tests():
    """Exécuter les tests pytest si disponibles"""
    project_root = Path(__file__).parent.absolute()
    tests_dir = project_root / "tests"

    if not tests_dir.exists() or not any(tests_dir.glob("test_*.py")):
        print("ℹ️  Aucun test pytest trouvé, ignoré")
        return True

    python_cmd = get_python_cmd()
    cmd = f'"{python_cmd}" -m pytest tests/ -v'
    return run_command(cmd, "Tests pytest", cwd=project_root)


def check_code_style():
    """Vérifier le style de code avec flake8 (si disponible)"""
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
            print("ℹ️  Aucun fichier cy8 trouvé")
            return True

        files_to_check = cy8_files + ["tests/"]

        # Configuration flake8 basique - ignorer les erreurs mineures pour une validation rapide
        cmd_parts = [python_cmd, "-m", "flake8"] + files_to_check + [
            "--max-line-length=127",
            "--ignore=E203,W503,E722,F401,F811,F541,E501,E226,E402"
        ]

        return run_command(cmd_parts, "Vérification style (flake8)", cwd=project_root)

    except ImportError:
        print("ℹ️  flake8 non installé, vérification de style ignorée")
        return True


def check_imports():
    """Vérifier que tous les imports cy8 fonctionnent"""
    print("📥 Vérification des imports...")

    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root / "src"))

    modules = [
        "cy8_database_manager",
        "cy8_popup_manager",
        "cy8_editable_tables",
        "cy8_prompts_manager_main",
    ]

    failed_imports = []
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"❌ Imports échoués: {', '.join(failed_imports)}")
        return False

    print("✅ Tous les imports réussissent")
    return True


def main():
    """Fonction principale de validation"""
    # Forcer l'encodage UTF-8 pour Windows
    if os.name == "nt":  # Windows
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

    print("🚀 Validation CI locale - cy8_workspace")
    print("=" * 50)

    checks = [
        ("Version Python", check_python_version),
        ("Dépendances", check_requirements),
        ("Imports", check_imports),
        ("Tests cy8", run_cy8_tests),
        ("Tests pytest", run_pytest_tests),
        ("Style de code", check_code_style),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}")
        print("-" * 30)
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DE LA VALIDATION")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 TOUTES LES VALIDATIONS ONT RÉUSSI !")
        print("💚 Prêt pour commit/push")
        return 0
    else:
        print("💥 CERTAINES VALIDATIONS ONT ÉCHOUÉ")
        print("🔧 Corrigez les erreurs avant de commiter/pusher")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
