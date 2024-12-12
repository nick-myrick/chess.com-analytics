from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QMouseEvent

class QRangeSlider(QWidget):
    rangeChanged = pyqtSignal(int, int)
    def __init__(self, window_instance, minimum=0, maximum=1000, parent=None):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.start = minimum
        self.end = maximum
        self.bar_color = QColor(67, 74, 58)
        self.range_color = QColor(140, 164, 100)
        self.handle_color = QColor(50, 50, 50)
        self.handle_radius = 10
        self.dragging_start = False
        self.dragging_end = False
        self.window_instance = window_instance

        self.setMinimumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw the full bar
        bar_rect = QRect(
            self.handle_radius,
            self.height() // 2 - 5,
            self.width() - 2 * self.handle_radius,
            10,
        )
        painter.setBrush(self.bar_color)
        painter.drawRect(bar_rect)

        # Draw the selected range
        range_rect = QRect(
            self.value_to_pos(self.start),
            self.height() // 2 - 5,
            self.value_to_pos(self.end) - self.value_to_pos(self.start),
            10,
        )
        painter.setBrush(self.range_color)
        painter.drawRect(range_rect)

        # Draw the handles
        painter.setBrush(self.handle_color)
        painter.drawEllipse(
            self.value_to_pos(self.start) - self.handle_radius,
            self.height() // 2 - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2,
        )
        painter.drawEllipse(
            self.value_to_pos(self.end) - self.handle_radius,
            self.height() // 2 - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2,
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos().x()
            start_distance = abs(self.value_to_pos(self.start) - pos)
            end_distance = abs(self.value_to_pos(self.end) - pos)
            if start_distance < self.handle_radius:
                self.dragging_start = True
            elif end_distance < self.handle_radius:
                self.dragging_end = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging_start:
            self.start = self.pos_to_value(event.pos().x())
            self.start = min(max(self.minimum, self.start), self.end - 1)
            self.update(self.window_instance)
        elif self.dragging_end:
            self.end = self.pos_to_value(event.pos().x())
            self.end = max(min(self.maximum, self.end), self.start + 1)
            self.update(self.window_instance)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging_start = False
        self.dragging_end = False
        self.rangeChanged.emit(self.start, self.end)

    def value_to_pos(self, value):
        """Convert a value to a position on the slider (integer)."""
        return int(
            self.handle_radius
            + (value - self.minimum)
            / (self.maximum - self.minimum)
            * (self.width() - 2 * self.handle_radius)
        )

    def pos_to_value(self, pos):
        """Convert a position on the slider to an integer value."""
        return int(
            round(
                self.minimum
                + (pos - self.handle_radius)
                / (self.width() - 2 * self.handle_radius)
                * (self.maximum - self.minimum)
            )
        )
