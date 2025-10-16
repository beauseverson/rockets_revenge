# Rocket's Revenge

Rocket's Revenge is a Pyxel-based dungeon crawler test project. It demonstrates modular game architecture with a focus on:

- **Room-based tilemaps**: Multiple rooms (mazes) are defined and loaded into a Pyxel tilemap, each with unique layouts and door connections.
- **Player class**: All player logic (movement, health, drawing) is encapsulated in a dedicated `Player` class.
- **MapManager class**: Handles all map, room, and transition logic, including tile lookups, walkability, and room transitions.
- **Room transitions**: Zelda-style smooth scrolling between rooms, with player position and state managed by the `MapManager`.
- **Extensible design**: Easy to add new rooms, features, or game logic by extending the relevant classes.

## Project Structure

```
rockets_revenge/
├── app/
│   ├── main.py                # Main game loop and App class
│   └── objects/
│       ├── player.py          # Player class
│       └── map_manager.py     # MapManager class
├── pyproject.toml
├── uv.lock
└── README.md
```

## How to Run

1. Install dependencies (Pyxel, etc.)
2. Run the game:
   ```sh
   uv run python app/main.py
   ```

## Features
- Three unique 20x15 mazes, each with multiple solutions and doorways connecting rooms
- Player movement and collision detection
- Room transitions with smooth scrolling
- Modular, maintainable codebase

## Controls
- Arrow keys: Move player
- Q: Quit game

## Requirements
- Python 3.8+
- [Pyxel](https://github.com/kitao/pyxel)
- [uv](https://github.com/astral-sh/uv) (for dependency management)

---
This project is for testing and learning purposes. Contributions and suggestions are welcome!
