# Matrix Screensaver

A Python-based Matrix-style screensaver with live configuration and enhanced visual effects.

## Features

### Core Matrix Effect
- Authentic Matrix-style falling characters using Katakana and numbers
- Configurable font size, speed, and stream length
- Customizable colors with RGB sliders
- Multi-monitor support
- Custom phrases that appear periodically

### Live Configuration (Press 'M' during screensaver)
- **Font Size**: Adjust character size (10-32)
- **Speed Control**: Set minimum and maximum drop speeds
- **Drop Chance**: Control frequency of new drops (0.05-1.0)
- **Character Switch**: Probability of characters changing (0.0-0.5)
- **Stream Length**: Average length of character streams
- **Color Control**: RGB sliders for custom colors
- **Custom Phrases**: Add your own Matrix-style messages

### Enhanced Visual Effects
- **Multiple Themes**: Classic, Cyberpunk, Retro, and Neon
- **Particle Effects**: Floating particles for added atmosphere
- **Glow Effects**: Character heads glow with theme colors
- **Rainbow Mode**: Dynamic color cycling across the screen
- **Pulse Effect**: Characters pulse with varying intensity
- **Particle Density**: Control the number of floating particles

### Controls
- **'M' Key**: Open live configuration screen
- **'C' Key**: Open full configuration screen
- **Mouse Movement**: Exit screensaver
- **Any Other Key**: Exit screensaver
- **ESC**: Close configuration screens

## Installation

### Requirements
- Python 3.6+
- Pygame
- pywin32 (for Windows)

### Setup
1. Install dependencies:
```bash
pip install pygame pywin32
```

2. Run the screensaver:
```bash
python matrix.py
```

### Windows Screensaver Installation
1. Copy `matrix.py` to a permanent location
2. Rename to `matrix.scr`
3. Copy to `C:\Windows\System32\`
4. Set as screensaver in Windows settings

## Configuration

### Command Line Arguments
- `/c` - Configuration mode
- `/s` - Screensaver mode
- `/p` - Preview mode
- `--display=N` - Specify display index

### Configuration File
Settings are saved to `matrix_config.json` and include:
- Font size and speed settings
- Color preferences
- Custom phrases
- Visual effects settings
- Theme selection

## Themes

### Classic
- Green Matrix characters on black background
- Traditional Matrix appearance

### Cyberpunk
- Cyan characters with white heads
- Dark blue background
- Futuristic aesthetic

### Retro
- Orange characters with yellow heads
- Dark red background
- Vintage computer feel

### Neon
- Magenta characters with white heads
- Dark purple background
- Bright neon appearance

## Visual Effects

### Particle System
- Floating particles that move across the screen
- Configurable density
- Theme-colored particles
- Smooth alpha blending

### Glow Effects
- Character heads emit a subtle glow
- Theme-appropriate glow colors
- Enhances visual depth

### Rainbow Mode
- Characters cycle through the color spectrum
- Position-based color variation
- Creates a psychedelic effect

### Pulse Effect
- Characters pulse with varying brightness
- Time-based animation
- Adds dynamic movement

## Customization Tips

1. **For a Classic Look**: Use Classic theme with green colors and disable extra effects
2. **For a Modern Feel**: Try Cyberpunk theme with particles and glow effects
3. **For Maximum Impact**: Enable rainbow mode with pulse effects
4. **For Performance**: Disable particles and effects on slower systems

## Performance Notes

- Particle effects may impact performance on older systems
- Rainbow and pulse effects are CPU-intensive
- Disable effects if you experience frame rate issues
- Multi-monitor setups require more resources

## Troubleshooting

### Common Issues
1. **Font not displaying correctly**: Install Japanese language support
2. **Performance issues**: Disable particle effects and visual enhancements
3. **Configuration not saving**: Check file permissions in the script directory
4. **Multi-monitor issues**: Ensure all monitors are properly detected

### Font Support
The screensaver tries multiple fonts in order:
- MS Gothic
- Meiryo
- Yu Gothic
- Arial Unicode MS
- Noto Sans CJK JP
- Arial (fallback)

## Development

### Adding New Themes
1. Add theme definition to `MATRIX_THEMES`
2. Include body_color, head_color, background, particle_color, and glow_color
3. Update the live configuration screen

### Adding New Effects
1. Create effect logic in the Drop.draw() method
2. Add configuration options to DEFAULT_CONFIG
3. Update configuration screens and apply functions

## License

This project is open source. Feel free to modify and distribute.

## Credits

Inspired by the iconic Matrix digital rain effect from the 1999 film "The Matrix". 