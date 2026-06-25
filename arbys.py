import sys
from pathlib import Path

from pynput import keyboard
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter
from PyQt6.QtWidgets import QApplication, QLabel, QMenu, QSystemTrayIcon, QWidget


class KeyWatcher(QObject):
    key_pressed = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.daemon = True

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def _on_press(self, key):
        self.key_pressed.emit()


class BurgerWindow(QWidget):
    def __init__(self, assets_dir: Path):
        super().__init__()
        self.assets_dir = assets_dir
        self.meat_count = 1
        self.key_count = 0
        self.target_width = 150

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setWindowTitle("Arby's")

        self.burger_label = QLabel(self)

        self.bottom_bun_pixmap = QPixmap(str(self.assets_dir / "bottombun.png")).scaledToWidth(
            self.target_width, Qt.TransformationMode.SmoothTransformation
        )
        self.meat_pixmap = QPixmap(str(self.assets_dir / "meat.png")).scaledToWidth(
            self.target_width, Qt.TransformationMode.SmoothTransformation
        )
        self.top_bun_pixmap = QPixmap(str(self.assets_dir / "topbun.png")).scaledToWidth(
            self.target_width, Qt.TransformationMode.SmoothTransformation
        )

        self._refresh_burger()
        self._drag_position = None

        tray_menu = QMenu(self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon = QSystemTrayIcon(QIcon(self.bottom_bun_pixmap), self)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Arby's burger")
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def _refresh_burger(self):
        bottom_h = self.bottom_bun_pixmap.height()
        meat_h = self.meat_pixmap.height()
        top_h = self.top_bun_pixmap.height()
        overlap = max(1, int(meat_h * 0.35))

        total_height = bottom_h + self.meat_count * (meat_h - overlap) + top_h - overlap
        previous_height = self.height() if self.height() > 0 else total_height
        self.setFixedSize(self.target_width, total_height)
        if total_height > previous_height:
            delta = total_height - previous_height
            self.move(self.x(), self.y() - delta)

        composite = QPixmap(self.target_width, total_height)
        composite.fill(Qt.GlobalColor.transparent)
        painter = QPainter(composite)

        current_y = total_height - bottom_h
        painter.drawPixmap(0, current_y, self.bottom_bun_pixmap)

        for _ in range(self.meat_count):
            current_y -= meat_h - overlap
            painter.drawPixmap(0, current_y, self.meat_pixmap)

        current_y -= top_h - overlap
        painter.drawPixmap(0, current_y, self.top_bun_pixmap)

        painter.end()

        self.burger_label.setPixmap(composite)
        self.burger_label.setFixedSize(composite.size())
        self.burger_label.move(0, 0)
        self.burger_label.show()

    def add_meat_layer(self):
        self.meat_count += 1
        self._refresh_burger()

    def on_key_pressed(self):
        self.key_count += 1
        if self.key_count % 10 == 0:
            self.add_meat_layer()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    assets_dir = Path(__file__).resolve().parent / "assets"
    if not assets_dir.exists():
        raise FileNotFoundError(f"Assets folder not found: {assets_dir}")

    window = BurgerWindow(assets_dir)
    window.show()

    watcher = KeyWatcher()
    watcher.key_pressed.connect(window.on_key_pressed)
    watcher.start()

    try:
        sys.exit(app.exec())
    finally:
        watcher.stop()


if __name__ == "__main__":
    main()
