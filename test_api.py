import requests
import json

def test_get_balance(address="83ca"):
    # Základní URL z tvého HTML příkladu
    base_url = "https://www.agamapoint.com/bbr/index.php?route=get_balance/"
    url = f"{base_url}{address}"
    
    print(f"[*] Dotazuji se na API: {url}")
    
    try:
        # Provedení GET požadavku
        response = requests.get(url)
        
        # Kontrola HTTP statusu (200 = OK)
        response.raise_for_status()
        
        # Parsování JSON odpovědi
        data = response.json()
        
        if data.get("status") == "ok":
            print("\n" + "="*30)
            print(f"ADRESA:  {data.get('address')}")
            print(f"BALANCE: {data.get('balance')} unitů")
            print(f"UTXOs:   {data.get('utxo_count')}")
            print("="*30)
            
            # Výpis jednotlivých UTXO
            print("\nSeznam UTXO (unspent outputs):")
            for utxo in data.get("unspent_outputs", []):
                print(f" - TXID: {utxo['txid']} | Hodnota: {utxo['value']}")
        else:
            print(f"[-] API vrátilo chybu: {data.get('status')}")

    except requests.exceptions.RequestException as e:
        print(f"[-] Chyba při spojení s API: {e}")
    except json.JSONDecodeError:
        print("[-] Chyba: Odpověď serveru není platný JSON.")
        print("Surová odpověď:", response.text)

if __name__ == "__main__":
    test_get_balance()