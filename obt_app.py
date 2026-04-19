#!/usr/bin/env python3
# obt_app.py
"""
OBT UART/API Application
Communication with device via UART + blockchain API queries
"""

import sys
import json
import time
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication

import serial
import serial.tools.list_ports
import requests

from obt_ui import MainWindow


class WorkerThread(QObject):
    """Worker for asynchronous operations – UART communication and API queries"""
    
    # Signals for UI
    log_signal = pyqtSignal(str)              # HTML messages to log
    status_signal = pyqtSignal(str)           # Status text
    ports_found_signal = pyqtSignal(list)     # List of found ports
    connected_signal = pyqtSignal(bool)       # Connection state
    address_received_signal = pyqtSignal(str) # Public key/address from device
    balance_received_signal = pyqtSignal(dict) # Balance data from API
    signature_received_signal = pyqtSignal(str) # Signature from device
    transaction_broadcast_signal = pyqtSignal(dict) # Broadcast result
    
    def __init__(self):
        super().__init__()
        self._serial: Optional[serial.Serial] = None
        self._device_address: str = ""
        self._debug_mode: bool = False
        
        # Transaction data for broadcast
        self._tx_from: str = ""
        self._tx_to: str = ""
        self._tx_utxo_txid: str = ""
        self._tx_utxo_value: int = 0  # Full UTXO value
        self._tx_value: int = 0        # Amount to send
        self._tx_signature: str = ""
    
    # ------------------------------------------------------------------ #
    #  UART operations                                                     #
    # ------------------------------------------------------------------ #
    
    @pyqtSlot()
    def scan_ports(self):
        """Scan available UART ports"""
        self._log("🔍 Scanning UART ports...", color="#ffb300")
        self.status_signal.emit("Scanning …")
        
        try:
            ports = serial.tools.list_ports.comports()
            if not ports:
                self._log("⚠️ No serial ports found", color="#f44336")
                self.status_signal.emit("Idle")
                self.ports_found_signal.emit([])
                return
            
            port_list = []
            for port in ports:
                info = f"{port.device} — {port.description}"
                port_list.append((port.device, info))
                if self._debug_mode:
                    self._log(f"  • {info}", color="#888")
            
            self._log(f"✓ Found {len(port_list)} port(s)", color="#4caf50")
            self.status_signal.emit("Idle")
            self.ports_found_signal.emit(port_list)
            
        except Exception as e:
            self._log(f"❌ Scan error: {e}", color="#f44336")
            self.status_signal.emit("Error")
            self.ports_found_signal.emit([])
    
    @pyqtSlot(str)
    def connect_port(self, port_name: str):
        """Connect to selected port"""
        self._log(f"🔌 Connecting to {port_name}...", color="#ffb300")
        self.status_signal.emit("Connecting …")
        
        try:
            self._serial = serial.Serial(port_name, 115200, timeout=2)
            self._log(f"✓ Connected to {port_name}", color="#4caf50")
            
            # ESP32 may reset when opening port
            self._log("⏳ Waiting for device initialization (2s)...", color="#888")
            time.sleep(2)
            self._serial.flushInput()
            
            self.status_signal.emit("Connected")
            self.connected_signal.emit(True)
            
            # Automatically request public key
            self._request_address()
            
        except Exception as e:
            self._log(f"❌ Connection error: {e}", color="#f44336")
            self.status_signal.emit("Error")
            self.connected_signal.emit(False)
            if self._serial and self._serial.is_open:
                self._serial.close()
                self._serial = None
    
    @pyqtSlot()
    def disconnect_port(self):
        """Disconnect UART port"""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._log("🔌 Port closed", color="#888")
        self._serial = None
        self._device_address = ""
        self.status_signal.emit("Idle")
        self.connected_signal.emit(False)
    
    def _request_address(self):
        """Request public key from device"""
        if not self._serial or not self._serial.is_open:
            return
        
        try:
            command = {"get": "addr"}
            json_command = json.dumps(command) + "\n"
            
            self._log("📤 Requesting public key...", color="#2196f3")
            if self._debug_mode:
                self._log(f"  TX: {json_command.strip()}", color="#666")
            
            self._serial.write(json_command.encode('utf-8'))
            
            # Read response
            found_address = False
            start_time = time.time()
            
            while (time.time() - start_time) < 5:
                line = self._serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if self._debug_mode:
                        self._log(f"  RX: {line}", color="#666")
                    
                    # Ignore debug outputs
                    if line.startswith("::") or line == "READY":
                        continue
                    
                    # Assume the rest is the address
                    self._device_address = line
                    self._log(f"🔑 Public key: <b>{line}</b>", color="#4caf50")
                    self.address_received_signal.emit(line)
                    found_address = True
                    break
            
            if not found_address:
                self._log("⚠️ Device did not respond in time", color="#f44336")
                
        except Exception as e:
            self._log(f"❌ Error reading address: {e}", color="#f44336")
    
    # ------------------------------------------------------------------ #
    #  API operations                                                      #
    # ------------------------------------------------------------------ #
    
    @pyqtSlot(str)
    def get_balance(self, address: str):
        """Get balance and UTXOs from API"""
        if not address:
            self._log("⚠️ No address provided", color="#f44336")
            return
        
        base_url = "https://www.agamapoint.com/bbr/index.php?route=get_balance/"
        url = f"{base_url}{address}"
        
        self._log(f"🌐 Querying API: {address}", color="#2196f3")
        if self._debug_mode:
            self._log(f"  URL: {url}", color="#666")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                balance = data.get("balance", 0)
                utxo_count = data.get("utxo_count", 0)
                
                self._log(f"✓ Balance: <b>{balance}</b> units | UTXOs: {utxo_count}", 
                         color="#4caf50")
                
                if self._debug_mode and data.get("unspent_outputs"):
                    for utxo in data["unspent_outputs"]:
                        # Fix: Convert txid to string to handle integer values
                        txid = str(utxo.get('txid', ''))
                        value = utxo.get('value', 0)
                        self._log(f"  • TXID: {txid[:16]}... | {value} units", 
                                 color="#888")
                
                self.balance_received_signal.emit(data)
            else:
                self._log(f"❌ API error: {data.get('status')}", color="#f44336")
                
        except requests.exceptions.Timeout:
            self._log("❌ Timeout - API did not respond in time", color="#f44336")
        except requests.exceptions.RequestException as e:
            self._log(f"❌ API request error: {e}", color="#f44336")
        except json.JSONDecodeError:
            self._log("❌ API returned invalid JSON", color="#f44336")
    
    @pyqtSlot(str, str, list, int)
    def send_transaction(self, to_address: str, from_address: str, selected_utxos: list, send_value: int):
        """Build transaction and send for signing"""
        
        # Validate: exactly one UTXO must be selected
        if len(selected_utxos) == 0:
            self._log("⚠️ No UTXO selected! Please select exactly one.", color="#f44336")
            return
        
        if len(selected_utxos) > 1:
            self._log("⚠️ Multiple UTXOs selected! Please select exactly one.", color="#f44336")
            return
        
        # Extract UTXO data
        utxo = selected_utxos[0]
        txid = str(utxo.get("txid", ""))
        utxo_value = utxo.get("value", 0)
        
        # Validate send_value
        if send_value <= 0:
            self._log("⚠️ Send value must be greater than 0!", color="#f44336")
            return
        
        if send_value > utxo_value:
            self._log(f"⚠️ Send value ({send_value}) cannot be greater than UTXO value ({utxo_value})!", color="#f44336")
            return
        
        # Store transaction data for later broadcast
        self._tx_from = from_address
        self._tx_to = to_address
        self._tx_utxo_txid = txid
        self._tx_utxo_value = utxo_value  # Full UTXO value (for val1)
        self._tx_value = send_value       # Amount to send (for val2)
        self._tx_signature = ""  # Will be filled when signature arrives
        
        # Build transaction string: FROM|TXID|TO|VALUE
        tx_string = f"{from_address}|{txid}|{to_address}|{send_value}"
        
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
        self._log("📝 <b>Building Transaction</b>", color="#2196f3")
        self._log(f"  From:       <b>{from_address}</b>", color="#888")
        self._log(f"  TXID:       <b>{txid}</b>", color="#888")
        self._log(f"  To:         <b>{to_address}</b>", color="#888")
        self._log(f"  UTXO Value: <b>{utxo_value}</b> units", color="#888")
        self._log(f"  Send Value: <b>{send_value}</b> units", color="#4caf50")
        if send_value < utxo_value:
            change = utxo_value - send_value
            self._log(f"  Change:     <b>{change}</b> units (will return to sender as new UTXO)", color="#2196f3")
        self._log(f"  TX String:  <b>{tx_string}</b>", color="#ffb300")
        
        # Send for signing via UART
        if not self._serial or not self._serial.is_open:
            self._log("❌ Not connected to device!", color="#f44336")
            return
        
        try:
            # Create sign command
            command = {"sign": tx_string}
            json_command = json.dumps(command) + "\n"
            
            self._log("📤 Sending to device for signature...", color="#2196f3")
            if self._debug_mode:
                self._log(f"  TX: {json_command.strip()}", color="#666")
            
            self._serial.write(json_command.encode('utf-8'))
            
            # Read response
            found_signature = False
            start_time = time.time()
            
            while (time.time() - start_time) < 10:  # 10 second timeout
                line = self._serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if self._debug_mode:
                        self._log(f"  RX: {line}", color="#666")
                    
                    # Ignore debug outputs from ESP32
                    if line.startswith("::"):
                        # Log ASH24 hash and signature info
                        self._log(f"  {line}", color="#666")
                        continue
                    
                    # Try to parse JSON response
                    try:
                        response = json.loads(line)
                        if "sig_res" in response:
                            signature = response["sig_res"]
                            self._log(f"✓ <b>Signature received:</b>", color="#4caf50")
                            self._log(f"  {signature}", color="#4caf50")
                            
                            # Store signature for broadcast
                            self._tx_signature = signature
                            
                            self.signature_received_signal.emit(signature)
                            found_signature = True
                            break
                    except json.JSONDecodeError:
                        # Not JSON, might be other output
                        if line and not line.startswith("READY"):
                            self._log(f"  Device: {line}", color="#888")
            
            if not found_signature:
                self._log("⚠️ Device did not return signature in time", color="#f44336")
            
            self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
                
        except Exception as e:
            self._log(f"❌ Error during signing: {e}", color="#f44336")
    
    @pyqtSlot()
    def broadcast_transaction(self):
        """Broadcast signed transaction to blockchain API"""
        
        # Validate we have all necessary data
        if not self._tx_from or not self._tx_to:
            self._log("❌ No transaction data available. Build and sign a transaction first!", color="#f44336")
            return
        
        if not self._tx_signature:
            self._log("❌ No signature available. Sign the transaction first!", color="#f44336")
            return
        
        # Build payload for API
        payload = {
            "from": self._tx_from,
            "utxo_txid": self._tx_utxo_txid,
            "to": self._tx_to,
            "val1": self._tx_utxo_value,  # Full UTXO value (must consume entire UTXO)
            "val2": self._tx_value,       # Amount to send (change returns to sender)
            "sig_hex": self._tx_signature
        }
        
        url = "https://www.agamapoint.com/bbr/index.php?route=send_transaction"
        
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
        self._log("📡 <b>Broadcasting Transaction to Blockchain</b>", color="#2196f3")
        self._log(f"  From:       <b>{self._tx_from}</b>", color="#888")
        self._log(f"  UTXO TXID:  <b>{self._tx_utxo_txid}</b>", color="#888")
        self._log(f"  To:         <b>{self._tx_to}</b>", color="#888")
        self._log(f"  UTXO Value: <b>{self._tx_utxo_value}</b> units (val1)", color="#888")
        self._log(f"  Send Value: <b>{self._tx_value}</b> units (val2)", color="#4caf50")
        
        if self._tx_utxo_value > self._tx_value:
            change = self._tx_utxo_value - self._tx_value
            self._log(f"  Change:     <b>{change}</b> units (returns to sender as new UTXO)", color="#2196f3")
        
        self._log(f"  Signature:  <b>{self._tx_signature[:32]}...</b>", color="#888")
        
        if self._debug_mode:
            self._log(f"  API URL: {url}", color="#666")
            self._log(f"  Payload: {json.dumps(payload, indent=2)}", color="#666")
        
        try:
            self._log("⏳ Sending POST request to API...", color="#ffb300")
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if self._debug_mode:
                self._log(f"  API Response: {json.dumps(data, indent=2)}", color="#666")
            
            if data.get("status") == "ok":
                txid = data.get("txid", "N/A")
                message = data.get("message", "Transaction broadcasted successfully")
                
                self._log(f"✓ <b>SUCCESS:</b> {message}", color="#4caf50")
                self._log(f"  <b>New TXID:</b> {txid}", color="#4caf50")
                
                # Emit success signal
                self.transaction_broadcast_signal.emit({
                    "status": "ok", 
                    "txid": txid, 
                    "message": message
                })
                
                # Refresh balance after successful broadcast
                self._log("⏳ Refreshing balance in 1 second...", color="#888")
                time.sleep(1)
                
                if self._tx_from:
                    self.get_balance(self._tx_from)
                
            else:
                message = data.get("message", "Unknown error from API")
                self._log(f"❌ <b>API ERROR:</b> {message}", color="#f44336")
                
                # Log verbose details if available
                if "error" in data:
                    self._log(f"  Error details: {data['error']}", color="#f44336")
                
                self.transaction_broadcast_signal.emit({
                    "status": "error", 
                    "message": message
                })
            
            self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
            
        except requests.exceptions.Timeout:
            self._log("❌ <b>Timeout</b> - API did not respond in time (15s)", color="#f44336")
            self.transaction_broadcast_signal.emit({
                "status": "error", 
                "message": "API timeout"
            })
            self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
            
        except requests.exceptions.RequestException as e:
            self._log(f"❌ <b>Network error:</b> {e}", color="#f44336")
            self.transaction_broadcast_signal.emit({
                "status": "error", 
                "message": f"Network error: {e}"
            })
            self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
            
        except json.JSONDecodeError as e:
            self._log(f"❌ <b>Invalid JSON response</b> from API: {e}", color="#f44336")
            self.transaction_broadcast_signal.emit({
                "status": "error", 
                "message": "Invalid API response (not JSON)"
            })
            self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color="#888")
    
    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #
    
    @pyqtSlot(bool)
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug mode"""
        self._debug_mode = enabled
        mode = "ENABLED" if enabled else "DISABLED"
        self._log(f"🐛 Debug mode {mode}", color="#888")
    
    def _log(self, message: str, color: str = "#e0e0e0"):
        """Internal helper for logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f"<span style='color:#666;'>[{timestamp}]</span> " \
               f"<span style='color:{color};'>{message}</span>"
        self.log_signal.emit(html)


def main():
    app = QApplication(sys.argv)
    
    # Worker runs in its own thread
    worker = WorkerThread()
    thread = QThread()
    worker.moveToThread(thread)
    thread.start()
    
    # UI window
    window = MainWindow(worker)
    window.show()
    
    try:
        exit_code = app.exec()
    finally:
        thread.quit()
        thread.wait()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
