# obt_ui.py
# UI layer for OBT application

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QCheckBox, QLineEdit, QLabel,
    QTextBrowser, QGroupBox, QComboBox, QScrollArea, QMessageBox,
    QRadioButton, QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSlot, QMetaObject
from PyQt6.QtGui import QFont
# Přidán import pro práci s SVG logem
from PyQt6.QtSvgWidgets import QSvgWidget


class MainWindow(QWidget):
    def __init__(self, worker):
        super().__init__()
        self._worker = worker
        self.setWindowTitle("OBT | UART Blockchain Tool")
        self.resize(900, 680)
        self.setMinimumWidth(750)
        self.setMaximumHeight(680)

        # Connect signals from worker
        self._worker.log_signal.connect(self._append_log)
        self._worker.status_signal.connect(self._set_status)
        self._worker.ports_found_signal.connect(self._update_port_list)
        self._worker.connected_signal.connect(self._on_connection_changed)
        self._worker.address_received_signal.connect(self._set_device_address)
        self._worker.balance_received_signal.connect(self._display_balance)
        self._worker.signature_received_signal.connect(self._on_signature_received)
        self._worker.transaction_broadcast_signal.connect(self._on_broadcast_result)
        self._worker.encrypt_received_signal.connect(self._on_encrypt_result)
        self._worker.decrypt_received_signal.connect(self._on_decrypt_result)

        self._utxo_checkboxes = []  # Store checkboxes for UTXOs
        self._current_font_size = 11  # Default font size
        self.FixedWidth = 90
        self.BtnWidth = 135

        self._build_ui()
        self.apply_dark_theme()

    # ------------------------------------------------------------------ #
    #  Layout                                                            #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial sizes (left panel narrower, right panel wider)
        # Total width ~1000, left gets 300, right gets 700
        splitter.setSizes([300, 700])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, stretch=1)

        # Bottom bar
        bottom = QHBoxLayout()
        clear_btn = QPushButton("Clear log")
        clear_btn.clicked.connect(self.log_box.clear)
        clear_btn.setFixedWidth(100)

        note_label = QLabel("Alice: 7214 | Bob: 83ca")
        note_label.setStyleSheet("color: #888; font-style: italic;")


        # Font size selector
        font_size_label = QLabel("Font size:")
        
        self.font_size_group = QButtonGroup(self)
        self.font_radio_1 = QRadioButton("1")
        self.font_radio_2 = QRadioButton("2")
        self.font_radio_3 = QRadioButton("3")
        
        self.font_size_group.addButton(self.font_radio_1, 1)
        self.font_size_group.addButton(self.font_radio_2, 2)
        self.font_size_group.addButton(self.font_radio_3, 3)
        
        self.font_radio_1.setChecked(True)  # Default: size 1 (11pt)
        
        self.font_radio_1.toggled.connect(lambda: self._change_font_size(11))
        self.font_radio_2.toggled.connect(lambda: self._change_font_size(13))
        self.font_radio_3.toggled.connect(lambda: self._change_font_size(17))

        self.theme_toggle = QCheckBox("Dark mode")
        self.theme_toggle.setChecked(True)
        self.theme_toggle.stateChanged.connect(self._toggle_theme)

        self.debug_checkbox = QCheckBox("Debug")
        self.debug_checkbox.stateChanged.connect(
            lambda state: self._worker.set_debug_mode(state == Qt.CheckState.Checked.value)
        )

        self.led1_checkbox = QCheckBox("L1")
        self.led1_checkbox.setEnabled(False)
        self.led1_checkbox.stateChanged.connect(self._on_led1_changed)

        bottom.addWidget(clear_btn)
        bottom.addWidget(note_label)
        bottom.addStretch()
        bottom.addWidget(self.debug_checkbox)
        bottom.addWidget(self.led1_checkbox)
        bottom.addStretch()
        bottom.addWidget(font_size_label)
        bottom.addWidget(self.font_radio_1)
        bottom.addWidget(self.font_radio_2)
        bottom.addWidget(self.font_radio_3)
        bottom.addSpacing(20)
        bottom.addWidget(self.theme_toggle)
        root.addLayout(bottom)

    # ------------------------------------------------------------------ #
    #  Left panel                                                        #
    # ------------------------------------------------------------------ #
    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(10)

        layout.addWidget(self._group_uart())
        layout.addWidget(self._group_connection())
        layout.addWidget(self._group_balance())
        layout.addWidget(self._group_payment())
        layout.addStretch()
        layout.addWidget(self._group_crypto())

        return panel

    def _group_uart(self) -> QGroupBox:
        """UART – scanning and port selection"""
        grp = QGroupBox("UART")
        lay = QVBoxLayout(grp)
        lay.setSpacing(6)

        # Scan button + status
        row = QHBoxLayout()
        self.scan_btn = QPushButton("⟳  Scan ports")
        self.scan_btn.clicked.connect(self._worker.scan_ports)
        self.scan_btn.setFixedWidth(self.BtnWidth)

        self.status_label = QLabel("● Idle")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        row.addWidget(self.scan_btn)
        row.addStretch()
        row.addWidget(self.status_label)
        lay.addLayout(row)

        # Port selector
        port_row = QHBoxLayout()
        port_lbl = QLabel("Port:")
        port_lbl.setFixedWidth(42)
        self.port_combo = QComboBox()
        self.port_combo.setFont(QFont("Monospace"))
        self.port_combo.setEnabled(False)
        port_row.addWidget(port_lbl)
        port_row.addWidget(self.port_combo, stretch=1)
        lay.addLayout(port_row)

        return grp

    def _group_connection(self) -> QGroupBox:
        """Connection – connect and display address"""
        grp = QGroupBox("Connection")
        lay = QVBoxLayout(grp)
        lay.setSpacing(6)

        # Connect button + Address in one row
        conn_row = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._toggle_connection)
        self.connect_btn.setEnabled(False)
        self.connect_btn.setFixedWidth(self.BtnWidth)  # Same width as Scan ports
        
        addr_lbl = QLabel("Address:")
        addr_lbl.setFixedWidth(self.FixedWidth)
        
        self.addr_label = QLabel("—")
        self.addr_label.setFont(QFont("Monospace"))
        self.addr_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.addr_label.setFixedWidth(60)  # Max 6 chars
        
        conn_row.addWidget(self.connect_btn)
        conn_row.addWidget(addr_lbl)
        conn_row.addWidget(self.addr_label)
        conn_row.addStretch()
        lay.addLayout(conn_row)

        return grp

    def _group_balance(self) -> QGroupBox:
        """Balance – Get Balance button and UTXO list"""
        grp = QGroupBox("Balance")
        lay = QVBoxLayout(grp)
        lay.setSpacing(6)

        # Get Balance button + Balance value in one row
        bal_row = QHBoxLayout()
        
        self.get_balance_btn = QPushButton("Get Balance")
        self.get_balance_btn.clicked.connect(self._on_get_balance)
        self.get_balance_btn.setEnabled(False)
        self.get_balance_btn.setFixedWidth(self.BtnWidth)
        
        self.balance_label = QLabel("—")
        self.balance_label.setFont(QFont("Monospace", -1, QFont.Weight.Bold))
        self.balance_label.setFixedWidth(40)  # Max 3 chars
        
        bal_row.addWidget(self.get_balance_btn)
        bal_row.addWidget(self.balance_label)
        bal_row.addStretch()
        lay.addLayout(bal_row)

        # UTXOs label
        utxo_lbl = QLabel("UTXOs (select to spend):")
        utxo_lbl.setObjectName("smallLabel")
        utxo_lbl.setStyleSheet("color: #888;")
        lay.addWidget(utxo_lbl)

        # Scrollable area for UTXOs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # scroll.setMaximumHeight(200)
        scroll.setFixedHeight(180)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #555; border-radius: 4px; }")
        
        self.utxo_container = QWidget()
        self.utxo_layout = QVBoxLayout(self.utxo_container)
        self.utxo_layout.setContentsMargins(4, 4, 4, 4)
        self.utxo_layout.setSpacing(2)
        self.utxo_layout.addStretch()
        
        scroll.setWidget(self.utxo_container)
        lay.addWidget(scroll)

        return grp

    def _group_payment(self) -> QGroupBox:
        """Payment – sign and broadcast transaction"""
        grp = QGroupBox("Payment")
        lay = QVBoxLayout(grp)
        lay.setSpacing(6)

        # Value and To address in one row
        inputs_row = QHBoxLayout()
        
        value_lbl = QLabel("Value:")
        value_lbl.setFixedWidth(50)
        
        self.value_input = QLineEdit()
        self.value_input.setText("1")  # Default: 1 unit
        self.value_input.setPlaceholderText("Value")
        self.value_input.setFont(QFont("Monospace"))
        self.value_input.setEnabled(False)
        self.value_input.setFixedWidth(40)  # Max 3 chars
        
        to_lbl = QLabel("To:")
        to_lbl.setFixedWidth(30)
        
        self.to_input = QLineEdit()
        self.to_input.setText("7214")  # Pre-fill with default target
        self.to_input.setPlaceholderText("Address")
        self.to_input.setFont(QFont("Monospace"))
        self.to_input.setEnabled(False)
        self.to_input.setFixedWidth(60)  # Max 6 chars
        
        inputs_row.addWidget(value_lbl)
        inputs_row.addWidget(self.value_input)
        inputs_row.addWidget(to_lbl)
        inputs_row.addWidget(self.to_input)
        inputs_row.addStretch()
        lay.addLayout(inputs_row)

        # Two separate buttons: Sign and Broadcast
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        
        self.sign_btn = QPushButton("🔏 Sign Transaction")
        self.sign_btn.setEnabled(False)
        self.sign_btn.clicked.connect(self._on_sign_transaction)
        
        self.broadcast_btn = QPushButton("📡 Broadcast")
        self.broadcast_btn.setEnabled(False)
        self.broadcast_btn.clicked.connect(self._on_broadcast_transaction)
        
        btn_row.addWidget(self.sign_btn, stretch=1)
        btn_row.addWidget(self.broadcast_btn, stretch=1)
        lay.addLayout(btn_row)

        return grp

    def _group_crypto(self) -> QGroupBox:
        """Crypto – encrypt and decrypt via ESP32"""
        grp = QGroupBox("Crypto")
        lay = QVBoxLayout(grp)
        lay.setSpacing(6)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.encrypt_btn = QPushButton("🔐 Encrypt")
        self.encrypt_btn.setEnabled(False)
        self.encrypt_btn.clicked.connect(self._on_encrypt)

        self.decrypt_btn = QPushButton("🔓 Decrypt")
        self.decrypt_btn.setEnabled(False)
        self.decrypt_btn.clicked.connect(self._on_decrypt)

        btn_row.addWidget(self.encrypt_btn, stretch=1)
        btn_row.addWidget(self.decrypt_btn, stretch=1)
        lay.addLayout(btn_row)

        # Input field
        input_row = QHBoxLayout()
        input_lbl = QLabel("Input:")
        input_lbl.setFixedWidth(42)
        self.crypto_input = QLineEdit()
        self.crypto_input.setPlaceholderText("text or hex (max 30)")
        self.crypto_input.setMaxLength(30)
        self.crypto_input.setFont(QFont("Monospace"))
        self.crypto_input.setEnabled(False)
        input_row.addWidget(input_lbl)
        input_row.addWidget(self.crypto_input)
        lay.addLayout(input_row)

        # Output label
        out_row = QHBoxLayout()
        out_lbl = QLabel("Output:")
        out_lbl.setFixedWidth(42)
        self.crypto_output = QLabel("—")
        self.crypto_output.setFont(QFont("Monospace"))
        self.crypto_output.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.crypto_output.setWordWrap(True)
        out_row.addWidget(out_lbl)
        out_row.addWidget(self.crypto_output, stretch=1)
        lay.addLayout(out_row)

        return grp

    # ------------------------------------------------------------------ #
    #  Right panel – log                                                 #
    # ------------------------------------------------------------------ #
    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 0, 0, 0)
        layout.setSpacing(4)

        # 1) Přidání loga nahoru vpravo nad log
        self.logo_widget = QSvgWidget("obt_logo.svg")
        self.logo_widget.setFixedWidth(500)
        self.logo_widget.setFixedHeight(85)  # Výška přizpůsobená pro zachování poměru
        layout.addWidget(self.logo_widget, alignment=Qt.AlignmentFlag.AlignLeft)

        log_label = QLabel("Verbose Log")
        log_label.setObjectName("smallLabel")
        log_label.setFont(QFont("Monospace"))
        log_label.setStyleSheet("color: #888;")
        layout.addWidget(log_label)

        self.log_box = QTextBrowser()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Monospace"))
        self.log_box.setOpenExternalLinks(False)
        layout.addWidget(self.log_box, stretch=1)

        return panel

    # ------------------------------------------------------------------ #
    #  Slots / handlers                                                  #
    # ------------------------------------------------------------------ #
    @pyqtSlot(str)
    def _append_log(self, html_msg: str):
        """Append message to log"""
        self.log_box.append(html_msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    @pyqtSlot(list)
    def _update_port_list(self, ports: list):
        """Update list of found ports"""
        self.port_combo.clear()
        if ports:
            for device, description in ports:
                self.port_combo.addItem(description, device)
            self.port_combo.setEnabled(True)
            self.connect_btn.setEnabled(True)
        else:
            self.port_combo.setEnabled(False)
            self.connect_btn.setEnabled(False)

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool):
        """React to connection state change"""
        self.connect_btn.setText("Disconnect" if connected else "Connect")
        self.scan_btn.setEnabled(not connected)
        self.port_combo.setEnabled(not connected)
        
        # Enable balance & payment controls when connected
        self.get_balance_btn.setEnabled(connected)
        self.value_input.setEnabled(connected)
        self.to_input.setEnabled(connected)
        self.sign_btn.setEnabled(connected)

        # Enable crypto controls when connected
        self.encrypt_btn.setEnabled(connected)
        self.decrypt_btn.setEnabled(connected)
        self.crypto_input.setEnabled(connected)

        # Enable LED1 control when connected
        self.led1_checkbox.setEnabled(connected)
        if not connected:
            self.led1_checkbox.setChecked(False)
        
        # Broadcast starts disabled until signature is received
        if not connected:
            self.broadcast_btn.setEnabled(False)

    @pyqtSlot(str)
    def _set_device_address(self, address: str):
        """Display received device address"""
        self.addr_label.setText(address)

    @pyqtSlot(str)
    def _on_signature_received(self, signature: str):
        """Handle received signature from device"""
        # Enable broadcast button when signature is received
        self.broadcast_btn.setEnabled(True)
        
        # Optional: Show a subtle notification
        # (The signature is already logged verbosely by the worker)

    @pyqtSlot(dict)
    def _on_broadcast_result(self, result: dict):
        """Handle broadcast transaction result"""
        if result.get("status") == "ok":
            txid = result.get("txid", "N/A")
            message = result.get("message", "Transaction broadcasted successfully")
            
            QMessageBox.information(
                self,
                "✓ Broadcast Success",
                f"{message}\n\nNew TXID:\n{txid}"
            )
            
            # Disable broadcast button after successful send
            self.broadcast_btn.setEnabled(False)
            
        else:
            message = result.get("message", "Unknown error")
            QMessageBox.warning(
                self,
                "❌ Broadcast Failed",
                f"Transaction broadcast failed:\n\n{message}"
            )

    @pyqtSlot(dict)
    def _display_balance(self, data: dict):
        """Display balance and UTXOs"""
        balance = data.get("balance", 0)
        self.balance_label.setText(f"{balance}")
        
        # Clear previous UTXOs
        for cb in self._utxo_checkboxes:
            cb.deleteLater()
        self._utxo_checkboxes.clear()
        
        # Add new UTXOs
        utxos = data.get("unspent_outputs", [])
        for utxo in utxos:
            # FIX: Convert txid to string to handle integer values from API
            txid = str(utxo.get("txid", ""))
            value = utxo.get("value", 0)
            
            cb = QCheckBox(f"{txid[:20]}... | {value} units")
            cb.setFont(QFont("Monospace"))
            cb.setProperty("utxo_data", utxo)
            
            self._utxo_checkboxes.append(cb)
            self.utxo_layout.insertWidget(self.utxo_layout.count() - 1, cb)

    @pyqtSlot(str)
    def _set_status(self, text: str):
        """Set status label"""
        colors = {
            "Connected":    "#4caf50",
            "Scanning …":    "#ffb300",
            "Connecting …": "#ffb300",
            "Idle":          "#9e9e9e",
        }
        color = colors.get(text, "#f44336")
        self.status_label.setText(f"● {text}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _toggle_connection(self):
        """Toggle connection state"""
        if self.connect_btn.text() == "Connect":
            selected_port = self.port_combo.currentData()
            if selected_port:
                self._worker.connect_port(selected_port)
        else:
            self._worker.disconnect_port()

    def _on_get_balance(self):
        """Call worker to get balance"""
        address = self.addr_label.text()
        if address and address != "—":
            self._worker.get_balance(address)

    def _on_sign_transaction(self):
        """Sign transaction with device"""
        to_addr = self.to_input.text().strip()
        from_addr = self.addr_label.text()
        
        if not to_addr:
            QMessageBox.warning(self, "Input Error", "Please enter recipient address")
            return
        
        # Validate value
        value_text = self.value_input.text().strip()
        try:
            send_value = int(value_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Value must be a valid integer")
            return
        
        if send_value <= 0:
            QMessageBox.warning(self, "Input Error", "Value must be greater than 0")
            return
        
        # Collect selected UTXOs
        selected = []
        for cb in self._utxo_checkboxes:
            if cb.isChecked():
                selected.append(cb.property("utxo_data"))
        
        if not selected:
            QMessageBox.warning(self, "Selection Error", "Please select exactly one UTXO to spend")
            return
        
        if len(selected) > 1:
            QMessageBox.warning(self, "Selection Error", "Please select exactly ONE UTXO (multiple inputs not supported)")
            return
        
        # Validate value against selected UTXO
        utxo_value = selected[0].get("value", 0)
        if send_value > utxo_value:
            QMessageBox.warning(
                self, 
                "Input Error", 
                f"Value ({send_value}) cannot be greater than UTXO value ({utxo_value})"
            )
            return
        
        # Disable broadcast button before signing (will be re-enabled when signature arrives)
        self.broadcast_btn.setEnabled(False)
        
        # Call worker to sign with specified value
        self._worker.send_transaction(to_addr, from_addr, selected, send_value)

    def _on_broadcast_transaction(self):
        """Broadcast signed transaction to blockchain"""
        # Call worker to broadcast
        QMetaObject.invokeMethod(
            self._worker,
            "broadcast_transaction",
            Qt.ConnectionType.QueuedConnection
        )

    def _on_led1_changed(self, state: int):
        """Send LED1 on/off command to device"""
        self._worker.set_led1(state == Qt.CheckState.Checked.value)

    def _on_encrypt(self):
        """Send text to ESP32 for encryption"""
        text = self.crypto_input.text().strip()
        if not text:
            return
        self.crypto_output.setText("…")
        self._worker.encrypt_text(text)

    def _on_decrypt(self):
        """Send hex to ESP32 for decryption"""
        hex_str = self.crypto_input.text().strip()
        if not hex_str:
            return
        self.crypto_output.setText("…")
        self._worker.decrypt_hex(hex_str)

    @pyqtSlot(str)
    def _on_encrypt_result(self, result: str):
        """Display encryption result"""
        self.crypto_output.setText(result)

    @pyqtSlot(str)
    def _on_decrypt_result(self, result: str):
        """Display decryption result"""
        self.crypto_output.setText(result)

    # ------------------------------------------------------------------ #
    #  Themes                                                            #
    # ------------------------------------------------------------------ #
    def _change_font_size(self, size: int):
        """Change font size for entire application"""
        if self.sender() and self.sender().isChecked():
            self._current_font_size = size
            # Reapply current theme to update font size
            if self.theme_toggle.isChecked():
                self.apply_dark_theme()
            else:
                self.apply_light_theme()
    
    def _toggle_theme(self):
        if self.theme_toggle.isChecked():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        # Calculate related sizes based on font size
        base_size = self._current_font_size
        small_size = max(8, int(base_size * 0.73))  # ~8pt for 11pt base
        mono_size = max(9, int(base_size * 0.82))   # ~9pt for 11pt base
        bold_size = max(10, int(base_size * 0.91))  # ~10pt for 11pt base
        
        self.setStyleSheet(f"""
            QWidget {{ 
                background: #2b2b2b; 
                color: #e0e0e0;
                font-size: {base_size}pt;
            }}
            QGroupBox {{
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 4px;
                font-weight: bold;
                color: #aaa;
                font-size: {small_size}pt;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}
            QTextBrowser, QLineEdit {{
                background: #1e1e1e;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                font-size: {mono_size}pt;
                font-family: Monospace;
            }}
            QComboBox {{
                background: #1e1e1e;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: {mono_size}pt;
                font-family: Monospace;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: #1e1e1e;
                selection-background-color: #3c3c3c;
                font-size: {mono_size}pt;
            }}
            QPushButton {{
                background: #3c3c3c;
                border: 1px solid #555;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: {base_size}pt;
            }}
            QPushButton:hover    {{ background: #505050; }}
            QPushButton:pressed  {{ background: #2a2a2a; }}
            QPushButton:disabled {{ color: #555; background: #2e2e2e; border-color: #3a3a3a; }}
            QLineEdit:disabled   {{ color: #555; }}
            QComboBox:disabled   {{ color: #555; }}
            QCheckBox {{ 
                spacing: 5px;
                font-size: {base_size}pt;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background: #e8e8e8;
                border: 1px solid #888;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background: #4caf50;
                border-color: #4caf50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+PC9zdmc+);
            }}
            QRadioButton {{
                font-size: {base_size}pt;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background: #e8e8e8;
                border: 1px solid #888;
                border-radius: 8px;
            }}
            QRadioButton::indicator:checked {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #4caf50, stop:0.5 #4caf50, stop:0.51 #e8e8e8, stop:1 #e8e8e8);
                border: 1px solid #4caf50;
            }}
            QLabel {{
                font-size: {base_size}pt;
            }}
            QLabel#smallLabel {{
                font-size: {small_size}pt;
            }}
            QSplitter::handle {{ background: #444; }}
            QScrollArea {{ background: transparent; }}
        """)
 
    def apply_light_theme(self):
        # Calculate related sizes based on font size
        base_size = self._current_font_size
        small_size = max(8, int(base_size * 0.73))  # ~8pt for 11pt base
        mono_size = max(9, int(base_size * 0.82))   # ~9pt for 11pt base
        bold_size = max(10, int(base_size * 0.91))  # ~10pt for 11pt base
        
        self.setStyleSheet(f"""
            QWidget {{ 
                background: #f0f0f0; 
                color: #222;
                font-size: {base_size}pt;
            }}
            QGroupBox {{
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 4px;
                font-weight: bold;
                color: #555;
                font-size: {small_size}pt;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}
            QTextBrowser, QLineEdit {{
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                font-size: {mono_size}pt;
                font-family: Monospace;
            }}
            QComboBox {{
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: {mono_size}pt;
                font-family: Monospace;
            }}
            QPushButton {{
                background: #e1e1e1;
                border: 1px solid #bbb;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: {base_size}pt;
            }}
            QPushButton:hover    {{ background: #d0d0d0; }}
            QPushButton:disabled {{ color: #aaa; }}
            QCheckBox {{ 
                spacing: 5px;
                font-size: {base_size}pt;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background: white;
                border: 1px solid #999;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background: #4caf50;
                border-color: #4caf50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+PC9zdmc+);
            }}
            QRadioButton {{
                font-size: {base_size}pt;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background: white;
                border: 1px solid #999;
                border-radius: 8px;
            }}
            QRadioButton::indicator:checked {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #4caf50, stop:0.5 #4caf50, stop:0.51 white, stop:1 white);
                border: 1px solid #4caf50;
            }}
            QLabel {{
                font-size: {base_size}pt;
            }}
            QLabel#smallLabel {{
                font-size: {small_size}pt;
            }}
            QSplitter::handle {{ background: #ccc; }}
            QScrollArea {{ background: transparent; }}
        """)
