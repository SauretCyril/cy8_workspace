"""
Tests pour cy8_workspace

Ce package contient tous les tests du projet cy8_prompts_manager.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent (racine du projet) au path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
