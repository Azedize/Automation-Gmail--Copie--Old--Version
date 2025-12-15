import os
import sys
import shutil
import zipfile
import traceback
from pathlib import Path
import importlib
import time
import io
import base64
import requests
import subprocess
import json
from datetime import datetime, timedelta
from base64 import b64encode, b64decode



SCRIPT_DIR           = Path(__file__).resolve().parent
PARENT_DIR           = os.path.dirname(SCRIPT_DIR)
DIRECTERY_VERSIONS   = os.path.join(SCRIPT_DIR, "Programme-main")


CHECK_URL_PROGRAMM       = "https://www.dropbox.com/scl/fi/78a38bc4papwzlw80hxti/version.json?rlkey=n7dx5mb8tcctvprn0wq4ojw7m&st=z6vzw0ox&dl=1"
SERVEUR_ZIP_URL_PROGRAMM = "https://github.com/Azedize/Programme/archive/refs/heads/main.zip"

# change to url from server 



# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')



# =========================================
# HEADER
# =========================================
HEADERS =   {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'}





# Flags for pip handling
updated_pip_23_3      = False
all_packages_installed = True  










def install_and_import(package, module_name=None, required_import=None, version=None):
    global updated_pip_23_3, all_packages_installed
    module = None
    module_to_import = module_name or package
    install_package = f"{package}=={version}" if version else package

    try:
        module = importlib.import_module(module_to_import)
        if required_import:
            importlib.import_module(f"{module_to_import}.{required_import}")
        # print(f"✅ {package} est déjà installé (version: {getattr(module,'__version__','inconnue')})")
    except (ModuleNotFoundError, ImportError):
        all_packages_installed = False
        print(f"⚠️ {package} n'est pas installé. Installation en cours...")

        # Mise à jour de pip si nécessaire
        if not updated_pip_23_3:
            try:
                print("⬆️ Mise à jour de pip vers la version 23.3 ...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip==23.3"])
                updated_pip_23_3 = True
            except subprocess.CalledProcessError:
                sys.exit("❌ Erreur lors de la mise à jour de pip")

        # Installation du package avec affichage
        try:
            print(f"📦 Installation du package : {install_package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", install_package])
            print(f"✅ {install_package} a été installé avec succès")
        except subprocess.CalledProcessError:
            sys.exit(f"❌ Erreur lors de l'installation de {install_package}")

        module = importlib.import_module(module_to_import)

    return module




# ⬇ Downgrade pip to 19.3.1 if needed (compatibility reasons)
def update_pip_to_19_3_1():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip==19.3.1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        sys.exit(1)




# 📦 Install all dependencies
urllib3 = install_and_import("urllib3" ,  version="2.2.3")
if urllib3:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PyQt6 = install_and_import("PyQt6", version="6.7.0", required_import="QtCore")
requests = install_and_import("requests" )
cryptography_module = install_and_import("cryptography", version="3.3.2")
psutil = install_and_import("psutil")


pytz = install_and_import("pytz" ) 

from cryptography.fernet import Fernet
import shutil


tqdm = install_and_import("tqdm")
from tqdm import tqdm

platformdirs = install_and_import("platformdirs")
from platformdirs import user_downloads_dir



selenium = install_and_import(
    package="selenium",
    module_name="selenium",
    required_import="webdriver",
    version="4.27.1"
)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# print("✅ Selenium version:", selenium.__version__)

# ✅ Ensure pip downgrade if packages had to be installed
if not all_packages_installed:
    update_pip_to_19_3_1()












def DownloadAndExtract(new_versions):
    try:
        if not isinstance(new_versions, dict):
            print("❌ [ERROR] Invalid new_versions (not a dict).")
            return -1

        path_DownloadFile =  os.path.abspath(SCRIPT_DIR)
        local_zip = os.path.join(path_DownloadFile, "Programme-main.zip")
        extracted_dir = os.path.join(path_DownloadFile, "Programme-main")

        print(f"🗂️ Download path: {path_DownloadFile}")
        print(f"📦 ZIP path: {local_zip}")
        print(f"📂 Extracted folder path: {extracted_dir}")

        need_interface = "version_interface" in new_versions
        need_python = "version_python" in new_versions

        if not need_interface and not need_python:
            print("✅ [INFO] No extension updates required.")
            return 0

        # إزالة ZIP القديم
        if os.path.exists(local_zip):
            print(f"🗑️ Removing old ZIP: {local_zip}")
            os.remove(local_zip)

        # إزالة مجلد الاستخراج القديم
        if os.path.exists(extracted_dir):
            print(f"🗑️ Removing old extracted folder: {extracted_dir}")
            shutil.rmtree(extracted_dir)

        # تحميل ZIP
        print("⬇️ Downloading update ZIP from GitHub...")

        resp = requests.get(SERVEUR_ZIP_URL_PROGRAMM, stream=True, headers=HEADERS, timeout=60)
        print(f"📡 HTTP status code: {resp.status_code}")
        if resp.status_code != 200:
            print(f"❌ [ERROR] Failed to download ZIP: HTTP {resp.status_code}")
            return -1

        total_size = int(resp.headers.get('content-length', 0))
        print(f"📏 ZIP size: {total_size / 1024:.2f} KB")

        with open(local_zip, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
            print(f"✅ Downloaded {downloaded / 1024:.2f} KB")

        # التأكد من أن ZIP موجود وحجمه > 0
        if not os.path.exists(local_zip) or os.path.getsize(local_zip) == 0:
            print("❌ ZIP file not downloaded properly!")
            return -1

        # استخراج ZIP
        print("📂 Extracting ZIP file...")
        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            names = [n for n in zip_ref.namelist() if n.strip()]
            if not names:
                print("❌ [ERROR] ZIP is empty.")
                return -1

            top_folder = names[0].split('/')[0]
            print(f"🗃️ Top folder in ZIP: {top_folder}")

            zip_ref.extractall(path_DownloadFile)

        # إذا اسم المجلد الرئيسي في ZIP مختلف عن extracted_dir → إعادة تسمية
        extracted_top_dir = os.path.join(path_DownloadFile, top_folder)
        if extracted_top_dir != extracted_dir:
            if os.path.exists(extracted_dir):
                shutil.rmtree(extracted_dir)
            print(f"🔀 Renaming extracted folder {extracted_top_dir} → {extracted_dir}")
            os.rename(extracted_top_dir, extracted_dir)

        # إزالة ZIP بعد الاستخراج
        if os.path.exists(local_zip):
            print(f"🗑️ Removing downloaded ZIP file: {local_zip}")
            os.remove(local_zip)

        print("🎉 [SUCCESS] Download and update process completed.")
        return 0

    except Exception as e:
        traceback.print_exc()
        print(f"❌ [EXCEPTION] Unexpected error in DownloadAndExtract: {e}")
        return -1





# 🔍 Vérifie les versions distantes et locales des composants, puis signale les mises à jour nécessaires
def checkVersion():
    """
    Check remote and local versions of Python, interface, and extensions.
    Returns a dict with updates if available, "_1" on error, or None if up to date.
    Detailed logging with emojis.
    """
    
    try:
        print("🌐 Checking latest versions from server...")
        response = requests.get(CHECK_URL_PROGRAMM, timeout=15)
        if response.status_code != 200:
            print(f"❌ [ERROR] Failed to fetch versions: HTTP {response.status_code}")
            return "_1"

        data = response.json()
        version_updates = {}

        # Server versions
        server_version_python = data.get("version_python")
        server_version_interface = data.get("version_interface")

        if not all([server_version_python, server_version_interface]):
            print("❌ [ERROR] Missing version information on server.")
            return "_1"

        # Local versions files
        client_files = {
            "version_python": os.path.join(SCRIPT_DIR,"Programme-main", "Python", "version.txt"),
            "version_interface": os.path.join(SCRIPT_DIR,"Programme-main", "interface", "version.txt")
        }

        client_versions = {}
        for key, path in client_files.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    client_versions[key] = f.read().strip()
                print(f"📄 {key}: Local version = {client_versions[key]}")
            else:
                client_versions[key] = None
                print(f"⚠️ {key}: Local version file not found → update required.")
                # 🔹 Si le fichier est manquant, on force la mise à jour
                if key == "version_python":
                    version_updates[key] = server_version_python
                elif key == "version_interface":
                    version_updates[key] = server_version_interface

        # Compare versions si fichier existe
        if client_versions["version_python"] and server_version_python != client_versions["version_python"]:
            version_updates["version_python"] = server_version_python
            print(f"⬆️ Python update available: {server_version_python}")

        if client_versions["version_interface"] and server_version_interface != client_versions["version_interface"]:
            version_updates["version_interface"] = server_version_interface
            print(f"⬆️ Interface update available: {server_version_interface}")

        # Résultats finaux
        if version_updates:
            print(f"✅ Updates detected: {version_updates}")
            return version_updates
        else:
            print("✅ All software versions are up to date.")
            return None

    except Exception as e:
        traceback.print_exc()
        print(f"❌ [EXCEPTION] Error checking versions: {e}")
        return "_1"




# 🔐 Generate an encrypted key to be passed to the launched app
def generate_encrypted_key():
    secret_key = Fernet.generate_key()
    fernet = Fernet(secret_key)
    message = b"authorized"
    encrypted_message = fernet.encrypt(message)
    return encrypted_message.decode(), secret_key.decode()




# 🚀 Main script logic: Check version, run app
if __name__ == "__main__":
    try:
        # 🪟 إخفاء نافذة الكونسول في الويندوز (اختياري)
        # if sys.platform == "win32":
        #     ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # 🔍 البحث عن pythonw.exe لتشغيل البرنامج بدون نافذة كونسول
        pythonw_path = None
        for path in os.environ["PATH"].split(os.pathsep):
            pythonw_exe = os.path.join(path, "pythonw.exe")
            if os.path.exists(pythonw_exe):
                pythonw_path = pythonw_exe
                break

        if not pythonw_path:
            pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if os.path.exists(pythonw_exe):
                pythonw_path = pythonw_exe

        if not pythonw_path:
            print("❌ Impossible de trouver pythonw.exe")
            sys.exit(1)


        # sys.stdout = open(os.devnull, 'w')
        # sys.stderr = open(os.devnull, 'w')
        # sys.stdin = open(os.devnull, 'r')
        
        # startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # startupinfo.wShowWindow = subprocess.SW_HIDE
        # 🚀 بداية التشغيل
        if len(sys.argv) == 1:
            # new_versions = checkVersion()
            # if new_versions:
            #     DownloadFile()
            #     extractAll()
            # 🔎 فحص النسخة
            # new_versions = checkVersion()

            # if new_versions == "_1":
            #     print("❌ We were unable to reach the server or retrieve the necessary version information.")
            #     sys.exit(1)

            # # 📥 إذا فيه تحديث
            # if new_versions and ('version_python' in new_versions or 'version_interface' in new_versions):
            #     print("🔄 Starting update process...")
            #     print(f"📌 Updates required: {list(new_versions.keys())}")

            #     result = DownloadAndExtract(new_versions)
            #     if result == 0:
            #         print("✅ Download and extraction finished without errors.")
            #         if 'version_python' in new_versions:
            #             print(f"⬆️ Python update installed → version {new_versions['version_python']}")
            #         if 'version_interface' in new_versions:
            #             print(f"⬆️ Interface update installed → version {new_versions['version_interface']}")
            #         print("🎉 Update completed successfully.")
            #     else:
            #         print("❌ Update failed during download or extraction.")
            #         sys.exit(1)

            # 🚀 سواء فيه تحديث أو لا → نشغل AppV2.py
            encrypted_key, secret_key = generate_encrypted_key()
            script_path = SCRIPT_DIR / 'Programme-main' / 'Python' / 'AppV2.py'

            if script_path.is_file():
                # print(f"▶️ Launching AppV2.py: {script_path}")
                subprocess.call([sys.executable, str(script_path), encrypted_key, secret_key])
            else:
                # print(f"❌ AppV2.py not found at {script_path}")
                sys.exit(1)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
