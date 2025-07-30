# carte encodées en utf-8

import genanki
import re
import subprocess
import os

# ══════════════════════════════════════════════════════
# Pas de CONFIGURATION ici ! Les paramètres seront passés à la fonction generate_deck
# ══════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════
# GENANKI SETUP (Ceci reste global car les modèles sont souvent statiques)
# ══════════════════════════════════════════════════════

MY_MODEL_ID = 1607392319
MY_DECK_ID = 2059400110  # L'ID du deck reste fixe pour qu'Anki mette a jour
CARD_CSS = """
.card {
    font-family: Arial;
    font-size: 24px;
    text-align: center;
    color: black;
    background-color: white;
}
.question {
    padding: 10px;
    max-width: 800px;
    margin: auto;
    word-wrap: break-word;
    box-sizing: border-box;
}
"""

# Le modèle est initialisé une fois pour toutes
model = genanki.Model(
    MY_MODEL_ID,
    'Text+Sound Auto Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'AudioQ'},
        {'name': 'AudioA'}
    ],
    templates=[
        {
            'name': 'Card Template',
            'qfmt': '<div class="question">{{Question}}</div><br>{{AudioQ}}',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="question">{{Answer}}</div><br>{{AudioA}}',
        },
    ],
    css=CARD_CSS
)


# Les variables deck et media_files seront initialisées DANS la fonction generate_deck
# car elles dépendent de chaque exécution et ne doivent pas persister entre les appels

# ══════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════

def convert_wav_to_mp3(wav_path, ffmpeg_path):  # Ajout de ffmpeg_path en parametre
    mp3_path = wav_path.replace('.wav', '.mp3')
    if not os.path.exists(ffmpeg_path) and ffmpeg_path != "ffmpeg":
        raise FileNotFoundError(f"FFmpeg introuvable au chemin spécifié: {ffmpeg_path}. Vérifiez votre configuration.")

    # Si ffmpeg_path est juste "ffmpeg", subprocess va le chercher dans le PATH
    ffmpeg_cmd = [ffmpeg_path, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path]

    if not os.path.exists(mp3_path) or os.path.getmtime(wav_path) > os.path.getmtime(mp3_path):
        print(f"🔄 Conversion WAV ➜ MP3 : {os.path.basename(wav_path)} ➜ {os.path.basename(mp3_path)}")
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            error_message = f"❌ ERREUR conversion {os.path.basename(wav_path)} :\n  Stdout: {e.stdout}\n  Stderr: {e.stderr}"
            print(error_message)
            raise Exception(f"Erreur de conversion audio: {error_message}")  # Propagate a more generic exception
        except FileNotFoundError:  # Gérer le cas où ffmpeg n'est pas trouvé dans le PATH
            raise FileNotFoundError(
                "FFmpeg introuvable. Assurez-vous qu'il est installé et que son chemin est configuré ou dans votre PATH.")
    return mp3_path


def extract_audio_path(text):
    match = re.search(r'"([^"]+\.(?:mp3|wav))"', text)
    return match.group(1) if match else None


def process_side(text, sounds_dir, ffmpeg_path):  # Ajout de ffmpeg_path en parametre
    audio_filename = extract_audio_path(text)
    audio_tag = ''
    full_audio_path = None
    cleaned_text = text.strip()

    if audio_filename:
        cleaned_text = cleaned_text.replace(f'"{audio_filename}"', '').strip()
        full_audio_path = os.path.join(sounds_dir, os.path.basename(audio_filename))

        if full_audio_path.lower().endswith('.wav'):
            try:
                # Appelle la fonction de conversion avec le chemin ffmpeg
                full_audio_path = convert_wav_to_mp3(full_audio_path, ffmpeg_path)
                audio_tag = f"[sound:{os.path.basename(full_audio_path)}]"
            except Exception as e:
                print(f"⚠️ Conversion échouée : {os.path.basename(full_audio_path)} ➜ {e}")
                # Ne pas ajouter le fichier au media_files si la conversion échoue
                return cleaned_text, '', None
        else:
            audio_tag = f"[sound:{os.path.basename(full_audio_path)}]"

    return cleaned_text, audio_tag, full_audio_path


# ══════════════════════════════════════════════════════
# LOGIQUE PRINCIPALE DE GENERATION DE DECK
# ══════════════════════════════════════════════════════

def generate_deck(cards_file, deck_name, ffmpeg_path, output_filepath):  # Tous les parametres sont passes ici
    print("🚀 Génération du deck Anki...")

    # Initialisation de deck et media_files pour chaque generation
    current_deck = genanki.Deck(MY_DECK_ID, deck_name)  # Utilisez le deck_name passe en parametre
    current_media_files = []

    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(cards_file)), 'sounds')
    if not os.path.exists(sounds_dir):
        print(f"⚠️ Dossier 'sounds' manquant : {sounds_dir}. Aucun audio ne sera ajouté.")
        os.makedirs(sounds_dir, exist_ok=True)  # Creer le dossier s'il n'existe pas

    try:
        with open(cards_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    if ' >> ' not in line:
                        raise ValueError("Séparateur '>>' manquant entre question et réponse.")

                    q_raw, a_raw = line.split(' >> ', 1)
                    # Passez ffmpeg_path a process_side
                    q_text, q_tag, q_path = process_side(q_raw, sounds_dir, ffmpeg_path)
                    a_text, a_tag, a_path = process_side(a_raw, sounds_dir, ffmpeg_path)

                    for path in (q_path, a_path):
                        if path:
                            if os.path.exists(path):
                                current_media_files.append(path)
                            else:
                                print(f"❌ Fichier audio introuvable (mentionné dans cards.txt) : {path}")

                    note = genanki.Note(
                        model=model,
                        fields=[q_text, a_text, q_tag, a_tag]
                    )
                    current_deck.add_note(note)

                except Exception as e:
                    print(
                        f"\n❌ LIGNE {line_num} ✖️\n   '{line}'\n   Erreur lors du traitement: {e}\n   Format attendu : Texte \"audio.mp3\" >> Réponse \"audio.mp3\"")
                    # Continue a la ligne suivante meme en cas d'erreur sur une carte


    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{cards_file}' n'a pas été trouvé.")
        raise  # Relaunch l'exception pour que la GUI la capture
    except Exception as e:
        print(f"❌ Erreur générale lors de la lecture/traitement de '{cards_file}': {e}")
        raise  # Relaunch l'exception

    # Sauvegarde du package Anki
    # Le chemin de sortie complet est deja passe en parametre
    genanki.Package(current_deck, current_media_files).write_to_file(output_filepath)
    print(f"\n🎉 Deck créé avec succès ➜ '{output_filepath}'")
    print(f"📦 Cartes: {len(current_deck.notes)} | Médias: {len(current_media_files)}")

# Le bloc __main__ est vide ou supprimé car le script est importé comme un module
# if __name__ == '__main__':
#    generate_deck() # Cette ligne ne sera plus executee lors de l'import