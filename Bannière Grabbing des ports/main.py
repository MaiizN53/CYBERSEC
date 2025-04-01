import socket
import threading


def grab_banner(ip, port, results, file):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((ip, port)) == 0:
                try:
                    if port in [80, 443]:  # Envoi d'une requête HEAD pour HTTP/HTTPS
                        s.sendall(b'HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n')
                    else:
                        s.sendall(b'\r\n')  # Requête minimale pour obtenir une bannière

                    banner = s.recv(1024).decode(errors='ignore').strip()
                    if banner:
                        result = f"[+] Port {port} ouvert – Service détecté : {banner}"
                        print(result)
                        results.append(result)
                        file.write(result + "\n")

                        # Reconnaissance par empreinte
                        if "SSH" in banner:
                            fingerprint = f"[*] Serveur SSH détecté sur le port {port}"
                            print(fingerprint)
                            file.write(fingerprint + "\n")
                        elif "HTTP" in banner:
                            fingerprint = f"[*] Serveur Web détecté sur le port {port}"
                            print(fingerprint)
                            file.write(fingerprint + "\n")
                except socket.error:
                    pass
    except socket.error:
        pass


def scan_ports(ip, start_port, end_port):
    threads = []
    results = []
    with open("scan_results.txt", "w") as file:
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=grab_banner, args=(ip, port, results, file))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


def main():
    ip = input("Entrez l'adresse IP à scanner : ")
    start_port = int(input("Port de début : "))
    end_port = int(input("Port de fin : "))
    print("")
    scan_ports(ip, start_port, end_port)
    print("\nRésultats sauvegardés dans scan_results.txt")


if __name__ == "__main__":
    main()
