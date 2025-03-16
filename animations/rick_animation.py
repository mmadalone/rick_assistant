#!/usr/bin/env python3
import sys
import random
import argparse
from typing import List, Tuple

# The original Rick ASCII art as a template
RICK_TEMPLATE = [
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢰⠀⢀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⢲⠶⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠈⣍⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠈⡄⠈⠑⠢⢄⡀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⣀⣤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠠⢵⠀⠀⠀⠀⠈⠓⠤⣤⠄⡼⠀⠀⠀⠀⠀⠘⣿⣿⣿⠤⠄⠀⣠⠴⠊⢡⣿⠀⠠⠤⣤⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠈⠲⠃⠀⠀⠀⠀⠀⠀⢻⣿⡿⠗⠒⠉⠀⠀⠀⣾⣏⣠⣴⣾⡏⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠂⠤⠄⣈⠁⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⡤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⢄⠀⠀⠀⠀⣼⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀",
    "⠔⡀⠉⠉⠉⠉⠈⠉⠉⠉⠀⢀⠎⠀⠀⠀⠀⣀⠤⢒⡠⠖⠂⠀⣀⣀⣀⠱⡀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠈⠑⣤⡀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠠⠄⠋⠒⢈⡠⠄⠒⣈⠡⠤⠐⠚⠁⠙⡄⠀⠙⠛⠛⠻⢿⡶⠓⢶⣦⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠙⢢⡀⠀⠀⠀⠀⢰⢁⡤⠐⠒⠒⢊⣉⡠⠔⠚⠉⡀⠀⠀⠀⠈⠒⢄⠰⡀⠀⠀⠀⣠⠞⢀⣴⣯⣅⣀⣀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠓⠤⡀⠀⠀⢸⠈⢉⠁⠉⠉⠀⠉⠢⡀⠀⡘⠀⢀⣀⣠⡤⠀⠘⢇⢣⠀⠀⣴⣭⣶⣿⣿⣿⣿⣿⡿⠟⠁",
    "⠀⠀⠀⠀⠀⠀⠀⣀⠼⠃⠀⢸⣠⠃⠀⠀⠀⣀⡠⠤⠼⡀⢻⠉⠁⠀⠉⠀⠀⠀⡼⠸⡀⠀⠈⠻⢿⣿⣿⣿⠟⠉⠀⠀⠀",
    "⠀⠀⢠⣠⠤⠒⠊⠁⠀⠀⠀⠈⡏⡦⠒⠈⠙⠃⠀⠀⢠⠇⠈⠢⣀⠀⠀⠀⣀⠔⠁⠀⣇⠀⠀⠀⢀⡽⠛⣿⣦⣀⡀⠀⠀",
    "⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⢇⠘⢆⡀⠀⠀⢀⡠⠊⡄⠀⢰⠀⠉⠉⠉⣠⣴⠏⠀⣻⠒⢄⢰⣏⣤⣾⣿⣿⣿⣦⣄⠀",
    "⠀⠀⠀⠀⠀⠀⠙⢻⣷⣦⡀⠀⢸⡀⠀⡈⠉⠉⢁⡠⠂⢸⠀⠀⡇⠙⠛⠛⠋⠁⠀⠀⣿⡇⢀⡟⣿⣿⣿⣿⣿⣿⠟⠋⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⡴⠇⠀⠈⠉⠉⠀⠀⠀⠀⢣⣠⠇⠀⠀⠀⠀⠀⠀⠀⣿⣿⡟⠀⢻⠻⣿⡟⠉⠉⠉⠁⠀",
    "⠀⠀⠀⠀⠀⠀⢀⡠⠖⠁⠀⢸⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠐⢶⣿⢷⣯⣭⣤⣶⣿⣿⣦⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠒⠛⠒⠒⠤⠤⢲⠑⠦⢧⠀⠀⠀⠀⢀⡤⢖⠂⠉⠉⡸⠁⠀⠀⠀⢀⣾⣾⠈⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠾⣿⠀⠀⠈⢆⠸⣄⠊⠁⠀⠀⡉⢆⠀⡆⣀⠀⠀⠀⣰⢿⣷⣶⣾⣿⣿⣏⠉⠉⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠠⠴⢞⣿⢦⠀⠀⠀⠀⠀⠛⠀⠉⠁⠛⠃⢀⣴⣿⣾⣿⣿⣿⣿⡿⠿⠆⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶⡷⢄⡀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⣿⠷⡖⠢⠤⠔⠒⠻⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢉⡩⢽⢻⠗⠤⢀⣀⣀⡠⢿⣿⣿⠿⣏⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠊⠁⢠⠊⣸⠀⠀⠀⠀⠀⠀⠀⢻⠈⢖⠂⢉⠒⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
]

def parse_braille_patterns(template: List[str]) -> List[List[str]]:
    """Parse the template into a 2D array of Braille characters."""
    return [list(line) for line in template]

def apply_procedural_variation(pattern: List[List[str]], variation: float = 0.1) -> List[List[str]]:
    """Apply procedural variation to the pattern.
    
    Args:
        pattern: The original pattern as a 2D array
        variation: Amount of variation to apply (0.0 to 1.0)
        
    Returns:
        Modified pattern with variations
    """
    # List of Braille patterns ordered by density
    braille_chars = "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿"
    
    # Create a mapping from character to density level
    char_to_idx = {char: idx for idx, char in enumerate(braille_chars)}
    
    modified = []
    for row in pattern:
        new_row = []
        for char in row:
            # Skip empty space or non-Braille characters
            if char not in char_to_idx:
                new_row.append(char)
                continue
                
            # Get the current density level
            idx = char_to_idx[char]
            
            # Apply random variation based on the variation parameter
            if random.random() < variation:
                # Calculate new index with variation
                variation_range = int(len(braille_chars) * variation)
                new_idx = max(0, min(len(braille_chars)-1, 
                                    idx + random.randint(-variation_range, variation_range)))
                new_row.append(braille_chars[new_idx])
            else:
                new_row.append(char)
                
        modified.append(new_row)
    
    return modified

def scale_pattern(pattern: List[List[str]], scale_x: float, scale_y: float) -> List[List[str]]:
    """Scale the pattern by the given factors.
    
    Args:
        pattern: The original pattern as a 2D array
        scale_x: Horizontal scaling factor
        scale_y: Vertical scaling factor
        
    Returns:
        Scaled pattern
    """
    height = len(pattern)
    width = len(pattern[0]) if height > 0 else 0
    
    new_height = int(height * scale_y)
    new_width = int(width * scale_x)
    
    # Initialize with spaces
    scaled = [[' ' for _ in range(new_width)] for _ in range(new_height)]
    
    # Map each position in the new grid to the closest position in the original
    for y in range(new_height):
        src_y = min(height - 1, int(y / scale_y))
        for x in range(new_width):
            src_x = min(width - 1, int(x / scale_x))
            scaled[y][x] = pattern[src_y][src_x]
    
    return scaled

def pattern_to_string(pattern: List[List[str]]) -> str:
    """Convert a 2D pattern array back to a string."""
    return '\n'.join([''.join(row) for row in pattern])

def generate_rick_ascii(variation: float = 0.1, scale_x: float = 1.0, scale_y: float = 1.0) -> str:
    """Generate Rick Sanchez ASCII art with procedural variations.
    
    Args:
        variation: Amount of variation to apply (0.0 to 1.0)
        scale_x: Horizontal scaling factor
        scale_y: Vertical scaling factor
        
    Returns:
        Rick ASCII art as a string
    """
    # Parse the template
    pattern = parse_braille_patterns(RICK_TEMPLATE)
    
    # Apply scaling if needed
    if scale_x != 1.0 or scale_y != 1.0:
        pattern = scale_pattern(pattern, scale_x, scale_y)
    
    # Apply variation if needed
    if variation > 0:
        pattern = apply_procedural_variation(pattern, variation)
    
    # Convert back to string
    return pattern_to_string(pattern)

def main():
    parser = argparse.ArgumentParser(description="Generate Rick Sanchez ASCII art procedurally")
    parser.add_argument("--variation", type=float, default=0.1, 
                        help="Amount of variation to apply (0.0 to 1.0)")
    parser.add_argument("--scale-x", type=float, default=1.0,
                        help="Horizontal scaling factor")
    parser.add_argument("--scale-y", type=float, default=1.0,
                        help="Vertical scaling factor")
    
    args = parser.parse_args()
    
    ascii_art = generate_rick_ascii(args.variation, args.scale_x, args.scale_y)
    print(ascii_art)

if __name__ == "__main__":
    main()