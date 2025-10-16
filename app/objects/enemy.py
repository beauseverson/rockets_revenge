import pyxel
import random

class Enemy:
    def __init__(self, app, x_tile, y_tile, room_id, sprite_u, sprite_v, max_health=2, move_speed=1):
        """Basic enemy class with health and room association."""
        self.app = app
        self.x_tile = x_tile
        self.y_tile = y_tile
        self.room_id = room_id  # controls what room the enemy exists in
        self.state = 'alive'  # alive, dying, dead
        self.max_health = max_health
        self.health = max_health
        self.move_speed = move_speed  # tiles per second
        self.move_timer = 0
        self.y_velocity = 0

        # Sprite properties
        self.sprite_bank = 0
        self.sprite_u = sprite_u
        self.sprite_v = sprite_v
        self.width = 8
        self.height = 8

    def update(self):
        """Update enemy logic, like movement and death animation."""
        if self.state == 'dead':
            return

        if self.state == 'dying':
            self.y_velocity += 0.25  # Gravity
            self.y_tile += self.y_velocity

            if self.y_tile * self.app.TILE_SIZE > self.app.SCREEN_H:
                self.state = 'dead'
            return

        if self.room_id != self.app.map_manager.current_room_id:
            return

        # Simple random movement logic
        self.move_timer += 1
        if self.move_timer >= 30:  # Move every second
            self.move_timer = 0
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            next_x = self.x_tile + direction[0]
            next_y = self.y_tile + direction[1]

            if self.app.map_manager.is_walkable(next_x, next_y):
                self.x_tile = next_x
                self.y_tile = next_y

    def draw(self, x_override: int = None, y_override: int = None):
        """Draw the enemy at the specified screen coordinates."""
        if self.state == 'dead':
            return

        screen_x = x_override if x_override is not None else self.x_tile * self.app.TILE_SIZE
        screen_y = y_override if y_override is not None else self.y_tile * self.app.TILE_SIZE

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

    def take_damage(self, amount):
        """Reduces health by the specified amount and checks for death."""
        if self.state != 'alive':
            return

        self.health -= amount
        if self.health <= 0:
            self.state = 'dying'
            self.y_velocity = -1  # Pop up

    def heal(self, amount):
        """Increases health by the specified amount."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health


class StrongEnemy(Enemy):
    def __init__(self, app, x_tile, y_tile, room_id):
        super().__init__(app, x_tile, y_tile, room_id, sprite_u=16, sprite_v=0, max_health=3)


class FastEnemy(Enemy):
    def __init__(self, app, x_tile, y_tile, room_id):
        super().__init__(app, x_tile, y_tile, room_id, sprite_u=24, sprite_v=0, max_health=1, move_speed=2)