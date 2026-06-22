"""NTFS Mount widget - scan and mount NTFS partitions with GUI."""
import subprocess
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox, QFrame
)

from naravisuals.core.base_widget import PanelWidget


class NtfsMountWidget(PanelWidget):
    WIDGET_NAME = "NTFS Mount"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(10000)  # Refresh every 10 seconds

        self._user = os.environ.get("USER", "user")
        self._mount_base = f"/media/{self._user}"

        # Header
        header = QLabel("NTFS Partition Manager")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        self._layout.addWidget(header)

        # Partition list
        self._partition_list = QListWidget()
        self._partition_list.setMaximumHeight(120)
        self._layout.addWidget(self._partition_list)

        # Buttons
        btn_layout = QHBoxLayout()

        self._mount_btn = QPushButton("Mount")
        self._mount_btn.clicked.connect(self._mount_selected)
        btn_layout.addWidget(self._mount_btn)

        self._unmount_btn = QPushButton("Unmount")
        self._unmount_btn.clicked.connect(self._unmount_selected)
        btn_layout.addWidget(self._unmount_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._scan_partitions)
        btn_layout.addWidget(refresh_btn)

        self._layout.addLayout(btn_layout)

        # Status label
        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("color: #888; font-size: 10px;")
        self._layout.addWidget(self._status_label)

        # Load partitions
        self._scan_partitions()

    def _on_tick(self):
        self._scan_partitions()

    def _scan_partitions(self):
        """Scan available partitions."""
        self._partition_list.clear()

        try:
            result = subprocess.run(
                ["lsblk", "-lnpo", "NAME,TYPE,FSTYPE,SIZE,LABEL"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                self._status_label.setText("Error scanning partitions")
                return

            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) < 3:
                    continue

                name, ptype = parts[0], parts[1]
                fstype = parts[2] if len(parts) > 2 else ""
                size = parts[3] if len(parts) > 3 else ""
                label = parts[4] if len(parts) > 4 else ""

                if ptype == "part" and "loop" not in name:
                    # Get UUID
                    uuid_result = subprocess.run(
                        ["blkid", "-s", "UUID", "-o", "value", name],
                        capture_output=True, text=True, timeout=5
                    )
                    uuid = uuid_result.stdout.strip() if uuid_result.returncode == 0 else ""

                    display_name = label or uuid[:8] if uuid else name
                    is_ntfs = "ntfs" in fstype.lower()

                    item_text = f"{display_name} ({size}) - {fstype}"
                    if is_ntfs:
                        item_text += " [NTFS]"

                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, {
                        "name": name,
                        "fstype": fstype,
                        "size": size,
                        "label": label,
                        "uuid": uuid,
                        "is_ntfs": is_ntfs,
                    })
                    self._partition_list.addItem(item)

            self._status_label.setText(f"Found {self._partition_list.count()} partitions")

        except Exception as e:
            self._status_label.setText(f"Error: {e}")

    def _mount_selected(self):
        """Mount the selected NTFS partition."""
        item = self._partition_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a partition to mount.")
            return

        data = item.data(Qt.ItemDataRole.UserRole)
        if not data["is_ntfs"]:
            reply = QMessageBox.question(
                self, "Non-NTFS Partition",
                f"Partition {data['name']} is {data['fstype']}, not NTFS.\nMount anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Create mount point
        mount_point = f"{self._mount_base}/{data['label'] or data['uuid'][:8]}"
        os.makedirs(mount_point, exist_ok=True)

        # Mount with pkexec
        self._status_label.setText(f"Mounting {data['name']}...")
        try:
            result = subprocess.run(
                ["pkexec", "mount", "-t", "ntfs3", data["name"], mount_point],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self._status_label.setText(f"Mounted at {mount_point}")
                QMessageBox.information(self, "Success", f"Mounted at:\n{mount_point}")
            else:
                # Try ntfs-3g as fallback
                result = subprocess.run(
                    ["pkexec", "mount", "-t", "ntfs-3g", data["name"], mount_point],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    self._status_label.setText(f"Mounted at {mount_point}")
                    QMessageBox.information(self, "Success", f"Mounted at:\n{mount_point}")
                else:
                    self._status_label.setText(f"Mount failed: {result.stderr}")
                    QMessageBox.critical(self, "Error", f"Failed to mount:\n{result.stderr}")
        except Exception as e:
            self._status_label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"Mount failed:\n{e}")

    def _unmount_selected(self):
        """Unmount the selected partition."""
        item = self._partition_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a partition to unmount.")
            return

        data = item.data(Qt.ItemDataRole.UserRole)
        mount_point = f"{self._mount_base}/{data['label'] or data['uuid'][:8]}"

        if not os.path.exists(mount_point):
            QMessageBox.warning(self, "Not Mounted", f"Mount point does not exist:\n{mount_point}")
            return

        reply = QMessageBox.question(
            self, "Unmount",
            f"Unmount {mount_point}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._status_label.setText(f"Unmounting {mount_point}...")
        try:
            result = subprocess.run(
                ["pkexec", "umount", mount_point],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self._status_label.setText(f"Unmounted {mount_point}")
                QMessageBox.information(self, "Success", f"Unmounted:\n{mount_point}")
            else:
                self._status_label.setText(f"Unmount failed: {result.stderr}")
                QMessageBox.critical(self, "Error", f"Failed to unmount:\n{result.stderr}")
        except Exception as e:
            self._status_label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"Unmount failed:\n{e}")


if __name__ == "__main__":
    NtfsMountWidget.launch_standalone()
