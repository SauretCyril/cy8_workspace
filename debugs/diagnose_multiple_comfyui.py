import os

def diagnose_comfyui_environments():
    """Diagnostic des environnements ComfyUI multiples"""
    print('=== DIAGNOSTIC ENVIRONNEMENTS COMFYUI MULTIPLES ===')

    # Chemins potentiels d'environnements ComfyUI
    potential_paths = [
        'E:/Comfyui_G11/',
        'E:/Comfyui_H12/',
        'H:/Comfyui_H12_01/',
        'H:/ComfyUI_H12_01/',
        'G:/Comfyui_G11_03/',
        'C:/ComfyUI/',
        'E:/ComfyUI/',
        'H:/ComfyUI/'
    ]

    print('\n🔍 SCAN DES ENVIRONNEMENTS COMFYUI :')
    found_envs = []

    for path in potential_paths:
        if os.path.exists(path):
            print(f'✅ TROUVÉ: {path}')
            found_envs.append(path)

            # Vérifier les sous-dossiers importants
            comfyui_subfolder = os.path.join(path, 'ComfyUI')
            if os.path.exists(comfyui_subfolder):
                print(f'  📂 ComfyUI/: {comfyui_subfolder}')

                # Vérifier le fichier de config
                config_file = os.path.join(comfyui_subfolder, 'extra_model_paths.yaml')
                if os.path.exists(config_file):
                    print(f'  ⚙️ Config: {config_file}')
                else:
                    print(f'  ❌ Pas de config: {config_file}')

            # Vérifier Python embedded
            python_embedded = os.path.join(path, 'python_embeded', 'python.exe')
            if os.path.exists(python_embedded):
                print(f'  🐍 Python: {python_embedded}')
            else:
                print(f'  ❌ Pas de Python: {python_embedded}')
        else:
            print(f'❌ ABSENT: {path}')

    print(f'\n📊 RÉSUMÉ: {len(found_envs)} environnements trouvés')

    # Analyser les conflits
    if len(found_envs) > 1:
        print('\n⚠️ CONFLIT DÉTECTÉ!')
        print('Plusieurs environnements ComfyUI présents:')
        for env in found_envs:
            print(f'  - {env}')

        print('\n💡 RECOMMANDATIONS:')
        print('1. Identifier quel environnement vous voulez utiliser')
        print('2. Configurer les custom nodes pour pointer vers le bon environnement')
        print('3. Vérifier la cohérence entre config et Python embedded')

    # Vérifier les variables d'environnement
    print('\n🔍 VARIABLES D\'ENVIRONNEMENT:')
    env_vars = ['COMFYUI_PATH', 'COMFYUI_ROOT', 'COMFYUI_DIR']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f'  {var}: {value}')
        else:
            print(f'  {var}: Non définie')

if __name__ == "__main__":
    diagnose_comfyui_environments()
