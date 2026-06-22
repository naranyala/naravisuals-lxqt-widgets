"""NaraVisuals D-Bus Daemon - Single process managing all widget data providers."""
import signal
import sys
import logging
from PyQt6.QtCore import QCoreApplication, QTimer

from naravisuals.daemon.dbus_service import NaraVisualsDaemon

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("naravisuals-daemon")


def main():
    app = QCoreApplication(sys.argv)
    app.setApplicationName("naravisuals-daemon")
    app.setOrganizationName("naravisuals")

    daemon = NaraVisualsDaemon()
    if not daemon.start():
        log.error("Failed to start D-Bus service")
        sys.exit(1)

    log.info("NaraVisuals daemon started")

    shutdown = lambda *_: (log.info("Shutting down..."), daemon.stop(), app.quit())
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
