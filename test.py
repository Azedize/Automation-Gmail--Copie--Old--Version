# -*- coding: utf-8 -*-
"""
index_fixed.py
Version corrigée et optimisée du script fourni par l'utilisateur.
Principales corrections / améliorations :
- Import explicite de Application et Desktop depuis pywinauto (évite NameError)
- Flag DEBUG pour ne pas masquer la console pendant le débogage
- Gestion robuste des installations de dépendances
- Vérifications avant d'utiliser des objets (Application, Desktop, etc.)
- Meilleure journalisation (prints) et gestion des exceptions
- Protection des appels pyautogui (failsafe) et délais configurables
- Nettoyage dans finally sans lever d'erreurs si `app` non défini

Remarque:
- Vérifiez les chemins constants en haut du fichier selon votre machine.
- Activez DEBUG=True pendant le développement pour garder la console visible.
"""

import os
import sys
import time
import json
import shutil
import zipfile
import tempfile
import subprocess
import stat
import io
import traceback
import importlib
from pathlib import Path
from typing import Union , List, Optional
from pathlib import Path


# ---- Configuration ----
DEBUG = False  # True -> ne pas masquer la console, afficher plus de logs
HIDE_CONSOLE_AFTER = not DEBUG

# Chemins / URLs (à adapter si besoin)
SCRIPT_DIR = Path(__file__).resolve().parent
EXT_BASE = Path(r"C:\RepProxy")
EXT1 = EXT_BASE / "Ext1"
EXT2 = EXT_BASE / "Ext2"
EXT3 = EXT_BASE / "Ext3"

MANIFEST_EX1 = EXT1 / "manifest.json"
VER_EX1 = EXT1 / "version.txt"
MANIFEST_EX2 = EXT2 / "manifest.json"
VER_EX2 = EXT2 / "version.txt"
MANIFEST_EX3 = EXT3 / "manifest.json"
VER_EX3 = EXT3 / "version.txt"

CONFIG_PROFILE = r"C:\Profile 3"
PROFILE_NAME = "Profile 3"
PORT = 8082
MITM_CA_FOLDER = r"C:\mitm_ca"
INSTALL_DIR = r"C:\mitmproxy"

# URLs (conserver les vôtres)
CHECK_URL_EX1 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=check&type=V4&ext=Ext1&k=..."
CHECK_URL_EX2 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=check&type=V4&ext=Ext2&k=..."
CHECK_URL_EX3 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=check&type=V4&ext=Ext3&k=..."

SERVEUR_ZIP_URL_EX1 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=download&type=V4&ext=Ext1&k=..."
SERVEUR_ZIP_URL_EX2 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=download&type=V4&ext=Ext2&k=..."
SERVEUR_ZIP_URL_EX3 = "https://reporting.nrb-apps.com/APP_R/redirect.php?nv=1&rv4=1&event=download&type=V4&ext=Ext3&k=..."

MITM_URL = "https://downloads.mitmproxy.org/11.1.3/mitmproxy-11.1.3-windows-x86_64.zip"

# Dépendances à vérifier/installer
DEPENDENCIES = [
    "pyautogui",
    "pyperclip",
    "requests",
    "urllib3",
    "pillow",
    "pyopenssl",
    "opencv-python",
    "mss",
    "pywinauto",
    "win32api",
    "psutil",
]

# Map pour importer correctement
SPECIAL_MODULES = {
    "pillow": "PIL",
    "pyopenssl": "OpenSSL",
    "opencv-python": "cv2",
}

# ---- Utilitaires d'installation et import dynamique ----

def install_and_import(package, version=None, required_import=None):
    """Installe via pip si nécessaire puis importe le module.
    Retourne le module importé ou None.
    """
    pkg_name = package
    module_name = SPECIAL_MODULES.get(package.lower(), package)
    install_target = f"{pkg_name}=={version}" if version else pkg_name

    try:
        module = importlib.import_module(module_name)
        # si on veut importer sous-module
        if required_import:
            importlib.import_module(f"{module_name}.{required_import}")
        if DEBUG:
            print(f"[OK] import {module_name}")
        return module
    except Exception:
        print(f"[INFO] {module_name} non présent. Tentative d'installation : {install_target}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", install_target])
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] echec pip install {install_target}: {e}")
            return None

        try:
            module = importlib.import_module(module_name)
            if required_import:
                importlib.import_module(f"{module_name}.{required_import}")
            print(f"[OK] {module_name} installé et importé")
            return module
        except Exception as e:
            print(f"[ERROR] impossible d'importer {module_name} après installation: {e}")
            traceback.print_exc()
            return None


# Installer toutes les dépendances essentielles (silencieux si déjà présentes)
for pkg in DEPENDENCIES:
    # on n'écrase pas pywin32 ici, utiliser default
    mod = install_and_import(pkg)
    if mod is None:
        print(f"❌ Échec de l'installation ou de l'import de: {pkg}. Le script peut ne pas fonctionner correctement.")

# Imports sûrs après installation
try:
    import pyautogui
    import pyperclip
    import requests
    import urllib3
    import psutil
    # si opencv etc. existent, import ci-dessous (peut échouer si non installés)
    try:
        import cv2
    except Exception:
        cv2 = None

except Exception as e:
    print("[ERROR] Import de modules critiques échoué:", e)
    traceback.print_exc()
    # On continue, mais beaucoup de fonctionnalités dépendront de ces modules

# Put pyautogui en mode failsafe
try:
    pyautogui.FAILSAFE = True
except Exception:
    pass

# Importer pywinauto helpers explicitement
Application = None
Desktop = None
try:
    from pywinauto.application import Application
    from pywinauto import Desktop
except Exception as e:
    print(f"[WARN] Impossible d'importer Application/Desktop depuis pywinauto: {e}")
    Application = None
    Desktop = None

# Désactiver warnings SSL d'urllib3 si requests/urllib3 présents
try:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

# ---- Fonctions utilitaires ----

def hide_console(show_message=True):
    """Masque la fenêtre console sous Windows si possible.
    Utiliser uniquement quand DEBUG=False.
    """
    if not os.name == 'nt':
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            if show_message:
                print("🪄 La fenêtre de la console va être masquée dans un instant...")
                time.sleep(0.7)
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception as e:
        print(f"[WARN] hide_console échoué: {e}")


def download_file(url, dest_path, timeout=30):
    try:
        print(f"⬇️ Téléchargement depuis : {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        with requests.get(url, headers=headers, stream=True, verify=False, timeout=timeout) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0) or 0)
            with open(dest_path, 'wb') as f:
                dl = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        if total:
                            print(f"   → {dl/total*100:.1f}%", end='\r')
        print(f"\n✅ Téléchargement terminé: {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] download_file: {e}")
        return False


def update_from_zip_to_folder(folder: Path, zip_source_path: Union[str, Path]):
    """Décompresse un zip puis remplace le dossier cible par le contenu.
    zip_source_path peut être chemin local ou zip téléchargé.
    """
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            zip_path = Path(zip_source_path)
            print(f"📂 Extraction du ZIP {zip_path} dans {tmp}")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmp)

            # trouver le sous-dossier extrait (premier dossier)
            extracted = None
            for p in tmp.iterdir():
                if p.is_dir():
                    extracted = p
                    break
            if extracted is None:
                print("[ERROR] Aucun dossier extrait trouvé dans le ZIP")
                return False

            # supprimer l'existant puis déplacer
            if folder.exists():
                shutil.rmtree(folder, onerror=lambda f, p, e: os.chmod(p, stat.S_IWRITE) or os.remove(p))
            shutil.move(str(extracted), str(folder))
            print(f"✅ Mise à jour effectuée -> {folder}")
            return True
    except Exception as e:
        print(f"[ERROR] update_from_zip_to_folder: {e}")
        traceback.print_exc()
        return False


def check_version_generic(dropbox_url, manifest_path, version_txt, retries=3, delay=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    attempt = 0
    while attempt < retries:
        try:
            print(f"\n🔎 Tentative de connexion au serveur ({attempt+1}/{retries}) ...")
            r = requests.get(dropbox_url, headers=headers, verify=False, timeout=15)
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            print(f"[WARN] tentative {attempt+1} échouée: {e}")
            attempt += 1
            time.sleep(delay)
            if attempt >= retries:
                print("[ERROR] Échec des tentatives de connexion au serveur.")
                return None
    # validation du JSON
    remote_version = data.get('version_Extention')
    remote_manifest = data.get('manifest_version')
    print(f"🌍 Version distante : {remote_version} / manifest {remote_manifest}")

    if not manifest_path.exists() or not version_txt.exists():
        print("[INFO] fichiers locaux introuvables -> update requis")
        return True

    try:
        local_manifest = json.loads(manifest_path.read_text(encoding='utf-8')).get('version')
    except Exception:
        local_manifest = None
    local_version = version_txt.read_text(encoding='utf-8').strip()
    print(f"📄 Version locale : {local_version} / manifest {local_manifest}")

    if str(local_version) != str(remote_version) or str(local_manifest) != str(remote_manifest):
        return True
    return False


# --- Fonctions d'interaction UI (pywinauto / pyautogui) ---

def handle_open_folder_dialog(path: str, timeout=12):
    """Tente d'abord avec pywinauto Desktop, sinon bascule sur pyautogui+clipboard.
    Retourne True si réussi.
    """
    print(f"⌨️ En attente de la boîte de dialogue pour : {path}")
    if Desktop is None:
        print("[WARN] pywinauto Desktop non disponible -> fallback pyautogui")
        try:
            pyperclip.copy(path)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            return True
        except Exception as e:
            print(f"[ERROR] fallback pyautogui failed: {e}")
            return False

    desktop = Desktop(backend='uia')
    dialog = None
    start = time.time()
    while time.time() - start < timeout:
        try:
            for w in desktop.windows():
                try:
                    if w.friendly_class_name() == '#32770' and w.is_visible():
                        dialog = w
                        break
                except Exception:
                    continue
            if dialog:
                break
        except Exception:
            pass
        time.sleep(0.3)

    if not dialog:
        print("[INFO] dialog not found -> fallback pyautogui")
        try:
            pyperclip.copy(path)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            return True
        except Exception as e:
            print(f"[ERROR] fallback pyautogui failed: {e}")
            return False

    try:
        print("✅ Fenêtre de dialogue trouvée — saisie du chemin...")
        dialog.set_focus()
        try:
            edit = dialog.child_window(control_type='Edit')
            edit.set_focus()
            edit.type_keys(path + '{ENTER}', pause=0.02, with_spaces=True)
        except Exception:
            dialog.type_keys(path + '{ENTER}', pause=0.02, with_spaces=True)
        time.sleep(0.8)
        return True
    except Exception as e:
        print(f"[ERROR] failed to type path in dialog: {e}")
        return False


def load_multiple_unpacked_extensions(extension_paths: List[str], delays=(1.5, 0.7, 0.3, 2.5)):
    """Charge plusieurs extensions non empaquetées via l'UI (assume chrome://extensions ouvert et 'Load unpacked' activé)
    delays: tuple -> (after_enter, after_copy, after_tab, after_confirm)
    """
    after_enter, after_copy, after_tab, after_confirm = delays
    for idx, p in enumerate(extension_paths, start=1):
        print(f"\n🔸 Chargement {idx}/{len(extension_paths)} : {p}")
        try:
            # appuie ENTER pour ouvrir le dialogue Load unpacked (déjà sur le bouton attendu)
            pyautogui.press('enter')
            time.sleep(after_enter)
            pyperclip.copy(p)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(after_copy)
            pyautogui.press('tab')
            time.sleep(after_tab)
            pyautogui.press('enter')
            time.sleep(after_confirm)
            print(f"✅ Extension {idx} chargée")
        except Exception as e:
            print(f"[ERROR] load extension {p}: {e}")


def free_port(port: int):
    print(f"\n🔍 Recherche de processus utilisant le port {port}...")
    try:
        killed = False
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.laddr.port == port:
                pid = conn.pid
                if pid:
                    p = psutil.Process(pid)
                    print(f"💀 Arrêt du processus PID={pid}...")
                    p.terminate()
                    p.wait(timeout=3)
                    killed = True
        if not killed:
            print(f"ℹ️ Aucun processus n'utilise le port {port}.")
    except Exception as e:
        print(f"[WARN] free_port error: {e}")


def install_mitmproxy():
    exe = Path(INSTALL_DIR) / 'mitmdump.exe'
    if exe.exists():
        print(f"✅ mitmproxy déjà installé: {exe}")
        return str(exe)
    try:
        os.makedirs(INSTALL_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / 'mitm.zip'
            if not download_file(MITM_URL, zip_path):
                return None
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(INSTALL_DIR)
        if exe.exists():
            return str(exe)
        print("[ERROR] mitmdump non trouvé après extraction")
        return None
    except Exception as e:
        print(f"[ERROR] install_mitmproxy: {e}")
        return None


# ---- Processus d'extensions (générique) ----

def process_extension(name, folder: Path, dropbox_url, manifest_path: Path, version_file: Path, github_zip_url, zip_name, icon):
    print(f"\n=== Lancement mise à jour {name} ===")
    if folder.exists():
        needs_update = check_version_generic(dropbox_url, manifest_path, version_file)
        if needs_update:
            print(f"[INFO] mise à jour nécessaire pour {name}")
            # télécharger zip dans tmp
            with tempfile.TemporaryDirectory() as tmp:
                zpath = Path(tmp) / zip_name
                if download_file(github_zip_url, zpath):
                    update_from_zip_to_folder(folder, zpath)
        else:
            print(f"✅ {name} à jour")
    else:
        print(f"[INFO] {name} absent localement, création du dossier et installation")
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            zpath = Path(tmp) / zip_name
            if download_file(github_zip_url, zpath):
                update_from_zip_to_folder(folder, zpath)


# ---- Main ----

def main():
    app = None
    try:
        if HIDE_CONSOLE_AFTER:
            hide_console(show_message=not DEBUG)

        # étapes de mise à jour des extensions
        process_extension('EXTENTION_PROXY', EXT1, CHECK_URL_EX1, MANIFEST_EX1, VER_EX1, SERVEUR_ZIP_URL_EX1, 'EX1.zip', '🛡️')
        process_extension('EXTENTION_LOG', EXT2, CHECK_URL_EX2, MANIFEST_EX2, VER_EX2, SERVEUR_ZIP_URL_EX2, 'EX2.zip', '🛡️')
        process_extension('EXTENTION_REP', EXT3, CHECK_URL_EX3, MANIFEST_EX3, VER_EX3, SERVEUR_ZIP_URL_EX3, 'EX3.zip', '🛡️')

        time.sleep(1)
        print("\n=== DÉMARRAGE DU SCRIPT DE CONTRÔLE DE CHROME ===")

        # récupérer chrome depuis le registre (fonction minimale)
        chrome_path = None
        try:
            import winreg as reg
            key_app_paths = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe"
            for hive, access in ((reg.HKEY_LOCAL_MACHINE, reg.KEY_READ | reg.KEY_WOW64_32KEY), (reg.HKEY_LOCAL_MACHINE, reg.KEY_READ | reg.KEY_WOW64_64KEY), (reg.HKEY_CURRENT_USER, reg.KEY_READ)):
                try:
                    with reg.OpenKey(hive, key_app_paths, 0, access) as k:
                        chrome_path = reg.QueryValueEx(k, None)[0]
                        break
                except Exception:
                    continue
        except Exception as e:
            print(f"[WARN] lecture registre chrome échouée: {e}")

        if not chrome_path or not Path(chrome_path).exists():
            raise FileNotFoundError("Google Chrome introuvable sur le système.")

        chrome_args = [f'--user-data-dir="{CONFIG_PROFILE}"', f'--profile-directory="{PROFILE_NAME}"', '--no-first-run', '--lang=fr-FR', '--start-maximized']
        cmd = f'"{chrome_path}" {" ".join(chrome_args)}'

        if Application is None:
            print('[ERROR] pywinauto Application non disponible. Abandon.')
            return

        print('[INFO] Lancement de Chrome via pywinauto...')
        app = Application(backend='uia').start(cmd)
        # attendre fenêtre
        main_window = app.window(title_re='.*Chrome.*')
        main_window.wait('ready', timeout=25)
        time.sleep(1)

        # ouvrir onglet extensions
        main_window.type_keys('^t')
        time.sleep(0.5)
        main_window.type_keys('^l')
        time.sleep(0.2)
        main_window.type_keys('chrome://extensions/{ENTER}')
        time.sleep(2)

        # activer le mode développeur: tentative générale
        try:
            enable_developer_mode_via_keyboard(main_window)
        except Exception as e:
            print(f"[WARN] enable_developer_mode failed: {e}")

        # charger les extensions
        extensions_to_load = [str(EXT1), str(EXT2), str(EXT3)]
        load_multiple_unpacked_extensions(extensions_to_load)
        print("=== ✅ Script terminé avec succès ===")

    except Exception as e:
        print("❌ Une erreur critique est survenue !")
        print(traceback.format_exc())
    finally:
        try:
            if app is not None:
                print("⏳ fermeture de l'application Chrome...")
                try:
                    app.kill()
                except Exception:
                    pass
        except Exception as e:
            print(f"[WARN] final cleanup error: {e}")

        # libérer port
        free_port(PORT)

        # installer mitmproxy si nécessaire
        mitm_path = install_mitmproxy()
        if mitm_path:
            Path(MITM_CA_FOLDER).mkdir(parents=True, exist_ok=True)
            bat_file = SCRIPT_DIR / 'run_mitmdump.bat'
            bat_file.write_text(f'@echo off\n"{mitm_path}" --set confdir={MITM_CA_FOLDER} --mode regular -p {PORT}\n', encoding='utf-8')
            print(f"📝 Fichier batch créé: {bat_file}")


# --- Fonctions UI supplémentaires ---

def enable_developer_mode_via_keyboard(main_window, retry=3):
    """Tentative d'activation du mode développeur via le controle UI.
    Doit recevoir un objet main_window valide (pywinauto window)
    """
    if main_window is None:
        print('[WARN] main_window is None')
        return False

    print('⌨️ Tentative d\'activation du mode développeur...')
    for attempt in range(1, retry+1):
        try:
            possibles = ["Mode développeur", "Developer mode", "Développeur", "Activer le mode développeur"]
            for name in possibles:
                try:
                    element = main_window.child_window(auto_id='devMode', control_type='Button')
                    element.wait('ready', timeout=3)
                    try:
                        state = element.get_toggle_state()
                    except Exception:
                        state = None
                    print(f"[INFO] état bouton = {state}")
                    if state == 1:
                        return True
                    element.set_focus()
                    element.click_input()
                    time.sleep(0.5)
                    try:
                        if element.get_toggle_state() == 1:
                            print('🎯 Mode développeur activé')
                            return True
                    except Exception:
                        pass
                except Exception:
                    continue
        except Exception as e:
            print(f"[WARN] tentative {attempt} failed: {e}")
        time.sleep(0.8)
    print('[WARN] impossible d\'activer le mode développeur')
    return False


# Point d'entrée
if __name__ == '__main__':
    main()
