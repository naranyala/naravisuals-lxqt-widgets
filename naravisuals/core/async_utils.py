import subprocess
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

class _WorkerSignals(QObject):
    on_success = pyqtSignal(str)
    on_error = pyqtSignal(str)

class _CommandWorker(QRunnable):
    """Asynchronous worker to run a shell command without blocking the UI thread."""
    def __init__(self, command, signals):
        super().__init__()
        self.command = command
        self.signals = signals

    def run(self):
        try:
            output = subprocess.check_output(self.command, stderr=subprocess.DEVNULL, timeout=5.0)
            self.signals.on_success.emit(output.decode().strip())
        except subprocess.TimeoutExpired:
            self.signals.on_error.emit("TimeoutExpired")
        except subprocess.CalledProcessError:
            self.signals.on_error.emit("ProcessError")
        except Exception as e:
            self.signals.on_error.emit(str(e))

def run_async_command(command: list[str], on_success_cb, on_error_cb=None):
    """
    Dispatch a shell command to a background thread to prevent UI freezing.
    
    Args:
        command: List of command arguments (e.g. ['docker', 'ps', '-q'])
        on_success_cb: Function called with the stripped stdout string upon success
        on_error_cb: Optional function called with the error string upon failure
    """
    signals = _WorkerSignals()
    signals.on_success.connect(on_success_cb)
    if on_error_cb:
        signals.on_error.connect(on_error_cb)
        
    worker = _CommandWorker(command, signals)
    QThreadPool.globalInstance().start(worker)

def run_sync_command(command: list[str], default: str = "", timeout: float = 2.0) -> str:
    """Safely run a command synchronously with a strict timeout."""
    try:
        return subprocess.check_output(command, stderr=subprocess.DEVNULL, timeout=timeout).decode().strip()
    except Exception:
        return default

def format_bytes(size: int) -> str:
    """Format an integer byte size into a human-readable string (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def format_time_mm_ss(seconds: int) -> str:
    """Format total seconds into MM:SS format."""
    mins, secs = divmod(max(0, int(seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

def get_theme_color(role: QPalette.ColorRole) -> str:
    """Safely fetch a hex color from the current system Qt Palette."""
    app = QApplication.instance()
    if not app:
        return "#ffffff"
    return app.palette().color(role).name()

def get_text_color() -> str:
    """Get the standard WindowText color for the current theme."""
    return get_theme_color(QPalette.ColorRole.WindowText)

def get_bg_color() -> str:
    """Get the standard Window (background) color for the current theme."""
    return get_theme_color(QPalette.ColorRole.Window)
