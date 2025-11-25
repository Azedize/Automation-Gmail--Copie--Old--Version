import os
import subprocess
import zipfile
import py_compile
from datetime import datetime
import shutil
import requests
import json




def update_version(version_file):
    try:
        print(f"🔄 Mise à jour de la version dans {version_file}...")
        with open(version_file, 'r+') as f:
            old_version = f.read().strip() or "1.0.0"
            major, minor, patch = map(int, old_version.split('.'))
            if patch < 9:
                patch += 1
            else:
                patch = 0
                if minor < 9:
                    minor += 1
                else:
                    minor = 0
                    major += 1
                   
            new_version = f"{major}.{minor}.{patch}"
            f.seek(0)
            f.write(new_version)
            f.truncate()
        print(f"✅ Nouvelle version : {new_version} (Ancienne version: {old_version})")
        return new_version, old_version
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de la version : {e}")
        exit(1)





def compile_python_files(source_directory):
    try:
        print(f"🔄 Compilation des fichiers Python dans {source_directory}...")
        exclude_dirs = {'Lib', 'Scripts', 'Include', '__pycache__', 'build', 'dist', 'interface', 
                       'tools', 'Programme-main', 'Tools-main', 'node_modules'}

        # Compile checkV2.py and AppV2.py in the root directory
        print(f"📂 Compilation des fichiers Python dans le répertoire racine...")
        for file in os.listdir(source_directory):
            if file.endswith('.py') and (file == 'checkV3.py'):
                py_file = os.path.join(source_directory, file)
                print(f"   ➡️ Compilation du fichier : {py_file}")
                try:
                    py_compile.compile(py_file, cfile=py_file + 'c', doraise=True)
                    print(f"   ✅ Compilation réussie pour {py_file}")
                except py_compile.PyCompileError as e:
                    print(f"❌ Erreur de compilation pour {py_file} : {e}")

        print(f"📂 Exploration du dossier {source_directory} pour les fichiers Python...")
        for root, dirs, files in os.walk(source_directory):
            print(f"🔍 En cours d'exploration: {root}")

            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            print(f"   ➖ Répertoires exclus: {exclude_dirs}")
            print(f"   ➡️ Répertoires à explorer: {dirs}")

            py_files = []
            for f in files:
                if f.endswith('.py') and (f == 'App.py'):
                    py_files.append(os.path.join(root, f))
            
            if py_files:
                print(f"   🔍 Fichiers Python trouvés: {py_files}")
            else:
                print(f"   🚫 Aucun fichier cible trouvé dans {root}.")

            for py_file in py_files:
                print(f"   ➡️ Compilation du fichier : {py_file}")
                try:
                    py_compile.compile(py_file, cfile=py_file + 'c', doraise=True)
                    print(f"   ✅ Compilation réussie pour {py_file}")
                except py_compile.PyCompileError as e:
                    print(f"❌ Erreur de compilation pour {py_file} : {e}")
                    continue

        print("✅ Compilation terminée avec succès pour les fichiers cibles.")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la compilation des fichiers Python : {e}")
        return False




def obfuscate_js(source_directory, destination_directory):
    url = "https://jsd-online-demo.preemptive.com/api/protect"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://jsd-online-demo.preemptive.com",
        "Referer": "https://jsd-online-demo.preemptive.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    protection_config = {
        "settings": {
            "booleanLiterals": {"randomize": False},
            "integerLiterals": {"radix": "none", "randomize": False, "lower": None, "upper": None},
            "debuggerRemoval": True,
            "stringLiterals": True,
            "propertyIndirection": True,
            "localDeclarations": {"nameMangling": "base52"},
            "controlFlow": {"randomize": False},
            "constantArgument": False,
            "domainLock": False,
            "functionReorder": False,
            "propertySparsing": False,
            "variableGrouping": False
        }
    }

    try:
        start_time = datetime.now()
        print(f"\n🔄 Début de l'obfuscation JavaScript dans [{source_directory}] à {start_time.strftime('%H:%M:%S')}")
        print(f"🔍 Recherche de fichiers .js dans l'arborescence...")

        total_files = 0
        success_count = 0
        skipped_files = []
        error_messages = []

        if not os.path.exists(destination_directory):
            print(f"📂 Création du répertoire de destination : {destination_directory}")
            os.makedirs(destination_directory)

        for root, dirs, files in os.walk(source_directory):
            if 'node_modules' in dirs:
                print(f"   ⚠️ Exclusion du dossier node_modules dans {root}")
                dirs.remove('node_modules')

            js_files = [f for f in files if f.endswith('.js')]
            total_files += len(js_files)

            if js_files:
                print(f"\n📁 Dossier traité : {root}")
                print(f"   🗃️ Fichiers JS trouvés : {len(js_files)}")

            for file in js_files:
                js_path = os.path.join(root, file)

                # Local obfuscation for gmail_process.js
                if file == "gmail_process.js":
                    print("🛠️ Utilisation de javascript-obfuscator en local...")
                    output_root = os.path.join(destination_directory, os.path.relpath(root, source_directory))
                    os.makedirs(output_root, exist_ok=True)
                    output_file = os.path.join(output_root, file)

                    try:
                        result = subprocess.run(
                            f'javascript-obfuscator "{js_path}" --output "{output_file}"',
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            shell=True
                        )

                        # mon besoin fait une 
                        
                        print("   ✅ Succès - Fichier obfusqué localement :", output_file)
                        print("   🔹 Sortie standard :", result.stdout) 
                        print("   🔸 Erreurs (s'il y en a) :", result.stderr)
                        success_count += 1
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Erreur lors de l'exécution de javascript-obfuscator ({file}) : {e.stderr}"
                        print(f"   ❌ {error_msg}")
                        error_messages.append(error_msg)
                        skipped_files.append(js_path)
                    continue 
                elif file == "background.js":
                    print("🛠️ Traitement spécial pour background.js : terser + javascript-obfuscator")
                    output_root = os.path.join(destination_directory, os.path.relpath(root, source_directory))
                    os.makedirs(output_root, exist_ok=True)
                    minified_file = os.path.join(output_root, "background.min.js")
                    obfuscated_file = os.path.join(output_root, file)

                    try:
                       

                        subprocess.run(
                            f'terser "{js_path}" -o "{minified_file}"',
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            shell=True
                        )

                        result = subprocess.run(
                            f'javascript-obfuscator "{minified_file}" --output "{obfuscated_file}" --self-defending --disable-console-output --string-array --split-strings',
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            shell=True
                        )
                        print("   ✅ Succès - Fichier background.js minifié et obfusqué :", obfuscated_file)
                        print("   🔹 Sortie standard :", result.stdout)
                        print("   🔸 Erreurs (s'il y en a) :", result.stderr)

                        with open(minified_file, 'r', encoding='utf-8') as f_in:
                            minified_content = f_in.read()

                        with open(obfuscated_file, 'w', encoding='utf-8') as f_out:
                            f_out.write(minified_content)

                        os.remove(minified_file)

                        success_count += 1
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Erreur lors du traitement de background.js : {e.stderr}"
                        print(f"   ❌ {error_msg}")
                        error_messages.append(error_msg)
                        skipped_files.append(js_path)
                    continue  


                # API Obfuscation for other JS files
                file_size = os.path.getsize(js_path)
                print(f"\n🔧 Traitement de : {file}")
                print(f"📏 Taille du fichier : {file_size} octets")

                try:
                    # Lecture du fichier source
                    with open(js_path, 'r', encoding='utf-8') as f:
                        js_content = f.read()

                    # Préparation de la payload
                    payload = {
                        "sourceFile": {
                            "name": file,
                            "source": js_content
                        },
                        "protectionConfiguration": protection_config
                    }

                    # Envoi de la requête
                    print("🛠️ Exécution de l'obfuscation via API...")
                    response = requests.post(url, headers=headers, json=payload)

                    if response.status_code == 200:
                        # Création de l'arborescence de destination
                        relative_path = os.path.relpath(root, source_directory)
                        output_root = os.path.join(destination_directory, relative_path)
                        os.makedirs(output_root, exist_ok=True)
                        output_file = os.path.join(output_root, file)

                        # Écriture du résultat
                        with open(output_file, 'w', encoding='utf-8') as f_out:
                            f_out.write(response.json().get('protectedCode', ''))

                        print(f"   ✅ Succès - Fichier généré : {output_file}")
                        success_count += 1
                    else:
                        error_msg = f"Erreur API ({file}) : {response.status_code} - {response.text}"
                        print(f"   ❌ {error_msg}")
                        error_messages.append(error_msg)
                        skipped_files.append(js_path)

                except Exception as e:
                    error_msg = f"Erreur générale ({file}) : {str(e)}"
                    print(f"   ❌ {error_msg}")
                    error_messages.append(error_msg)
                    skipped_files.append(js_path)

        duration = datetime.now() - start_time
        print(f"\n{'━'*40}")
        print(f"📊 Récapitulatif de l'obfuscation JS :")
        print(f"🕒 Temps total : {duration.total_seconds():.2f} secondes")
        print(f"📂 Dossier traité : {source_directory}")
        print(f"🗃️ Fichiers traités : {total_files}")
        print(f"✅ Succès : {success_count}")
        print(f"⏭️ Fichiers ignorés/échoués : {len(skipped_files)}")

        if error_messages:
            print(f"\n🔴 Erreurs rencontrées :")
            for i, error in enumerate(error_messages[:3], 1):
                print(f"{i}. {error}")
            if len(error_messages) > 3:
                print(f"... ({len(error_messages)-3} erreurs supplémentaires)")

        if skipped_files:
            print(f"\n📄 Fichiers non traités :")
            for f in skipped_files[:3]:
                print(f"- {f}")
            if len(skipped_files) > 3:
                print(f"... ({len(skipped_files)-3} fichiers supplémentaires)")

        print(f"\n✅ Obfuscation terminée pour {source_directory} avec {success_count}/{total_files} fichiers traités avec succès")

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        exit(1)





def create_zip(zip_name, source_directory):
    try:
        print(f"🔄 Création de l'archive ZIP : {zip_name}...")

        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            checkV2_pyc_path = os.path.join(source_directory, "checkV3.pyc")
            if os.path.exists(checkV2_pyc_path):
                zipf.write(checkV2_pyc_path, "checkV3.pyc")  
                print(f"   ➡️ Ajout au ZIP : {checkV2_pyc_path} en tant que checkV3.pyc")
            else:
                print(f"   ❌ checkV3.pyc non trouvé dans {source_directory}")

            
            zipf.write(source_directory, "Programme-main")
            print(f"   ➡️ Création du répertoire Programme-main dans l'archive")

            for root, dirs, files in os.walk(source_directory):
                dirs[:] = [d for d in dirs if d not in {'Lib', 'Scripts', 'Include', '__pycache__', 'node_modules', 'build', 'dist', 'obfuscated_js'}]
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path != checkV2_pyc_path and file != "checkV3.py" and file != "AppV2.py":
                        archive_path = os.path.join("Programme-main", os.path.relpath(file_path, source_directory))
                        zipf.write(file_path, archive_path)
                        print(f"   ➡️ Ajout au ZIP : {file_path} en tant que {archive_path}")
        print(f"✅ Archive ZIP créée avec succès : {zip_name}")
    except Exception as e:
        print(f"❌ Erreur lors de la création du ZIP : {e}")
        exit(1)






if __name__ == "__main__":
    build_dir = "build"
    os.makedirs(build_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied_dir = os.path.join(build_dir, f"Programme-main_{timestamp}")

    print(f"🔄 Copie du dossier Programme-main vers {copied_dir}...")
    shutil.copytree("Programme-main", copied_dir)
    print("✅ Copie terminée.")
    
    print(f"🔄 Copie de checkV3.py vers {copied_dir}...")
    shutil.copy("checkV3.py", copied_dir)
    print("✅ Copie terminée.")

    python_old_version = None
    extension_old_version = None

    change_version = input("🛠️ Voulez-vous changer la version (Y/N)? ").strip().upper()
    while change_version not in {'Y', 'N'}:
        print("❌ Réponse invalide. Veuillez entrer 'Y' pour Oui ou 'N' pour Non.")
        change_version = input("🛠️ Voulez-vous changer la version (Y/N)? ").strip().upper()

    if change_version == 'Y':
        version_type = input("📌 Quelle version mettre à jour? Python (P) ou Extension (E)? [P par défaut] ").strip().upper() or 'P'
        
        if version_type == 'P':
            python_version, python_old_version = update_version(os.path.join(copied_dir, 'tools', 'version.txt'))
        elif version_type == 'E':
            extension_version, extension_old_version = update_version(os.path.join(copied_dir, 'interface', 'version.txt'))
        else:
            print("❌ Choix invalide")
            exit(1)

    try:
        with open(os.path.join(copied_dir, 'tools', 'version.txt'), 'r') as f:
            python_version = f.read().strip()
    except Exception as e:
        print(f"❌ Erreur lecture version Python: {e}")
        exit(1)

    try:
        with open(os.path.join(copied_dir, 'interface', 'version.txt'), 'r') as f:
            extension_version = f.read().strip()
    except Exception as e:
        print(f"❌ Erreur lecture version Extension: {e}")
        exit(1)

    if not compile_python_files(copied_dir):
        print("❌ Erreur lors de la compilation des fichiers Python")
        exit(1)

    obfuscate_js(
        os.path.join(copied_dir, 'tools', 'ExtensionTemplateChrome'),
        os.path.join(copied_dir, 'tools', 'ExtensionTemplateChrome')
    )

    obfuscate_js(
        os.path.join(copied_dir, 'tools', 'ExtensionTemplateFirefox'),
        os.path.join(copied_dir, 'tools', 'ExtensionTemplateFirefox')
    )


    zip_name = f"Application_P{python_version}_E{extension_version}.zip"
    create_zip(zip_name, copied_dir)

    # Affichage du récapitulatif
    print("\n🎉 Fichier ZIP créé avec succès:")
    print(f"📁 Dossier source: {copied_dir}")
    print(f"📦 Fichier ZIP: {zip_name}")
    if python_old_version:
        print(f"🐍 Python: {python_old_version} → {python_version}")
    else:
        print(f"🐍 Python: {python_version}")
    if extension_old_version:
        print(f"🧩 Extension: {extension_old_version} → {extension_version}")
    else:
        print(f"🧩 Extension: {extension_version}")

    try:
        print(f"\n🧹 Nettoyage du répertoire de build...")
        shutil.rmtree(build_dir)
        print(f"✅ Répertoire '{build_dir}' supprimé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression du répertoire de build : {e}")
        exit(1)



