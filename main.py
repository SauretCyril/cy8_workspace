#!/usr/bin/env python3
"""
Point d'entrée principal pour cy8_prompts_manager
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from cy8_prompts_manager_main import main
    if __name__ == "__main__":
        print("🚀 Lancement de cy8_prompts_manager...")
        main()
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous que tous les fichiers sont présents dans src/")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur lors du lancement: {e}")
    sys.exit(1)