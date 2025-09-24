"""
Tests pytest pour cy8_workspace
Complément à la suite de tests cy8 existante
"""

import pytest
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_imports():
    """Test que tous les modules s'importent correctement"""
    try:
        import cy8_database_manager
        import cy8_popup_manager
        import cy8_editable_tables
        import cy8_prompts_manager_main
    except ImportError as e:
        pytest.fail(f"Import échoué: {e}")


def test_database_manager_class():
    """Test que la classe DatabaseManager peut être instanciée"""
    from cy8_database_manager import cy8_database_manager

    # Test avec un chemin temporaire
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_manager = cy8_database_manager(tmp.name)
        assert db_manager is not None
        assert db_manager.status_options == ("new", "test", "ok", "nok")

        # Cleanup
        try:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
        except:
            pass


def test_cy8_test_suite_execution():
    """Test que la suite de tests cy8 peut s'exécuter"""
    import subprocess
    import tempfile

    result = subprocess.run(
        [sys.executable, str(project_root / "src" / "cy8_test_suite.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"cy8_test_suite a échoué: {result.stderr}"
    assert "Tous les tests cy8 ont réussi" in result.stdout


@pytest.mark.parametrize(
    "module_name",
    [
        "cy8_database_manager",
        "cy8_popup_manager",
        "cy8_editable_tables",
        "cy8_prompts_manager_main",
    ],
)
def test_individual_module_import(module_name):
    """Test l'import individuel de chaque module"""
    try:
        __import__(module_name)
    except ImportError as e:
        pytest.fail(f"Ne peut pas importer {module_name}: {e}")


def test_project_structure():
    """Test que la structure du projet est correcte"""
    expected_files = [
        "src/cy8_database_manager.py",
        "src/cy8_test_suite.py",
        "requirements.txt",
        "README.md",
    ]

    for file_path in expected_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Fichier manquant: {file_path}"


def test_requirements_file():
    """Test que le fichier requirements.txt existe et n'est pas vide"""
    req_file = project_root / "requirements.txt"
    assert req_file.exists(), "requirements.txt manquant"

    content = req_file.read_text().strip()
    assert len(content) > 0, "requirements.txt est vide"

    # Vérifier quelques dépendances clés
    assert (
        "requests" in content or "websocket" in content
    ), "Dépendances manquantes dans requirements.txt"
