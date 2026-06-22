"""System data providers for CPU, RAM, disk, network, battery, uptime, etc."""
import time
from typing import Any

import psutil

from naravisuals.daemon.dbus_service import WidgetProvider


def _format_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


class SystemMonitorProvider(WidgetProvider):
    PROVIDER_ID = "system-monitor"

    def __init__(self):
        super().__init__()
        self._last_net = 0
        self._interface = None  # None = all interfaces

    def start(self):
        self._last_net = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )

    def get_data(self) -> dict[str, Any]:
        cpu_total = psutil.cpu_percent(interval=0)
        cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        swap = psutil.swap_memory()

        now = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        net_rate = now - self._last_net
        self._last_net = now

        # Temperature sensors (if available)
        temps = {}
        try:
            for name, entries in psutil.sensors_temperatures().items():
                if entries:
                    temps[name] = entries[0].current
        except (AttributeError, Exception):
            pass

        return {
            "cpu_percent": cpu_total,
            "cpu_per_core": cpu_per_core,
            "cpu_count": psutil.cpu_count(),
            "ram_percent": mem.percent,
            "ram_used": _format_bytes(mem.used),
            "ram_total": _format_bytes(mem.total),
            "disk_percent": disk.percent,
            "disk_used": _format_bytes(disk.used),
            "disk_total": _format_bytes(disk.total),
            "swap_percent": swap.percent,
            "swap_used": _format_bytes(swap.used),
            "swap_total": _format_bytes(swap.total),
            "net_rate": _format_bytes(net_rate) + "/s",
            "temperatures": temps,
        }


class NetworkMonitorProvider(WidgetProvider):
    PROVIDER_ID = "network-monitor"

    def __init__(self):
        super().__init__()
        self._last_sent = 0
        self._last_recv = 0
        self._last_time = time.time()
        self._interface = None  # None = all interfaces

    def start(self):
        counters = psutil.net_io_counters(pernic=True)
        total_sent = sum(c.bytes_sent for c in counters.values())
        total_recv = sum(c.bytes_recv for c in counters.values())
        self._last_sent = total_sent
        self._last_recv = total_recv
        self._last_time = time.time()

    def set_interface(self, interface: str):
        """Set specific network interface to monitor (None = all)."""
        self._interface = interface
        self.start()  # Reset counters

    def get_data(self) -> dict[str, Any]:
        counters = psutil.net_io_counters(pernic=True)

        if self._interface and self._interface in counters:
            nic = counters[self._interface]
            sent = nic.bytes_sent
            recv = nic.bytes_recv
            packets_sent = nic.packets_sent
            packets_recv = nic.packets_recv
        else:
            sent = sum(c.bytes_sent for c in counters.values())
            recv = sum(c.bytes_recv for c in counters.values())
            packets_sent = sum(c.packets_sent for c in counters.values())
            packets_recv = sum(c.packets_recv for c in counters.values())

        now_time = time.time()
        elapsed = max(now_time - self._last_time, 0.001)

        upload_rate = (sent - self._last_sent) / elapsed
        download_rate = (recv - self._last_recv) / elapsed

        self._last_sent = sent
        self._last_recv = recv
        self._last_time = now_time

        # Get available interfaces
        interfaces = list(counters.keys())

        return {
            "interface": self._interface or "all",
            "interfaces": interfaces,
            "bytes_sent": sent,
            "bytes_recv": recv,
            "upload_rate": _format_bytes(int(upload_rate)) + "/s",
            "download_rate": _format_bytes(int(download_rate)) + "/s",
            "total_rate": _format_bytes(int(upload_rate + download_rate)) + "/s",
            "packets_sent": packets_sent,
            "packets_recv": packets_recv,
        }


class BatteryProvider(WidgetProvider):
    PROVIDER_ID = "battery"

    def get_data(self) -> dict[str, Any]:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"available": False, "percent": 0, "charging": False, "time_left": ""}

        secs = bat.secsleft
        if secs > 0:
            h, r = divmod(int(secs), 3600)
            m, s = divmod(r, 60)
            time_left = f"{h}h {m}m"
        else:
            time_left = "N/A"

        return {
            "available": True,
            "percent": bat.percent,
            "charging": bat.power_plugged,
            "time_left": time_left,
        }


class UptimeProvider(WidgetProvider):
    PROVIDER_ID = "uptime"

    def get_data(self) -> dict[str, Any]:
        boot = psutil.boot_time()
        delta = int(time.time() - boot)
        days, rem = divmod(delta, 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        return {
            "days": days,
            "hours": hours,
            "minutes": mins,
            "seconds": secs,
            "formatted": f"{days}d {hours}h {mins}m",
        }


class PingProvider(WidgetProvider):
    PROVIDER_ID = "ping-monitor"

    def __init__(self):
        super().__init__()
        self._host = "8.8.8.8"
        self._last_ping = -1.0

    def get_data(self) -> dict[str, Any]:
        import subprocess

        try:
            out = subprocess.check_output(
                ["ping", "-c", "1", "-W", "2", self._host],
                stderr=subprocess.DEVNULL,
                timeout=5,
            ).decode()
            for line in out.splitlines():
                if "time=" in line:
                    idx = line.index("time=") + 5
                    end = line.index(" ", idx)
                    self._last_ping = float(line[idx:end])
                    break
        except Exception:
            self._last_ping = -1.0

        return {
            "host": self._host,
            "latency_ms": self._last_ping,
            "reachable": self._last_ping >= 0,
        }


class KernelProvider(WidgetProvider):
    PROVIDER_ID = "kernel-version"

    def get_data(self) -> dict[str, Any]:
        import platform

        return {
            "kernel": platform.release(),
            "full": platform.version(),
            "machine": platform.machine(),
        }
