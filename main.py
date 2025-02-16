#!/usr/bin/env python3
import sys, threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QPushButton, QLabel, QInputDialog, QAction
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap
from evdev import InputDevice, categorize, ecodes, list_devices

class WiiMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Wii Menu")
        self.showFullScreen()
        # Set a background color similar to the Wii menu’s blue
        self.setStyleSheet("background-color: #1A237E;")
        
        # Central widget and grid layout for game icons
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(40)
        
        self.game_buttons = []
        # Create a 3x4 grid of sample game icons (circular buttons)
        for i in range(3):
            for j in range(4):
                btn = QPushButton(f"Game {i*4+j+1}")
                btn.setFixedSize(150, 150)
                # Circular appearance with a white background
                btn.setStyleSheet("background-color: white; border-radius: 75px;")
                self.grid_layout.addWidget(btn, i, j)
                self.game_buttons.append(btn)
        
        # Pointer: a QLabel with an image (provide your own 'pointer.png')
        self.pointer = QLabel(self)
        try:
            self.pointer.setPixmap(QPixmap("pointer.png").scaled(32, 32, Qt.KeepAspectRatio))
        except Exception:
            self.pointer.setText("•")
            self.pointer.setStyleSheet("color: red; font-size: 32px;")
        self.pointer.setFixedSize(32, 32)
        # Start pointer at center of the screen
        self.pointer_pos = QPoint(self.width()//2, self.height()//2)
        self.pointer.move(self.pointer_pos)
        self.pointer.show()
        
        # Timer to update pointer widget position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pointer)
        self.timer.start(30)  # update every 30 ms
        
        # Add a menu action for folder creation
        menubar = self.menuBar()
        folder_menu = menubar.addMenu("Folders")
        create_folder_action = QAction("Create Folder", self)
        create_folder_action.triggered.connect(self.create_folder)
        folder_menu.addAction(create_folder_action)
    
    def update_pointer(self):
        self.pointer.move(self.pointer_pos)
    
    def move_pointer(self, dx, dy):
        # Update pointer position with bounds checking
        new_x = max(0, min(self.width() - self.pointer.width(), self.pointer_pos.x() + dx))
        new_y = max(0, min(self.height() - self.pointer.height(), self.pointer_pos.y() + dy))
        self.pointer_pos = QPoint(new_x, new_y)
    
    def create_folder(self):
        # Pop up a dialog to name the folder; then add a new button
        text, ok = QInputDialog.getText(self, "Create Folder", "Folder Name:")
        if ok and text:
            btn = QPushButton(text)
            btn.setFixedSize(150, 150)
            btn.setStyleSheet("background-color: lightgray; border-radius: 75px;")
            # Add new folder to the next available position
            row = len(self.game_buttons) // 4
            col = len(self.game_buttons) % 4
            self.grid_layout.addWidget(btn, row, col)
            self.game_buttons.append(btn)

def wiimote_listener(app_window):
    """
    Listens for Wiimote events using evdev.
    This example assumes the Wiimote is registered as an input device.
    Adjust the axis normalization as needed.
    """
    devices = [InputDevice(path) for path in list_devices()]
    wiimote = None
    # Try to locate a device with 'Wiimote' or 'Nintendo' in its name
    for dev in devices:
        if "Wiimote" in dev.name or "Nintendo" in dev.name:
            wiimote = dev
            break
    if not wiimote:
        print("No Wiimote found. Make sure it is paired and recognized by Linux.")
        return

    print("Wiimote connected on", wiimote.path)
    for event in wiimote.read_loop():
        if event.type == ecodes.EV_ABS:
            # Use ABS_RX and ABS_RY as an example for pointer motion.
            if event.code == ecodes.ABS_RX:
                # Simple normalization: adjust sensitivity as needed.
                dx = int((event.value - 128) / 10)
                app_window.move_pointer(dx, 0)
            elif event.code == ecodes.ABS_RY:
                dy = int((event.value - 128) / 10)
                app_window.move_pointer(0, dy)
        elif event.type == ecodes.EV_KEY and event.value == 1:
            # On button press, check if the pointer is over a button and trigger its click.
            pos = app_window.pointer_pos + app_window.pointer.rect().center()
            widget = app_window.childAt(pos)
            if widget and isinstance(widget, QPushButton):
                print("Activating:", widget.text())
                # You could add additional visual feedback here before triggering.
                widget.click()

def main():
    app = QApplication(sys.argv)
    window = WiiMenu()
    window.show()
    
    # Start the Wiimote listener in a separate thread so the GUI remains responsive.
    t = threading.Thread(target=wiimote_listener, args=(window,), daemon=True)
    t.start()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


