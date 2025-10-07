import os

def modify_custom_node_for_debug():
    """Modifier temporairement les custom nodes pour identifier lequel est utilisé"""
    print('=== MODIFICATION CUSTOM NODES POUR DEBUG ===')

    # Chemins des custom nodes
    g11_path = r"E:\Comfyui_G11\ComfyUI\custom_nodes\extra_path_reader.py"
    h12_path = r"E:\Comfyui_H12\ComfyUI\custom_nodes\extra_path_reader.py"

    # Code de debug à ajouter
    debug_code = '''        # DEBUG: Identifier l'environnement utilisé
        debug_info = f"CUSTOM_NODE_DEBUG: Exécuté depuis {comfyui_root}"
        print(debug_info)'''

    for path, env_name in [(g11_path, "G11"), (h12_path, "H12")]:
        if os.path.exists(path):
            print(f'\n📝 Modification du custom node {env_name}: {path}')

            # Lire le fichier
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chercher la ligne où ajouter le debug (après la détection de comfyui_root)
            if 'if not comfyui_root:' in content and 'DEBUG: Identifier' not in content:
                # Ajouter le debug après la détection de comfyui_root
                modified_content = content.replace(
                    'if not comfyui_root:',
                    f'''        # DEBUG: Identifier l'environnement utilisé - {env_name}
        debug_info = f"CUSTOM_NODE_DEBUG_{env_name}: Exécuté depuis {{comfyui_root}}"
        print(debug_info)

        if not comfyui_root:'''
                )

                # Sauvegarder le fichier modifié
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)

                print(f'✅ Debug ajouté dans {env_name}')
            else:
                print(f'⚠️ Debug déjà présent ou pattern non trouvé dans {env_name}')

def restore_custom_nodes():
    """Restaurer les custom nodes originaux"""
    print('\n=== RESTAURATION CUSTOM NODES ===')

    # Copier notre version originale vers les deux environnements
    source_path = r"g:\G_WCS\cy8_workspace\custom_nodes\extra_path_reader.py"
    g11_path = r"E:\Comfyui_G11\ComfyUI\custom_nodes\extra_path_reader.py"
    h12_path = r"E:\Comfyui_H12\ComfyUI\custom_nodes\extra_path_reader.py"

    if os.path.exists(source_path):
        import shutil
        for target_path, env_name in [(g11_path, "G11"), (h12_path, "H12")]:
            try:
                shutil.copy2(source_path, target_path)
                print(f'✅ {env_name} restauré: {target_path}')
            except Exception as e:
                print(f'❌ Erreur restauration {env_name}: {e}')

if __name__ == "__main__":
    # Modifier pour le debug
    modify_custom_node_for_debug()

    print('\n💡 Maintenant, testez avec votre application et regardez les logs ComfyUI')
    print('💡 Vous devriez voir "CUSTOM_NODE_DEBUG_G11" ou "CUSTOM_NODE_DEBUG_H12"')

    input('\n⏸️  Appuyez sur Entrée après avoir testé pour restaurer...')

    # Restaurer les originaux
    restore_custom_nodes()
