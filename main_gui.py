import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog  # Ajout de simpledialog pour l'input
import json
import os

# ancienne deck gen logique dans un script séparé
import DeckGenerator  # On importe toujours le module

CONFIG_FILE = "config.json"
CARDS_FILE = "cards.txt"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Erreur de Fichier",
                                 f"Le fichier de config '{CONFIG_FILE}' est corrompu. Relancer la configuration.")
            os.remove(CONFIG_FILE)  # Supprime le fichier corrompu
    return None


def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


# Utilisation de simpledialog pour l'input simple
def run_setup():
    config = {}

    # Deck name
    deck_name = simpledialog.askstring("Nom du Deck", "Comment voulez-vous appeler votre deck Anki ?", parent=root)
    if not deck_name:
        messagebox.showwarning("Annulé", "Le nom du deck est requis. Opération annulée.")
        return

    # FFMPEG path
    ffmpeg_path = filedialog.askopenfilename(title="Sélectionner ffmpeg.exe (laissez vide si déjà dans le PATH)",
                                             filetypes=[("Executable", "*.exe")], parent=root)
    # L'utilisateur peut ne rien selectionner, on le laisse vide si c'est le cas
    if not ffmpeg_path:
        ffmpeg_path = "ffmpeg"  # Valeur par defaut pour chercher dans le PATH

    # Output location (seulement le dossier pour le apkg, pas le nom du fichier)
    output_dir = filedialog.askdirectory(title="Où voulez-vous exporter le fichier .apkg ?", parent=root)
    if not output_dir:
        messagebox.showwarning("Annulé", "Le dossier d'exportation est requis. Opération annulée.")
        return

    config["deck_name"] = deck_name
    config["ffmpeg_path"] = ffmpeg_path
    config["output_directory"] = output_dir  # Changé pour 'output_directory'

    save_config(config)
    messagebox.showinfo("Configuration Complète", "Configuration sauvegardée avec succès.")
    update_generate_button_state()


def run_generator():
    config = load_config()
    if not config:
        messagebox.showerror("Erreur", "Aucune configuration trouvée. Veuillez lancer le Setup d'abord.")
        return

    # Construire le chemin complet de l'APKG ici, comme il sera utilisé dans DeckGenerator
    output_filepath = os.path.join(config["output_directory"], "output.apkg")

    if not os.path.exists(CARDS_FILE):
        messagebox.showerror("Erreur", f"Le fichier de cartes '{CARDS_FILE}' n'a pas été trouvé.")
        return

    try:
        # On passe tous les parametres necessaires a la fonction generate_deck
        DeckGenerator.generate_deck(
            cards_file=CARDS_FILE,
            deck_name=config["deck_name"],
            ffmpeg_path=config["ffmpeg_path"],
            output_filepath=output_filepath  # Nouveau parametre
        )
        messagebox.showinfo("Succès", "Deck généré avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue lors de la génération du deck:\n\n{e}")
        # Log l'erreur pour le debug si besoin
        print(f"Erreur détaillée lors de la génération du deck: {e}")


def open_cards_txt():
    # S'assurer que le fichier cards.txt est créé s'il n'existe pas
    if not os.path.exists(CARDS_FILE):
        try:
            with open(CARDS_FILE, "w", encoding="utf-8") as f:
                f.write("# Voici comment ajouter tes cartes :\n")
                f.write("# Question >> Réponse\n")
                f.write("# Question \"nom_audio_q.mp3\" >> Réponse \"nom_audio_r.wav\"\n")
                f.write("# Place tes fichiers audio dans le dossier 'sounds' à côté de l'outil.\n")
                f.write("\n")
                f.write("# EXEMPLES :\n")
                f.write("Hello >> Bonjour\n")
                f.write("Bienvenue >> Welcome\n")
                f.write("Combien ça coûte ? \"how_much.mp3\" >> Ça coûte cher. \"too_much.mp3\"\n")
        except Exception as e:
            messagebox.showerror("Erreur de Fichier", f"Impossible de créer '{CARDS_FILE}':\n{e}")
            return
    os.startfile(CARDS_FILE)


def open_output_folder():
    config = load_config()
    if config:
        folder = config.get("output_directory")  # Utilisez .get pour une meilleure robustesse
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("Dossier introuvable", "Le dossier de sortie n'existe pas ou n'a pas été configuré.")
    else:
        messagebox.showerror("Erreur", "Aucune configuration trouvée. Veuillez lancer le Setup d'abord.")


def update_generate_button_state():
    if os.path.exists(CONFIG_FILE):
        config = load_config()
        # Assurez-vous que les clés essentielles sont présentes
        if config and "deck_name" in config and "output_directory" in config and "ffmpeg_path" in config:
            btn_generate.config(state="normal")
            btn_open_output.config(state="normal")
            return
    btn_generate.config(state="disabled")
    btn_open_output.config(state="disabled")


# gui
root = tk.Tk()
root.title("Anki Deck Generator")
root.geometry("300x250")  # Taille fixe pour une meilleure presentation
root.resizable(False, False)  # Empecher le redimensionnement

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

tk.Label(frame, text="Anki Deck Generator", font=("Arial", 14, "bold")).pack(pady=10)

btn_setup = tk.Button(frame, text="1. Configurer l'Outil", width=25, command=run_setup)
btn_setup.pack(pady=5)

btn_edit_cards = tk.Button(frame, text="2. Editer cards.txt", width=25, command=open_cards_txt)
btn_edit_cards.pack(pady=5)

btn_generate = tk.Button(frame, text="3. Générer/Mettre à jour le Deck", width=25, command=run_generator)
btn_generate.pack(pady=5)

btn_open_output = tk.Button(frame, text="Ouvrir le Dossier de Sortie", width=25, command=open_output_folder)
btn_open_output.pack(pady=5)

update_generate_button_state()
root.mainloop()
