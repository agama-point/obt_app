# Changelog

All notable changes to OBT - UART Blockchain Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-04-19

### Added
- Initial release of OBT - UART Blockchain Tool
- UART serial communication with ESP32 hardware wallets
- Automatic public key/address retrieval from device
- Balance and UTXO query via blockchain API
- Transaction building with UTXO selection
- Hardware-based transaction signing
- Transaction broadcasting to blockchain network
- UTXO model with automatic change handling
- Dark and light theme support
- Adjustable font sizes (11pt, 15pt, 31pt)
- Resizable UI panels with drag-and-drop splitter
- Real-time verbose logging with color coding
- Debug mode for detailed protocol traces
- Connection state management
- Error handling and validation
- Auto-refresh balance after successful broadcast

### Features
- PyQt6-based modern GUI
- Thread-safe worker for I/O operations
- HTML-formatted log output
- Monospace fonts for technical data
- Status indicators for connection state
- UTXO checkbox selection
- Transaction validation (value checks)
- Signature verification
- API error reporting

### Security
- Private keys remain on hardware device
- All signatures generated on-device
- Transaction verification before signing
- Clear logging of all operations

---

## [Unreleased]

### Planned
- Support for multiple UTXO inputs
- Hardware wallet firmware updates
- Transaction history viewer
- QR code address scanning
- Multi-signature transactions
- Additional blockchain network support
- Offline signing mode
- Transaction templates

---

## Version History

- **1.0.0** (2025-04-19) - Initial release
