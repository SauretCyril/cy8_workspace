import requests
import sys
import os
import time
from dotenv import load_dotenv
from datetime import datetime


def get_mistral_answer(question, role, texte):
    try:
        # Charger le fichier .env
        load_dotenv()

        # Récupérer la clé API Mistral depuis les variables d'environnement
        print(f"Python utilisé dans cy_mistral.py : {sys.executable}")
        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError(
                "La clé API Mistral n'est pas définie dans le fichier .env"
            )

        # Construire les messages pour l'API
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": f"Contenu: {texte}\n\nQuestion: {question}"},
        ]

        # Configuration de la requête à l'API Mistral
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Données à envoyer à l'API Mistral
        data = {
            "model": "mistral-medium",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 9000,  # Augmenter cette valeur (était 5000)
        }

        # Appel à l'API Mistral
        time.sleep(10)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Ajoute cette ligne
        response_json = response.json()
        if "choices" in response_json and response_json["choices"]:
            content = response_json["choices"][0]["message"]["content"]
            print(f"dbg-678 : Réponse de l'API Mistral: {content}")
            return content
        else:
            # Retourner le message d'erreur de l'API si présent
            error_msg = response_json.get(
                "error", "Réponse inattendue de l'API Mistral"
            )
            return f'{{"error": "{error_msg}"}}'
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            print(f"dbg-678 : Trop de requêtes envoyées à l'API Mistral: {e}")
            return '{"error": "Trop de requêtes envoyées à l\'API Mistral. Merci de patienter avant de réessayer."}'
        else:
            print(f"dbg-678 : Erreur de l'API Mistral: {e}")
            return f'{{"error": "Erreur lors de l\'appel à l\'API Mistral: {str(e)}"}}'
    except Exception as e:
        print(f"dbg-678 : Erreur inattendue: {e}")
        return f'{{"error": "Erreur lors de l\'appel à l\'API Mistral: {str(e)}"}}'


def analyze_comfyui_error(error_line, error_context="", timestamp=""):
    """
    Analyser une erreur ComfyUI avec Mistral AI

    Args:
        error_line: La ligne d'erreur extraite du log
        error_context: Contexte additionnel autour de l'erreur
        timestamp: Timestamp de l'erreur

    Returns:
        str: Solution proposée par Mistral AI
    """
    role = (
        "Tu es un assistant expert Python et ComfyUI. Tu analyses les erreurs des logs ComfyUI "
        "et tu proposes des solutions claires et détaillées. Tu dois expliquer l'erreur de façon "
        "compréhensible et donner des étapes concrètes pour la résoudre."
    )

    question = (
        f"Aide-moi à comprendre cette erreur du log ComfyUI et propose une solution:\n\n"
        f"Timestamp: {timestamp}\n"
        f"Ligne d'erreur: {error_line}\n"
        f"Contexte: {error_context}\n\n"
        f"Merci de fournir:\n"
        f"1. Explication de l'erreur\n"
        f"2. Causes possibles\n"
        f"3. Solutions étape par étape\n"
        f"4. Conseils de prévention"
    )

    # Utiliser la fonction existante avec le contexte spécialisé
    response = get_mistral_answer(question, role, error_line)

    return response


def save_error_solution(timestamp, error_line, solution, solutions_dir):
    """
    Sauvegarder l'erreur et sa solution dans un fichier

    Args:
        timestamp: Timestamp de l'erreur pour le nom du fichier
        error_line: Ligne d'erreur originale
        solution: Solution proposée par Mistral AI
        solutions_dir: Répertoire où sauvegarder le fichier

    Returns:
        str: Chemin du fichier créé ou None si erreur
    """
    try:
        # Créer le répertoire s'il n'existe pas
        os.makedirs(solutions_dir, exist_ok=True)

        # Nettoyer le timestamp pour le nom de fichier (remplacer caractères interdits)
        safe_timestamp = timestamp.replace(":", "-").replace(" ", "_").replace(".", "-")
        filename = f"error_solution_{safe_timestamp}.txt"
        filepath = os.path.join(solutions_dir, filename)

        # Contenu du fichier
        content = f"""ANALYSE D'ERREUR COMFYUI
=======================
Timestamp: {timestamp}
Date d'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ERREUR ORIGINALE:
{error_line}

SOLUTION PROPOSÉE:
{solution}

---
Généré automatiquement par cy8_prompts_manager avec Mistral AI
"""

        # Écrire le fichier
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Solution sauvegardée: {filepath}")
        return filepath

    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None


def load_error_solution(timestamp, solutions_dir):
    """
    Charger une solution existante depuis un fichier

    Args:
        timestamp: Timestamp de l'erreur
        solutions_dir: Répertoire où chercher le fichier

    Returns:
        str: Contenu du fichier ou None si non trouvé
    """
    try:
        # Nettoyer le timestamp pour le nom de fichier
        safe_timestamp = timestamp.replace(":", "-").replace(" ", "_").replace(".", "-")
        filename = f"error_solution_{safe_timestamp}.txt"
        filepath = os.path.join(solutions_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Solution chargée: {filepath}")
            return content

        return None

    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        return None


def analyze_comfyui_log_complete(log_content, question, role):
    """
    Analyser un log ComfyUI complet avec Mistral AI

    Args:
        log_content: Contenu complet du log
        question: Question à poser à Mistral AI
        role: Rôle/contexte pour Mistral AI

    Returns:
        str: Analyse complète du log par Mistral AI
    """
    try:
        print("Démarrage de l'analyse complète du log ComfyUI...")

        # Tronquer le log si trop long (pour éviter les limites de l'API)
        max_chars = 50000  # Limite raisonnable pour l'API
        if len(log_content) > max_chars:
            print(f"Log tronqué de {len(log_content)} à {max_chars} caractères")
            log_content = log_content[
                -max_chars:
            ]  # Prendre la fin du log (plus récent)
            log_content = "[...LOG TRONQUÉ...]\n" + log_content

        # Améliorer le contexte pour l'analyse complète
        enhanced_role = f"{role}. Tu analyses un log ComfyUI complet pour identifier TOUTES les erreurs, leur contexte, leurs causes possibles et proposer des solutions détaillées. Sois méthodique et exhaustif."

        enhanced_question = f"""Analyse complète de ce log ComfyUI:

{question}

Instructions spécifiques:
1. Identifie TOUTES les erreurs présentes dans le log
2. Analyse le contexte global et la séquence des événements
3. Explique les causes probables de chaque erreur
4. Propose des solutions concrètes et détaillées
5. Donne des recommandations pour éviter ces problèmes à l'avenir
6. Structure ta réponse de manière claire avec des sections distinctes

Format de réponse souhaité:
📊 RÉSUMÉ EXÉCUTIF
🔍 ERREURS IDENTIFIÉES
⚠️ ANALYSE DES CAUSES
💡 SOLUTIONS PROPOSÉES
🔧 RECOMMANDATIONS
"""

        # Appeler l'API Mistral
        result = get_mistral_answer(enhanced_question, enhanced_role, log_content)

        if result:
            print("Analyse complète terminée avec succès")
            return result
        else:
            return "❌ Erreur lors de l'analyse : Aucune réponse reçue de Mistral AI"

    except Exception as e:
        error_msg = f"❌ Erreur lors de l'analyse complète du log : {str(e)}"
        print(error_msg)
        return error_msg


def translate_to_french(text):
    """
    Traduire un texte anglais vers le français avec Mistral AI

    Args:
        text: Texte à traduire

    Returns:
        str: Texte traduit en français ou message d'erreur
    """
    try:
        role = (
            "Tu es un traducteur professionnel spécialisé dans la traduction technique. "
            "Tu traduis uniquement du texte anglais vers le français de manière précise et naturelle. "
            "Conserve le formatage et la structure du texte original. "
            "Ne traduis pas les termes techniques spécifiques à ComfyUI ou à l'IA générative. "
            "Réponds UNIQUEMENT avec la traduction, sans commentaire."
        )

        question = (
            "Traduis ce texte anglais vers le français en conservant le sens technique "
            "et en gardant les termes spécialisés en anglais quand approprié:"
        )

        result = get_mistral_answer(question, role, text)

        # Nettoyer la réponse si elle contient des marqueurs JSON d'erreur
        if result and result.startswith('{"error"'):
            return f"❌ Erreur de traduction : {result}"

        return result

    except Exception as e:
        return f"❌ Erreur lors de la traduction : {str(e)}"


def translate_to_english(text):
    """
    Traduire un texte français vers l'anglais avec Mistral AI

    Args:
        text: Texte à traduire

    Returns:
        str: Texte traduit en anglais ou message d'erreur
    """
    try:
        role = (
            "Tu es un traducteur professionnel spécialisé dans la traduction technique. "
            "Tu traduis uniquement du texte français vers l'anglais de manière précise et naturelle. "
            "Conserve le formatage et la structure du texte original. "
            "Utilise un anglais technique approprié pour les contextes d'IA générative et ComfyUI. "
            "Réponds UNIQUEMENT avec la traduction, sans commentaire."
        )

        question = (
            "Traduis ce texte français vers l'anglais en utilisant un vocabulaire "
            "technique approprié pour l'IA générative et ComfyUI:"
        )

        result = get_mistral_answer(question, role, text)

        # Nettoyer la réponse si elle contient des marqueurs JSON d'erreur
        if result and result.startswith('{"error"'):
            return f"❌ Erreur de traduction : {result}"

        return result

    except Exception as e:
        return f"❌ Erreur lors de la traduction : {str(e)}"


def detect_language(text):
    """
    Détecter la langue d'un texte avec Mistral AI

    Args:
        text: Texte à analyser

    Returns:
        str: 'french', 'english' ou 'unknown'
    """
    try:
        role = (
            "Tu es un détecteur de langue. Tu analyses un texte et détermines s'il est "
            "principalement en français ou en anglais. Réponds UNIQUEMENT avec 'french', "
            "'english' ou 'unknown' si tu ne peux pas déterminer."
        )

        question = "Quelle est la langue principale de ce texte ?"

        result = get_mistral_answer(question, role, text)

        if result:
            result = result.strip().lower()
            if 'french' in result or 'français' in result:
                return 'french'
            elif 'english' in result or 'anglais' in result:
                return 'english'

        return 'unknown'

    except Exception as e:
        print(f"Erreur détection langue : {e}")
        return 'unknown'
