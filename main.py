import pygame
import os
import json
import subprocess
import sys
import time

# Configuration
CONFIG_FILE = os.path.expanduser("~/.wiilauncher_config.json")
SCREEN_SIZE = (1280, 720)
ICON_SIZE = 150
PADDING = 30
THEME_COLOR = (0, 70, 140)
HIGHLIGHT_COLOR = (255, 255, 0)

class GameIcon:
    def __init__(self, title, path, emulator, position):
        self.title = title
        self.path = path
        self.emulator = emulator
        self.position = position
        self.target_position = position
        self.image = pygame.Surface((ICON_SIZE, ICON_SIZE))
        self.image.fill((200, 200, 200))  # Placeholder
        self.rect = self.image.get_rect(topleft=position)
        self.scale = 1.0

    def update(self, dt):
        self.rect.x += (self.target_position[0] - self.rect.x) * dt * 10
        self.rect.y += (self.target_position[1] - self.rect.y) * dt * 10
        self.scale += (1.0 - self.scale) * dt * 10

    def draw(self, surface):
        scaled_image = pygame.transform.scale(self.image, 
            (int(ICON_SIZE * self.scale), int(ICON_SIZE * self.scale)))
        surface.blit(scaled_image, scaled_image.get_rect(center=self.rect.center))

class Folder:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.target_position = position
        self.icons = []
        self.image = pygame.Surface((ICON_SIZE, ICON_SIZE))
        self.image.fill((150, 150, 150))  # Folder color
        self.rect = self.image.get_rect(topleft=position)
        self.scale = 1.0

    def update(self, dt):
        # Similar animation to GameIcon
        pass

    def draw(self, surface):
        # Similar drawing to GameIcon
        pass

class WiiLauncher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.icons = []
        self.folders = []
        self.selected_index = 0
        self.current_folder = None
        self.config = self.load_config()
        self.joystick = self.init_wiimote()
        self.mouse_control = True

        # Load initial content
        self.scan_games()
        self.arrange_icons()

    def init_wiimote(self):
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            return joystick
        return None

    def load_config(self):
        default_config = {
            "platforms": [
                {
                    "name": "GameCube",
                    "path": os.path.expanduser("~/Games/GameCube"),
                    "extensions": [".iso", ".gcm"],
                    "emulator": "dolphin-emu"
                }
            ],
            "folders": [],
            "settings": {
                "grid_cols": 6,
                "grid_rows": 2,
                "theme_color": THEME_COLOR
            }
        }
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
            except FileNotFoundError:
            return default_config

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def scan_games(self):
        for platform in self.config['platforms']:
            if os.path.exists(platform['path']):
                for file in os.listdir(platform['path']):
                    if file.endswith(tuple(platform['extensions'])):
                        self.icons.append(GameIcon(
                            os.path.splitext(file)[0],
                            os.path.join(platform['path'], file),
                            platform['emulator'],
                            (0, 0)  # Position will be set in arrange_icons
                        ))

    def arrange_icons(self):
        cols = self.config['settings']['grid_cols']
        for i, icon in enumerate(self.icons + self.folders):
            row = i // cols
            col = i % cols
            x = PADDING + col * (ICON_SIZE + PADDING)
            y = PADDING + row * (ICON_SIZE + PADDING + 50)
            icon.target_position = (x, y)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click()
            elif event.type == pygame.JOYBUTTONDOWN:
                self.handle_joystick_buttons(event.button)
            elif event.type == pygame.JOYAXISMOTION:
                self.handle_joystick_axis(event.axis, event.value)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def handle_joystick_buttons(self, button):
        # Wii Remote button mapping
        if button == 0:  # A Button
            self.activate_selected()
        elif button == 1:  # B Button
            self.navigate_back()
        elif button == 4:  # + Button
            self.show_settings_menu()

    def handle_joystick_axis(self, axis, value):
        # Handle pointing with IR sensor
        pass

    def activate_selected(self):
        selected = self.icons[self.selected_index]
        if isinstance(selected, Folder):
            self.current_folder = selected
            self.arrange_icons()
        else:
            self.launch_game(selected)

    def launch_game(self, icon):
        try:
            subprocess.Popen([icon.emulator, icon.path])
            self.running = False
        except Exception as e:
            print(f"Error launching game: {e}")

    def show_settings_menu(self):
        # Implement settings UI
        pass

    def navigate_back(self):
        if self.current_folder:
            self.current_folder = None
            self.arrange_icons()

    def update(self, dt):
        for icon in self.icons + self.folders:
            icon.update(dt)

    def draw(self):
        self.screen.fill(self.config['settings']['theme_color'])
        
        # Draw exit button
        pygame.draw.circle(self.screen, (200, 0, 0), (40, 40), 20)
        exit_font = pygame.font.Font(None, 30)
        exit_text = exit_font.render("X", True, (255, 255, 255))
        self.screen.blit(exit_text, (30, 30))

        # Draw all items
        for icon in self.icons + self.folders:
            icon.draw(self.screen)

        # Draw selection highlight
        selected = self.icons[self.selected_index]
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, selected.rect, 3)

        pygame.display.flip()

    def run(self):
        last_time = time.time()
        while self.running:
            dt = time.time() - last_time
            last_time = time.time()
            
            self.handle_input()
            self.update(dt)
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    launcher = WiiLauncher()
    launcher.run()
