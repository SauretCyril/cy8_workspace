#!/usr/bin/env python3
"""
Démonstration des nouvelles fonctionnalités de l'onglet Images
cy8_prompts_manager - Version cy8
"""

import os
import sys
import tempfile
from PIL import Image

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager


def create_demo_image(path, size=(200, 150), color=(100, 150, 200)):
    """Créer une image de démonstration"""
    img = Image.new('RGB', size, color)

    # Ajouter du texte simple
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)

        # Essayer d'utiliser une police par défaut
        try:
            font = ImageFont.load_default()
        except:
            font = None

        text = f"Demo Image\n{os.path.basename(path)}"
        if font:
            draw.text((10, 10), text, fill=(255, 255, 255), font=font)
        else:
            draw.text((10, 10), text, fill=(255, 255, 255))

    except ImportError:
        # Si ImageDraw n'est pas disponible, on sauvegarde quand même l'image
        pass

    img.save(path)
    return path


def demo_images_functionality():
    """Démonstration des fonctionnalités images"""
    print("=== Démonstration des fonctionnalités Images ===")
    print("cy8_prompts_manager - Onglet Images")
    print("=" * 50)

    # Créer une base de données temporaire
    db_path = "demo_prompts.db"
    temp_dir = tempfile.mkdtemp()

    try:
        # 1. Initialiser la base de données
        print("1. Initialisation de la base de données...")
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database("init")
        print("   ✓ Base de données créée avec table prompt_image")

        # 2. Créer quelques prompts de démonstration
        print("\n2. Création de prompts de démonstration...")

        prompts_demo = [
            {
                "name": "Portrait femme vintage",
                "prompt": "vintage portrait of a beautiful woman in 1920s style",
                "model": "stable_diffusion_xl.safetensors"
            },
            {
                "name": "Paysage montagne",
                "prompt": "majestic mountain landscape with lake reflection",
                "model": "realistic_vision_v5.safetensors"
            },
            {
                "name": "Architecture futuriste",
                "prompt": "futuristic cityscape with flying cars and neon lights",
                "model": "dreamshaper_v8.safetensors"
            }
        ]

        prompt_ids = []
        for prompt_data in prompts_demo:
            prompt_id = db_manager.create_prompt(
                name=prompt_data["name"],
                prompt_values=f'{{"1": {{"id": "6", "type": "prompt", "value": "{prompt_data["prompt"]}"}}}}',
                workflow='{"6": {"inputs": {"text": ""}, "class_type": "CLIPTextEncode"}}',
                url="",
                model=prompt_data["model"],
                status="ok",
                comment=f"Prompt de démonstration pour {prompt_data['name']}"
            )
            prompt_ids.append(prompt_id)
            print(f"   ✓ Prompt '{prompt_data['name']}' créé (ID: {prompt_id})")

        # 3. Créer des images de démonstration
        print("\n3. Création d'images de démonstration...")

        demo_images = []
        colors = [(220, 100, 120), (100, 220, 150), (120, 150, 220)]

        for i, (prompt_id, prompt_data) in enumerate(zip(prompt_ids, prompts_demo)):
            # Créer 2-3 images par prompt
            for j in range(2 + (i % 2)):  # 2 ou 3 images selon le prompt
                img_filename = f"{prompt_data['name'].replace(' ', '_').lower()}_{j+1}.png"
                img_path = os.path.join(temp_dir, img_filename)

                create_demo_image(img_path, color=colors[i % len(colors)])
                demo_images.append((prompt_id, img_path))

                print(f"   ✓ Image créée: {img_filename}")

        # 4. Ajouter les images à la base de données
        print("\n4. Association des images aux prompts...")

        for prompt_id, img_path in demo_images:
            success = db_manager.add_prompt_image(prompt_id, img_path)
            if success:
                print(f"   ✓ Image associée au prompt {prompt_id}: {os.path.basename(img_path)}")
            else:
                print(f"   ✗ Échec association image: {os.path.basename(img_path)}")

        # 5. Démonstration des requêtes
        print("\n5. Démonstration des requêtes d'images...")

        for prompt_id, prompt_data in zip(prompt_ids, prompts_demo):
            images = db_manager.get_prompt_images(prompt_id)
            print(f"\n   Prompt: '{prompt_data['name']}' (ID: {prompt_id})")
            print(f"   Nombre d'images: {len(images)}")

            for image_id, image_path, created_at in images:
                file_exists = "✓" if os.path.exists(image_path) else "✗"
                print(f"     {file_exists} Image {image_id}: {os.path.basename(image_path)} ({created_at})")

        # 6. Test de suppression
        print("\n6. Test de suppression d'image...")

        # Supprimer une image du premier prompt
        first_prompt_images = db_manager.get_prompt_images(prompt_ids[0])
        if first_prompt_images:
            image_to_delete = first_prompt_images[0]
            success = db_manager.delete_prompt_image(image_to_delete[0])
            if success:
                print(f"   ✓ Image {image_to_delete[0]} supprimée de la base")

                # Vérifier
                remaining_images = db_manager.get_prompt_images(prompt_ids[0])
                print(f"   ✓ Images restantes pour le prompt {prompt_ids[0]}: {len(remaining_images)}")

        # 7. Statistiques finales
        print("\n7. Statistiques finales...")

        total_images = 0
        for prompt_id in prompt_ids:
            images = db_manager.get_prompt_images(prompt_id)
            total_images += len(images)

        print(f"   Total prompts créés: {len(prompt_ids)}")
        print(f"   Total images en base: {total_images}")
        print(f"   Images sur disque: {len([img for _, img in demo_images if os.path.exists(img)])}")

        print("\n" + "=" * 50)
        print("🎉 Démonstration terminée avec succès!")
        print("\nPour tester l'interface graphique:")
        print("1. Lancez: python src/cy8_prompts_manager_main.py")
        print("2. Sélectionnez un prompt dans la liste")
        print("3. Allez dans l'onglet 'Images'")
        print("4. Testez les fonctionnalités d'ajout/suppression d'images")

        print(f"\nFichiers de démonstration créés dans: {temp_dir}")
        print(f"Base de données de démonstration: {db_path}")

    except Exception as e:
        print(f"\n✗ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            db_manager.close()
        except:
            pass

    return True


if __name__ == "__main__":
    print("Démonstration des nouvelles fonctionnalités Images")
    print("cy8_prompts_manager - Version cy8\n")

    success = demo_images_functionality()

    if success:
        print("\n✓ Démonstration réussie!")

        # Proposer de nettoyer
        response = input("\nVoulez-vous nettoyer les fichiers de démonstration? (o/N): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            try:
                if os.path.exists("demo_prompts.db"):
                    os.unlink("demo_prompts.db")
                    print("✓ Base de démonstration supprimée")

                import shutil
                temp_dirs = [d for d in os.listdir(tempfile.gettempdir()) if d.startswith('tmp')]
                print(f"Note: {len(temp_dirs)} dossiers temporaires trouvés dans {tempfile.gettempdir()}")
                print("Les images temporaires seront nettoyées automatiquement par le système.")

            except Exception as e:
                print(f"Erreur lors du nettoyage: {e}")

    sys.exit(0 if success else 1)
