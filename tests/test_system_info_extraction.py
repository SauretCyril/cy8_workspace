#!/usr/bin/env python3
"""
Test de la fonction generate_expert_system_info
"""

import sys
import os
import sqlite3
import re

def test_system_info_extraction():
    """Test de l'extraction des informations système"""

    print("🔍 TEST EXTRACTION INFORMATIONS SYSTÈME")
    print("=" * 60)

    db_path = "G:\\tmp\\prompts_manager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Récupérer les analyses comme le ferait la vraie fonction
        cursor.execute("""
            SELECT id, environment_id, fichier, type, niveau, message, details
            FROM resultats_analyses
            WHERE environment_id = 'G11_05'
            ORDER BY timestamp_analyse DESC
            LIMIT 50
        """)

        recent_analyses = cursor.fetchall()

        print(f"📊 Analyses récupérées: {len(recent_analyses)}")

        # Simulation de la logique d'extraction
        pytorch_info = None
        cuda_info = None
        vram_info = None
        ram_info = None
        python_info = None

        print(f"\n🔍 **RECHERCHE D'INFORMATIONS SYSTÈME:**")

        for analysis in recent_analyses:
            result_id, env_id, fichier, type_result, niveau, message, details = analysis
            message_lower = message.lower()

            print(f"\n📋 ID {result_id}: {message[:80]}...")

            # PyTorch version
            if 'pytorch version' in message_lower:
                pytorch_match = re.search(r'pytorch version:\s*([^\s]+)', message_lower)
                if pytorch_match:
                    pytorch_info = pytorch_match.group(1)
                    print(f"   🧠 PyTorch trouvé: {pytorch_info}")

                    # Extraire CUDA depuis PyTorch (ex: 2.1.2+cu118)
                    cuda_match = re.search(r'\+cu(\d+)', pytorch_info)
                    if cuda_match:
                        cuda_version = cuda_match.group(1)
                        cuda_info = f"CUDA {cuda_version[:2]}.{cuda_version[2:]}"  # cu118 -> CUDA 11.8
                        print(f"   🎮 CUDA trouvé: {cuda_info}")

            # VRAM/RAM
            if 'vram' in message_lower and 'ram' in message_lower:
                vram_match = re.search(r'vram\s+(\d+)\s*mb', message_lower)
                ram_match = re.search(r'ram\s+(\d+)\s*mb', message_lower)
                if vram_match:
                    vram_info = f"{vram_match.group(1)} MB"
                    print(f"   💾 VRAM trouvée: {vram_info}")
                if ram_match:
                    ram_info = f"{ram_match.group(1)} MB"
                    print(f"   💾 RAM trouvée: {ram_info}")

            # Python info depuis les paths
            if 'python' in message_lower and 'embeded' in message_lower:
                python_info = "Python Embedded (ComfyUI)"
                print(f"   🐍 Python trouvé: {python_info}")

        # Simulation de la réponse d'expert
        print(f"\n🤖 **SIMULATION RÉPONSE EXPERT:**")
        print("🔍 **INFORMATIONS SYSTÈME - ENVIRONNEMENT COMFYUI**")
        print("=" * 55)
        print("")
        print(f"🆔 **Environnement:** `G11_05`")
        print("")

        # Section PyTorch/CUDA
        print("🧠 **FRAMEWORKS & ACCÉLÉRATION:**")
        if pytorch_info:
            print(f"• **PyTorch:** {pytorch_info}")
            if cuda_info:
                print(f"• **CUDA:** {cuda_info} (intégrée à PyTorch)")
            else:
                print("• **CUDA:** Version intégrée (détails dans PyTorch)")
        else:
            print("• **PyTorch:** ⚠️ Version non détectée dans les logs")
            print("• **CUDA:** ⚠️ Information non disponible")

        print("")

        # Section Mémoire
        print("💾 **RESSOURCES MÉMOIRE:**")
        if vram_info:
            print(f"• **VRAM GPU:** {vram_info}")
        else:
            print("• **VRAM GPU:** ⚠️ Non détectée")

        if ram_info:
            print(f"• **RAM Système:** {ram_info}")
        else:
            print("• **RAM Système:** ⚠️ Non détectée")

        print("")

        # Section Python
        print("🐍 **ENVIRONNEMENT PYTHON:**")
        if python_info:
            print(f"• **Type:** {python_info}")
        else:
            print("• **Type:** Python (détection automatique)")

        print("")

        # Conseils d'expert
        print("💡 **CONSEILS D'EXPERT:**")

        if pytorch_info and '2.1' in pytorch_info:
            print("⚠️ **PyTorch ancien détecté**")
            print("   • Version recommandée: PyTorch 2.4+")
            print("   • Risque: Chargement non sécurisé des modèles")
            print("   • Action: Mise à jour recommandée")
            print("")

        if vram_info and 'MB' in vram_info:
            vram_value = int(vram_info.split()[0])
            if vram_value < 6000:  # Moins de 6GB
                print("⚠️ **VRAM limitée détectée**")
                print("   • Utiliser des modèles optimisés")
                print("   • Réduire la taille des batches")
                print("   • Considérer l'offloading CPU")
            elif vram_value >= 12000:  # 12GB+
                print("✅ **VRAM excellente**")
                print("   • Capable de gérer les gros modèles")
                print("   • Workflows complexes supportés")

        print("")
        print("🔍 **Note:** Informations extraites des logs ComfyUI récents")

        # Validation
        print(f"\n🎯 **VALIDATION:**")
        success_count = 0
        if pytorch_info:
            print(f"✅ PyTorch détecté: {pytorch_info}")
            success_count += 1
        else:
            print("❌ PyTorch non détecté")

        if cuda_info:
            print(f"✅ CUDA détecté: {cuda_info}")
            success_count += 1
        else:
            print("❌ CUDA non détecté")

        if vram_info:
            print(f"✅ VRAM détectée: {vram_info}")
            success_count += 1
        else:
            print("❌ VRAM non détectée")

        print(f"\n📊 Score: {success_count}/3 informations extraites")

        conn.close()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_system_info_extraction()
