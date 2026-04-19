# Contributing to OBT - UART Blockchain Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Include detailed information**:
   - Python version
   - Operating system
   - Hardware device model
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant log output (enable Debug mode)

### Suggesting Features

1. **Check the roadmap** in README.md
2. **Open a discussion** before submitting a feature request
3. **Explain the use case** and how it benefits users
4. **Consider backward compatibility**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Follow coding standards** (see below)
4. **Write clear commit messages**:
   ```
   Add: New feature description
   Fix: Bug description
   Update: Changes to existing feature
   Refactor: Code restructuring
   ```
5. **Test your changes** thoroughly
6. **Update documentation** if needed
7. **Submit PR** with clear description

## 📝 Coding Standards

### Python Style
- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Maximum line length: **100 characters**
- Use **meaningful variable names**

### Code Organization
```python
# 1. Imports (standard library, third-party, local)
import sys
from datetime import datetime

from PyQt6.QtCore import QObject
import serial

from obt_ui import MainWindow

# 2. Constants
BAUD_RATE = 115200
TIMEOUT = 2

# 3. Classes
class WorkerThread(QObject):
    """Docstring with description"""
    pass

# 4. Functions
def main():
    """Entry point"""
    pass
```

### Comments & Docstrings
```python
def send_transaction(self, to_address: str, from_address: str, 
                     selected_utxos: list, send_value: int):
    """Build transaction and send for signing.
    
    Args:
        to_address: Recipient blockchain address
        from_address: Sender blockchain address
        selected_utxos: List of selected UTXO dictionaries
        send_value: Amount to send in base units
        
    Returns:
        None
        
    Emits:
        signature_received_signal: When signature is obtained
    """
    pass
```

### UI Guidelines
- Use **consistent spacing** (6-10px between elements)
- Follow **existing color scheme**
- Test in both **dark and light themes**
- Test all **font sizes** (11pt, 15pt, 31pt)
- Ensure **accessibility** (keyboard navigation, screen readers)

## 🧪 Testing

### Manual Testing Checklist
- [ ] UART connection/disconnection
- [ ] Address retrieval
- [ ] Balance query
- [ ] UTXO selection
- [ ] Transaction signing
- [ ] Transaction broadcast
- [ ] Error handling
- [ ] UI responsiveness
- [ ] Theme switching
- [ ] Font size changes
- [ ] Panel resizing

### Before Submitting
1. Test on your target platform
2. Enable Debug mode and check logs
3. Test edge cases (no UTXOs, invalid input, etc.)
4. Verify no regression in existing features

## 🏗️ Development Setup

```bash
# 1. Clone your fork
git clone https://github.com/yourusername/obt-uart-blockchain-tool.git
cd obt-uart-blockchain-tool

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development tools
pip install black flake8 mypy pytest

# 5. Run the application
python obt_app.py
```

## 📋 Commit Message Format

```
<type>: <short description>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add support for multiple UTXO inputs

Implement multi-input transaction building with automatic
fee calculation and change distribution.

Closes #42
```

```
fix: Prevent crash on invalid UTXO selection

Added validation to ensure exactly one UTXO is selected
before attempting to build transaction.

Fixes #38
```

## 🔍 Code Review Process

1. **Automated checks** run on every PR
2. **Maintainer review** within 48 hours
3. **Address feedback** in new commits (don't force-push)
4. **Squash commits** before merge (if requested)

## 🤝 Community Guidelines

- **Be respectful** and professional
- **Help others** in discussions and issues
- **Stay on topic** in discussions
- **Search first** before asking questions
- **Provide context** when reporting issues

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- CHANGELOG.md for significant features
- Release notes

---

Thank you for contributing to OBT - UART Blockchain Tool! 🚀
