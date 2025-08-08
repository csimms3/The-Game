# The Game - Roguelike Adventure

A sophisticated roguelike game built with Python and Pygame, featuring both campaign and open-world modes with procedural generation, combat systems, and item management.

## Features

### Core Gameplay
- **Dual Game Modes**: Campaign mode with structured progression and Open World mode with endless exploration
- **Procedural World Generation**: Unique worlds created using noise algorithms with multiple biomes
- **Combat System**: Real-time combat with different enemy types and AI behaviors
- **Character Progression**: Leveling system with experience points and stat improvements
- **Item System**: Weapons, armor, and consumables with rarity tiers and effects

### World & Environment
- **Multiple Biomes**: Grass, forest, water, mountains, desert, and snow regions
- **Procedural Structures**: Ruins, towers, and caves scattered throughout the world
- **Dynamic Terrain**: Different movement costs and walkability for each terrain type
- **Item Distribution**: Items scattered throughout the world with varying rarity

### Combat & Enemies
- **Enemy AI**: Smart enemies with detection ranges, patrol behaviors, and combat tactics
- **Enemy Types**: Goblins, Orcs, Skeletons, and basic enemies with unique stats
- **Combat Mechanics**: Attack cooldowns, damage calculation, and health systems
- **Enemy Spawning**: Dynamic enemy spawning system that maintains challenge

### Player Systems
- **Movement**: Smooth WASD movement with collision detection
- **Inventory**: Item management with equipment slots for weapons and armor
- **Health & Stats**: Health bars, level indicators, and stat tracking
- **Experience**: Leveling system with increasing experience requirements

### Technical Features
- **State Management**: Clean state machine for menu, game, and pause states
- **Camera System**: Smooth camera following with world bounds
- **Performance Optimized**: Efficient rendering with visible area culling
- **Comprehensive Testing**: Full test suite covering all major systems
- **Logging System**: Detailed logging for debugging and monitoring

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd The-Game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

## Controls

### Movement
- **W/↑**: Move up
- **A/←**: Move left
- **S/↓**: Move down
- **D/→**: Move right

### Combat & Interaction
- **SPACE**: Attack nearest enemy
- **E**: Pickup nearby items
- **I**: View inventory
- **M**: View map

### Menu Navigation
- **↑/↓**: Navigate menus
- **ENTER**: Select option
- **ESC**: Pause game / Return to menu

## Game Modes

### Campaign Mode
- Structured progression through levels
- Increasing difficulty and enemy strength
- Story-driven objectives (coming soon)

### Open World Mode
- Endless exploration in procedurally generated worlds
- Dynamic enemy spawning
- Free-form gameplay with no time limits

## Gameplay Guide

### Getting Started
1. Choose your game mode from the main menu
2. Use WASD to move your character (blue square)
3. Explore the world to find items and enemies
4. Press SPACE to attack nearby enemies
5. Press E to pickup items when close to them
6. Level up by defeating enemies to gain experience

### Combat Tips
- Keep moving to avoid being surrounded by enemies
- Use terrain to your advantage - some areas are easier to navigate
- Equip better weapons and armor to increase your combat effectiveness
- Health potions can be found throughout the world

### Item System
- **Weapons**: Increase your attack power
- **Armor**: Provide defense and health bonuses
- **Consumables**: Health potions and other temporary effects
- **Rarity Tiers**: Common (gray), Uncommon (green), Rare (blue), Epic (purple), Legendary (orange)

### Enemy Types
- **Basic**: Standard enemies with balanced stats
- **Goblin**: Fast but weak enemies
- **Orc**: Slow but strong enemies with high health
- **Skeleton**: Fast enemies with moderate damage

## Development

### Project Structure
```
The-Game/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── game/                  # Main game package
│   ├── core/             # Core systems (settings, game engine)
│   ├── entities/         # Game entities (player, enemies)
│   ├── items/           # Item system
│   ├── states/          # Game states (menu, game, pause)
│   ├── world/           # World generation
│   └── utils/           # Utilities (logging)
├── tests/               # Test suite
└── assets/             # Game assets (auto-created)
```

### Running Tests
```bash
python -m pytest tests/
# or
python tests/test_game.py
```

### Adding Features
The game is designed with a modular architecture:
- Add new entities by extending the `Entity` base class
- Create new items by extending the `Item` class
- Add game states by extending `BaseState`
- Extend world generation in `WorldGenerator`

## Technical Details

### Performance
- Efficient rendering with visible area culling
- Optimized collision detection
- Smooth 60 FPS gameplay
- Memory-efficient world generation

### Architecture
- **State Machine**: Clean separation of game states
- **Component System**: Modular entity design
- **Factory Pattern**: Item creation system
- **Observer Pattern**: Event-driven systems

### Dependencies
- **pygame**: Game engine and graphics
- **numpy**: Numerical operations
- **noise**: Procedural generation
- **pytmx**: Tile map support (future)
- **pyscroll**: Scrolling support (future)

## Future Enhancements

### Planned Features
- **Sound System**: Music and sound effects
- **Particle Effects**: Combat and environmental effects
- **More Enemy Types**: Bosses and special enemies
- **Quest System**: Objectives and rewards
- **Save/Load System**: Game state persistence
- **Multiplayer**: Cooperative and competitive modes
- **Modding Support**: Custom content creation

### Technical Improvements
- **Sprite System**: Replace colored rectangles with proper sprites
- **Animation System**: Character and effect animations
- **Audio Engine**: Background music and sound effects
- **UI Improvements**: Better menus and HUD
- **Performance Optimization**: Further rendering optimizations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with Python and Pygame
- Procedural generation inspired by classic roguelikes
- Game design influenced by modern roguelike games