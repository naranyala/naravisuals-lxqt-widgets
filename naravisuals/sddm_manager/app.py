import sys
import os
import subprocess
import configparser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class SDDMManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals SDDM Manager")
        self.setGeometry(100, 100, 500, 400)
        
        self.selected_image = None
        self.theme_dir = "/usr/share/sddm/themes"
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        header = QLabel("<h2>🔒 SDDM Login Manager</h2>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Theme Selector
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("<b>Target Theme:</b>"))
        self.theme_selector = QComboBox()
        self.populate_themes()
        theme_row.addWidget(self.theme_selector)
        layout.addLayout(theme_row)
        
        # Image Preview
        self.preview_lbl = QLabel("No Image Selected")
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.setFrameShape(QFrame.Shape.Box)
        self.preview_lbl.setFixedSize(450, 250)
        self.preview_lbl.setStyleSheet("background-color: #222; color: #888;")
        layout.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        btn_row = QHBoxLayout()
        pick_btn = QPushButton("🖼️ Browse Image...")
        pick_btn.clicked.connect(self.pick_image)
        btn_row.addWidget(pick_btn)
        
        apply_btn = QPushButton("💾 Apply to SDDM (Requires Password)")
        apply_btn.clicked.connect(self.apply_background)
        apply_btn.setStyleSheet("background-color: #0082fc; color: white; font-weight: bold;")
        btn_row.addWidget(apply_btn)
        layout.addLayout(btn_row)
        
    def populate_themes(self):
        if os.path.exists(self.theme_dir):
            themes = [d for d in os.listdir(self.theme_dir) if os.path.isdir(os.path.join(self.theme_dir, d))]
            self.theme_selector.addItems(themes)
            
            # Try to guess current theme
            if os.path.exists("/etc/sddm.conf"):
                parser = configparser.ConfigParser()
                parser.read("/etc/sddm.conf")
                if "Theme" in parser and "Current" in parser["Theme"]:
                    current = parser["Theme"]["Current"]
                    if current in themes:
                        self.theme_selector.setCurrentText(current)
        else:
            self.theme_selector.addItem("SDDM not found")
            self.theme_selector.setEnabled(False)
            
    def pick_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_image = file_path
            pix = QPixmap(file_path)
            # Scale dynamically while preserving aspect ratio
            self.preview_lbl.setPixmap(pix.scaled(self.preview_lbl.width(), self.preview_lbl.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
            self.preview_lbl.setText("")
            
    def apply_background(self):
        if not self.selected_image:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
            
        theme = self.theme_selector.currentText()
        if theme == "SDDM not found":
            return
            
        target_dir = os.path.join(self.theme_dir, theme)
        target_conf = os.path.join(target_dir, "theme.conf")
        target_img = os.path.join(target_dir, "naravisuals_bg.jpg")
        
        # pkexec script to overwrite the background file and update the SDDM theme.conf
        script = f"""
        cp "{self.selected_image}" "{target_img}" && \
        chmod 644 "{target_img}" && \
        sed -i 's/^background=.*$/background=naravisuals_bg.jpg/' "{target_conf}"
        """
        
        try:
            # Pkexec invokes Polkit authentication
            process = subprocess.Popen(['pkexec', 'bash', '-c', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                QMessageBox.information(self, "Success", f"Successfully updated SDDM background for theme '{theme}'!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to apply background. Password cancelled or denied.\\n{stderr.decode()}")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "pkexec not found. Is polkit installed?")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SDDMManagerWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
