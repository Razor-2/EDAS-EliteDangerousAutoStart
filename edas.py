import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
import json

# Funktion zum Ermitteln des Pfades für eingebettete Ressourcen
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Pfad zur Konfigurationsdatei
config_file = "config.json"

# GUI erstellen
root = tk.Tk()
root.title("Elite:Dangerous AutoStart")
root.minsize(600,360)
root.maxsize(600,360)
root.configure(bg='#001322')

# Fokus auf die GUI legen
root.focus_force()

# Hintergrund hinzufügen
bg_path = resource_path("edas_bg.png")
bg = tk.PhotoImage(file=bg_path)
logo_label = tk.Label(root, image=bg, bg='#001322')
logo_label.place(x=0, y=0, anchor="nw")

# Icon einfügen
icon_path = resource_path("edas.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# Listen für die Checkboxen (Commander und Programme)
cmdr_checkboxes = []
program_checkboxes = []

import os
import json

# Pfad zur Konfigurationsdatei
config_file = "config.json"

# Funktion zum Speichern der Konfiguration mit relativen Pfaden
def save_config():
    config_data = {
        "commanders": [
            [radiobutton.cget("text"), os.path.basename(file_path)] for radiobutton, file_path in cmdr_checkboxes
        ],
        "programs": [
            [checkbox.cget("text"), os.path.basename(file_path), var.get()] for checkbox, file_path, var in program_checkboxes
        ],
        "selected_cmdr": os.path.basename(selected_cmdr.get()) if selected_cmdr.get() else ""
    }
    try:
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
        print("Konfiguration gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")

# Funktion zum Laden der Konfiguration und Konvertieren zu absoluten Pfaden
def load_config():
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)

            # Basispfad des Programms
            base_dir = os.path.abspath(os.path.dirname(__file__))

            # Lade Commander und konvertiere Pfade
            for name, relative_path in config_data.get("commanders", []):
                abs_path = os.path.join(base_dir, relative_path)
                add_cmdr(abs_path, name)

            # Lade Programme und konvertiere Pfade
            for item in config_data.get("programs", []):
                if len(item) == 3:
                    name, relative_path, selected = item
                    abs_path = os.path.join(base_dir, relative_path)
                    var = tk.BooleanVar()
                    var.set(selected)
                    add_program(abs_path, name, var)

            # Setze den ausgewählten Commander, falls vorhanden
            selected_cmdr_value = config_data.get("selected_cmdr")
            if selected_cmdr_value:
                selected_cmdr.set(os.path.join(base_dir, selected_cmdr_value))

            print("Konfiguration geladen.")
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
    else:
        print("Keine Konfigurationsdatei gefunden.")


import winreg
import os
from tkinter import messagebox, simpledialog

# Funktion zum Ermitteln des Steam-Pfads aus der Registry
def get_steam_path():
    try:
        # Öffne den Registry-Schlüssel
        reg_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"steam\Shell\Open\Command")

        # Lese den Wert des Standardschlüssels
        steam_path, _ = winreg.QueryValueEx(reg_key, "")

        # Entferne zusätzliche Parameter ("--" und "%1"), die möglicherweise am Pfad hängen
        steam_path = steam_path.split(" -- ")[0].strip('"')

        # Schließe den Registry-Schlüssel
        winreg.CloseKey(reg_key)

        return steam_path
    except FileNotFoundError:
        messagebox.showerror("Fehler", "Steam-Pfad konnte nicht gefunden werden.")
        return None

# Funktion zum Erstellen einer .bat-Datei
def create_bat_file():
    # Setzt den Fokus auf das Hauptfenster, bevor simpledialog geöffnet wird
    root.focus_set()

    # Hole den Steam-Pfad
    steam_path = get_steam_path()
    if not steam_path:
        return  # Abbrechen, falls der Pfad nicht gefunden wurde

    # Frage nach Benutzername und Passwort
    username = simpledialog.askstring("Benutzername", "Bitte gib deinen Steam-Benutzernamen ein:", parent=root)
    if not username:
        return
    password = simpledialog.askstring("Passwort", "Bitte gib dein Steam-Passwort ein:", show="*", parent=root)
    if not password:
        return
    filename = simpledialog.askstring("Dateiname", "Wie soll die .bat Datei heißen? (ohne .bat):", parent=root)
    if not filename:
        return

    # Dateipfad für die .bat-Datei erstellen
    file_path = f"{filename}.bat"

    # Prüfe, ob die Datei existiert, und frage nach Überschreiben
    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("Überschreiben?",
                                        f"Die Datei '{filename}.bat' existiert bereits. Möchtest Du sie überschreiben?",
                                        parent=root)
        if not overwrite:
            return

    # Inhalt der .bat-Datei, dynamischer Steam-Pfad eingefügt
    bat_content = f"""@echo off
tasklist /FI "IMAGENAME eq steam.exe" | findstr /I steam.exe
if not errorlevel 1 (
    taskkill /F /IM steam.exe
    timeout /t 2 /nobreak
) else (
    echo Steam ist nicht gestartet, daher wird nichts beendet.
)
start "" "{steam_path}" -login {username} {password}
timeout /t 5 /nobreak
start "" steam://rungameid/359320
exit
    """

    # Schreibe die .bat-Datei
    with open(file_path, "w") as bat_file:
        bat_file.write(bat_content)

    # Erfolgsmeldung anzeigen
    messagebox.showinfo("Erfolg", f"Die .bat Datei wurde erfolgreich als '{filename}.bat' erstellt.", parent=root)

    # Automatisches Hinzufügen der erstellten Datei zur Commander-Liste
    add_cmdr(file_path, filename)  # Füge die Datei hinzu

# Frame für Commander-Radiobuttons
cmdr_frame = tk.Frame(root, bg='#001322')
cmdr_frame.place(x=40, y=55)

# Gemeinsame Variable für die Commander-Radiobuttons
selected_cmdr = tk.StringVar()

# Erstelle Frames für zwei Spalten im Commander-Bereich
cmdr_frame_col1 = tk.Frame(cmdr_frame, width=150, bg='#001322')
cmdr_frame_col2 = tk.Frame(cmdr_frame, width=150, bg='#001322')
cmdr_frame_col1.grid(row=0, column=0, padx=5, pady=5)
cmdr_frame_col2.grid(row=0, column=1, padx=5, pady=5)

# Funktion zum Aktualisieren von selected_cmdr und Speichern der Konfiguration
def on_select_cmdr():
    save_config()  # Speichere die Konfiguration, wenn ein Commander ausgewählt wird


# Funktion zum Hinzufügen eines Commander-Radiobuttons
def add_cmdr(file_path=None, name=None):
    global selected_cmdr
    if len(cmdr_checkboxes) < 4:
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("Batch Files", "*.bat")])
        if file_path:
            if not name:
                name = simpledialog.askstring("Commander Name eingeben", "Gib einen Namen für den Commander ein:")
                if not name:
                    name = os.path.basename(file_path)
            radiobutton = tk.Radiobutton(
                cmdr_frame_col1 if len(cmdr_checkboxes) % 2 == 0 else cmdr_frame_col2,
                text=name, variable=selected_cmdr, value=file_path,  # Aktualisiere selected_cmdr beim Auswählen
                command=on_select_cmdr,  # Ruft on_select_cmdr auf, wenn der Radiobutton ausgewählt wird
                bg='#001322', fg='white', selectcolor='#001322'
            )
            cmdr_checkboxes.append((radiobutton, file_path))
            radiobutton.pack(anchor="w", pady=5)
    else:
        messagebox.showwarning("Limit erreicht", "Es können nur 4 Commander hinzugefügt werden.")


# Frame für Programm-Checkboxen
program_frame = tk.Frame(root, bg='#001322')
program_frame.place(x=40, y=190)

# Erstelle Frames für zwei Spalten im Programm-Bereich
program_frame_col1 = tk.Frame(program_frame, width=150, bg='#001322')
program_frame_col2 = tk.Frame(program_frame, width=150, bg='#001322')
program_frame_col1.grid(row=0, column=0, padx=10, pady=5)
program_frame_col2.grid(row=0, column=1, padx=50, pady=5)

# Funktion zum Hinzufügen eines Programms
def add_program(file_path=None, name=None, var=None):
    if len(program_checkboxes) < 8:
        if not file_path:
            file_path = filedialog.askopenfilename()
        if file_path:
            if not name:
                name = simpledialog.askstring("Programm Name eingeben", "Gib einen Namen für das Programm ein:")
                if not name:
                    name = os.path.basename(file_path)
            if var is None:
                var = tk.BooleanVar()
            # Verwende trace_add, um die Konfiguration nur bei Statusänderungen zu speichern
            var.trace_add("write", lambda *args: save_config())
            checkbox = tk.Checkbutton(
                program_frame_col1 if len(program_checkboxes) % 2 == 0 else program_frame_col2,
                text=name, variable=var, bg='#001322', fg='white', selectcolor='#001322'
            )
            program_checkboxes.append((checkbox, file_path, var))
            checkbox.pack(anchor="w", pady=5)
    else:
        messagebox.showwarning("Limit erreicht", "Es können nur 8 Programme hinzugefügt werden.")

import subprocess
import os

# Funktion zum Starten ausgewählter Programme
def start_selected():
    # Verarbeitung der Commander-Radiobuttons
    for radiobutton, file_path in cmdr_checkboxes:
        if selected_cmdr.get() == file_path:  # Prüfe, ob dieser Commander ausgewählt ist
            if file_path.endswith(".bat"):
                subprocess.Popen(file_path, shell=True)
            else:
                os.startfile(file_path)

    # Verarbeitung der Programme-Checkboxen
    for checkbox, file_path, var in program_checkboxes:
        if var.get():  # Prüfe, ob das Programm ausgewählt ist
            if file_path.endswith(".bat"):
                subprocess.Popen(file_path, shell=True)
            else:
                os.startfile(file_path)


# Funktion zum Löschen einer Checkbox oder eines Radiobuttons
def delete_selected():
    name = simpledialog.askstring("Checkbox/Radiobutton löschen", "Geben den Namen der Checkbox oder des Radiobuttons ein:")
    if name:
        for i, (radiobutton, file_path) in enumerate(cmdr_checkboxes):
            if radiobutton.cget("text") == name:
                radiobutton.destroy()
                del cmdr_checkboxes[i]
                save_config()
                return
        for i, (checkbox, file_path, var) in enumerate(program_checkboxes):
            if checkbox.cget("text") == name:
                checkbox.destroy()
                del program_checkboxes[i]
                save_config()
                return
        messagebox.showinfo("Nicht gefunden", "Checkbox oder Radiobutton mit diesem Namen wurde nicht gefunden.")

# Funktion zum Umbenennen einer Checkbox oder eines Radiobuttons
def rename_checkbox():
    current_name = simpledialog.askstring("Umbenennen", "Gebe den aktuellen Namen der Checkbox oder des Radiobuttons ein:")
    if current_name:
        for radiobutton, file_path in cmdr_checkboxes:
            if radiobutton.cget("text") == current_name:
                new_name = simpledialog.askstring("Neuer Name", "Gebe den neuen Namen ein:")
                if new_name:
                    radiobutton.config(text=new_name)
                    save_config()
                return

        for checkbox, file_path, var in program_checkboxes:
            if checkbox.cget("text") == current_name:
                new_name = simpledialog.askstring("Neuer Name", "Gebe den neuen Namen ein:")
                if new_name:
                    checkbox.config(text=new_name)
                    save_config()
                return
        messagebox.showinfo("Nicht gefunden", "Checkbox oder Radiobutton mit diesem Namen wurde nicht gefunden.")

# Funktion zur Anzeige der Hilfe in einem anpassbaren Fenster
def show_Anleitung():
    # Erstelle ein neues Fenster für die Hilfeanzeige
    help_window = tk.Toplevel(root)
    help_window.title("Anleitung")
    help_window.geometry("500x600")  # Fenstergröße nach Bedarf anpassen
    help_window.configure(bg='#001322')  # Hintergrundfarbe

    # Icon einfügen
    icon_path = resource_path("edas.ico")
    if os.path.exists(icon_path):
        help_window.iconbitmap(icon_path)

    # Scrollbar hinzufügen, falls der Text länger ist als das Fenster
    text_widget = tk.Text(help_window, wrap="word", bg="#001322", borderwidth=0, fg="white", font=("Helvetica", 12))
    scrollbar = tk.Scrollbar(help_window, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    # Anleitungstext einfügen
    help_text = (
        "Anleitung zum EDAS (Elite Dangerous Autostart Programm)\n\n\n"
        "Überblick:\n\n"
        "EDAS ermöglicht es, mehrere Konfigurationen (Commander) für Elite Dangerous zu speichern und automatisch "
        "verschiedene Programme zusammen mit dem Spiel zu starten. Die Konfigurationen und Programme werden in"
        "sogenannten 'Batch-Dateien' (.bat) gespeichert und können individuell verwaltet werden.\n\n\n"
        "Programmstart:\n\n"
        "1. Starte das Programm durch Ausführen des Skripts.\n"
        "2. Die GUI öffnet sich in einem Fenster mit mehreren Bereichen und Menüpunkten oben.\n\n\n"
        "Menüoptionen:\n\n"
        "- Datei → Beenden: Schließt das Programm.\n"
        "- Datei → .bat-Datei erstellen: Erstellt eine .bat-Datei mit den Steam-Login-Daten für einen Commander"
        " und fügt den Commander in die Auswahl-Liste ein\n\n\n"
        "Commander-Batchdatei (.bat-Datei) erstellen:\n\n"
        "1. Wähle im Menü Datei → .bat-Datei erstellen.\n"
        "2. Gib deinen Steam-Benutzernamen und dein Passwort ein.\n"
        "3. Gib einen Namen für die .bat-Datei ein (z. B. Commander_1_login).\n"
        "4. Die erstellte .bat-Datei startet Steam mit deinen Login-Daten und anschließend das Spiel Elite Dangerous.\n"
        "ACHTUNG: Die .bat-Dateien speichern Steam-Anmeldedaten im Klartext. Stelle sicher, dass diese Dateien sicher\n"
        "aufbewahrt werden, insbesondere wenn das Programm auf gemeinsam genutzten Rechnern verwendet wird.\n\n\n"
        "Commander hinzufügen:\n\n"
        "1. Gehe zum Menü Bearbeiten → CMDR hinzufügen.\n"
        "2. Wähle eine Batch-Datei (.bat) aus, die dem Commander zugeordnet werden soll.\n"
        "3. Gib in dem Dialogfenster einen Namen für den Commander ein. Falls kein Name eingegeben wird, wird der Dateiname verwendet.\n"
        "4. Der Commander wird als Radiobutton in der Liste angezeigt. Beachte, dass maximal 4 Commander hinzugefügt werden können.\n"
        "5. Nur ein Commander kann gleichzeitig ausgewählt sein. Die Auswahl wird gespeichert.\n\n\n"
        "Programme hinzufügen:\n\n"
        "1. Gehe zum Menü Bearbeiten → Programm hinzufügen.\n"
        "2. Wähle die auszuführende Datei aus.\n"
        "3. Gib einen Namen für das Programm ein, oder verwende den Dateinamen, wenn kein Name eingegeben wird.\n"
        "4. Das Programm wird als Checkbox in der Liste angezeigt. Es können maximal 8 Programme hinzugefügt werden.\n"
        "5. Die Auswahl der Checkboxen wird automatisch gespeichert.\n\n\n"
        "Programme und Commander starten:\n\n"
        "1. Wähle den gewünschten Commander (Radiobutton) und die Programme (Checkboxen) aus, die gestartet werden sollen.\n"
        "2. Klicke auf den Button „Elite & Tools starten“. Das Programm führt die ausgewählten Dateien nacheinander aus.\n\n\n"
        "Einträge umbenennen:\n\n"
        "1. Gehe zum Menü Bearbeiten → Checkbox umbenennen.\n"
        "2. Gib den aktuellen Namen des Commanders oder Programms ein, das umbenannt werden soll (Case-sensitiv).\n"
        "3. Gib im nächsten Fenster den neuen Namen ein und bestätige. Der Eintrag wird sofort aktualisiert.\n\n\n"
        "Einträge löschen:\n\n"
        "1. Gehe zum Menü Bearbeiten → Checkbox löschen.\n"
        "2. Gib den Namen des Commanders oder Programms ein, das gelöscht werden soll (Case-sensitiv).\n"
        "3. Der Eintrag wird entfernt und kann bei Bedarf erneut hinzugefügt werden.\n\n\n"
        "Beenden:\n\n"
        "- Klicke auf Datei → Beenden oder den „Beenden“ Button, um das Programm zu beenden. Alle Änderungen werden automatisch gespeichert.\n"
    )

    # Text in das Text-Widget einfügen
    text_widget.insert("1.0", help_text)
    text_widget.configure(state="disabled")  # Setze das Text-Widget auf schreibgeschützt

    # Widgets positionieren
    text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10,)
    scrollbar.pack(side="right", fill="y")

# Menüleiste erstellen
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label=".bat-Datei erstellen", command=create_bat_file)
file_menu.add_command(label="Beenden", command=root.quit)
menu_bar.add_cascade(label="Datei", menu=file_menu)

edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="CMDR hinzufügen", command=add_cmdr)
edit_menu.add_command(label="Programm hinzufügen", command=add_program)
edit_menu.add_command(label="Checkbox umbenennen", command=rename_checkbox)
edit_menu.add_command(label="Checkbox löschen", command=delete_selected)
menu_bar.add_cascade(label="Bearbeiten", menu=edit_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Über EDAS", command=lambda: messagebox.showinfo("Über EDAS", "EDAS - Elite Dangerous Auto Start\nVersion 1.0"))
help_menu.add_command(label="Anleitung", command=show_Anleitung)
menu_bar.add_cascade(label="Hilfe", menu=help_menu)

# Menüleiste zum Hauptfenster hinzufügen
root.config(menu=menu_bar)

# Menüleiste erstellen
menu_bar = tk.Menu(root)

# "Datei"-Menü
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label=".bat-Datei erstellen", command=create_bat_file)
file_menu.add_command(label="Beenden", command=root.quit)
menu_bar.add_cascade(label="Datei", menu=file_menu)

# "Bearbeiten"-Menü
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="CMDR hinzufügen", command=add_cmdr)
edit_menu.add_command(label="Programm hinzufügen", command=add_program)
edit_menu.add_command(label="Checkbox umbenennen", command=rename_checkbox)
edit_menu.add_command(label="Checkbox löschen", command=delete_selected)
menu_bar.add_cascade(label="Bearbeiten", menu=edit_menu)

# "Hilfe"-Menü
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Über EDAS", command=lambda: messagebox.showinfo("Über EDAS", "EDAS - Elite Dangerous Auto Start\nVersion 1.0.1\n(C) 2024 Razor 2"))
help_menu.add_command(label="Anleitung", command=show_Anleitung)
menu_bar.add_cascade(label="Hilfe", menu=help_menu)

# Menüleiste zum Hauptfenster hinzufügen
root.config(menu=menu_bar)

# Copyright-Info Label
copyright_label = tk.Label(root, text="© 2024 by Razor 2", bg="#001322", fg="white", font=("Arial", 7))
copyright_label.place(x=483, y=190, anchor="center")  # Setze die x- und y-Koordinaten nach Bedarf

# "Programme starten"-Button
start_button = tk.Button(root, text=" Elite & Tools starten ", command=start_selected, bg="#f07b05", activebackground="lightgrey")
start_button.place(x=483, y=250, anchor="center")  # Setze hier die gewünschten x- und y-Koordinaten

# "Programme beenden"-Button
quit_button = tk.Button(root, text=" Beenden ", command=root.quit, bg="lightgrey", activebackground="#f07b05")
quit_button.place(x=483, y=300, anchor="center")  # Setze hier die gewünschten x- und y-Koordinaten

# Konfiguration laden beim Start
load_config()

# Haupt-Loop der GUI
root.mainloop()
