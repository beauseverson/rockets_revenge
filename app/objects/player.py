import pyxel

class Player:
    def __init__(self, x_tile: int, y_tile: int, health: int = 3, player_speed: int = 8):
        self.x_tile = x_tile  # Player's x position in tiles
        self.y_tile = y_tile  # Player's y position in tiles
        self.width = 8    # Player width in pixels
        self.height = 8   # Player height in pixels
        self.health = health  # Player's health
        self.player_speed = player_speed  # Player speed in pixels per move
        self.sprite_bank = 0  # Image bank for the sprite
        self.sprite_u = 24    # U (x) coordinate for sprite sheet
        self.sprite_v = 0   # V (y) coordinate for sprite sheet
        self.is_moving = False  # Flag to prevent multiple moves per frame

    def move(self, dx, dy):
        """Move the player by dx, dy tiles."""
        self.x_tile += dx
        self.y_tile += dy

    def take_damage(self, amount):
        """Reduce player's health by the specified amount."""
        self.health -= amount
        if self.health < 0:
            self.health = 0  # Prevent negative health

    def heal(self, amount):
        """Increase player's health by the specified amount."""
        self.health += amount

    def draw(self, x_override: int = None, y_override: int = None):
        """Draw the player at the specified screen coordinates."""
        screen_x = x_override if x_override is not None else self.x_tile * 8
        screen_y = y_override if y_override is not None else self.y_tile * 8

        pyxel.blt(
            screen_x,
            screen_y,
            self.sprite_bank,
            self.sprite_u,
            self.sprite_v,
            self.width,
            self.height,
            pyxel.COLOR_BLACK
        )