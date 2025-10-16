import pyxel

class MapManager:
    SCROLL_SPEED = 4 # Pixels per frame for smooth transition
    TILE_SIZE = 8

    def __init__(self, app, room_data, room_tiles_w, room_tiles_h):
        self.app = app
        self.room_data = room_data
        self.room_tiles_w = room_tiles_w
        self.room_tiles_h = room_tiles_h
        self.room_h = room_tiles_h * self.TILE_SIZE # in pixels
        self.room_w = room_tiles_w * self.TILE_SIZE # in pixels
        self.current_room_id = list(room_data.keys())[0]
    
        # Transition State Variables for Zelda-style scrolling
        self.transition_state = "IDLE"  # 'IDLE', 'SCROLLING'
        self.transition_direction = None # 'R', 'L', 'U', 'D'
        self.scroll_offset_x = 0 # Current pixel offset for horizontal scroll
        self.scroll_offset_y = 0 # Current pixel offset for vertical scroll
        self.target_room_id = None # ID of the room we are scrolling into
        self.next_player_pos = (1, 1) # Player's target tile in the new room

        self.load_resources()

    def _update_transition(self):
        """Handles the smooth room scrolling transition."""
        speed = self.SCROLL_SPEED
        direction = self.transition_direction
        
        # Scroll the offsets
        if direction == "R":
            self.scroll_offset_x += speed
            if self.scroll_offset_x >= self.room_w:
                self.scroll_offset_x = self.room_w
                self._complete_transition()
        elif direction == "L":
            self.scroll_offset_x -= speed
            if self.scroll_offset_x <= -self.room_w:
                self.scroll_offset_x = -self.room_w
                self._complete_transition()
        elif direction == "D":
            self.scroll_offset_y += speed
            if self.scroll_offset_y >= self.room_h:
                self.scroll_offset_y = self.room_h
                self._complete_transition()
        elif direction == "U":
            self.scroll_offset_y -= speed
            if self.scroll_offset_y <= -self.room_h:
                self.scroll_offset_y = -self.room_h
                self._complete_transition()

    def _complete_transition(self):
        """Finalizes the transition and moves to the new room."""
        # Update current room state
        self.current_room_id = self.target_room_id

        # move the apps player to the new position
        self.app.player.x_tile, self.app.player.y_tile = self.next_player_pos

        # Reset transition variables
        self.transition_state = "IDLE"
        self.transition_direction = None
        self.scroll_offset_x = 0
        self.scroll_offset_y = 0
        self.target_room_id = None
        self.app.game_message = ""

    def load_resources(self):
        # Load all rooms into tilemap 0
        for room_id, room in self.room_data.items():
            map_data = room["map_data"]
            offset_y_tiles = room["tm_offset_y"]

            # convert the flat list of tile IDs (0, 1, 2) into rows and set them in the tilemap
            map_rows_hex = []

            for y in range(self.room_tiles_h):
                start = y * self.room_tiles_w
                end = start + self.room_tiles_w
                row = map_data[start:end]

                hex_row_string = ""

                for tile_id in row:
                    # u coordinate is tile_id, v coordinate is always 0 in the image bank
                    u = tile_id
                    v = 0
                    # Format: "{u:02x}{v:02x}"
                    hex_string = f"{u:02x}{v:02x}"
                    hex_row_string += hex_string

                map_rows_hex.append(hex_row_string)

            pyxel.tilemaps[0].set(0, offset_y_tiles, map_rows_hex)

    def get_tile_id(self, tx, ty, room_id=None):
        if room_id is None:
            room_id = self.current_room_id
        room = self.room_data[room_id]
        if 0 <= tx < self.room_tiles_w and 0 <= ty < self.room_tiles_h:
            index = ty * self.room_tiles_w + tx
            return room["map_data"][index]
        return 1  # Wall

    def is_walkable(self, tx, ty, room_id=None):
        """
        Check if a tile at x and y in a given room is walkable.
        Defaults to the current room if no room_id is provided.
        """
        if room_id is None:
            room_id = self.current_room_id

        tile_id = self.get_tile_id(tx, ty, room_id)
        return tile_id in (0, 2)

    def set_current_room(self, room_id):
        self.current_room_id = room_id

    def get_current_room(self):
        return self.room_data[self.current_room_id]

    def get_neighbors(self, room_id=None):
        """
        Get the neighboring room IDs for the current room.
        """
        if room_id is None:
            room_id = self.current_room_id
        return self.room_data[room_id].get("neighbors", {})

    def get_neighbor(self, direction, room_id=None):
        """
        Get the neighboring room ID in a given direction.
        """
        if room_id is None:
            room_id = self.current_room_id
        neighbors = self.get_neighbors(room_id)
        return neighbors.get(direction)
    
    def transition_room(self, direction, player_x, player_y):
        """Returns (new_room_id, new_player_x, new_player_y) if transition is possible, else None."""
        neighbor = self.get_neighbor(direction)
        if not neighbor:
            return None
        # Calculate new player position based on direction
        if direction == "R":
            new_x, new_y = 1, player_y
        elif direction == "L":
            new_x, new_y = self.room_tiles_w - 2, player_y
        elif direction == "D":
            new_x, new_y = player_x, 1
        elif direction == "U":
            new_x, new_y = player_x, self.room_tiles_h - 2
        else:
            return None
        self.current_room_id = neighbor
        return neighbor, new_x, new_y
    
    def draw(self):
        # 1. Draw Room 1 (Current Room, scrolling out)
        room_to_draw_1_id = self.current_room_id
        offset_y1_tiles = self.room_data[room_to_draw_1_id]["tm_offset_y"]
        v_offset_pixels1 = offset_y1_tiles * self.TILE_SIZE 

        # Drawing position of the current room (Room 1) is offset by the scroll
        draw_x1 = -self.scroll_offset_x
        draw_y1 = -self.scroll_offset_y
        
        # Draw Room 1
        pyxel.bltm(draw_x1, draw_y1, 0, 0, v_offset_pixels1, self.room_w, self.room_h)

        if self.transition_state == "SCROLLING":
            # 2. Draw Room 2 (Target Room, scrolling in)
            room_to_draw_2_id = self.target_room_id
            offset_y2_tiles = self.room_data[room_to_draw_2_id]["tm_offset_y"]
            v_offset_pixels2 = offset_y2_tiles * self.TILE_SIZE
            
            direction = self.transition_direction
            draw_x2 = 0
            draw_y2 = 0

            # Determine position of Room 2 relative to Room 1
            if direction == "R":
                draw_x2 = self.room_w - self.scroll_offset_x
            elif direction == "L":
                draw_x2 = -self.room_w - self.scroll_offset_x
            elif direction == "D":
                draw_y2 = self.room_h - self.scroll_offset_y
            elif direction == "U":
                draw_y2 = -self.room_h - self.scroll_offset_y

            # Draw Room 2
            pyxel.bltm(draw_x2, draw_y2, 0, 0, v_offset_pixels2, self.room_w, self.room_h)
