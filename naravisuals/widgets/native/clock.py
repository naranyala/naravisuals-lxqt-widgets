import datetime
from PyQt6.QtWidgets import QCalendarWidget, QMenu
from naravisuals.core.base_widget import TextWidget

class ClockWidget(TextWidget):
    WIDGET_NAME = "Clock & Calendar"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)
        self.calendar_menu = None

    def _on_tick(self):
        now = datetime.datetime.now()
        self.set_text(now.strftime("%H:%M  |  %a, %b %d"))

    def mousePressEvent(self, event):
        if not self.calendar_menu:
            self.calendar_menu = QMenu(self)
            cal = QCalendarWidget(self.calendar_menu)
            from PyQt6.QtWidgets import QWidgetAction
            action = QWidgetAction(self.calendar_menu)
            action.setDefaultWidget(cal)
            self.calendar_menu.addAction(action)
        self.calendar_menu.popup(event.globalPosition().toPoint())
