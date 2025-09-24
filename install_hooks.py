#!/usr/bin/env python3
"""
Script d'installation des hooks Git pour cy8_workspace
"""

import os
import stat
import shutil
from pathlib import Path


def install_hooks():
    """Installer les hooks Git"""
    project_root = Path(__file__).parent.absolute()
    hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        print("[FAIL] Repertoire .git/hooks non trouve")
        print("[INFO] Assurez-vous d'etre dans un depot Git")
        return False

    # Hook pre-push
    pre_push_content = """#!/bin/sh
# Pre-push hook pour cy8_workspace
# Execute les tests avant chaque push

echo "[INFO] Hook pre-push: Validation des tests avant push..."

# Changer vers le repertoire du projet
cd "$(git rev-parse --show-toplevel)"

# Executer le script de validation
python validate_ci.py

# Recuperer le code de sortie
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "[OK] Validation reussie - Push autorise"
    exit 0
else
    echo "[FAIL] Validation echouee - Push bloque"
    echo "[INFO] Corrigez les erreurs et recommencez"
    exit 1
fi"""

    pre_push_file = hooks_dir / "pre-push"

    try:
        # Écrire le hook
        with open(pre_push_file, "w", encoding="utf-8") as f:
            f.write(pre_push_content)

        # Rendre exécutable sur Unix/Linux/Mac
        if os.name != "nt":  # Non-Windows
            st = os.stat(pre_push_file)
            os.chmod(pre_push_file, st.st_mode | stat.S_IEXEC)

        print("[OK] Hook pre-push installe avec succes")
        return True

    except Exception as e:
        print(f"[FAIL] Erreur lors de l'installation du hook: {e}")
        return False


def main():
    """Fonction principale"""
    print("[INFO] Installation des hooks Git pour cy8_workspace")
    print("=" * 50)

    if install_hooks():
        print("\n[OK] Installation terminee !")
        print("[INFO] Hooks installes:")
        print("   • pre-push: Execute les tests avant chaque push")
        print("\n[TIP] Pour desactiver temporairement:")
        print("   git push --no-verify")
    else:
        print("\n[FAIL] Installation echouee")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
