from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import os

# Clé de chiffrement fixe
key = b"zBb1hDM4nU8NQCHjKd8Vkfz86S4qTaXmFh5n0sguDCg="
fernet = Fernet(key)

# Préfixe pour les dates
PREFIX = "demo::"

def encrypt_date(date_str: str) -> str:
    # Ajouter le préfixe avant de chiffrer
    date_with_prefix = PREFIX + date_str
    return fernet.encrypt(date_with_prefix.encode()).decode()

def decrypt_date(encrypted_str: str) -> str:
    # Déchiffrer et retirer le préfixe "demo::"
    decrypted_str = fernet.decrypt(encrypted_str.encode()).decode()
    if decrypted_str.startswith(PREFIX):
        return decrypted_str[len(PREFIX):]  # Retirer le préfixe
    return decrypted_str  # Retourne tel quel si le préfixe est absent

def is_date_already_exists(target_date: str, file_path: str) -> bool:
    """Vérifie si la date existe déjà dans le fichier (après déchiffrement)"""
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                if decrypt_date(line) == target_date:
                    return True
            except Exception as e:
                print(f"⛔ Erreur de déchiffrement: {e}")
                continue
    return False

def save_encrypted_date(date_str: str, file_path: str) -> bool:
    """Ajoute la date chiffrée seulement si elle n'existe pas déjà"""
    if is_date_already_exists(date_str, file_path):
        return False
        
    encrypted_date = encrypt_date(date_str)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(encrypted_date + "\n")
    return True

# Exemple d'utilisation
if __name__ == "__main__":
    FILE_PATH = "encrypted_dates.txt"
    
    # Exemple : date d'il y a 3 jours
    date_str = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    
    if save_encrypted_date(date_str, FILE_PATH):
        print(f"✅ Date ajoutée: {date_str}")
    else:
        print(f"⛔ Date déjà existante: {date_str}")
    
    # Nouvelle date actuelle
    new_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if save_encrypted_date(new_date, FILE_PATH):
        print(f"✅ Date ajoutée: {new_date}")
    else:
        print(f"⛔ Date déjà existante: {new_date}")

    # Exemple de décryptage
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            decrypted_date = decrypt_date(line.strip())
            print(f"Date décryptée: {decrypted_date}")
