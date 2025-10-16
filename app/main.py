# title: Rocket's Revenge
# author: Beau Severson
# desc: A Pyxel dungeon crawler test
# site: https://github.com/bseverson/rockets_revenge
# license: MIT
# version: 1.0

import pyxel

from objects.player import Player
from objects.map_manager import MapManager
from assets.maps import ROOM_DATA


# --- Constants ---
TILE_SIZE = 8
SCREEN_W = 160
SCREEN_H = 120

# Define the size of a single room in tiles (20x15)
ROOM_TILES_W = SCREEN_W // TILE_SIZE # 20 tiles wide
ROOM_TILES_H = SCREEN_H // TILE_SIZE # 15 tiles high

# Transition Speed (Zelda-style room scroll)
SCROLL_SPEED = 4 # Pixels per frame for smooth transition

# --- Room Data Definition ---
# tm_offset_y is the starting TILE ROW index where this room's 
# 15 rows of data are stored in Tilemap 0.



class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Rocket's Revenge", fps=30)
        pyxel.mouse(False) # disable mouse cursor

        # load assets
        pyxel.load("assets/rockets_revenge.pyxres")

        # Game Map and Tilemap Setup
        self.map_manager = MapManager(self, ROOM_DATA, ROOM_TILES_W, ROOM_TILES_H)
        self.map_manager.load_resources()

        # Game State
        self.current_room_id = self.map_manager.current_room_id
        self.game_state = "PLAYING" # 'PLAYING', 'GAME_OVER'
        self.game_message = "Welcome to the Dungeon!"

        # Game Objects
        self.player = Player(1, 1, health=3, player_speed=TILE_SIZE)

        pyxel.run(self.update, self.draw)

    def handle_movement(self):
        """Handles player input and movement."""
        # Only allow movement input if not currently transitioning
        if self.map_manager.transition_state == "SCROLLING":
            return
            
        # Using the correct D-pad button constants for gamepad input
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.attempt_move(self.player.x_tile, self.player.y_tile - 1, 0, -1)
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.attempt_move(self.player.x_tile, self.player.y_tile + 1, 0, 1)
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.attempt_move(self.player.x_tile - 1, self.player.y_tile, -1, 0)
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.attempt_move(self.player.x_tile + 1, self.player.y_tile, 1, 0)


    def attempt_move(self, next_x, next_y, dx, dy):
        """Checks for collision, room transitions, and updates position."""

        # Determine the direction moved for neighbor lookup
        direction = ""
        if dx == 1: direction = "R"
        elif dx == -1: direction = "L"
        elif dy == 1: direction = "D"
        elif dy == -1: direction = "U"

        current_room = self.map_manager.get_current_room()

        # 1. Check for Room Transition (if moving past the edge)
        is_transition = False

        # Check for L/R transitions
        if (direction == "R" and next_x == ROOM_TILES_W) or \
           (direction == "L" and next_x == -1):
            is_transition = True

        # Check for U/D transitions
        if (direction == "D" and next_y == ROOM_TILES_H) or \
           (direction == "U" and next_y == -1):
            is_transition = True

        if is_transition and direction in current_room["neighbors"]:
            next_room_id = current_room["neighbors"][direction]

            # 1a. Calculate player target position in the NEXT room
            target_x = self.player.x_tile
            target_y = self.player.y_tile

            if direction == "R":
                target_x = 1 # Start on the left side of the new room
            elif direction == "L":
                target_x = ROOM_TILES_W - 2 # Start on the right side of the new room
            elif direction == "D":
                target_y = 1 # Start on the top side of the new room
            elif direction == "U":
                target_y = ROOM_TILES_H - 2 # Start on the bottom side of the new room
            
            # 1b. Start the SCROLLING transition
            self.map_manager.transition_state = "SCROLLING"
            self.map_manager.transition_direction = direction
            self.map_manager.target_room_id = next_room_id
            self.map_manager.next_player_pos = (target_x, target_y)
            self.game_message = f"Transitioning to {next_room_id.replace('_', ' ')}..."
            return

        # 2. Check for Wall Collision (within room boundaries) - Player moves normally if not transitioning
        if 0 <= next_x < ROOM_TILES_W and 0 <= next_y < ROOM_TILES_H:
            if self.map_manager.is_walkable(next_x, next_y):
                self.player.x_tile = next_x
                self.player.y_tile = next_y
                self.game_message = "" # Clear message on successful move
            else:
                self.game_message = "Wall!" # Show collision message
        else:
            # If the move was blocked but didn't trigger a room change 
            self.game_message = "Boundary!"

    def update(self):
        """Called 30 times per second to update game logic."""
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.map_manager.transition_state == "SCROLLING":
            self.map_manager._update_transition()
        else:
            self.handle_movement()

    def draw(self):
        """Called 30 times per second to draw the screen."""
        pyxel.cls(0) # Clear screen to black (COLOR_BLACK)
        
        self.map_manager.draw()

        if self.map_manager.transition_state == "SCROLLING":
            # During transition, the player sprite moves with the old room via the scroll offset.
            player_screen_x = (self.player.x_tile * TILE_SIZE) - self.map_manager.scroll_offset_x
            player_screen_y = (self.player.y_tile * TILE_SIZE) - self.map_manager.scroll_offset_y
        else:
            # Not scrolling: Player is drawn at their current tile position in the fixed room
            player_screen_x = self.player.x_tile * TILE_SIZE
            player_screen_y = self.player.y_tile * TILE_SIZE

        # 3. Draw the player sprite
        self.player.draw(x_override=player_screen_x, y_override=player_screen_y)

        # Debug: Display current room info
        if self.map_manager.transition_state == "SCROLLING":
            # Display transition text
            pyxel.text(5, 5, f"Room: {self.map_manager.current_room_id} -> {self.map_manager.target_room_id}", pyxel.COLOR_WHITE)
        else:
            pyxel.text(5, 5, f"Room: {self.map_manager.current_room_id}", pyxel.COLOR_WHITE)

        # 4. Draw UI elements
        if self.game_message:
            pyxel.text(5, SCREEN_H - 12, self.game_message, pyxel.COLOR_ORANGE)

        pyxel.text(5, SCREEN_H - 5, "Use Arrow Keys. (Q) to quit.", pyxel.COLOR_GRAY)


# Start the application
App()
