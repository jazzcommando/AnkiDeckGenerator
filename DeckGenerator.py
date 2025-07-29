# IMPORT DES PACKAGES REQUIS
import genanki
import re
import subprocess
import os

# --- CHEMIN VERS FFMPEG, ULTRA PUTAIN D'IMPORTANT ---
FFMPEG_PATH = r"C:\FFMPEG\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
# --------------------------


def convert_wav_to_mp3(wav_path):
    mp3_path = wav_path.replace('.wav', '.mp3')

    if not os.path.exists(FFMPEG_PATH):
        raise FileNotFoundError(f"FFmpeg non trouvé au chemin spécifié : {FFMPEG_PATH}")

    if not os.path.exists(mp3_path):  # On évite de reconvertir si le MP3 existe déjà
        print(f"🔄 Conversion : {wav_path} ➜ {mp3_path}")
        try:
            subprocess.run([
                FFMPEG_PATH,
                "-y",  # DELETE THE WAV, NEPHEW
                "-i", wav_path,  # OUTPUT
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",  # ça fait surement un truc ça
                mp3_path
            ], check=True, capture_output=True, text=True) # erreur check, debugging
        except subprocess.CalledProcessError as e:
            print(f"❌ ERREUR LORS DE LA CONVERSION AUDIO DE {wav_path}:")
            print(f"  Stdout: {e.stdout}")
            print(f"  Stderr: {e.stderr}")
            raise
    return mp3_path


# MAGIE NOIRE
# ID de modèle aléatoires pour éviter les conflits
MY_MODEL_ID = 1607392319
MY_DECK_ID = 2059400110

# CSS pour centrer le texte
CARD_CSS = """
.card {
    font-family: Arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
.question {
    padding: 10px;
    max-width: 800px; /* Limite la largeur du texte */
    margin: auto; /* Centre le bloc de texte */
    word-wrap: break-word; /* Permet aux mots longs de se casser et de passer à la ligne */
    box-sizing: border-box; /* Inclut le padding et la bordure dans la largeur totale */
}
"""

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
            # On ajoute une div avec une classe 'question' pour appliquer le CSS
            'qfmt': '<div class="question">{{Question}}</div><br>{{AudioQ}}',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="question">{{Answer}}</div><br>{{AudioA}}',
        },
    ],
    css=CARD_CSS
)

deck = genanki.Deck(MY_DECK_ID, 'Englando Deck')
media_files = []  # Liste pour stocker les chemins des fichiers média


# Définit la fonction qui permet d'identifier les pointeurs audio dans une chaîne de texte
# Cherche "chemin/vers/fichier.mp3" ou "chemin/vers/fichier.wav"
def extract_audio_path(text_with_audio):
    match = re.search(r'"([^"]+\.(?:mp3|wav))"', text_with_audio)
    return match.group(1) if match else None


# Juicy stuff: extraction du .txt en un truc que python peut lire
def parse_file(filepath):
    # Chemin absolu du dossier 'sounds' pour la gestion des médias. KEYWORD: ABSOLU.
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(filepath)), 'sounds')
    if not os.path.exists(sounds_dir):
        print(f"⚠️ GAFFE, ERREUR : LE DOSSIER 'sounds' N'EXISTE PAS A L'EMPLACEMENT ATTENDU : {sounds_dir}")
        print(" Solution: mettre les audios dans ce dossier là.")


    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()


    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'): #ignore les lignes avec les hashtags, simplifie la vie
            continue

        try:
            if ' >> ' not in stripped_line:
                raise ValueError("Erreur: oublié de mettre les deux fléches (>>) entre question et réponse")

            q_raw, a_raw = stripped_line.split(' >> ', 1)

            # aucune idée de ce que ce truc fait
            q_text, q_audio_tag, q_audio_filepath = process_side(q_raw, sounds_dir)
            a_text, a_audio_tag, a_audio_filepath = process_side(a_raw, sounds_dir)

            # same
            if q_audio_filepath and os.path.exists(q_audio_filepath):
                media_files.append(q_audio_filepath)
            elif q_audio_filepath and not os.path.exists(q_audio_filepath):
                print(f"❌ ERREUR : Fichier audio manquant pour la question (ligne {line_num}): {q_audio_filepath}")

            if a_audio_filepath and os.path.exists(a_audio_filepath):
                media_files.append(a_audio_filepath)
            elif a_audio_filepath and not os.path.exists(a_audio_filepath):
                print(f"❌ ERREUR : Fichier audio manquant pour la réponse (ligne {line_num}): {a_audio_filepath}")


            note = genanki.Note(
                model=model,
                fields=[q_text, a_text, q_audio_tag, a_audio_tag]
            )
            deck.add_note(note)

        except Exception as e:
            print(f"\n❌ ERREUR DE SYNTAXE DANS LE FICHIER '{filepath}' LIGNE {line_num}:")
            print(f"   Ligne : '{line.strip()}'")
            print(f"   Erreur: {e}")
            print("   Vérifier cards.txt: 'Question text \"audio_q.mp3\" >> Answer text \"audio_a.mp3\"'\n")


# génération des cartes via les données extraites de cards.txt
def process_side(raw_text_side, sounds_base_dir):
    audio_file_in_text = extract_audio_path(raw_text_side)
    audio_tag = ''
    audio_full_path = None
    processed_text = raw_text_side.strip() # Commence avec le texte brut

    if audio_file_in_text:
        # Supprime le chemin audio du texte pour n'afficher que le texte pur sur la carte (sinon tout est fuckd)
        processed_text = raw_text_side.replace(f'"{audio_file_in_text}"', '').strip()

        # Construction du chemin absolu du fichier audio
        # ça c'est juste de la magie noire mais ok
        audio_full_path = os.path.join(sounds_base_dir, os.path.basename(audio_file_in_text))

        # Vérifie si c'est un PUTAIN DE WAV et convertit si nécessaire
        if audio_full_path.lower().endswith(".wav"):
            try:
                converted_mp3_path = convert_wav_to_mp3(audio_full_path)
                # Le tag Anki doit pointer vers le fichier MP3 converti
                audio_tag = f"[sound:{os.path.basename(converted_mp3_path)}]"
                audio_full_path = converted_mp3_path # Met à jour le chemin pour l'ajouter aux médias
            except Exception as e:
                print(f"⚠️ Echec de la converssion d'un putain de WAV. ({audio_full_path}). L'audio ne sera pas inclus. Erreur: {e}")
                audio_tag = ''  # Pas de tag si la conversion échoue
                audio_full_path = None
        else:
            # Si c'est déjà un MP3 ou autre format supporté (et non WAV), on utilise tel quel
            audio_tag = f"[sound:{os.path.basename(audio_full_path)}]"

    return processed_text, audio_tag, audio_full_path


# Processing final et génération du deck (mon dieu enfin)
print('Ca génère, croise les doigts.')
parse_file('cards.txt')
genanki.Package(deck, media_files).write_to_file('output.apkg')
print(f"\n DECK CREE AVEC FUCKING SUCCES : 'output.apkg'")
print(f"Total cartes: {len(deck.notes)} | Total fichiers média: {len(media_files)}")
print("OUBLIE PAS DE METTRE LE FICHIER ANKI A JOUR!")
