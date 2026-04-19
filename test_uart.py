# test_uart.py

import serial
import serial.tools.list_ports
import json
import time

def find_ports():
    """Najde a vypíše všechny dostupné sériové porty."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("[-] Nebyly nalezeny žádné sériové porty.")
        return None
    
    print("\n--- Dostupné porty ---")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    return ports

def main():
    ports = find_ports()
    if not ports:
        return

    # Výběr portu uživatelem
    try:
        choice = int(input("\nVyberte číslo portu pro připojení: "))
        selected_port = ports[choice].device
    except (ValueError, IndexError):
        print("[-] Neplatná volba.")
        return

    try:
        # Otevření portu (standardní baudrate pro ESP32 je 115200)
        # Timeout je důležitý, aby čtení nezamrzlo
        ser = serial.Serial(selected_port, 115200, timeout=2)
        print(f"[+] Připojeno k {selected_port}")
        
        # ESP32 se při otevření portu může resetovat, počkáme na inicializaci
        print("[*] Čekám na inicializaci zařízení...")
        time.sleep(2) 
        ser.flushInput() # Vyčistíme uvítací zprávy z bufferu

        # Příprava JSON požadavku
        command = {"get": "addr"}
        json_command = json.dumps(command) + "\n"

        print(f"[*] Odesílám dotaz na veřejný klíč...")
        ser.write(json_command.encode('utf-8'))

        # Čtení odpovědi
        # Protože ESP32 vypisuje i debug info (:: start, READY), musíme najít řádek s adresou
        found_address = False
        start_time = time.time()
        
        while (time.time() - start_time) < 5:  # Timeout 5 sekund na odpověď
            line = ser.readline().decode('utf-8').strip()
            if line:
                # Ignorujeme debug výpisy začínající "::"
                if line.startswith("::") or line == "READY":
                    continue
                
                # Předpokládáme, že co zbude a není prázdné, je naše adresa/klíč
                print("-" * 30)
                print(f"VEŘEJNÝ KLÍČ (Addr): {line}")
                print("-" * 30)
                found_address = True
                break

        if not found_address:
            print("[-] Zařízení neodpovědělo adresou včas.")

        ser.close()
        print("[+] Port uzavřen.")

    except Exception as e:
        print(f"[-] Chyba: {e}")

if __name__ == "__main__":
    main()