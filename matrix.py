import pygame
import random
import sys
import json
import os
import subprocess
import win32gui
import win32con
import win32api
import math


# --- Utility Functions ---
def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color values"""
    # Ensure inputs are within valid ranges
    h = max(0.0, min(1.0, h))
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    
    if s == 0.0:
        return v, v, v
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    
    if i == 0:
        return v, t, p
    elif i == 1:
        return q, v, p
    elif i == 2:
        return p, v, t
    elif i == 3:
        return p, q, v
    elif i == 4:
        return t, p, v
    else:
        return v, p, q


# --- Default Configuration ---
DEFAULT_CONFIG = {
    "font_size": 27,
    "min_speed": 5,
    "max_speed": 10,
    "new_drop_chance": 0.9,
    "char_change_prob": 0.08,
    "stream_length_min": 34,
    "stream_length_max": 56,
    "body_color_r": 0,
    "body_color_g": 152,
    "body_color_b": 0,
    "custom_phrases": ["Neo...", "Wake up Neo...", "Follow the White Rabbit"],
    "enable_particles": True,
    "enable_sound": False,
    "matrix_theme": "classic",  # classic, cyberpunk, retro, neon
    "particle_density": 0.3,
    "glow_effect": True,
    "rainbow_mode": False,
    "pulse_effect": False,
}
CONFIG_FILE = "matrix_config.json"

# --- Global Screensaver Variables (will be loaded from config) ---
FONT_SIZE = DEFAULT_CONFIG["font_size"]
MIN_SPEED = DEFAULT_CONFIG["min_speed"]
MAX_SPEED = DEFAULT_CONFIG["max_speed"]
NEW_DROP_CHANCE = DEFAULT_CONFIG["new_drop_chance"]
CHAR_CHANGE_PROB = DEFAULT_CONFIG["char_change_prob"]
STREAM_LENGTH_MIN = DEFAULT_CONFIG["stream_length_min"]
STREAM_LENGTH_MAX = DEFAULT_CONFIG["stream_length_max"]

DROP_COLOR_BODY = (
    DEFAULT_CONFIG["body_color_r"],
    DEFAULT_CONFIG["body_color_g"],
    DEFAULT_CONFIG["body_color_b"],
)
DROP_COLOR_HEAD = (
    min(255, DEFAULT_CONFIG["body_color_r"] + 75),
    min(255, DEFAULT_CONFIG["body_color_g"] + 75),
    min(255, DEFAULT_CONFIG["body_color_b"] + 75),
)

# New global variables for enhanced features
ENABLE_PARTICLES = DEFAULT_CONFIG["enable_particles"]
ENABLE_SOUND = DEFAULT_CONFIG["enable_sound"]
MATRIX_THEME = DEFAULT_CONFIG["matrix_theme"]
PARTICLE_DENSITY = DEFAULT_CONFIG["particle_density"]
GLOW_EFFECT = DEFAULT_CONFIG["glow_effect"]
RAINBOW_MODE = DEFAULT_CONFIG["rainbow_mode"]
PULSE_EFFECT = DEFAULT_CONFIG["pulse_effect"]


# --- Other Constants ---
BACKGROUND_COLOR = (0, 0, 0)
FRAME_RATE = 30
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0

# --- Character List Definition ---
KATAKANA_START = 0x30A0
KATAKANA_END = 0x30FF
katakana_characters = [chr(i) for i in range(KATAKANA_START, KATAKANA_END + 1)]
number_characters = [str(i) for i in range(10)]

# MODIFIED LINE: Repeat katakana_characters to make them appear more frequently
CHAR_LIST = (katakana_characters * 2) + (number_characters * 8)
# You can also add Latin alphabet characters if you like:
# latin_uppercase = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
# CHAR_LIST = (katakana_characters * 2) + latin_uppercase + number_characters


# --- Theme Definitions ---
MATRIX_THEMES = {
    "classic": {
        "body_color": (0, 152, 0),
        "head_color": (0, 255, 0),
        "background": (0, 0, 0),
        "particle_color": (0, 100, 0),
        "glow_color": (0, 200, 0)
    },
    "cyberpunk": {
        "body_color": (0, 255, 255),
        "head_color": (255, 255, 255),
        "background": (0, 0, 20),
        "particle_color": (0, 150, 255),
        "glow_color": (0, 255, 255)
    },
    "retro": {
        "body_color": (255, 165, 0),
        "head_color": (255, 255, 0),
        "background": (20, 0, 0),
        "particle_color": (255, 100, 0),
        "glow_color": (255, 200, 0)
    },
    "neon": {
        "body_color": (255, 0, 255),
        "head_color": (255, 255, 255),
        "background": (10, 0, 10),
        "particle_color": (255, 0, 200),
        "glow_color": (255, 100, 255)
    }
}


# --- Particle Class for Enhanced Visual Effects ---
class Particle:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(1, 4)
        self.life = random.randint(30, 90)
        self.max_life = self.life
        self.size = random.randint(1, 3)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.alpha = 255
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.alpha = int((self.life / self.max_life) * 255)
        
        # Add some randomness to movement
        if random.random() < 0.1:
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.2, 0.2)
            
        # Keep particles within bounds
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx)
        elif self.x > self.screen_width:
            self.x = self.screen_width
            self.vx = -abs(self.vx)
            
    def is_dead(self):
        return self.life <= 0 or self.y > self.screen_height
        
    def draw(self, surface, theme_colors):
        if self.alpha > 0:
            color = theme_colors["particle_color"]
            alpha_color = (*color, self.alpha)
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, alpha_color, (self.size, self.size), self.size)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


# --- Configuration Loading/Saving & UI (Slider, Button classes) ---
# (All functions: update_drop_colors, load_config, save_config,
#  Slider class, Button class, show_config_screen remain THE SAME as the previous version)
def update_drop_colors(r, g, b):
    global DROP_COLOR_BODY, DROP_COLOR_HEAD
    DROP_COLOR_BODY = (int(r), int(g), int(b))
    brightness_increase = 75
    head_r = min(255, int(r) + brightness_increase)
    head_g = min(255, int(g) + brightness_increase)
    head_b = min(255, int(b) + brightness_increase)
    if r + g + b > 600:  # if body is very bright
        head_r, head_g, head_b = 255, 255, 255
    elif r + g + b < 50:  # If body color is very dark
        head_r = min(255, int(r) + 100)
        head_g = min(255, int(g) + 100)
        head_b = min(255, int(b) + 100)
    DROP_COLOR_HEAD = (head_r, head_g, head_b)


def load_config():
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX
    global ENABLE_PARTICLES, ENABLE_SOUND, MATRIX_THEME, PARTICLE_DENSITY, GLOW_EFFECT, RAINBOW_MODE, PULSE_EFFECT
    loaded_values = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                loaded_values.update(user_config)
            print("Config loaded.")
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Error loading config: {e}. Using defaults and attempting to save.")
            try:
                with open(CONFIG_FILE, "w") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
                print("Default config saved.")
            except IOError as ioe:
                print(f"Error saving default config: {ioe}")
            loaded_values = DEFAULT_CONFIG.copy()
    else:
        print("No config file found. Using defaults and creating one.")
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print("Default config file created.")
        except IOError as e:
            print(f"Error creating default config file: {e}")
        loaded_values = DEFAULT_CONFIG.copy()
    FONT_SIZE = int(loaded_values["font_size"])
    MIN_SPEED = int(loaded_values["min_speed"])
    MAX_SPEED = int(loaded_values["max_speed"])
    NEW_DROP_CHANCE = float(loaded_values["new_drop_chance"])
    CHAR_CHANGE_PROB = float(loaded_values["char_change_prob"])
    STREAM_LENGTH_MIN = int(loaded_values["stream_length_min"])
    STREAM_LENGTH_MAX = int(loaded_values["stream_length_max"])
    ENABLE_PARTICLES = loaded_values.get("enable_particles", True)
    ENABLE_SOUND = loaded_values.get("enable_sound", False)
    MATRIX_THEME = loaded_values.get("matrix_theme", "classic")
    PARTICLE_DENSITY = float(loaded_values.get("particle_density", 0.3))
    GLOW_EFFECT = loaded_values.get("glow_effect", True)
    RAINBOW_MODE = loaded_values.get("rainbow_mode", False)
    PULSE_EFFECT = loaded_values.get("pulse_effect", False)
    update_drop_colors(
        loaded_values["body_color_r"],
        loaded_values["body_color_g"],
        loaded_values["body_color_b"],
    )
    # Ensure custom_phrases is always a list
    if "custom_phrases" not in loaded_values or not isinstance(
        loaded_values["custom_phrases"], list
    ):
        loaded_values["custom_phrases"] = []
    if MIN_SPEED > MAX_SPEED:
        MIN_SPEED = MAX_SPEED
    if STREAM_LENGTH_MIN > STREAM_LENGTH_MAX:
        STREAM_LENGTH_MIN = STREAM_LENGTH_MAX
    return loaded_values


def save_config(config_data):
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX
    global ENABLE_PARTICLES, ENABLE_SOUND, MATRIX_THEME, PARTICLE_DENSITY, GLOW_EFFECT, RAINBOW_MODE, PULSE_EFFECT
    FONT_SIZE = int(config_data["font_size"])
    MIN_SPEED = int(config_data["min_speed"])
    MAX_SPEED = int(config_data["max_speed"])
    NEW_DROP_CHANCE = float(config_data["new_drop_chance"])
    CHAR_CHANGE_PROB = float(config_data["char_change_prob"])
    STREAM_LENGTH_MIN = int(config_data["stream_length_min"])
    STREAM_LENGTH_MAX = int(config_data["stream_length_max"])
    ENABLE_PARTICLES = config_data.get("enable_particles", True)
    ENABLE_SOUND = config_data.get("enable_sound", False)
    MATRIX_THEME = config_data.get("matrix_theme", "classic")
    PARTICLE_DENSITY = float(config_data.get("particle_density", 0.3))
    GLOW_EFFECT = config_data.get("glow_effect", True)
    RAINBOW_MODE = config_data.get("rainbow_mode", False)
    PULSE_EFFECT = config_data.get("pulse_effect", False)
    update_drop_colors(
        config_data["body_color_r"],
        config_data["body_color_g"],
        config_data["body_color_b"],
    )
    if MIN_SPEED > MAX_SPEED:
        config_data["min_speed"] = MAX_SPEED
        MIN_SPEED = MAX_SPEED
    if STREAM_LENGTH_MIN > STREAM_LENGTH_MAX:
        config_data["stream_length_min"] = STREAM_LENGTH_MAX
        STREAM_LENGTH_MIN = STREAM_LENGTH_MAX
    # Ensure custom_phrases is always a list
    if "custom_phrases" not in config_data or not isinstance(
        config_data["custom_phrases"], list
    ):
        config_data["custom_phrases"] = []
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        print("Config saved.")
    except IOError as e:
        print(f"Error saving config: {e}")


def get_katakana_font(size):
    # List of fonts with good Katakana support, in order of preference
    font_candidates = [
        "MS Gothic",
        "Meiryo",
        "Yu Gothic",
        "Arial Unicode MS",
        "Noto Sans CJK JP",
        "Noto Sans JP",
        "SimHei",
        "Arial",
        "monospace",
    ]
    for font_name in font_candidates:
        try:
            font = pygame.font.SysFont(font_name, size)
            # Test if font can render a Katakana char (e.g., 'カ')
            if font.render("カ", True, (255, 255, 255)).get_width() > 0:
                return font
        except Exception:
            continue
    # Fallback: default font
    return pygame.font.SysFont(None, size)


class Slider:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        min_val,
        max_val,
        current_val,
        label,
        val_type=float,
        step=0.1,
        color_preview=None,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = max(min_val, min(max_val, current_val))
        self.label = label
        self.val_type = val_type
        self.step = step if val_type == float else int(max(1, step))
        self.knob_radius = h // 2 + 3
        self.track_rect = pygame.Rect(x, y + h // 4, w, h // 2)
        self.dragging = False
        self.font = get_katakana_font(20)
        self.color_preview = color_preview

    def _get_knob_pos(self):
        ratio = (
            (self.current_val - self.min_val) / (self.max_val - self.min_val)
            if (self.max_val - self.min_val) != 0
            else 0
        )
        track_visual_width = self.track_rect.width - self.knob_radius
        return self.track_rect.x + self.knob_radius // 2 + ratio * track_visual_width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                knob_x_center = self._get_knob_pos()
                dx = event.pos[0] - knob_x_center
                dy = event.pos[1] - self.track_rect.centery
                if (
                    dx * dx + dy * dy <= self.knob_radius * self.knob_radius
                    or self.track_rect.collidepoint(event.pos)
                ):
                    self.dragging = True
                    self._update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])

    def _update_value(self, mouse_x):
        track_visual_width = self.track_rect.width - self.knob_radius
        raw_x = mouse_x - (self.track_rect.x + self.knob_radius // 2)
        if track_visual_width <= 0:
            ratio = 0
        else:
            ratio = raw_x / track_visual_width
        new_val = self.min_val + ratio * (self.max_val - self.min_val)
        new_val = max(self.min_val, min(self.max_val, new_val))
        if self.val_type == float:
            self.current_val = round(new_val / self.step) * self.step
            self.current_val = float(f"{self.current_val:.2f}")
        else:
            self.current_val = int(round(new_val))
        self.current_val = max(self.min_val, min(self.max_val, self.current_val))

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (60, 60, 60),
            self.track_rect,
            border_radius=self.track_rect.height // 2,
        )
        pygame.draw.rect(
            surface,
            (100, 100, 100),
            self.track_rect,
            width=1,
            border_radius=self.track_rect.height // 2,
        )
        knob_x = self._get_knob_pos()
        pygame.draw.circle(
            surface,
            (200, 200, 200),
            (int(knob_x), self.track_rect.centery),
            self.knob_radius,
        )
        pygame.draw.circle(
            surface,
            (80, 80, 80),
            (int(knob_x), self.track_rect.centery),
            self.knob_radius,
            2,
        )
        val_display = (
            f"{self.current_val:.2f}"
            if self.val_type == float
            else str(self.current_val)
        )
        text_color = (220, 220, 220)
        if self.label.lower().startswith("red"):
            text_color = (255, 150, 150)
        elif self.label.lower().startswith("green"):
            text_color = (150, 255, 150)
        elif self.label.lower().startswith("blue"):
            text_color = (150, 150, 255)
        label_surface = self.font.render(
            f"{self.label}: {val_display}", True, text_color
        )
        surface.blit(label_surface, (self.rect.x, self.rect.y - 22))


class Button:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        text,
        color=(70, 70, 70),
        hover_color=(110, 110, 110),
        text_color=(230, 230, 230),
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        # Use smaller font size to prevent text overflow
        font_size = min(20, max(14, h // 2))
        self.font = get_katakana_font(font_size)
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (40, 40, 40), self.rect, width=2, border_radius=10)
        
        # Truncate text if it's too long for the button
        display_text = self.text
        text_width = self.font.size(display_text)[0]
        while text_width > self.rect.width - 10 and len(display_text) > 3:
            display_text = display_text[:-1]
            text_width = self.font.size(display_text)[0]
        
        text_surf = self.font.render(display_text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        self.is_hovered = self.rect.collidepoint(
            event.pos if event.type == pygame.MOUSEMOTION else pygame.mouse.get_pos()
        )
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return True
        return False


# --- Add a simple TextBox class for multi-line input ---
class TextBox:
    def __init__(self, x, y, w, h, text="", font=None, max_lines=5):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font or get_katakana_font(20)
        self.active = False
        self.max_lines = max_lines
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = len(text)
        self.scroll_offset = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.text = (
                    self.text[:self.cursor_position]
                    + "\n"
                    + self.text[self.cursor_position:]
                )
                self.cursor_position += 1
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_position > 0:
                    self.text = (
                        self.text[:self.cursor_position - 1]
                        + self.text[self.cursor_position:]
                    )
                    self.cursor_position -= 1
            elif event.key == pygame.K_DELETE:
                self.text = (
                    self.text[:self.cursor_position]
                    + self.text[self.cursor_position + 1:]
                )
            elif event.key == pygame.K_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
            elif event.key == pygame.K_HOME:
                self.cursor_position = 0
            elif event.key == pygame.K_END:
                self.cursor_position = len(self.text)
            elif event.unicode and event.key != pygame.K_TAB:
                self.text = (
                    self.text[:self.cursor_position]
                    + event.unicode
                    + self.text[self.cursor_position:]
                )
                self.cursor_position += len(event.unicode)

    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.rect, border_radius=6)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=6)
        lines = self.text.split("\n")
        visible_lines = lines[-self.max_lines:]
        for i, line in enumerate(visible_lines):
            txt_surf = self.font.render(line, True, (220, 255, 220))
            surface.blit(
                txt_surf,
                (self.rect.x + 6, self.rect.y + 6 + i * (self.font.get_height() + 2)),
            )
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_line = self.text[:self.cursor_position].count("\n")
            cursor_col = len(self.text[:self.cursor_position].split("\n")[-1])
            if cursor_line < self.max_lines:
                cursor_x = (
                    self.rect.x
                    + 6
                    + self.font.size(visible_lines[cursor_line][:cursor_col])[0]
                    if cursor_line < len(visible_lines)
                    else self.rect.x + 6
                )
                cursor_y = self.rect.y + 6 + cursor_line * (self.font.get_height() + 2)
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.font.get_height()),
                    2,
                )
        # Blink cursor
        self.cursor_timer += 1
        if self.cursor_timer > 20:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def get_lines(self):
        return [line.strip() for line in self.text.split("\n") if line.strip()]

    def set_lines(self, lines):
        self.text = "\n".join(lines)
        self.cursor_position = len(self.text)


def show_config_screen(surface):
    current_config_values = load_config()
    avg_stream_length = (
        current_config_values["stream_length_min"]
        + current_config_values["stream_length_max"]
    ) // 2
    slider_width = 280
    column_padding = 40
    column_gap = 70
    color_preview_width = 50
    color_preview_gap = 15
    slider_x_col1 = column_padding
    slider_x_col2 = column_padding + slider_width + column_gap
    y_start = 75
    y_step = 60
    sliders = []
    col1_y = y_start
    sliders.append(
        Slider(
            slider_x_col1,
            col1_y,
            slider_width,
            20,
            10,
            32,
            current_config_values["font_size"],
            "Font Size",
            int,
            1,
        )
    )
    col1_y += y_step
    sliders.append(
        Slider(
            slider_x_col1,
            col1_y,
            slider_width,
            20,
            1,
            10,
            current_config_values["min_speed"],
            "Min Speed",
            int,
            1,
        )
    )
    col1_y += y_step
    sliders.append(
        Slider(
            slider_x_col1,
            col1_y,
            slider_width,
            20,
            2,
            15,
            current_config_values["max_speed"],
            "Max Speed",
            int,
            1,
        )
    )
    col1_y += y_step
    sliders.append(
        Slider(
            slider_x_col1,
            col1_y,
            slider_width,
            20,
            0.05,
            1.0,
            current_config_values["new_drop_chance"],
            "Drop Chance",
            float,
            0.05,
        )
    )
    col1_y += y_step
    sliders.append(
        Slider(
            slider_x_col1,
            col1_y,
            slider_width,
            20,
            0.0,
            0.5,
            current_config_values["char_change_prob"],
            "Char Switch",
            float,
            0.01,
        )
    )
    col2_y = y_start
    sliders.append(
        Slider(
            slider_x_col2,
            col2_y,
            slider_width,
            20,
            10,
            70,
            avg_stream_length,
            "Avg Length",
            int,
            1,
        )
    )
    col2_y += y_step
    r_slider = Slider(
        slider_x_col2,
        col2_y,
        slider_width,
        20,
        0,
        255,
        current_config_values["body_color_r"],
        "Red",
        int,
        1,
    )
    sliders.append(r_slider)
    col2_y += y_step
    g_slider = Slider(
        slider_x_col2,
        col2_y,
        slider_width,
        20,
        0,
        255,
        current_config_values["body_color_g"],
        "Green",
        int,
        1,
    )
    sliders.append(g_slider)
    col2_y += y_step
    b_slider = Slider(
        slider_x_col2,
        col2_y,
        slider_width,
        20,
        0,
        255,
        current_config_values["body_color_b"],
        "Blue",
        int,
        1,
    )
    sliders.append(b_slider)
    # --- Add TextBox for custom phrases ---
    phrases_label_font = get_katakana_font(22)
    phrases_label = phrases_label_font.render(
        "Custom Phrases (one per line):", True, (180, 255, 180)
    )
    phrases_box_x = slider_x_col2
    phrases_box_y = b_slider.rect.bottom + 30
    phrases_box_w = slider_width + 60
    phrases_box_h = 100
    phrases_box = TextBox(
        phrases_box_x,
        phrases_box_y,
        phrases_box_w,
        phrases_box_h,
        "",
        get_katakana_font(18),
        max_lines=5,
    )
    # Set initial phrases
    if "custom_phrases" in current_config_values:
        phrases_box.set_lines(current_config_values["custom_phrases"])
    max_slider_y = max(col1_y, col2_y)
    button_y_pos = max(phrases_box_y + phrases_box_h, max_slider_y + y_step - 10)
    button_width = 170
    button_spacing = 25
    total_button_width = 2 * button_width + button_spacing
    button_start_x = (surface.get_width() - total_button_width) // 2
    save_button = Button(button_start_x, button_y_pos, button_width, 45, "Save & Start")
    default_button = Button(
        button_start_x + button_width + button_spacing,
        button_y_pos,
        button_width,
        45,
        "Defaults",
    )
    title_font = get_katakana_font(30)
    config_bg_color = (25, 30, 35)
    running_config = True
    while running_config:
        current_body_color_preview = (
            r_slider.current_val,
            g_slider.current_val,
            b_slider.current_val,
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    load_config()
                    running_config = False
            for slider in sliders:
                slider.handle_event(event)
            phrases_box.handle_event(event)
            if sliders[1].current_val > sliders[2].current_val:
                sliders[1].current_val = sliders[2].current_val
            if save_button.handle_event(event):
                avg_len_val = sliders[5].current_val
                len_spread = max(5, avg_len_val // 4)
                s_min = max(5, avg_len_val - len_spread)
                s_max = avg_len_val + len_spread
                config_to_save = {
                    "font_size": sliders[0].current_val,
                    "min_speed": sliders[1].current_val,
                    "max_speed": sliders[2].current_val,
                    "new_drop_chance": sliders[3].current_val,
                    "char_change_prob": sliders[4].current_val,
                    "stream_length_min": s_min,
                    "stream_length_max": s_max,
                    "body_color_r": r_slider.current_val,
                    "body_color_g": g_slider.current_val,
                    "body_color_b": b_slider.current_val,
                    "custom_phrases": phrases_box.get_lines(),
                }
                save_config(config_to_save)
                running_config = False
            if default_button.handle_event(event):
                defaults = DEFAULT_CONFIG.copy()
                sliders[0].current_val = defaults["font_size"]
                sliders[1].current_val = defaults["min_speed"]
                sliders[2].current_val = defaults["max_speed"]
                sliders[3].current_val = defaults["new_drop_chance"]
                sliders[4].current_val = defaults["char_change_prob"]
                sliders[5].current_val = (
                    defaults["stream_length_min"] + defaults["stream_length_max"]
                ) // 2
                r_slider.current_val = defaults["body_color_r"]
                g_slider.current_val = defaults["body_color_g"]
                b_slider.current_val = defaults["body_color_b"]
                phrases_box.set_lines(defaults["custom_phrases"])
                save_config(defaults)
        surface.fill(config_bg_color)
        title_color_preview = (
            min(255, r_slider.current_val + 60),
            min(255, g_slider.current_val + 60),
            min(255, b_slider.current_val + 60),
        )
        title_surf = title_font.render(
            "Screensaver Configuration", True, title_color_preview
        )
        surface.blit(
            title_surf, (surface.get_width() // 2 - title_surf.get_width() // 2, 20)
        )
        for slider_obj in sliders:
            slider_obj.draw(surface)
        preview_x = slider_x_col2 + slider_width + color_preview_gap
        preview_y = sliders[6].rect.y
        preview_h = sliders[8].rect.bottom - sliders[6].rect.top
        pygame.draw.rect(
            surface,
            current_body_color_preview,
            (preview_x, preview_y, color_preview_width, preview_h),
        )
        pygame.draw.rect(
            surface,
            (180, 180, 180),
            (preview_x, preview_y, color_preview_width, preview_h),
            2,
        )
        preview_font = get_katakana_font(16)
        preview_text = preview_font.render("Color", True, (200, 200, 200))
        surface.blit(
            preview_text,
            (
                preview_x + (color_preview_width - preview_text.get_width()) // 2,
                preview_y - 20,
            ),
        )
        # Draw phrases label and box
        surface.blit(phrases_label, (phrases_box_x, phrases_box_y - 28))
        phrases_box.draw(surface)
        save_button.draw(surface)
        default_button.draw(surface)
        pygame.display.flip()
        pygame.time.Clock().tick(FRAME_RATE)


# --- Drop Class, run_screensaver, main function (Remain THE SAME as previous version) ---
class Drop:
    def __init__(self, x_pos, font, screen_h):
        self.x = x_pos
        self.font = font
        self.screen_height = screen_h
        self.y = random.randint(-int(screen_h * 0.5), 0)
        current_min_speed = MIN_SPEED
        current_max_speed = MAX_SPEED
        if current_min_speed > current_max_speed:
            current_min_speed = current_max_speed
        self.speed = (
            random.randint(current_min_speed, current_max_speed)
            if current_max_speed >= current_min_speed
            else current_min_speed
        )
        current_s_min = STREAM_LENGTH_MIN
        current_s_max = STREAM_LENGTH_MAX
        if current_s_min > current_s_max:
            current_s_min = current_s_max
        self.length = (
            random.randint(current_s_min, current_s_max)
            if current_s_max >= current_s_min
            else current_s_min
        )
        if self.length <= 0:
            self.length = 1
        self.characters = []
        self.is_active = True
        self._generate_initial_characters()

    def _generate_initial_characters(self):
        current_y = self.y
        for i in range(self.length):
            self.characters.append(
                {
                    "char": random.choice(CHAR_LIST),
                    "y": current_y - (i * FONT_SIZE),
                    "color": DROP_COLOR_BODY,
                    "is_head": False,
                }
            )
        if self.characters:
            self.characters[0]["is_head"] = True
            self.characters[0]["color"] = DROP_COLOR_HEAD

    def fall(self):
        if not self.is_active:
            return
        for char_data in self.characters:
            char_data["y"] += self.speed
        if self.characters and self.characters[0]["y"] > self.y + FONT_SIZE:
            self.characters[0]["is_head"] = False
            self.characters[0]["color"] = DROP_COLOR_BODY
            self.characters.insert(
                0,
                {
                    "char": random.choice(CHAR_LIST),
                    "y": self.y,
                    "color": DROP_COLOR_HEAD,
                    "is_head": True,
                },
            )
        elif not self.characters:
            self._generate_initial_characters()
        for i in range(1, len(self.characters)):
            if random.random() < CHAR_CHANGE_PROB:
                self.characters[i]["char"] = random.choice(CHAR_LIST)
        self.characters = [
            cd for cd in self.characters if cd["y"] < self.screen_height + FONT_SIZE * 2
        ]
        while len(self.characters) > self.length:
            self.characters.pop()
        if not self.characters or (
            self.characters[-1]["y"] > self.screen_height + FONT_SIZE
            and self.characters[0]["y"] > self.screen_height
        ):
            self.is_active = False

    def draw(self, surface):
        if not self.is_active:
            return
        
        # Get theme colors
        theme_colors = MATRIX_THEMES.get(MATRIX_THEME, MATRIX_THEMES["classic"])
        base_body_r, base_body_g, base_body_b = DROP_COLOR_BODY
        
        # Apply rainbow mode if enabled
        if RAINBOW_MODE:
            rainbow_offset = (pygame.time.get_ticks() // 50) % 360
            hue = (rainbow_offset + self.x * 2) % 360
            r, g, b = hsv_to_rgb(hue / 360.0, 1.0, 1.0)
            base_body_r = max(0, min(255, int(r * 255)))
            base_body_g = max(0, min(255, int(g * 255)))
            base_body_b = max(0, min(255, int(b * 255)))
        
        # Apply pulse effect if enabled
        pulse_factor = 1.0
        if PULSE_EFFECT:
            pulse_factor = max(0.1, 0.8 + 0.4 * math.sin(pygame.time.get_ticks() * 0.005))
        
        for i, char_data in enumerate(self.characters):
            if (
                char_data["y"] < -FONT_SIZE
                or char_data["y"] > self.screen_height + FONT_SIZE
            ):
                continue
                
            current_char_color_tuple = (
                DROP_COLOR_HEAD if char_data["is_head"] else DROP_COLOR_BODY
            )
            current_char_color = list(current_char_color_tuple)
            
            if not char_data["is_head"]:
                fade_multiplier = 120
                fade_factor_ratio = i / max(1, self.length)
                fade_intensity_scale = fade_multiplier * fade_factor_ratio
                current_char_color[0] = max(
                    0, min(255, base_body_r - fade_intensity_scale * (base_body_r / 255.0) * 1.2)
                )
                current_char_color[1] = max(
                    0, min(255, base_body_g - fade_intensity_scale * (base_body_g / 255.0) * 1.2)
                )
                current_char_color[2] = max(
                    0, min(255, base_body_b - fade_intensity_scale * (base_body_b / 255.0) * 1.2)
                )
            
            # Apply pulse effect
            if PULSE_EFFECT:
                current_char_color = [int(c * pulse_factor) for c in current_char_color]
            
            # Ensure color values are valid (0-255)
            current_char_color = [max(0, min(255, int(c))) for c in current_char_color]
            
            try:
                char_surface = self.font.render(
                    char_data["char"], True, tuple(current_char_color)
                )
                
                # Apply glow effect if enabled
                if GLOW_EFFECT and char_data["is_head"]:
                    glow_color = theme_colors["glow_color"]
                    glow_surface = self.font.render(char_data["char"], True, glow_color)
                    glow_surface.set_alpha(100)
                    surface.blit(glow_surface, (self.x + 1, char_data["y"] + 1))
                    surface.blit(glow_surface, (self.x - 1, char_data["y"] - 1))
                
                surface.blit(char_surface, (self.x, char_data["y"]))
            except pygame.error:
                pass


def run_screensaver(screen):
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX, DROP_COLOR_BODY, DROP_COLOR_HEAD
    global ENABLE_PARTICLES, ENABLE_SOUND, MATRIX_THEME, PARTICLE_DENSITY, GLOW_EFFECT, RAINBOW_MODE, PULSE_EFFECT
    pygame.mouse.set_visible(False)
    
    # Get monitor regions (offset_x, offset_y, width, height)
    try:
        display_sizes = pygame.display.get_desktop_sizes()
    except Exception:
        display_sizes = [(screen.get_width(), screen.get_height())]
    
    # Calculate offsets for each monitor (assume horizontal arrangement)
    monitor_regions = []
    offset_x = 0
    for w, h in display_sizes:
        monitor_regions.append((offset_x, 0, w, h))
        offset_x += w
    
    # Initialize particles if enabled
    particles = []
    if ENABLE_PARTICLES:
        for _ in range(int(screen.get_width() * screen.get_height() * PARTICLE_DENSITY / 10000)):
            particles.append(Particle(
                random.randint(0, screen.get_width()),
                random.randint(0, screen.get_height()),
                screen.get_width(),
                screen.get_height()
            ))
    
    # For each monitor, create its own drops/columns
    while True:
        config = load_config()
        FONT_SIZE = config["font_size"]
        MIN_SPEED = config["min_speed"]
        MAX_SPEED = config["max_speed"]
        NEW_DROP_CHANCE = config["new_drop_chance"]
        CHAR_CHANGE_PROB = config["char_change_prob"]
        STREAM_LENGTH_MIN = config["stream_length_min"]
        STREAM_LENGTH_MAX = config["stream_length_max"]
        ENABLE_PARTICLES = config.get("enable_particles", True)
        ENABLE_SOUND = config.get("enable_sound", False)
        MATRIX_THEME = config.get("matrix_theme", "classic")
        PARTICLE_DENSITY = float(config.get("particle_density", 0.3))
        GLOW_EFFECT = config.get("glow_effect", True)
        RAINBOW_MODE = config.get("rainbow_mode", False)
        PULSE_EFFECT = config.get("pulse_effect", False)
        
        DROP_COLOR_BODY = (
            config["body_color_r"],
            config["body_color_g"],
            config["body_color_b"],
        )
        DROP_COLOR_HEAD = (
            min(255, config["body_color_r"] + 75),
            min(255, config["body_color_g"] + 75),
            min(255, config["body_color_b"] + 75),
        )
        
        custom_phrases = config.get("custom_phrases", [])
        active_font = get_katakana_font(FONT_SIZE)
        
        # Get theme colors
        theme_colors = MATRIX_THEMES.get(MATRIX_THEME, MATRIX_THEMES["classic"])
        background_color = theme_colors["background"]
        
        # For each monitor, create drops/columns
        monitor_drops = []
        for region in monitor_regions:
            _, _, w, h = region
            num_columns = w // FONT_SIZE if FONT_SIZE > 0 else w // 20
            drops = [None] * num_columns
            monitor_drops.append(drops)
        
        clock = pygame.time.Clock()
        running = True
        pygame.event.clear()
        pygame.mouse.get_pos()
        time_since_last_significant_move = pygame.time.get_ticks()
        significant_move_delay = 500
        last_mouse_pos = pygame.mouse.get_pos()
        phrase_next_time = pygame.time.get_ticks() + random.randint(5000, 10000)
        phrase_showing = False
        phrase_text = ""
        phrase_start_time = 0
        phrase_font = get_katakana_font(max(42, FONT_SIZE * 2))
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        pygame.mouse.set_visible(True)
                        show_config_screen(screen)
                        pygame.mouse.set_visible(False)
                        # Reset mouse position tracking after config
                        last_mouse_pos = pygame.mouse.get_pos()
                        time_since_last_significant_move = current_time
                        continue
                    elif event.key == pygame.K_m:
                        pygame.mouse.set_visible(True)
                        show_live_config_screen(screen, monitor_drops, monitor_regions)
                        pygame.mouse.set_visible(False)
                        # Reset mouse position tracking after live config
                        last_mouse_pos = pygame.mouse.get_pos()
                        time_since_last_significant_move = current_time
                        # Reload config after live configuration
                        load_config()
                        continue
                    else:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    if (
                        current_time - time_since_last_significant_move
                        > significant_move_delay
                    ):
                        current_mouse_pos = event.pos
                        if (
                            abs(current_mouse_pos[0] - last_mouse_pos[0]) > 3
                            or abs(current_mouse_pos[1] - last_mouse_pos[1]) > 3
                        ):
                            running = False
                    last_mouse_pos = event.pos
            
            if not running:
                break
            
            # Fill background with theme color
            screen.fill(background_color)
            
            # Update and draw particles if enabled
            if ENABLE_PARTICLES:
                # Remove dead particles
                particles = [p for p in particles if not p.is_dead()]
                
                # Add new particles if needed
                while len(particles) < int(screen.get_width() * screen.get_height() * PARTICLE_DENSITY / 10000):
                    particles.append(Particle(
                        random.randint(0, screen.get_width()),
                        random.randint(-50, 0),
                        screen.get_width(),
                        screen.get_height()
                    ))
                
                # Update and draw particles
                for particle in particles:
                    particle.update()
                    particle.draw(screen, theme_colors)
            
            # Draw matrix for each monitor
            for m, region in enumerate(monitor_regions):
                ox, oy, w, h = region
                drops = monitor_drops[m]
                num_columns = len(drops)
                for i in range(num_columns):
                    if drops[i] is None or not drops[i].is_active:
                        if random.random() < NEW_DROP_CHANCE:
                            drops[i] = Drop(ox + i * FONT_SIZE, active_font, h)
                    if drops[i] is not None:
                        drops[i].fall()
                        drops[i].draw(screen)
                        if not drops[i].is_active:
                            drops[i] = None
            
            # --- Phrase display logic (centered on primary monitor only) ---
            if custom_phrases and monitor_regions:
                # Center phrase on the first monitor (primary)
                ox, oy, w, h = monitor_regions[0]
                if not phrase_showing and current_time >= phrase_next_time:
                    phrase_text = random.choice(custom_phrases)
                    phrase_showing = True
                    phrase_start_time = current_time
                if phrase_showing:
                    elapsed = current_time - phrase_start_time
                    if elapsed < 1000:
                        alpha = int(255 * (elapsed / 1000.0))  # Fade in
                    elif elapsed < 3000:
                        alpha = 255  # Hold
                    elif elapsed < 4000:
                        alpha = int(255 * (1 - (elapsed - 3000) / 1000.0))  # Fade out
                    else:
                        phrase_showing = False
                        phrase_next_time = current_time + random.randint(5000, 10000)
                        alpha = 0
                    if alpha > 0 and phrase_text:
                        phrase_surf = phrase_font.render(
                            phrase_text, True, (255, 255, 255)
                        )
                        phrase_surf = phrase_surf.convert_alpha()
                        phrase_surf.set_alpha(alpha)
                        x = ox + (w - phrase_surf.get_width()) // 2
                        y = oy + (h - phrase_surf.get_height()) // 2
                        shadow = phrase_font.render(phrase_text, True, (0, 0, 0))
                        shadow = shadow.convert_alpha()
                        shadow.set_alpha(int(alpha * 0.7))
                        screen.blit(shadow, (x + 2, y + 2))
                        screen.blit(phrase_surf, (x, y))
            
            pygame.display.flip()
            clock.tick(FRAME_RATE)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            continue
        else:
            break


def show_live_config_screen(surface, current_drops, monitor_regions):
    """Show configuration screen that applies changes immediately to running screensaver"""
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX, DROP_COLOR_BODY, DROP_COLOR_HEAD
    global ENABLE_PARTICLES, ENABLE_SOUND, MATRIX_THEME, PARTICLE_DENSITY, GLOW_EFFECT, RAINBOW_MODE, PULSE_EFFECT
    
    # No full-screen overlay needed - we'll only draw the panel background
    
    # Get current config values
    current_config = {
        "font_size": FONT_SIZE,
        "min_speed": MIN_SPEED,
        "max_speed": MAX_SPEED,
        "new_drop_chance": NEW_DROP_CHANCE,
        "char_change_prob": CHAR_CHANGE_PROB,
        "stream_length_min": STREAM_LENGTH_MIN,
        "stream_length_max": STREAM_LENGTH_MAX,
        "body_color_r": DROP_COLOR_BODY[0],
        "body_color_g": DROP_COLOR_BODY[1],
        "body_color_b": DROP_COLOR_BODY[2],
        "custom_phrases": load_config().get("custom_phrases", []),
        "enable_particles": ENABLE_PARTICLES,
        "enable_sound": ENABLE_SOUND,
        "matrix_theme": MATRIX_THEME,
        "particle_density": PARTICLE_DENSITY,
        "glow_effect": GLOW_EFFECT,
        "rainbow_mode": RAINBOW_MODE,
        "pulse_effect": PULSE_EFFECT
    }
    
    # Calculate center position for the config panel
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    
    # Create a centered configuration panel with scrolling capability
    panel_width = 600
    panel_height = min(500, screen_height - 100)  # Ensure panel fits on screen
    panel_x = (screen_width - panel_width) // 2
    panel_y = (screen_height - panel_height) // 2
    
    # Content area dimensions (smaller than panel to allow for scrollbar)
    content_width = panel_width - 60  # Leave space for scrollbar
    content_height = 800  # Total content height (larger than visible area)
    scroll_offset = 0
    max_scroll = max(0, content_height - panel_height + 120)  # Maximum scroll distance
    
    # Create sliders for live configuration
    slider_width = 250
    y_start = 80  # Start from top of content area
    y_step = 50
    x_start = 50  # Relative to content area
    
    sliders = []
    
    # Font Size
    sliders.append(Slider(x_start, y_start, slider_width, 20, 10, 32, current_config["font_size"], "Font Size", int, 1))
    y_start += y_step
    
    # Min Speed
    sliders.append(Slider(x_start, y_start, slider_width, 20, 1, 10, current_config["min_speed"], "Min Speed", int, 1))
    y_start += y_step
    
    # Max Speed
    sliders.append(Slider(x_start, y_start, slider_width, 20, 2, 15, current_config["max_speed"], "Max Speed", int, 1))
    y_start += y_step
    
    # Drop Chance
    sliders.append(Slider(x_start, y_start, slider_width, 20, 0.05, 1.0, current_config["new_drop_chance"], "Drop Chance", float, 0.05))
    y_start += y_step
    
    # Char Switch
    sliders.append(Slider(x_start, y_start, slider_width, 20, 0.0, 0.5, current_config["char_change_prob"], "Char Switch", float, 0.01))
    y_start += y_step
    
    # Stream Length
    avg_length = (current_config["stream_length_min"] + current_config["stream_length_max"]) // 2
    sliders.append(Slider(x_start, y_start, slider_width, 20, 10, 70, avg_length, "Avg Length", int, 1))
    y_start += y_step
    
    # Color sliders
    r_slider = Slider(x_start, y_start, slider_width, 20, 0, 255, current_config["body_color_r"], "Red", int, 1)
    sliders.append(r_slider)
    y_start += y_step
    
    g_slider = Slider(x_start, y_start, slider_width, 20, 0, 255, current_config["body_color_g"], "Green", int, 1)
    sliders.append(g_slider)
    y_start += y_step
    
    b_slider = Slider(x_start, y_start, slider_width, 20, 0, 255, current_config["body_color_b"], "Blue", int, 1)
    sliders.append(b_slider)
    y_start += y_step
    
    # Custom phrases textbox
    phrases_box = TextBox(x_start, y_start, slider_width + 100, 80, "", get_katakana_font(16), max_lines=4)
    phrases_box.set_lines(current_config["custom_phrases"])
    
    # Theme selection
    y_start += 110
    theme_label = get_katakana_font(18).render("Theme:", True, (180, 255, 180))
    theme_buttons = []
    theme_names = list(MATRIX_THEMES.keys())
    theme_button_width = 90
    theme_button_spacing = 15
    for i, theme_name in enumerate(theme_names):
        theme_buttons.append(Button(
            x_start + i * (theme_button_width + theme_button_spacing),
            y_start,
            theme_button_width,
            35,
            theme_name.capitalize(),
            color=(70, 70, 70) if theme_name != current_config["matrix_theme"] else (110, 110, 70)
        ))
    
    # Effect toggles
    y_start += 70
    effect_label = get_katakana_font(18).render("Effects:", True, (180, 255, 180))
    effect_buttons = []
    effects = [
        ("Particles", "enable_particles"),
        ("Glow", "glow_effect"),
        ("Rainbow", "rainbow_mode"),
        ("Pulse", "pulse_effect")
    ]
    effect_button_width = 75
    effect_button_spacing = 15
    for i, (effect_name, effect_key) in enumerate(effects):
        effect_buttons.append(Button(
            x_start + i * (effect_button_width + effect_button_spacing),
            y_start,
            effect_button_width,
            30,
            effect_name,
            color=(70, 70, 70) if not current_config[effect_key] else (110, 70, 70)
        ))
    
    # Particle density slider
    y_start += 50
    particle_density_slider = Slider(
        x_start, y_start, slider_width, 20, 0.1, 1.0, 
        current_config["particle_density"], "Particle Density", float, 0.1
    )
    
    # Buttons
    button_y = y_start + 80
    save_button = Button(x_start, button_y, 120, 40, "Save")
    reset_button = Button(x_start + 130, button_y, 120, 40, "Reset")
    close_button = Button(x_start + 260, button_y, 120, 40, "Close")
    
    # Title
    title_font = get_katakana_font(28)
    title_text = "Live Configuration (Press ESC to close)"
    
    running = True
    clock = pygame.time.Clock()
    panel_alpha = 0  # For UI elements fade-in animation
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    # Save and close
                    _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                             current_config, current_drops, monitor_regions)
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(max_scroll, scroll_offset + 30)
                elif event.key == pygame.K_PAGEUP:
                    scroll_offset = max(0, scroll_offset - 100)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_offset = min(max_scroll, scroll_offset + 100)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.button == 5:  # Mouse wheel down
                    scroll_offset = min(max_scroll, scroll_offset + 30)
            
            # Adjust event coordinates for scrolling if it's a mouse event
            scroll_adjusted_event = event
            if hasattr(event, 'pos') and event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                # Adjust mouse position for scroll offset within the content area
                mouse_x, mouse_y = event.pos
                if content_rect.collidepoint(mouse_x, mouse_y):
                    # Convert screen coordinates to content coordinates
                    content_mouse_x = mouse_x - (panel_x + 20)
                    content_mouse_y = mouse_y - (panel_y + 50) + scroll_offset
                    scroll_adjusted_event = type('Event', (), {
                        'type': event.type,
                        'pos': (content_mouse_x, content_mouse_y),
                        'button': getattr(event, 'button', None),
                    })()
            
            # Handle slider events with proper positioning
            slider_changed = False
            for slider in sliders:
                # Temporarily adjust slider positions to match screen coordinates
                temp_rect = slider.rect.copy()
                temp_track_rect = slider.track_rect.copy()
                # Adjust for panel position and scroll offset
                slider.rect.x += panel_x + 20
                slider.rect.y += panel_y + 50 - scroll_offset
                slider.track_rect.x += panel_x + 20
                slider.track_rect.y += panel_y + 50 - scroll_offset
                old_val = slider.current_val
                slider.handle_event(event)
                if old_val != slider.current_val:
                    slider_changed = True
                slider.rect = temp_rect
                slider.track_rect = temp_track_rect
            
            # Handle particle density slider
            temp_rect = particle_density_slider.rect.copy()
            temp_track_rect = particle_density_slider.track_rect.copy()
            particle_density_slider.rect.x += panel_x + 20
            particle_density_slider.rect.y += panel_y + 50 - scroll_offset
            particle_density_slider.track_rect.x += panel_x + 20
            particle_density_slider.track_rect.y += panel_y + 50 - scroll_offset
            old_particle_val = particle_density_slider.current_val
            particle_density_slider.handle_event(event)
            if old_particle_val != particle_density_slider.current_val:
                slider_changed = True
            particle_density_slider.rect = temp_rect
            particle_density_slider.track_rect = temp_track_rect
            
            # Force re-draw if any slider changed
            if slider_changed:
                _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                         current_config, current_drops, monitor_regions, save_to_file=False)
            
            # Handle textbox events
            temp_rect = phrases_box.rect.copy()
            phrases_box.rect.x += panel_x + 20
            phrases_box.rect.y += panel_y + 50 - scroll_offset
            phrases_box.handle_event(event)
            phrases_box.rect = temp_rect
            
            # Handle theme button events
            for i, theme_button in enumerate(theme_buttons):
                temp_rect = theme_button.rect.copy()
                theme_button.rect.x += panel_x + 20
                theme_button.rect.y += panel_y + 50 - scroll_offset
                if theme_button.handle_event(event):
                    # Update button colors
                    for j, btn in enumerate(theme_buttons):
                        btn.color = (70, 70, 70) if j != i else (110, 110, 70)
                    current_config["matrix_theme"] = theme_names[i]
                    # Force re-draw of the screensaver
                    _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                             current_config, current_drops, monitor_regions, save_to_file=False)
                theme_button.rect = temp_rect
            
            # Handle effect button events
            for i, effect_button in enumerate(effect_buttons):
                temp_rect = effect_button.rect.copy()
                effect_button.rect.x += panel_x + 20
                effect_button.rect.y += panel_y + 50 - scroll_offset
                if effect_button.handle_event(event):
                    effect_key = effects[i][1]
                    current_config[effect_key] = not current_config[effect_key]
                    effect_button.color = (110, 70, 70) if current_config[effect_key] else (70, 70, 70)
                    # Force re-draw of the screensaver
                    _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                             current_config, current_drops, monitor_regions, save_to_file=False)
                effect_button.rect = temp_rect
            
            # Handle button events
            temp_rect = save_button.rect.copy()
            save_button.rect.x += panel_x + 20
            save_button.rect.y += panel_y + 50 - scroll_offset
            save_clicked = save_button.handle_event(event)
            save_button.rect = temp_rect
            
            temp_rect = reset_button.rect.copy()
            reset_button.rect.x += panel_x + 20
            reset_button.rect.y += panel_y + 50 - scroll_offset
            reset_clicked = reset_button.handle_event(event)
            reset_button.rect = temp_rect
            
            temp_rect = close_button.rect.copy()
            close_button.rect.x += panel_x + 20
            close_button.rect.y += panel_y + 50 - scroll_offset
            close_clicked = close_button.handle_event(event)
            close_button.rect = temp_rect
            
            if save_clicked:
                _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                         current_config, current_drops, monitor_regions)
                running = False
            elif reset_clicked:
                # Reset to current config
                sliders[0].current_val = current_config["font_size"]
                sliders[1].current_val = current_config["min_speed"]
                sliders[2].current_val = current_config["max_speed"]
                sliders[3].current_val = current_config["new_drop_chance"]
                sliders[4].current_val = current_config["char_change_prob"]
                sliders[5].current_val = avg_length
                r_slider.current_val = current_config["body_color_r"]
                g_slider.current_val = current_config["body_color_g"]
                b_slider.current_val = current_config["body_color_b"]
                phrases_box.set_lines(current_config["custom_phrases"])
                particle_density_slider.current_val = current_config["particle_density"]
                # Reset theme and effects
                for i, theme_name in enumerate(theme_names):
                    theme_buttons[i].color = (70, 70, 70) if theme_name != current_config["matrix_theme"] else (110, 110, 70)
                for i, (effect_name, effect_key) in enumerate(effects):
                    effect_buttons[i].color = (110, 70, 70) if current_config[effect_key] else (70, 70, 70)
                _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, 
                                         current_config, current_drops, monitor_regions)
            elif close_clicked:
                running = False
        
        # Apply changes in real-time
        _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, current_config, current_drops, monitor_regions, save_to_file=False)
        
        # Draw the configuration panel background with fade-in animation (no full-screen overlay)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Draw shadow first
        shadow_surface = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (*[0, 0, 0], 100), (10, 10, panel_width, panel_height), border_radius=15)
        surface.blit(shadow_surface, (panel_x - 5, panel_y - 5))
        
        # Semi-transparent dark background for the panel only
        pygame.draw.rect(panel_surface, (*[20, 25, 30], 200), (0, 0, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(panel_surface, (*[80, 100, 120], 255), (0, 0, panel_width, panel_height), width=3, border_radius=15)
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Simple fade in animation for UI elements
        if panel_alpha < 255:
            panel_alpha = min(255, panel_alpha + 15)
        
        # Draw title with fade-in
        title_surf = title_font.render(title_text, True, (255, 255, 255))
        title_surf.set_alpha(panel_alpha)
        surface.blit(title_surf, (panel_x + (panel_width - title_surf.get_width()) // 2, panel_y + 20))
        
        # Create a clipping area for scrollable content
        content_rect = pygame.Rect(panel_x + 20, panel_y + 50, content_width, panel_height - 100)
        content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
        
        # Draw all content to the content surface (with scroll offset applied)
        content_y_offset = -scroll_offset
        
        # Draw content to content surface with scroll offset
        # Temporarily adjust slider positions for content surface
        for slider in sliders:
            # Draw slider to content surface at relative position
            temp_rect = slider.rect.copy()
            temp_track_rect = slider.track_rect.copy()
            slider.rect.y += content_y_offset
            slider.track_rect.y += content_y_offset
            slider.draw(content_surface)
            slider.rect = temp_rect
            slider.track_rect = temp_track_rect
        
        # Draw color preview
        current_color = (r_slider.current_val, g_slider.current_val, b_slider.current_val)
        preview_x = x_start + slider_width + 20
        preview_y = sliders[6].rect.y - scroll_offset + content_y_offset
        preview_size = 40
        preview_surface_small = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
        pygame.draw.rect(preview_surface_small, current_color, (0, 0, preview_size, preview_size))
        pygame.draw.rect(preview_surface_small, (255, 255, 255), (0, 0, preview_size, preview_size), 2)
        content_surface.blit(preview_surface_small, (preview_x, preview_y))
        
        # Draw phrases label and box
        phrases_label = get_katakana_font(18).render("Custom Phrases:", True, (180, 255, 180))
        content_surface.blit(phrases_label, (x_start, phrases_box.rect.y - 25 + content_y_offset))
        temp_rect = phrases_box.rect.copy()
        phrases_box.rect.y += content_y_offset
        phrases_box.draw(content_surface)
        phrases_box.rect = temp_rect
        
        # Draw theme selection
        content_surface.blit(theme_label, (x_start, theme_buttons[0].rect.y - 25 + content_y_offset))
        for theme_button in theme_buttons:
            temp_rect = theme_button.rect.copy()
            theme_button.rect.y += content_y_offset
            theme_button.draw(content_surface)
            theme_button.rect = temp_rect
        
        # Draw effect toggles
        content_surface.blit(effect_label, (x_start, effect_buttons[0].rect.y - 25 + content_y_offset))
        for effect_button in effect_buttons:
            temp_rect = effect_button.rect.copy()
            effect_button.rect.y += content_y_offset
            effect_button.draw(content_surface)
            effect_button.rect = temp_rect
        
        # Draw particle density slider
        temp_rect = particle_density_slider.rect.copy()
        temp_track_rect = particle_density_slider.track_rect.copy()
        particle_density_slider.rect.y += content_y_offset
        particle_density_slider.track_rect.y += content_y_offset
        particle_density_slider.draw(content_surface)
        particle_density_slider.rect = temp_rect
        particle_density_slider.track_rect = temp_track_rect
        
        # Draw buttons
        temp_rect = save_button.rect.copy()
        save_button.rect.y += content_y_offset
        save_button.draw(content_surface)
        save_button.rect = temp_rect
        
        temp_rect = reset_button.rect.copy()
        reset_button.rect.y += content_y_offset
        reset_button.draw(content_surface)
        reset_button.rect = temp_rect
        
        temp_rect = close_button.rect.copy()
        close_button.rect.y += content_y_offset
        close_button.draw(content_surface)
        close_button.rect = temp_rect
        
        # Blit the content surface to the main surface with clipping
        surface.set_clip(content_rect)
        surface.blit(content_surface, (panel_x + 20, panel_y + 50))
        surface.set_clip(None)
        
        # Draw scrollbar if needed
        if max_scroll > 0:
            scrollbar_x = panel_x + panel_width - 25
            scrollbar_y = panel_y + 50
            scrollbar_height = panel_height - 100
            scrollbar_width = 15
            
            # Draw scrollbar track
            pygame.draw.rect(surface, (40, 40, 40), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            
            # Draw scrollbar thumb
            thumb_height = max(20, scrollbar_height * (panel_height - 100) // content_height)
            thumb_y = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height)
            pygame.draw.rect(surface, (100, 100, 100), (scrollbar_x, int(thumb_y), scrollbar_width, int(thumb_height)))
        
        # Draw instructions at bottom (outside scroll area)
        instruction_font = get_katakana_font(14)
        instructions = [
            "Use arrow keys or mouse wheel to scroll",
            "Press ENTER or Save to save permanently",
            "Press ESC or Close to cancel"
        ]
        for i, instruction in enumerate(instructions):
            inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
            inst_surf.set_alpha(panel_alpha)
            surface.blit(inst_surf, (panel_x + 20, panel_y + panel_height - 45 + i * 15))
        
        pygame.display.flip()
        clock.tick(30)


def _apply_live_config(sliders, phrases_box, current_drops, monitor_regions, save_to_file=True):
    """Apply configuration changes immediately to the running screensaver"""
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX, DROP_COLOR_BODY, DROP_COLOR_HEAD
    
    # Update global variables
    FONT_SIZE = sliders[0].current_val
    MIN_SPEED = sliders[1].current_val
    MAX_SPEED = sliders[2].current_val
    NEW_DROP_CHANCE = sliders[3].current_val
    CHAR_CHANGE_PROB = sliders[4].current_val
    
    # Calculate stream length from average
    avg_len = sliders[5].current_val
    len_spread = max(5, avg_len // 4)
    STREAM_LENGTH_MIN = max(5, avg_len - len_spread)
    STREAM_LENGTH_MAX = avg_len + len_spread
    
    # Update colors
    r, g, b = sliders[6].current_val, sliders[7].current_val, sliders[8].current_val
    update_drop_colors(r, g, b)
    
    # Update drops with new font and parameters
    for monitor_drops in current_drops:
        for i, drop in enumerate(monitor_drops):
            if drop is not None:
                # Update existing drop parameters
                drop.font = get_katakana_font(FONT_SIZE)
                drop.screen_height = monitor_regions[0][3] if monitor_regions else 1080
                
                # Update speed
                if MIN_SPEED > MAX_SPEED:
                    drop.speed = MAX_SPEED
                else:
                    drop.speed = random.randint(MIN_SPEED, MAX_SPEED)
                
                # Update length
                if STREAM_LENGTH_MIN > STREAM_LENGTH_MAX:
                    drop.length = STREAM_LENGTH_MAX
                else:
                    drop.length = random.randint(STREAM_LENGTH_MIN, STREAM_LENGTH_MAX)
                
                # Regenerate characters with new font
                drop._generate_initial_characters()
    
    # Save to file if requested
    if save_to_file:
        config_to_save = {
            "font_size": FONT_SIZE,
            "min_speed": MIN_SPEED,
            "max_speed": MAX_SPEED,
            "new_drop_chance": NEW_DROP_CHANCE,
            "char_change_prob": CHAR_CHANGE_PROB,
            "stream_length_min": STREAM_LENGTH_MIN,
            "stream_length_max": STREAM_LENGTH_MAX,
            "body_color_r": r,
            "body_color_g": g,
            "body_color_b": b,
            "custom_phrases": phrases_box.get_lines(),
        }
        save_config(config_to_save)


def _apply_live_config_enhanced(sliders, phrases_box, particle_density_slider, current_config, current_drops, monitor_regions, save_to_file=True):
    """Apply enhanced configuration changes immediately to the running screensaver"""
    global FONT_SIZE, MIN_SPEED, MAX_SPEED, NEW_DROP_CHANCE, CHAR_CHANGE_PROB, STREAM_LENGTH_MIN, STREAM_LENGTH_MAX, DROP_COLOR_BODY, DROP_COLOR_HEAD
    global ENABLE_PARTICLES, ENABLE_SOUND, MATRIX_THEME, PARTICLE_DENSITY, GLOW_EFFECT, RAINBOW_MODE, PULSE_EFFECT
    
    # Update basic global variables
    FONT_SIZE = sliders[0].current_val
    MIN_SPEED = sliders[1].current_val
    MAX_SPEED = sliders[2].current_val
    NEW_DROP_CHANCE = sliders[3].current_val
    CHAR_CHANGE_PROB = sliders[4].current_val
    
    # Calculate stream length from average
    avg_len = sliders[5].current_val
    len_spread = max(5, avg_len // 4)
    STREAM_LENGTH_MIN = max(5, avg_len - len_spread)
    STREAM_LENGTH_MAX = avg_len + len_spread
    
    # Update colors
    r, g, b = sliders[6].current_val, sliders[7].current_val, sliders[8].current_val
    update_drop_colors(r, g, b)
    
    # Update enhanced features
    ENABLE_PARTICLES = current_config["enable_particles"]
    ENABLE_SOUND = current_config["enable_sound"]
    MATRIX_THEME = current_config["matrix_theme"]
    PARTICLE_DENSITY = particle_density_slider.current_val
    GLOW_EFFECT = current_config["glow_effect"]
    RAINBOW_MODE = current_config["rainbow_mode"]
    PULSE_EFFECT = current_config["pulse_effect"]
    
    # Update drops with new font and parameters
    for monitor_drops in current_drops:
        for i, drop in enumerate(monitor_drops):
            if drop is not None:
                # Update existing drop parameters
                drop.font = get_katakana_font(FONT_SIZE)
                drop.screen_height = monitor_regions[0][3] if monitor_regions else 1080
                
                # Update speed
                if MIN_SPEED > MAX_SPEED:
                    drop.speed = MAX_SPEED
                else:
                    drop.speed = random.randint(MIN_SPEED, MAX_SPEED)
                
                # Update length
                if STREAM_LENGTH_MIN > STREAM_LENGTH_MAX:
                    drop.length = STREAM_LENGTH_MAX
                else:
                    drop.length = random.randint(STREAM_LENGTH_MIN, STREAM_LENGTH_MAX)
                
                # Regenerate characters with new font
                drop._generate_initial_characters()
    
    # Save to file if requested
    if save_to_file:
        config_to_save = {
            "font_size": FONT_SIZE,
            "min_speed": MIN_SPEED,
            "max_speed": MAX_SPEED,
            "new_drop_chance": NEW_DROP_CHANCE,
            "char_change_prob": CHAR_CHANGE_PROB,
            "stream_length_min": STREAM_LENGTH_MIN,
            "stream_length_max": STREAM_LENGTH_MAX,
            "body_color_r": r,
            "body_color_g": g,
            "body_color_b": b,
            "custom_phrases": phrases_box.get_lines(),
            "enable_particles": ENABLE_PARTICLES,
            "enable_sound": ENABLE_SOUND,
            "matrix_theme": MATRIX_THEME,
            "particle_density": PARTICLE_DENSITY,
            "glow_effect": GLOW_EFFECT,
            "rainbow_mode": RAINBOW_MODE,
            "pulse_effect": PULSE_EFFECT,
        }
        save_config(config_to_save)


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    load_config()
    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
    show_config_ui = False
    run_full_screensaver = True
    arg = ""
    display_index = None

    # Parse arguments for display index
    for a in sys.argv[1:]:
        if a.startswith("--display="):
            display_index = int(a.split("=")[-1])
        else:
            arg = a.lower()

    if arg.startswith("/c"):
        show_config_ui = True
        run_full_screensaver = False
    elif arg == "/s":
        pass
    elif arg.startswith("/p"):
        print("Preview mode (/p) runs fullscreen for this script version.")
    elif len(sys.argv) > 1:
        print(f"Unknown argument: {arg}. Running screensaver with current settings.")
    elif not os.path.exists(CONFIG_FILE):
        show_config_ui = True

    if show_config_ui:
        config_screen_width = 780
        config_screen_height = 480
        try:
            screen = pygame.display.set_mode(
                (config_screen_width, config_screen_height), 0, 32
            )
            pygame.display.set_caption("Screensaver Configuration")
            pygame.mouse.set_visible(True)
            show_config_screen(screen)
            load_config()
        except pygame.error as e:
            print(f"Could not set display mode for config: {e}.")
            if arg.startswith("/c"):
                pygame.quit()
                sys.exit("Failed to display config.")
        if arg.startswith("/c") and not run_full_screensaver:
            pygame.quit()
            sys.exit()

    if run_full_screensaver:
        load_config()
        # --- Single large window spanning all displays ---
        try:
            display_sizes = pygame.display.get_desktop_sizes()
            total_width = sum(w for w, h in display_sizes)
            max_height = max(h for w, h in display_sizes)
            screen = pygame.display.set_mode((total_width, max_height), pygame.FULLSCREEN | pygame.NOFRAME)
        except Exception:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
        run_screensaver(screen)
    pygame.quit()
    sys.exit()


def set_window(hwnd, x, y, w, h):
    # Set window position and parent
    pygame.display.set_mode((w, h), pygame.NOFRAME)
    window = pygame.display.get_wm_info()['window']
    win32gui.SetWindowLong(window, win32con.GWL_STYLE, win32con.WS_VISIBLE)
    win32gui.SetParent(window, int(hwnd))
    win32gui.MoveWindow(window, x, y, w, h, True)

# Parse args for --hwnd, --x, --y, --w, --h
hwnd, x, y, w, h = None, 0, 0, 800, 600
for arg in sys.argv:
    if arg.startswith('--hwnd='):
        hwnd = int(arg.split('=')[1])
    elif arg.startswith('--x='):
        x = int(arg.split('=')[1])
    elif arg.startswith('--y='):
        y = int(arg.split('=')[1])
    elif arg.startswith('--w='):
        w = int(arg.split('=')[1])
    elif arg.startswith('--h='):
        h = int(arg.split('=')[1])

if hwnd:
    set_window(hwnd, x, y, w, h)

if __name__ == "__main__":
    main()
