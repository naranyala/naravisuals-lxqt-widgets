"""NTFS Mount widget - scan and mount NTFS partitions with pkexec privilege escalation."""
import subprocess
import os
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider


def _run_pkexec(command: list[str]) -> tuple[bool, str]:
    """Run a command with pkexec for root privileges."""
    try:
        full_cmd = ["pkexec"] + command
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def _run_cmd(command: list[str]) -> tuple[bool, str]:
    """Run a command without privileges."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


class NtfsMountProvider(WidgetProvider):
    PROVIDER_ID = "ntfs-mount"

    def __init__(self):
        super().__init__()
        self._user = os.environ.get("USER", "user")
        self._mount_base = f"/media/{self._user}"
        self._partitions: list[dict[str, Any]] = []
        self._mounted: list[dict[str, Any]] = []

    def start(self):
        os.makedirs(self._mount_base, exist_ok=True)
        self._scan_partitions()

    def get_data(self) -> dict[str, Any]:
        self._scan_partitions()
        self._scan_mounted()
        return {
            "partitions": self._partitions,
            "mounted": self._mounted,
            "mount_base": self._mount_base,
            "user": self._user,
        }

    def _scan_partitions(self):
        """Scan all NTFS partitions."""
        self._partitions = []
        ok, output = _run_cmd(["lsblk", "-lnpo", "NAME,TYPE,FSTYPE,SIZE,LABEL"])
        if not ok:
            return

        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            name, ptype = parts[0], parts[1]
            fstype = parts[2] if len(parts) > 2 else ""
            size = parts[3] if len(parts) > 3 else ""
            label = parts[4] if len(parts) > 4 else ""

            if ptype == "part" and "loop" not in name:
                # Get UUID
                ok, uuid_out = _run_cmd(["blkid", "-s", "UUID", "-o", "value", name])
                uuid = uuid_out if ok else ""

                # Check if NTFS
                is_ntfs = "ntfs" in fstype.lower()

                self._partitions.append({
                    "name": name,
                    "fstype": fstype,
                    "size": size,
                    "label": label or uuid[:8] if uuid else "Unknown",
                    "uuid": uuid,
                    "is_ntfs": is_ntfs,
                })

    def _scan_mounted(self):
        """Scan currently mounted NTFS partitions."""
        self._mounted = []
        ok, output = _run_cmd(["mount", "-t", "ntfs3,ntfs"])
        if not ok:
            # Try alternative
            ok, output = _run_cmd(["findmnt", "-t", "ntfs3,ntfs", "-o", "SOURCE,TARGET,FSTYPE,OPTIONS"])
        if not ok:
            return

        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                self._mounted.append({
                    "source": parts[0],
                    "target": parts[1],
                })

    def mount_partition(self, partition_name: str) -> tuple[bool, str]:
        """Mount an NTFS partition using pkexec."""
        # Find partition info
        part_info = None
        for p in self._partitions:
            if p["name"] == partition_name:
                part_info = p
                break

        if not part_info:
            return False, f"Partition {partition_name} not found"

        # Create mount point
        mount_point = f"{self._mount_base}/{part_info['label']}"
        os.makedirs(mount_point, exist_ok=True)

        # Mount with pkexec
        ok, msg = _run_pkexec(["mount", "-t", "ntfs3", partition_name, mount_point])
        if ok:
            return True, f"Mounted at {mount_point}"
        else:
            # Try ntfs-3g as fallback
            ok, msg = _run_pkexec(["mount", "-t", "ntfs-3g", partition_name, mount_point])
            if ok:
                return True, f"Mounted at {mount_point}"
            return False, msg

    def unmount_partition(self, mount_point: str) -> tuple[bool, str]:
        """Unmount a partition using pkexec."""
        ok, msg = _run_pkexec(["umount", mount_point])
        if ok:
            return True, f"Unmounted {mount_point}"
        return False, msg
