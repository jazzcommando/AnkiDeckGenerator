import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os
import webbrowser
import winshell

import DeckGenerator

CONFIG_FILE = "config.json"
CARDS_FILE = "cards.txt"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Oopsie",
                                 f"Fichier de config '{CONFIG_FILE}' est corrompu, relancer setup")
            os.remove(CONFIG_FILE)  # Supprime le fichier corrompu pour qu'on puisse le recréer
    return None


def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def create_desktop_shortcut():
    try:
        exe_path = os.path.abspath(__file__)

        # direct sur le bureau
        desktop = winshell.desktop()
        shortcut_name = "Anki Deck Generator"
        shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")

        with winshell.shortcut(shortcut_path) as link:
            link.path = exe_path
            link.description = "scuffed mais fonctionne"

        messagebox.showinfo("Raccourci Créé!",
                            f"c'est quand même plus pratique :)")
    except ImportError:
        messagebox.showerror("Erreur de Module",
                             'BIG FUCK\n'
                             f'Merci de contacter le dév :)))\n\n'
                             f'SI TU TE SENS BRAVE:\n'
                             f'1) installe python (google juste python installeur windows)'
                             f'2) ouvre ton terminal (appuie sur win+r et tape cmd.exe)\n'
                             f'3) tape: \'pip install winshell\n'
                             f'4) redémarre le programme et prie.')
    except Exception as e:
        messagebox.showerror("oopsie", f"Impossible de créer le raccourci.\n"
                                       f"Essaie de relancer en adminstrateur?\nErreur : {e}")


def run_setup():
    config = {}

    # --- ÉTAPE 1 : Nom du Deck  ---
    deck_name = simpledialog.askstring("Nom du Deck (Étape 1/3)",
                                       "Comme il apparaitra dans Anki", parent=root)
    if not deck_name:
        messagebox.showwarning("Annulé", "sans nom ça marchera pas trop")
        return
    config["deck_name"] = deck_name

    # --- ÉTAPE 2 : Chemin FFMPEG  ---
    messagebox.showinfo(
        "FFMPEG : IMPORTANT AS FUCK (Étape 2/3)",
        "ETAPE 2: Configurer et installer FFMPEG.`\n\n"
        "FFMPEG est un programme qui permet de convertir un format audio en autre, GLOBALEMENT.\n."
        "Important car Anki déteste les fichier wav\n"
        "Donc, on converti tout en MP3.",
        parent=root
    )
    # Proposer d'ouvrir le site FFMPEG avant de demander le chemin
    if messagebox.askyesno("Télécharger FFMPEG ?", "Telecharger directement FFMPEG? (indice: oui)",
                           parent=root):
        webbrowser.open("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")

    # --- quick explication de comment unzip --- #
    messagebox.showinfo(
        "Installer FFMPEG",
        f"Extrait le zip que tu viens de télécharger dans un nouveau dossier. Idéalement,\n"
        "à un endroit où il sera hors de vue (par exemple, dans C:).\n\n"
        "L'étape suivante demandera accés à ce nouveau dossier.\n"
        "Il faudrat selectionner FFMPEG.EXE, quelquepart dans BIN."
        "",
        parent=root)

    ffmpeg_path = filedialog.askopenfilename(
        title="Trouver executable FFMPEG ? (Regarde dans le dossier 'bin')",
        filetypes=[("Exécutable FFMPEG", "ffmpeg.exe"), ("Tous les fichiers", "*.*")],
        parent=root
    )
    # valeur par defaut "ffmpeg" pour PATH
    config["ffmpeg_path"] = ffmpeg_path if ffmpeg_path else "ffmpeg"

    # --- ÉTAPE 3 : Dossier d'Export (NOUVEAU DIALOGUE + Nom du fichier) ---
    messagebox.showinfo(
        "Dossier de Sortie (Étape 3/3)",
        f'Dernière étape, choisi donc où ton deck sera sauvegardé.\n\n'
        '(choisis un endroit facile à retrouver,\n'
        'je pense pas avoir codé une manière de le changer)',
        parent=root
    )

    # nom de l'output = nom selectionné au début
    output_filepath = filedialog.asksaveasfilename(
        title=f"Sauvegarder le deck Anki '{deck_name}'",
        defaultextension=".apkg",
        filetypes=[("Deck Anki", "*.apkg")],
        initialfile=f"{deck_name}.apkg",  # APKG match le nom du deck
        parent=root
    )
    if not output_filepath:
        messagebox.showwarning("Annulé !", ":(.")
        return

    config["output_filepath"] = output_filepath

    save_config(config)
    messagebox.showinfo("Setup Terminé!",
                        "oh mon dieu ça a marché. ready to go bitches")
    update_generate_button_state()


def run_generator():
    config = load_config()
    if not config:
        messagebox.showerror("oopsie", "Fichier config manquant. Lance le setup queen.")
        return

    # fetch back à partir du cfg
    output_filepath = config.get("output_filepath")
    if not output_filepath:
        messagebox.showerror("oopsie", "Dossier de sortie du deck non configuré.\n\n"
                                       "relance le setup queen")
        return

    if not os.path.exists(CARDS_FILE):
        messagebox.showerror("oopsie",
                             f"{CARDS_FILE}' n'a pas été trouvé.\n\n"
                             f"Il devrait être dans le même dossier que ce .exe.")
        return

    try:
        # verification de l'existance du dossier
        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)  # crée le s'il existe pas

        DeckGenerator.generate_deck(
            cards_file=CARDS_FILE,
            deck_name=config["deck_name"],
            ffmpeg_path=config["ffmpeg_path"],
            output_filepath=output_filepath
        )
        messagebox.showinfo("Succès!", "Deck généré avec succés. LETS FUCKING GO.")
    except Exception as e:
        messagebox.showerror("oh non",
                             f"erreur pendant la génération. very not good. \n\nErreur détaillée : {e}")
        # je prie que que ce message ne pop up jamais


def open_cards_txt():
    if not os.path.exists(CARDS_FILE):
        try:
            with open(CARDS_FILE, "w", encoding="utf-8") as f:
                f.write("#-------GUIDE DE SYNTAXE---------\n")
                f.write("# 1) Chaque ligne commencant par un hashtag sera ignorée par le script.\n")
                f.write("# 2) Chaque ligne *sans* hashtag représente une carte.\n")
                f.write("# 3) Pour ajouter une nouvelle carte, le format est simple:\n")
                f.write("#Question >> Réponse (les doubles fléches séparent la question de la réponse)\n")
                f.write("#Pour ajouter de l'audio:\n")
                f.write("#Déjà s'assurer que le fichier est bien présent dans le dossier sounds\n")
                f.write("# Si oui, simplement rajouter \"nomdufichier.mp3\" là ou tu veux ton son.\n")
                f.write("#-------------------------------\n")
                f.write("\n")
                f.write("2+2? >> 4\n")
                f.write("Le chiffre quatre se prononce: >> \"four.wav\"\n")
                f.write("wat dat sound: \"meow.mp3\"  >>  the gato.\n")
        except Exception as e:
            messagebox.showerror("oopsie",
                                 f"impossible de créer '{CARDS_FILE}'. \n\n"
                                 f"Vérifie que le dossier n'est pas en lecture seule?\nErreur : {e}")
            return
    os.startfile(CARDS_FILE)


def open_output_folder():
    config = load_config()
    if config:
        # Extraire chemin complet APKG
        folder = os.path.dirname(config.get("output_filepath", ""))
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("oopsie: dossier introuvable",
                                   "Le dossier de sortie n'existe pas ou n'a pas été configuré. Setup encore ?")
    else:
        messagebox.showerror("oopsie", "fichier de config manquant, faut faire le setup d'abord.")


def update_generate_button_state():
    if os.path.exists(CONFIG_FILE):
        config = load_config()
        # check clés pour générer les cartes
        if config and \
                config.get("deck_name") and \
                config.get("ffmpeg_path") and \
                config.get("output_filepath"):  # chemin custom
            btn_generate.config(state="normal")
            btn_open_output.config(state="normal")
            return
    btn_generate.config(state="disabled")
    btn_open_output.config(state="disabled")


# GUI principale (root)
root = tk.Tk()
root.title("Anki Deck Generator: Slightly Less Scuffed")
root.geometry("600x400")
root.resizable(True, True)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

tk.Label(frame, text="-Anki Deck Generator- FOR PRO HACKERS ONLY", font=("Arial", 14, "bold")).pack(pady=10)

btn_setup = tk.Button(frame, text="1. Setup (configure tout, A FAIRE EN PREMIER)", width=60, command=run_setup)
btn_setup.pack(pady=5)

btn_edit_cards = tk.Button(frame, text="2. Ouvrir cards.txt (pour éditer les cartes)", width=60, command=open_cards_txt)
btn_edit_cards.pack(pady=5)

btn_generate = tk.Button(frame, text="3. Générer/Mettre à jour le deck", width=60, command=run_generator)
btn_generate.pack(pady=5)

btn_open_output = tk.Button(frame, text="Ouvrir le Dossier de Sortie (pour trouver le fichier deck)", width=60,
                            command=open_output_folder)
btn_open_output.pack(pady=5)

btn_shortcut = tk.Button(frame, text="Créer un raccourci sur le Bureau", width=30, command=create_desktop_shortcut)
btn_shortcut.pack(pady=10)

update_generate_button_state()
root.mainloop()
