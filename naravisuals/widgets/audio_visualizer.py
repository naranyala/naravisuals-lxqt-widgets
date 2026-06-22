import random
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from naravisuals.base import PanelWidget

class AudioVisualizer(PanelWidget):
    WIDGET_NAME = "Audio Visualizer"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(50) # 20fps for smooth animation
        self.setMinimumSize(100, 30)
        self.bars = [0] * 10

    def _on_tick(self):
        # MVP: Simulate audio frequency bands. 
        # TODO: Hook into pyaudio or pipewire-alsa to read actual PCM data
        for i in range(len(self.bars)):
            target = random.randint(5, 30)
            self.bars[i] += (target - self.bars[i]) * 0.3
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bar_width = self.width() / len(self.bars)
        for i, height in enumerate(self.bars):
            x = int(i * bar_width)
            y = int(self.height() - height)
            
            # Draw gradient bar
            color = QColor(0, 255, 150)
            color.setAlpha(200)
            painter.fillRect(x + 1, y, int(bar_width) - 2, int(height), color)
