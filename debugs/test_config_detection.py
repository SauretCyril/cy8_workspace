import os
import tempfile
import time

def create_unique_config_files():
    """Créer des fichiers de config uniques pour identifier lequel est lu"""
    print('=== CRÉATION DE CONFIGS UNIQUES POUR TEST ===')

    configs = {
        "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml": "G11_UNIQUE_MARKER",
        "E:/Comfyui_H12/ComfyUI/extra_model_paths.yaml": "H12_UNIQUE_MARKER"
    }

    backups = {}

    for config_path, marker in configs.items():
        if os.path.exists(config_path):
            # Sauvegarder l'original
            backup_path = config_path + ".backup"
            try:
                import shutil
                shutil.copy2(config_path, backup_path)
                backups[config_path] = backup_path
                print(f'✅ Sauvegarde: {backup_path}')

                # Créer un config unique avec marqueur
                unique_config = f'''# {marker} - Fichier de test
comfyui:
  base_path: {os.path.dirname(config_path).replace(os.sep, "/")}

# MARKER: {marker}
# TIMESTAMP: {time.time()}'''

                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(unique_config)

                print(f'✅ Config unique créé: {config_path} ({marker})')

            except Exception as e:
                print(f'❌ Erreur {config_path}: {e}')

    return backups

def restore_config_files(backups):
    """Restaurer les fichiers de config originaux"""
    print('\n=== RESTAURATION DES CONFIGS ===')

    for original_path, backup_path in backups.items():
        try:
            import shutil
            if os.path.exists(backup_path):
                shutil.move(backup_path, original_path)
                print(f'✅ Restauré: {original_path}')
            else:
                print(f'⚠️ Backup introuvable: {backup_path}')
        except Exception as e:
            print(f'❌ Erreur restauration {original_path}: {e}')

def test_config_detection():
    """Tester quel config est effectivement lu"""
    print('\n🔍 TEST DE DÉTECTION DU CONFIG...')

    # Créer les configs uniques
    backups = create_unique_config_files()

    try:
        # Maintenant tester avec l'application
        print('\n💡 Les configs uniques sont créés.')
        print('💡 Lancez maintenant l\'identification dans votre application.')
        print('💡 Le résultat contiendra G11_UNIQUE_MARKER ou H12_UNIQUE_MARKER')

        input('\n⏸️ Appuyez sur Entrée après avoir testé...')

    finally:
        # Restaurer les originaux
        restore_config_files(backups)

if __name__ == "__main__":
    test_config_detection()
