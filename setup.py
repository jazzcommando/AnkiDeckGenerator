import configparser
import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# CHEMIN DU CFG
CONFIG_FILE = 'config.ini'


def create_config_gui():
    def save_settings():
        deck_name = deck_name_entry.get().strip()
        output_dir = output_dir_entry.get().strip()
        ffmpeg_path = ffmpeg_path_entry.get().strip()

        if not deck_name:
            messagebox.showwarning("NO", "Le deck doit avoir un nom. Utilisation de 'Englando Deck' par défaut.")
            deck_name = "Englando Deck"

        if not output_dir:
            messagebox.showerror("NO",
                                 "Chemin d'exportation vide. Créer un nouveau dossier ou choisir un autre chemin.")
            return

        # dossier existe? si non, proposition d'en créer un
        if not os.path.isdir(output_dir):
            if messagebox.askyesno("Dossier inexistant. Bravo.",
                                   f"Le dossier '{output_dir}' n'existe pas. On en crée un ?"):
                try:
                    os.makedirs(output_dir)
                    messagebox.showinfo("Création de dossier", f"Dossier '{output_dir}' créé.")
                except OSError as e:
                    messagebox.showerror("ERREUR", f"Erreur lors de la création du dossier: {e}.")
                    return
            else:
                messagebox.showwarning("CANCELLD", "Création impossible. Essayer un autre chemin.")
                return

        config = configparser.ConfigParser()
        config['DECK_SETTINGS'] = {
            'deck_name': deck_name,
            'output_directory': output_dir
        }
        config['TOOL_PATHS'] = {
            'ffmpeg_executable': ffmpeg_path if ffmpeg_path else "ffmpeg"  # Utilise 'ffmpeg' si vide
        }

        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            messagebox.showinfo("HUGE SUCCESS", f"Fichier de config sauvegardé dans '{CONFIG_FILE}'.")
            if update_main_script():
                messagebox.showinfo("Installation terminée!",
                                    "L'installation est terminée !\n'Lancer DeckGenerator.exe!.")
                root.destroy()
            else:
                messagebox.showerror("Erreur :(",
                                     "La mise à jour du script principal a échoué. :( je sais pas pourquoi")
        except Exception as e:
            messagebox.showerror("Erreur de sauvegarde", f"wtf: {e}")

    def browse_output_dir():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            output_dir_entry.delete(0, tk.END)
            output_dir_entry.insert(0, folder_selected)

    def browse_ffmpeg_path():
        file_selected = filedialog.askopenfilename(title="Sélectionner ffmpeg.exe",
                                                   filetypes=[("Executables", "*.exe")])
        if file_selected:
            ffmpeg_path_entry.delete(0, tk.END)
            ffmpeg_path_entry.insert(0, file_selected)

    root = tk.Tk()
    root.title("Configuration du Générateur de Deck Anki")
    root.geometry("680x200")
    root.resizable(False, False)  # Empêche le redimensionnement

    # Cadre principal pour le padding
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Nom du Deck
    tk.Label(main_frame, text="Nom du Deck:").grid(row=0, column=0, sticky="w", pady=5)
    deck_name_entry = tk.Entry(main_frame, width=50)
    deck_name_entry.grid(row=0, column=1, pady=5)
    deck_name_entry.insert(0, "Englando Deck")  # Valeur par défaut

    # Dossier d'exportation
    tk.Label(main_frame, text="Dossier d'exportation du deck (fichier .apkg):").grid(row=1, column=0, sticky="w", pady=5)
    output_dir_entry = tk.Entry(main_frame, width=50)
    output_dir_entry.grid(row=1, column=1, pady=5)
    tk.Button(main_frame, text="Parcourir...", command=browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
    output_dir_entry.insert(0, os.path.join(os.path.expanduser("~"), "Documents",
                                            "AnkiDecks"))  # Chemin par défaut Documents/AnkiDecks

    # Chemin FFMPEG
    tk.Label(main_frame, text="Chemin de ffmpeg.exe (optionnel):").grid(row=2, column=0, sticky="w", pady=5)
    ffmpeg_path_entry = tk.Entry(main_frame, width=50)
    ffmpeg_path_entry.grid(row=2, column=1, pady=5)
    tk.Button(main_frame, text="Parcourir...", command=browse_ffmpeg_path).grid(row=2, column=2, padx=5, pady=5)
    ffmpeg_path_entry.insert(0, "ffmpeg")  # Valeur par défaut

    # Bouton Sauvegarder
    save_button = tk.Button(main_frame, text="Sauvegarder et Configurer", command=save_settings)
    save_button.grid(row=3, column=0, columnspan=3, pady=20)

    root.mainloop()


def update_main_script():
    """Met à jour le script DeckGenerator.py pour lire les paramètres du fichier config.ini."""
    # Le script setup.py doit être dans le même dossier que DeckGenerator.py pour cette logique
    main_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DeckGenerator.py')

    if not os.path.exists(main_script_path):
        messagebox.showerror("Erreur de Fichier",
                             f"Le script principal '{main_script_path}' n'a pas été trouvé. Placez 'setup.py' dans le "
                             f"même dossier.")
        return False

    try:
        with open(main_script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        config_import_added = False
        ffmpeg_path_updated = False
        model_deck_name_updated = False
        output_path_updated = False

        for i, line in enumerate(lines):
            # Ajout de l'import de configparser et du chemin du fichier config
            if not config_import_added and "import genanki" in line:
                updated_lines.append("import configparser\n")
                updated_lines.append("CONFIG_FILE = 'config.ini'\n")
                updated_lines.append("config = configparser.ConfigParser()\n")
                updated_lines.append("try:\n")
                updated_lines.append("    config.read(CONFIG_FILE, encoding='utf-8')\n")
                updated_lines.append("except Exception as e:\n")
                updated_lines.append("    # Plutôt qu'un exit brutal, on log l'erreur et on utilise des fallbacks\n")
                updated_lines.append(
                    "    print(f\"[DECKGEN] Erreur lecture config: {e}. Utilisation des valeurs par défaut.\")\n")
                updated_lines.append("    config.add_section('DECK_SETTINGS')\n")
                updated_lines.append("    config.add_section('TOOL_PATHS')\n")
                updated_lines.append("\n")  # Ligne vide pour la lisibilité
                config_import_added = True
                updated_lines.append(line)  # Ajoute la ligne "import genanki" après les ajouts
                continue

            # Remplacement du chemin FFMPEG
            if "FFMPEG_PATH =" in line and not ffmpeg_path_updated:
                updated_lines.append("FFMPEG_PATH = config.get('TOOL_PATHS', 'ffmpeg_executable', fallback='ffmpeg')\n")
                ffmpeg_path_updated = True
                continue

            # Remplacement du nom du deck
            if "deck = genanki.Deck(" in line and not model_deck_name_updated:
                deck_id_match = re.search(r'genanki\.Deck\((\d+),', line)
                deck_id = deck_id_match.group(
                    1) if deck_id_match else "2059400110"  # Utilise l'ID existant ou un défaut
                updated_lines.append(
                    "deck_name_from_config = config.get('DECK_SETTINGS', 'deck_name', fallback='Englando Deck')\n")
                updated_lines.append(f"deck = genanki.Deck({deck_id}, deck_name_from_config)\n")
                model_deck_name_updated = True
                continue

            # Remplacement du chemin d'exportation
            if "genanki.Package(deck, media_files).write_to_file(" in line and not output_path_updated:
                updated_lines.append(
                    "output_dir_from_config = config.get('DECK_SETTINGS', 'output_directory', "
                    "fallback=os.path.dirname(os.path.abspath(__file__)))\n")
                updated_lines.append("output_filepath = os.path.join(output_dir_from_config, 'output.apkg')\n")
                updated_lines.append("genanki.Package(deck, media_files).write_to_file(output_filepath)\n")
                updated_lines.append(
                    "print(f\"\\n🎉 Deck créé avec succès : '{output_filepath}'\")\n")  # Met à jour le print final
                output_path_updated = True
                continue

            updated_lines.append(line)

        with open(main_script_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        return True
    except Exception as e:
        messagebox.showerror("Erreur de Mise à Jour", f"Échec de la mise à jour de DeckGenerator.py: {e}")
        return False


if __name__ == "__main__":
    create_config_gui()
