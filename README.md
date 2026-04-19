# OBT - ONE BYTE TOY - UART Blockchain Tool

A PyQt6-based desktop application for "secure" blockchain transactions using external hardware wallet devices connected via UART.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-orange.svg)

## 🎯 Overview

OBT (OneByte Toy) is a simple blockchain transaction tool that interfaces with hardware wallet devices (ESP32-S3, ESP32-C3, TROPIC01) via UART serial communication. The application allows users to manage cryptocurrency transactions with hardware-level security by keeping private keys isolated on the hardware device.

### Key Features

✅ **Hardware Wallet Integration**
- Connect to ESP32-based hardware wallets via UART
- Automatic device detection and initialization
- Secure key storage on hardware device

✅ **Blockchain Operations**
- Query balance and UTXO (Unspent Transaction Outputs)
- Build and sign transactions with hardware wallet
- Broadcast signed transactions to blockchain network
- Automatic change handling (UTXO model)

✅ **User Interface**
- Modern dark/light theme support
- Adjustable font sizes (accessibility)
- Real-time verbose logging
- Resizable panels with drag-and-drop splitter

✅ **Security**
- Private keys never leave hardware device
- All signatures generated on-device
- Transaction verification before broadcast

---

## 📋 Requirements

### System Requirements
- **OS**: Windows, Linux, macOS
- **Python**: 3.8 or higher
- **Hardware**: ESP32-S3, ESP32-C3, or TROPIC01 device with UART support

### Python Dependencies
```
PyQt6>=6.0.0
pyserial>=3.5
requests>=2.28.0
```

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/obt-uart-blockchain-tool.git
cd obt-uart-blockchain-tool
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python obt_app.py
```

---

## 📖 Usage Guide

### Step 1: Connect Hardware Wallet

1. **Scan for Ports**
   - Click "⟳ Scan ports" to detect available serial ports
   - Select your hardware device from the dropdown

2. **Connect**
   - Click "Connect" button
   - Application automatically requests public key from device
   - Device address is displayed in the "Connection" section

### Step 2: Check Balance

1. Click "Get Balance" to query blockchain API
2. Balance and available UTXOs are displayed
3. Select UTXO to spend by checking the checkbox

### Step 3: Create Transaction

1. **Enter Transaction Details**
   - `Value`: Amount to send (must be ≤ UTXO value)
   - `To`: Recipient address

2. **Sign Transaction**
   - Click "🔏 Sign Transaction"
   - Transaction data is sent to hardware device
   - Device computes signature using private key
   - Signature is returned and displayed in log

3. **Broadcast Transaction**
   - Click "📡 Broadcast" (enabled after signing)
   - Signed transaction is sent to blockchain API
   - New transaction ID (TXID) is returned
   - Balance automatically refreshed

---

## 🔧 Transaction Protocol

### UTXO Model

This application implements the **UTXO (Unspent Transaction Output)** model:

```
┌─────────────────────────────────────────────┐
│ UTXO Input: 5 units                         │
├─────────────────────────────────────────────┤
│ Output 1 (Recipient): 3 units               │
│ Output 2 (Change to Sender): 2 units        │
└─────────────────────────────────────────────┘
```

**Important**: The entire UTXO must be consumed. Any difference between UTXO value and send amount returns to sender as **change** (new UTXO).

### Transaction Format

**TX String sent to hardware device for signing:**
```
FROM_ADDRESS|UTXO_TXID|TO_ADDRESS|SEND_VALUE
```

**Example:**
```
abc123def456|9876543210abcdef|7214|3
```

**API Payload for broadcast:**
```json
{
  "from": "abcd",
  "utxo_txid": "123",
  "to": "7214",
  "val1": 5,      // Full UTXO value (must consume entire UTXO)
  "val2": 3,      // Amount to send
  "sig_hex": "..."  // Signature from hardware device
}
```

**Change Calculation:**
```
change = val1 - val2 = 5 - 3 = 2 units
```
This change automatically returns to sender as a new UTXO.

---

## 🔌 Hardware Device Communication

### UART Protocol

**Baud Rate**: 115200  
**Timeout**: 2 seconds  
**Format**: JSON commands over serial

### Command Set

#### 1. Get Public Key/Address
**TX (to device):**
```json
{"get": "addr"}
```

**RX (from device):**
```
abc
```

#### 2. Sign Transaction
**TX (to device):**
```json
{"sign": "abcd|123|7214|3"}
```

**RX (from device):**
```json
{"sig_res": "abc12..."}
```

### Debug Output

Hardware devices may output debug information prefixed with `::` which is logged but not processed:
```
::ASH24 hash: 0x1234...
::Signature computed
```

---

## 🌐 Blockchain API

### Endpoints

#### Get Balance & UTXOs
```
GET https://www.agamapoint.com/bbr/index.php?route=get_balance/{address}
```

**Response:**
```json
{
  "status": "ok",
  "balance": 10,
  "utxo_count": 2,
  "unspent_outputs": [
    {"txid": "123abc", "value": 5},
    {"txid": "456def", "value": 5}
  ]
}
```

#### Broadcast Transaction
```
POST https://www.agamapoint.com/bbr/index.php?route=send_transaction
```

**Request:**
```json
{
  "from": "sender_address",
  "utxo_txid": "input_txid",
  "to": "recipient_address",
  "val1": 5,  // Full UTXO value
  "val2": 3,  // Send amount
  "sig_hex": "signature_from_device"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Transaction broadcasted successfully",
  "txid": "new_transaction_id"
}
```

---

## 🎨 UI Features

### Theme Customization
- **Dark Mode** (default): Optimized for low-light environments
- **Light Mode**: High-contrast theme for daylight use

### Font Sizes
1. **Size 1** (11pt): Default size for standard displays
2. **Size 2** (15pt): Larger text for high-DPI screens
3. **Size 3** (31pt): Extra-large for presentations or accessibility

### Resizable Panels
- Drag the center splitter to adjust left/right panel widths
- Default: 300px (left) / 700px (right)

### Verbose Logging
- Timestamped entries with color-coded severity
- HTML-formatted output with syntax highlighting
- Auto-scroll to latest entry
- Optional debug mode for detailed protocol traces

---

## 🏗️ Architecture

### Project Structure
```
obt-uart-blockchain-tool/
├── obt_app.py           # Main application & worker thread
├── obt_ui.py            # PyQt6 UI components
├── obt_logo.svg         # Application logo
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Threading Model

```
┌──────────────────────────────────────┐
│         Main Thread (UI)              │
│  ┌──────────────────────────────┐    │
│  │   MainWindow (PyQt6)         │    │
│  │  - User interactions         │    │
│  │  - Display updates           │    │
│  └──────────────────────────────┘    │
└──────────────────┬───────────────────┘
                   │ Signals/Slots
┌──────────────────▼───────────────────┐
│       Worker Thread                   │
│  ┌──────────────────────────────┐    │
│  │   WorkerThread (QObject)     │    │
│  │  - UART communication        │    │
│  │  - API requests              │    │
│  │  - Transaction building      │    │
│  └──────────────────────────────┘    │
└───────────────────────────────────────┘
```

**Benefits:**
- Non-blocking UI during I/O operations
- Smooth user experience
- Thread-safe communication via Qt signals

---

## 🛡️ Security Considerations

### ✅ Secure Practices
- Private keys **never** leave hardware device
- All cryptographic operations performed on-device
- Transaction details verified before signing
- Clear separation between UI and crypto operations

### ⚠️ User Responsibilities
- Verify recipient address before signing
- Check transaction amount carefully
- Ensure hardware device is authentic
- Keep hardware device firmware updated
- Review verbose logs for unexpected behavior

---

## 🐛 Troubleshooting

### Device Not Detected
```
Problem: No serial ports found
Solution: 
  1. Check USB cable connection
  2. Install CH340/CP2102 drivers if needed
  3. Check device appears in system device manager
  4. Try different USB port
```

### Connection Fails
```
Problem: "Connection error" in log
Solution:
  1. Ensure no other application is using the port
  2. Try unplugging and reconnecting device
  3. Check baud rate is 115200
  4. Verify device powers on (LED indicator)
```

### Transaction Fails
```
Problem: "API ERROR" after broadcast
Solution:
  1. Verify UTXO is still unspent
  2. Check network connectivity
  3. Ensure sufficient balance
  4. Review API response in debug mode
```

### Signature Timeout
```
Problem: "Device did not return signature in time"
Solution:
  1. Enable debug mode to see device responses
  2. Check device is ready (not processing other commands)
  3. Increase timeout in code if needed
  4. Verify device firmware supports signing
```

---

## 📊 Example Workflow

```
1. [User] Scan ports → [App] Detects /dev/ttyUSB0

2. [User] Connect → [App] Opens serial port
                  → [Device] Sends "READY"
                  → [App] Requests address
                  → [Device] Returns "abc123def456"

3. [User] Get Balance → [App] API call to get_balance
                      → [API] Returns balance: 10, UTXOs: 2

4. [User] Selects UTXO (5 units)
          Enters: Value=3, To=7214
          Clicks "Sign"
   
   → [App] Builds TX string: "abc123|txid456|7214|3"
   → [App] Sends to device: {"sign": "..."}
   → [Device] Computes signature
   → [Device] Returns: {"sig_res": "abcd..."}

5. [User] Clicks "Broadcast"
   
   → [App] Sends POST to send_transaction API
           Payload: {from, utxo_txid, to, val1:5, val2:3, sig_hex}
   → [API] Validates & broadcasts to blockchain
   → [API] Returns: {status: "ok", txid: "new_tx_123"}
   
6. [App] Auto-refreshes balance
   → Balance now shows: 9 (10 - 3 + 2 change)
   → New UTXO created with value: 2
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/obt-uart-blockchain-tool.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Additional dev tools

# Run tests (if available)
pytest
```

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **PyQt6** for the excellent GUI framework
- **PySerial** for reliable serial communication
- **Anthropic** for Claude AI assistance in development
- ESP32 community for hardware wallet inspiration

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/obt-uart-blockchain-tool/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/obt-uart-blockchain-tool/discussions)
- **Email**: your.email@example.com

---

## 🔮 Roadmap

- [ ] Support for multiple UTXO inputs (batch transactions)
- [ ] Hardware wallet firmware update via application
- [ ] Transaction history viewer
- [ ] QR code scanning for addresses
- [ ] Multi-signature support
- [ ] Integration with additional blockchain networks
- [ ] Offline transaction signing mode
- [ ] Export/import transaction templates

---

**Made with ❤️ for secure blockchain transactions**
