#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Menu System Module for Rick Assistant.

This module provides a rich menu system with Rick-themed styling.
It supports various menu types and seamless navigation with typing animations.

Example usage:
    from src.ui.menu import Menu, MenuItem, display_menu, get_selection
    
    # Create and display a simple menu
    menu = Menu("Rick Assistant", [
        MenuItem("Run diagnostics", callback=run_diagnostics),
        MenuItem("Configure settings", callback=open_settings),
        MenuItem("Exit", callback=exit_program)
    ])
    
    # Display the menu and get selection
    selected = display_menu(menu)
"""

import os
import sys
import time
import random
import shutil
import locale
from typing import List, Dict, Any, Optional, Union, Tuple, Callable, TypeVar
import select

# Set up proper encoding for terminal output to fix character display issues
def setup_terminal_encoding():
    """
    Configure terminal to properly display Unicode characters.
    This addresses the issue where menu icons appear as '' until selected.
    """
    # Set Python's encoding for terminal I/O
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Configure locale to properly display Unicode characters
    try:
        # Use the user's preferred locale with UTF-8 encoding
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        try:
            # Try multiple common UTF-8 locales
            utf8_locales = ['en_US.UTF-8', 'C.UTF-8', 'en_GB.UTF-8', 'en.UTF-8', 'UTF-8']
            for loc in utf8_locales:
                try:
                    locale.setlocale(locale.LC_ALL, loc)
                    break
                except locale.Error:
                    continue
        except Exception as e:
            print(f"Warning: Could not set UTF-8 locale: {e}")
    
    # On Windows, try to set console output mode to support Unicode
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Set UTF-8 codepage (65001)
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception as e:
            print(f"Warning: Could not set Windows console to UTF-8 mode: {e}")
    
    # Force stdout encoding to UTF-8 if possible
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        except Exception as e:
            print(f"Warning: Could not reconfigure stdout: {e}")
    
    # For WSL environments, which may have additional encoding quirks
    if 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False:
        try:
            # WSL-specific settings might be needed here
            pass 
        except Exception:
            pass

# Run encoding setup immediately
setup_terminal_encoding()

# Import utility functions
try:
    from src.utils.logger import get_logger
    from src.utils.errors import safe_execute, RickAssistantError
    from src.utils.config import get_config_value
    from src.ui.text import (
        color_text, format_text, stream_text, 
        format_error, format_warning, format_success, format_info,
        get_terminal_width, get_terminal_height, supports_ansi_color, supports_unicode,
        clear_screen
    )
    from src.ui.input import get_single_key, get_input, get_selection as get_input_selection
except ImportError as e:
    # Fallback for when importing as standalone
    print(f"Warning: Could not import all Rick Assistant modules: {e}")
    # Define minimal versions of required functions
    def get_logger(name): 
        import logging
        return logging.getLogger(name)
    def safe_execute(default_return=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}")
                    return default_return
            return wrapper
        return decorator
    def get_config_value(key, default=None): return default
    def color_text(text, color): return text
    def format_text(text, width=80): return text
    def stream_text(text, speed=0.03): print(text)
    def format_error(message): return f"Error: {message}"
    def format_warning(message): return f"Warning: {message}"
    def format_success(message): return f"Success: {message}"
    def format_info(message): return f"Info: {message}"
    def get_terminal_width(): return 80
    def get_terminal_height(): return 24
    def supports_ansi_color(): return False
    def supports_unicode(): return False
    def clear_screen(): print("\n" * 5)
    def get_single_key(prompt=None): 
        if prompt: print(prompt)
        return input()[0] if input() else ""
    def get_input(prompt=None): 
        return input(prompt if prompt else "")
    def get_input_selection(options, prompt=None):
        if prompt: print(prompt)
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        try:
            return int(input("Select: ")) - 1
        except:
            return 0

# Set up logger
logger = get_logger("menu")

# Detect terminal compatibility issues
def detect_terminal_compatibility_issues():
    """
    Detect known terminal compatibility issues and set appropriate 
    fallback options for problematic environments.
    """
    # Get terminal environment details
    terminal = os.environ.get('TERM', '').lower()
    
    # Check for WSL (Windows Subsystem for Linux)
    in_wsl = False
    if sys.platform == 'linux':
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    in_wsl = True
        except Exception:
            pass
    
    # List of terminals with known Unicode/emoji issues
    problem_terminals = ['dumb', 'vt100', 'xterm-mono', 'linux']
    
    # Determine if we're in a problematic environment
    has_terminal_issues = (
        terminal in problem_terminals or
        in_wsl or
        (sys.platform == 'win32' and not terminal.startswith('xterm'))
    )
    
    logger.debug(f"Terminal compatibility check: Terminal={terminal}, WSL={in_wsl}, "
                 f"Platform={sys.platform}, Has Issues={has_terminal_issues}")
    
    return has_terminal_issues

# Color constants for Rick & Morty portal theme
PORTAL_GREEN = "\033[38;5;120m"
PORTAL_BLUE = "\033[38;5;39m"
PORTAL_CYAN = "\033[38;5;51m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Check for Unicode support only once at import time
_UNICODE_SUPPORTED = supports_unicode()

# Set to true if we detect terminal compatibility issues
TERMINAL_COMPATIBILITY_MODE = get_config_value("menu.terminal_compatibility_mode", 
                                              detect_terminal_compatibility_issues())

# Define both Unicode and ASCII symbol sets
UNICODE_SYMBOLS = {
    "arrow": "→",
    "checkbox_on": "✓",
    "checkbox_off": "☐",
    "radio_on": "●",
    "radio_off": "○",
    "folder": "📁",
    "folder_open": "📂",
    "action": "🔬",
    "toggle_on": "🟢",
    "toggle_off": "⚪",
    "back": "🔙",
    "portal": "🌀",
    "diamond": "◆",
    "status": "📊",
    "debug": "🐞",
    "version": "ℹ️",
    "help": "❓",
    "settings": "⚙️",
    "tools": "🔧",
}

ASCII_SYMBOLS = {
    "arrow": "->",
    "checkbox_on": "[X]",
    "checkbox_off": "[ ]",
    "radio_on": "(•)",
    "radio_off": "( )",
    "folder": "[+]",
    "folder_open": "[=]",
    "action": "[>]",
    "toggle_on": "[ON]",
    "toggle_off": "[OFF]",
    "back": "<-",
    "portal": "(*)",
    "diamond": "<>",
    "status": "[S]",
    "debug": "[D]",
    "version": "[V]",
    "help": "[?]",
    "settings": "[#]",
    "tools": "[T]",
}

# Pre-render all menu icons to ensure they're properly loaded
def initialize_menu_icons():
    """
    Pre-render all menu icons to ensure they're properly loaded and
    fall back to ASCII if encoding fails or if in compatibility mode.
    """
    global MENU_SYMBOLS
    
    # Start with Unicode symbols if supported
    if _UNICODE_SUPPORTED and not TERMINAL_COMPATIBILITY_MODE:
        base_symbols = UNICODE_SYMBOLS
    else:
        # Use ASCII symbols if Unicode not supported or in compatibility mode
        base_symbols = ASCII_SYMBOLS
    
    # Create a new dictionary for the symbols
    validated_symbols = {}
    
    # Validate each symbol and fall back to ASCII if needed
    for key, icon in base_symbols.items():
        try:
            # Try to encode/decode the icon to check if it renders properly
            encoded = icon.encode(sys.stdout.encoding or 'utf-8', errors='replace')
            decoded = encoded.decode(sys.stdout.encoding or 'utf-8')
            
            # If the decoded char doesn't match or contains replacement char, use ASCII fallback
            if decoded != icon or '' in decoded:
                validated_symbols[key] = ASCII_SYMBOLS.get(key, "*")
            else:
                validated_symbols[key] = icon
        except Exception:
            # On any error, use the ASCII fallback
            validated_symbols[key] = ASCII_SYMBOLS.get(key, "*")
    
    # Update the global MENU_SYMBOLS with our validated set
    MENU_SYMBOLS = validated_symbols
    
    logger.debug(f"Menu icons initialized with {'Unicode' if _UNICODE_SUPPORTED and not TERMINAL_COMPATIBILITY_MODE else 'ASCII'} base")
    logger.debug(f"TERMINAL_COMPATIBILITY_MODE: {TERMINAL_COMPATIBILITY_MODE}")

# Use appropriate symbol set based on terminal capability and initialize 
initialize_menu_icons()

# Animation speed configuration
# Reduce default durations for more responsive menu
DEFAULT_TYPING_SPEED = 0.015   # Seconds per character (was 0.03)

# Animation speed can be controlled by a multiplier from config
ANIMATION_SPEED_MULTIPLIER = get_config_value('animation_speed_multiplier', 1.0)

# Apply the multiplier to the typing speed
TYPING_SPEED = DEFAULT_TYPING_SPEED * ANIMATION_SPEED_MULTIPLIER

# Menu display configuration
USE_STATIC_PORTAL = True  # Always use static portal

# Static portal ASCII art
STATIC_PORTAL_ART_OPEN = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢰⠀⢀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢲⠶⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠈⣍⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⡄⠈⠑⠢⢄⡀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⣀⣤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⢵⠀⠀⠀⠀⠈⠓⠤⣤⠄⡼⠀⠀⠀⠀⠀⠘⣿⣿⣿⠤⠄⠀⣠⠴⠊⢡⣿⠀⠠⠤⣤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠈⠲⠃⠀⠀⠀⠀⠀⠀⢻⣿⡿⠗⠒⠉⠀⠀⠀⣾⣏⣠⣴⣾⡏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠂⠤⠄⣈⠁⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⡤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⢄⠀⠀⠀⠀⣼⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀
⠔⡀⠉⠉⠉⠉⠈⠉⠉⠉⠀⢀⠎⠀⠀⠀⠀⣀⠤⢒⡠⠖⠂⠀⣀⣀⣀⠱⡀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠑⣤⡀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠠⠄⠋⠒⢈⡠⠄⠒⣈⠡⠤⠐⠚⠁⠙⡄⠀⠙⠛⠛⠻⢿⡶⠓⢶⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠙⢢⡀⠀⠀⠀⠀⢰⢁⡤⠐⠒⠒⢊⣉⡠⠔⠚⠉⡀⠀⠀⠀⠈⠒⢄⠰⡀⠀⠀⠀⣠⠞⢀⣴⣯⣅⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠓⠤⡀⠀⠀⢸⠈⢉⠁⠉⠉⠀⠉⠢⡀⠀⡘⠀⢀⣀⣠⡤⠀⠘⢇⢣⠀⠀⣴⣭⣶⣿⣿⣿⣿⣿⡿⠟⠁
⠀⠀⠀⠀⠀⠀⠀⣀⠼⠃⠀⢸⣠⠃⠀⠀⠀⣀⡠⠤⠼⡀⢻⠉⠁⠀⠉⠀⠀⠀⡼⠸⡀⠀⠈⠻⢿⣿⣿⣿⠟⠉⠀⠀⠀
⠀⠀⢠⣠⠤⠒⠊⠁⠀⠀⠀⠈⡏⡦⠒⠈⠙⠃⠀⠀⢠⠇⠈⠢⣀⠀⠀⠀⣀⠔⠁⠀⣇⠀⠀⠀⢀⡽⠛⣿⣦⣀⡀⠀⠀
⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⢇⠘⢆⡀⠀⠀⢀⡠⠊⡄⠀⢰⠀⠉⠉⠉⣠⣴⠏⠀⣻⠒⢄⢰⣏⣤⣾⣿⣿⣿⣦⣄⠀
⠀⠀⠀⠀⠀⠀⠙⢻⣷⣦⡀⠀⢸⡀⠀⡈⠉⠉⢁⡠⠂⢸⠀⠀⡇⠙⠛⠛⠋⠁⠀⠀⣿⡇⢀⡟⣿⣿⣿⣿⣿⣿⠟⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⡴⠇⠀⠈⠉⠉⠀⠀⠀⠀⢣⣠⠇⠀⠀⠀⠀⠀⠀⠀⣿⣿⡟⠀⢻⠻⣿⡟⠉⠉⠉⠁⠀
⠀⠀⠀⠀⠀⠀⢀⡠⠖⠁⠀⢸⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠐⢶⣿⢷⣯⣭⣤⣶⣿⣿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠒⠛⠒⠒⠤⠤⢲⠑⠦⢧⠀⠀⠀⠀⢀⡤⢖⠂⠉⠉⡸⠁⠀⠀⠀⢀⣾⣾⠈⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠾⣿⠀⠀⠈⢆⠸⣄⠊⠁⠀⠀⡉⢆⠀⡆⣀⠀⠀⠀⣰⢿⣷⣶⣾⣿⣿⣏⠉⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠠⠴⢞⣿⢦⠀⠀⠀⠀⠀⠛⠀⠉⠁⠛⠃⢀⣴⣿⣾⣿⣿⣿⣿⡿⠿⠆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶⡷⢄⡀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⣿⠷⡖⠢⠤⠔⠒⠻⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢉⡩⢽⢻⠗⠤⢀⣀⣀⡠⢿⣿⣿⠿⣏⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠊⠁⢠⠊⣸⠀⠀⠀⠀⠀⠀⠀⢻⠈⢖⠂⢉⠒⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀
"""

STATIC_PORTAL_ART = """
    art
"""

# Flag to track if we're returning from a command execution
RETURNING_FROM_COMMAND = False


# Static portal ASCII art for the CLOSED state (portal when closed)
STATIC_PORTAL_ART_CLOSED = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⢿⣿⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠈⠀⢘⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣧⣀⠀⠀⠀⠀⠀⠐⠽⣿⣿⣿⣏⠀⢈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⡇⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠐⠀⠀⠀⢀⡐⣿⣿⣿⣿⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣠⠀⠀⠀⣸⣿⣿⣿⣿⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠉⢛⠋⠉⣁⣀⣠⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⢀⣤⡆⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠉⠉⠀⠉⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡿⠋⠀⣠⣶⣿⣿⣇⠀⠂⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡿⠁⢠⣾⣿⣿⣿⣿⣿⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⡀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⠃⢀⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡄⠐⠀⠀⢠⣤⣤⣾⣿⣿⡿⠿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⡏⠀⣼⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠉⠁⠀⠀⠀⢠⠀⠈⠱⢿⡿⠟⠋⣠⣤⣾⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⡟⠁⠐⣆⠙⠛⠛⠛⠉⠀⠀⠐⡤⠤⠄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣤⣶⠖⠈⠀⠀⠀⣼⣷⣦⣷⣤⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣦⣴⣿⣷⣤⣀⣀⣠⣴⣷⣾⣆⠀⠀⠈⠉⠉⠛⠛⠻⠿⢿⣿⣿⣿⣿⣿⠟⠃⣴⣿⣿⠏⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⢠⣿⣷⣶⣶⣦⣤⠀⠀⣾⣿⣿⣿⣿⣦⣼⣿⣿⠏⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⣾⣿⣿⣿⣿⡿⠃⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⣸⣿⣿⣿⣿⡟⠁⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⣰⣿⣿⣿⣿⠟⢀⣾⣿⣿⡿⢃⣈⡛⠛⠿⣿⡿⠋⠀⣠⣶⣤⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⢀⣴⣿⣿⣿⣿⣧⡀⠈⢿⣿⣿⣿⣿⣿⣿⣶⣤⣀⢀⣴⣾⣿⣿⣿⣿⣷⣄⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠅⣀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣟⠁⠐⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣬⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
"""

# Original braille art portal (just for backwards compatibility)
STATIC_PORTAL_ART = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
"""

# Rick's menu commentary phrases
RICK_MENU_COMMENTS = [
    "What are you looking at? Just pick something!",
    "Oh great, *burp* another menu. How exciting...",
    "Don't just stare at it, make a choice already!",
    "Some of us don't live forever, you know. Pick an option.",
    "These options won't select themselves, genius.",
    "You know what would be great? If you made a selection sometime this century.",
    "Look at you, paralyzed by simple choices. Reminds me of Jerry.",
    "This isn't rocket science... though I could turn it into that if you want.",
    "I've created portals to infinite dimensions faster than you're picking an option.",
    "Your indecisiveness is physically painful to watch, you know that?"
]

# Base classes for menu components
class MenuItem:
    """Individual selectable menu item"""
    
    def __init__(self, text: str, value: Any = None, enabled: bool = True, 
                 callback: Callable = None, icon: str = None):
        """
        Initialize a menu item.
        
        Args:
            text: Display text for the item
            value: Value associated with this item (optional)
            enabled: Whether this item can be selected
            callback: Function to call when this item is selected
            icon: Custom icon to display (will use default if None)
        """
        self.text = text
        self.value = value if value is not None else text
        self.enabled = enabled
        self.callback = callback
        
        # Auto-determine icon based on value if it's a rick command
        if icon is None:
            self.icon = self._determine_icon()
        else:
            # Validate the icon to ensure it's displayable
            self.icon = self._validate_icon(icon)
            
        self.parent = None  # Will be set when added to a menu/category
    
    def _validate_icon(self, icon: str) -> str:
        """
        Validate that an icon is displayable and fall back if needed.
        
        Args:
            icon: The icon to validate
            
        Returns:
            str: The validated icon or a fallback
        """
        if not icon:
            return MENU_SYMBOLS.get("action")
            
        try:
            # Try to encode/decode the icon to check if it renders properly
            encoded = icon.encode(sys.stdout.encoding or 'utf-8', errors='replace')
            decoded = encoded.decode(sys.stdout.encoding or 'utf-8')
            
            # If the decoded char doesn't match or contains replacement char, use ASCII fallback
            if decoded != icon or '' in decoded:
                return MENU_SYMBOLS.get("action")
            return icon
        except Exception:
            # On any error, use the fallback
            return MENU_SYMBOLS.get("action")
    
    def _determine_icon(self) -> str:
        """
        Determine the appropriate icon for this menu item based on its value.
        
        Returns:
            str: Icon appropriate for this menu item
        """
        # If it's a string value, check if it's a rick command
        if isinstance(self.value, str):
            cmd_value = self.value.lower()
            
            # For rick commands, match specific commands
            if cmd_value.startswith("rick "):
                cmd_parts = cmd_value.split()
                if len(cmd_parts) > 1:
                    subcmd = cmd_parts[1]
                    
                    # Map specific commands to their icons
                    if subcmd == "status":
                        return MENU_SYMBOLS.get("status")
                    elif subcmd == "debug":
                        return MENU_SYMBOLS.get("debug")
                    elif subcmd == "version":
                        return MENU_SYMBOLS.get("version")
                    elif subcmd == "help":
                        return MENU_SYMBOLS.get("help")
                    elif subcmd in ["prompt", "p10k"]:
                        return MENU_SYMBOLS.get("settings")
                    elif subcmd in ["cleanup", "diagnose"]:
                        return MENU_SYMBOLS.get("tools")
            
            # Check for text-based matching
            lower_text = self.text.lower()
            if "status" in lower_text:
                return MENU_SYMBOLS.get("status")
            elif "debug" in lower_text:
                return MENU_SYMBOLS.get("debug")
            elif "version" in lower_text or "info" in lower_text:
                return MENU_SYMBOLS.get("version")
            elif "help" in lower_text:
                return MENU_SYMBOLS.get("help")
            elif "settings" in lower_text or "config" in lower_text:
                return MENU_SYMBOLS.get("settings")
            elif "tool" in lower_text or "utility" in lower_text:
                return MENU_SYMBOLS.get("tools")
        
        # Default action icon
        return MENU_SYMBOLS.get("action")
    
    def execute(self):
        """Execute the callback function if it exists"""
        if self.callback and callable(self.callback):
            return self.callback(self.value)
        return self.value
    
    def render(self, width: int, selected: bool = False) -> str:
        """
        Render the menu item with consistent icon display.
        
        Args:
            width: Available width for rendering
            selected: Whether this item is currently selected
            
        Returns:
            str: Formatted string representation of the item
        """
        # Ensure icon is defined and valid
        if not hasattr(self, 'icon') or self.icon is None:
            self.icon = MENU_SYMBOLS.get("action", "*")
        
        # Format the text with icon - ensure space between icon and text
        item_text = f"{self.icon} {self.text}"
        
        # If disabled, gray it out
        if not self.enabled:
            formatted = color_text(item_text, "gray")
        # If selected, highlight it
        elif selected:
            formatted = color_text(f"{BOLD}{item_text}{RESET}", "cyan")
        # Otherwise, normal formatting
        else:
            formatted = item_text
        
        # Ensure the item fits within the width
        if width and len(item_text) > width:
            # Truncate and add ellipsis
            formatted = formatted[:width-3] + "..."
            
        return formatted

class MenuCategory(MenuItem):
    """Grouping of related menu items"""
    
    def __init__(self, text: str, items: List[MenuItem] = None, expanded: bool = False):
        """
        Initialize a menu category.
        
        Args:
            text: Display text for the category
            items: List of menu items in this category
            expanded: Whether this category is expanded by default
        """
        # Use folder icon for categories (will update based on expanded state)
        super().__init__(text=text, value=text, icon=MENU_SYMBOLS["folder"])
        self.items = items or []
        self._expanded = expanded
        
        # Set parent reference for all items
        for item in self.items:
            item.parent = self
    
    @property
    def expanded(self) -> bool:
        """Get the expanded state"""
        return self._expanded
    
    @expanded.setter
    def expanded(self, value: bool):
        """Set the expanded state and update icon accordingly"""
        self._expanded = value
        # Update the icon based on expanded state
        self.icon = MENU_SYMBOLS["folder_open"] if value else MENU_SYMBOLS["folder"]
    
    def add_item(self, item: MenuItem):
        """Add an item to this category"""
        self.items.append(item)
        item.parent = self
    
    def render(self, width: int, selected: bool = False) -> str:
        """
        Render the menu category with an indicator if it has items.
        
        Args:
            width: Available width for rendering
            selected: Whether this item is currently selected
            
        Returns:
            str: Formatted string representation of the category
        """
        # Update icon based on expanded state
        self.icon = MENU_SYMBOLS["folder_open"] if self._expanded else MENU_SYMBOLS["folder"]
        
        # Create the category text with the appropriate icon
        text = super().render(width, selected)
        
        # Add a submenu indicator if there are items
        if self.items:
            # Use an arrow symbol if it's selected or expanded
            if selected or self._expanded:
                indicator = MENU_SYMBOLS["arrow"] + " "
            else:
                indicator = "  "
            
            # Add the indicator to show it has items
            return text + indicator
        
        return text

class MenuAction(MenuItem):
    """Item that triggers a function"""
    
    def __init__(self, text: str, callback: Callable, value: Any = None, enabled: bool = True):
        """
        Initialize a menu action item.
        
        Args:
            text: Display text for the action
            callback: Function to call when this action is selected
            value: Value to pass to the callback (optional)
            enabled: Whether this action can be selected
        """
        super().__init__(text=text, value=value, enabled=enabled, 
                         callback=callback, icon=MENU_SYMBOLS["action"])
        
class MenuToggle(MenuItem):
    """Menu item that can be toggled on/off"""
    
    def __init__(self, text: str, key: str = None, default: bool = False, 
                 callback: Callable = None, enabled: bool = True):
        """
        Create a toggle menu item.
        
        Args:
            text: Display text
            key: Configuration key to update when toggled
            default: Initial toggle state
            callback: Function to call when toggled
            enabled: Whether this toggle can be selected
        """
        self.state = default
        self.key = key
        super().__init__(text=text, value=self.state, enabled=enabled, 
                         callback=callback, icon=self._get_icon())
    
    def _get_icon(self) -> str:
        """Get the appropriate icon based on state"""
        return MENU_SYMBOLS["toggle_on"] if self.state else MENU_SYMBOLS["toggle_off"]
    
    def update_config(self, key: str, value: bool):
        """Update configuration with the toggle value"""
        try:
            # Import here to avoid circular imports
            from src.utils.config import set_config_value
            logger.debug(f"Updating config: {key} = {value}")
            set_config_value(key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to update config {key}: {e}")
            return False
    
    def toggle(self):
        """Toggle the state"""
        self.state = not self.state
        self.value = self.state
        self.icon = self._get_icon()
        
        # Update configuration if key is provided
        if self.key:
            self.update_config(self.key, self.state)
            
        # Execute callback if provided
        if self.callback and callable(self.callback):
            return self.callback(self.state)
            
        return self.state
    
    def render(self, width: int, selected: bool = False) -> str:
        """
        Render the toggle item.
        
        Args:
            width: Available width for rendering
            selected: Whether this item is currently selected
            
        Returns:
            str: Formatted string representation of the toggle
        """
        # Update icon based on current state
        self.icon = self._get_icon()
        
        # Format the text with state-dependent icon
        item_text = f"{self.icon} {self.text}"
        
        # If disabled, gray it out
        if not self.enabled:
            formatted = color_text(item_text, "gray")
        # If selected, highlight it
        elif selected:
            formatted = color_text(f"{BOLD}{item_text}{RESET}", "cyan")
        # Otherwise, normal formatting
        else:
            formatted = item_text
            
        return formatted

class Menu:
    """Base class for all menus"""
    
    def __init__(self, title: str, items: List[MenuItem] = None, width: int = None, 
                 height: int = None, parent: 'Menu' = None):
        """
        Initialize a menu.
        
        Args:
            title: Menu title
            items: List of menu items
            width: Custom width (uses terminal width if None)
            height: Custom height (uses terminal height if None)
            parent: Parent menu if this is a submenu
        """
        self.title = title
        self.items = items or []
        self.width = width or get_terminal_width()
        self.height = height or get_terminal_height()
        self.parent = parent
        self.selected_index = 0
        self.scroll_offset = 0
        self.exit_requested = False
        
        # Set parent reference for all items
        for item in self.items:
            item.parent = self
    
    def add_item(self, item: MenuItem) -> MenuItem:
        """
        Add an item to the menu.
        
        Args:
            item: MenuItem to add
            
        Returns:
            MenuItem: The added item (for chaining)
        """
        item.parent = self
        self.items.append(item)
        return item
    
    def add_category(self, text: str, items: List[MenuItem] = None) -> MenuCategory:
        """
        Add a category to the menu.
        
        Args:
            text: Category display text
            items: List of items in the category
            
        Returns:
            MenuCategory: The added category (for chaining)
        """
        category = MenuCategory(text=text, items=items or [])
        self.add_item(category)
        return category
    
    def add_action(self, text: str, callback: Callable, value: Any = None) -> MenuAction:
        """
        Add an action item to the menu.
        
        Args:
            text: Action display text
            callback: Function to call when selected
            value: Value to pass to callback
            
        Returns:
            MenuAction: The added action (for chaining)
        """
        action = MenuAction(text=text, callback=callback, value=value)
        self.add_item(action)
        return action
    
    def add_toggle(self, text: str, key: str = None, default: bool = False) -> MenuToggle:
        """
        Add a toggle item to the menu.
        
        Args:
            text: Toggle display text
            key: Configuration key
            default: Default state
            
        Returns:
            MenuToggle: The added toggle (for chaining)
        """
        toggle = MenuToggle(text=text, key=key, default=default)
        self.add_item(toggle)
        return toggle
    
    def get_visible_items(self) -> List[MenuItem]:
        """
        Get all visible items, including those in expanded categories.
        
        Returns:
            List[MenuItem]: All visible menu items
        """
        visible_items = []
        
        for item in self.items:
            visible_items.append(item)
            
            # If this is an expanded category, add its items
            if isinstance(item, MenuCategory) and item.expanded:
                for sub_item in item.items:
                    visible_items.append(sub_item)
                    
        return visible_items
    
    def get_item_at_index(self, index: int) -> Optional[MenuItem]:
        """
        Get the item at the specified index from visible items.
        
        Args:
            index: Index to get
            
        Returns:
            Optional[MenuItem]: The item at that index or None if invalid
        """
        visible_items = self.get_visible_items()
        
        if 0 <= index < len(visible_items):
            return visible_items[index]
            
        return None
    
    def get_current_item(self) -> Optional[MenuItem]:
        """
        Get the currently selected item.
        
        Returns:
            Optional[MenuItem]: Currently selected item or None
        """
        return self.get_item_at_index(self.selected_index)
    
    def select_next(self):
        """Select the next item in the menu"""
        visible_items = self.get_visible_items()
        
        if visible_items:
            self.selected_index = (self.selected_index + 1) % len(visible_items)
    
    def select_previous(self):
        """Select the previous item in the menu"""
        visible_items = self.get_visible_items()
        
        if visible_items:
            self.selected_index = (self.selected_index - 1) % len(visible_items)
    
    def activate_selected(self):
        """Activate the currently selected item"""
        item = self.get_current_item()
        
        if not item or not item.enabled:
            return None
            
        # Handle different item types
        if isinstance(item, MenuCategory):
            # Toggle category expansion
            item.expanded = not item.expanded
            return None
        elif isinstance(item, MenuToggle):
            # Toggle the item
            return item.toggle()
        else:
            # Execute the item
            return item.execute()
    
    def exit(self):
        """Exit the menu"""
        self.exit_requested = True

# =====================================================================
# Animation Functions
# =====================================================================

# Portal animation ASCII art for different sizes
PORTAL_SMALL = [
    # Frame 1
    """
    1
    """,
    # Frame 2
    """
    2
    """,
    # Frame 3
    """
    3
    """
]

PORTAL_MEDIUM = [
    # Frame 1
    """
    1
    """,
    # Frame 2
    """
    2
    """,
    # Frame 3
    """
    3
    """
]

PORTAL_LARGE = [
    # Frame 1
    """
    1
    """,
    # Frame 2
    """
    2
    """,
    # Frame 3
    """
    3
    """
]

@safe_execute()
def colorize_portal(frame: str) -> str:
    """
    Colorize a portal frame with the Rick & Morty color scheme.
    
    Args:
        frame: ASCII art frame to colorize
        
    Returns:
        str: Colorized frame
    """
    result = ""
    for i, char in enumerate(frame):
        if char in "*/\\":
            result += PORTAL_GREEN + char + RESET
        elif char in "~.'-":
            result += PORTAL_BLUE + char + RESET
        elif char in "|":
            result += PORTAL_CYAN + char + RESET
        else:
            result += char
            
    return result

@safe_execute()
def colorize_portal_frame(frame: str) -> str:
    """
    Wrapper function for colorize_portal to fix naming issue.
    
    Args:
        frame: ASCII art frame to colorize
        
    Returns:
        str: Colorized frame
    """
    return colorize_portal(frame)

@safe_execute()
def animate_portal_open(width: int = None, height: int = None, frames: int = None, 
                        frame_duration: float = None) -> None:
    """
    Show portal opening animation, properly centered in the terminal.
    
    Args:
        width: Terminal width (auto-detected if None)
        height: Terminal height (auto-detected if None)
    """
    logger.debug("Showing portal open animation")
    
    # If returning from a command execution, skip animation
    global RETURNING_FROM_COMMAND
    if RETURNING_FROM_COMMAND:
        logger.debug("Skipping animation as returning from command")
        display_static_portal_open()
        RETURNING_FROM_COMMAND = False
        return
    
    # Determine if animations should be shown or if we should use static portal
    try:
        # Default to static portal and no animations for safety
        use_static = True
        animations_enabled = False
        
        # Check if the config system is available
        try:
            from src.utils.config import get_config_value, CONFIG_LOADED
            
            # Only query config if it's been properly loaded
            if CONFIG_LOADED:
                # Get animation settings from config
                use_static = get_config_value("menu.use_static_portal", True)
                animations_enabled = get_config_value("menu.animations_enabled", False)
                logger.debug(f"Animation settings from config: static={use_static}, enabled={animations_enabled}")
            else:
                logger.debug("Config not loaded, using default animation settings")
        except ImportError:
            logger.debug("Config module not available, using default animation settings")
        except Exception as e:
            logger.debug(f"Error accessing config: {e}, using default animation settings")
            
        # Check for terminal compatibility mode
        terminal_compatibility_mode = False
        try:
            if CONFIG_LOADED:
                terminal_compatibility_mode = get_config_value("menu.terminal_compatibility_mode", False)
        except Exception:
            pass
            
        # Use static portal if animations are disabled or static portal is enabled
        if use_static or not animations_enabled or terminal_compatibility_mode:
            logger.debug(f"Using static portal (static={use_static}, animations={animations_enabled}, compat={terminal_compatibility_mode})")
            display_static_portal_open()
            return
            
       
        # Select portal size based on terminal dimensions
        width = width or get_terminal_width()
        height = height or get_terminal_height()
        
        if height < 10:
            portal_frames = PORTAL_SMALL
        elif width < 50:
            portal_frames = PORTAL_SMALL
        else:
            portal_frames = PORTAL_MEDIUM
        
        # Run the animation
        for _ in range(frames):
            for i, frame in enumerate(portal_frames):
                # Clear screen for clean animation
                clear_screen()
                
                # Split frame into lines
                frame_lines = frame.strip().split('\n')
                
                # Center each line
                centered_frame = []
                for line in frame_lines:
                    centered_line = line.center(width)
                    centered_frame.append(centered_line)
                
                # Add some vertical spacing
                print("\n" * 2)
                
                # Colorize and print the portal frame
                try:
                    for line in centered_frame:
                        colored_line = colorize_portal(line)
                        print(colored_line)
                except Exception as e:
                    # Fallback if colorize_portal fails
                    logger.debug(f"Error in portal animation colorizing: {e}")
                    for line in centered_frame:
                        print(line)
                
                # Add some bottom spacing
                print("\n" * 2)
                
                # Wait for next frame
                time.sleep(frame_duration)
        
        # Pause on the final frame
        time.sleep(frame_duration * 2)
        
    except KeyboardInterrupt:
        # Allow cancelling the animation
        logger.debug("Animation cancelled by keyboard interrupt")
        clear_screen()
    except Exception as e:
        # Fallback to static display if animation fails
        logger.error(f"Error in portal animation: {e}")
        display_static_portal_open()

@safe_execute()
def animate_portal_close(width: int = None, height: int = None, frames: int = None, 
                         frame_duration: float = None) -> None:
    """
    Show portal closing animation, properly centered in the terminal.
    
    Args:
        width: Terminal width (auto-detected if None)
        height: Terminal height (auto-detected if None)
    """
    logger.debug("Showing portal close animation")
    
    # If returning from a command execution, skip animation
    global RETURNING_FROM_COMMAND
    if RETURNING_FROM_COMMAND:
        logger.debug("Skipping close animation as returning from command")
        display_static_portal_closed()
        RETURNING_FROM_COMMAND = False
        return
    
    # Determine if animations should be shown or if we should use static portal
    try:
        # Default to static portal and no animations for safety
        use_static = True
        animations_enabled = False
        
        # Check if the config system is available
        try:
            from src.utils.config import get_config_value, CONFIG_LOADED
            
            # Only query config if it's been properly loaded
            if CONFIG_LOADED:
                # Get animation settings from config
                use_static = get_config_value("menu.use_static_portal", True)
                animations_enabled = get_config_value("menu.animations_enabled", False)
                logger.debug(f"Animation settings from config: static={use_static}, enabled={animations_enabled}")
            else:
                logger.debug("Config not loaded, using default animation settings")
        except ImportError:
            logger.debug("Config module not available, using default animation settings")
        except Exception as e:
            logger.debug(f"Error accessing config: {e}, using default animation settings")
            
        # Check for terminal compatibility mode
        terminal_compatibility_mode = False
        try:
            if CONFIG_LOADED:
                terminal_compatibility_mode = get_config_value("menu.terminal_compatibility_mode", False)
        except Exception:
            pass
            
        # Use static portal if animations are disabled or static portal is enabled
        if use_static or not animations_enabled or terminal_compatibility_mode:
            logger.debug(f"Using static portal (static={use_static}, animations={animations_enabled}, compat={terminal_compatibility_mode})")
            display_static_portal_closed()
            return
        
        # Use default animation parameters if not specified
        frame_duration = FRAME_DURATION if frame_duration is None else frame_duration
        
        # Select portal size based on terminal dimensions
        width = width or get_terminal_width()
        height = height or get_terminal_height()
        
        if height < 10:
            portal_frames = PORTAL_SMALL
        elif width < 50:
            portal_frames = PORTAL_SMALL
        else:
            portal_frames = PORTAL_MEDIUM
        
        # Run the animation - reversed frames for closing
        for _ in range(frames):
            for i, frame in enumerate(reversed(portal_frames)):
                # Clear screen for clean animation
                clear_screen()
                
                # Split frame into lines
                frame_lines = frame.strip().split('\n')
                
                # Center each line
                centered_frame = []
                for line in frame_lines:
                    centered_line = line.center(width)
                    centered_frame.append(centered_line)
                
                # Add some vertical spacing
                print("\n" * 2)
                
                # Colorize and print the portal frame
                try:
                    for line in centered_frame:
                        colored_line = colorize_portal(line)
                        print(colored_line)
                except Exception as e:
                    # Fallback if colorize_portal fails
                    logger.debug(f"Error in portal animation colorizing: {e}")
                    for line in centered_frame:
                        print(line)
                
                # Add some bottom spacing
                print("\n" * 2)
                
                # Wait for next frame
                time.sleep(frame_duration)
        
        # Final clear after closing
        clear_screen()
        
    except KeyboardInterrupt:
        # Allow cancelling the animation
        logger.debug("Animation cancelled by keyboard interrupt")
        clear_screen()
    except Exception as e:
        # Fallback to static display if animation fails
        logger.error(f"Error in portal animation: {e}")
        display_static_portal_closed()
        clear_screen()

@safe_execute()
def animate_transition(from_menu: Optional[Menu] = None, to_menu: Optional[Menu] = None, 
                       frame_duration: float = None) -> None:
    """
    Transition between menus with portal effect.
    
    Args:
        from_menu: Source menu (optional)
        to_menu: Destination menu (optional)
        frame_duration: Seconds per frame (uses FRAME_DURATION if None)
    """
    # Use default animation parameters if not specified
    frame_duration = FRAME_DURATION if frame_duration is None else frame_duration
    
    # Skip if animations disabled
    if not get_config_value("animations_enabled", True):
        return
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    logger.debug("Showing menu transition animation")
    
    # Simplified portal swirl animation
    swirl_chars = ['*', '.', 'o', 'O', '@', '*']
    swirl_frames = []
    
    # Build the swirl frames
    for i in range(5):
        # Pattern gets more intense with each frame
        pattern = swirl_chars[i % len(swirl_chars)] * (i + 1)
        line = pattern.center(width)
        colored_line = ""
        for j, char in enumerate(line):
            if char in swirl_chars:
                if random.random() < 0.5:
                    colored_line += PORTAL_GREEN + char + RESET
                else:
                    colored_line += PORTAL_BLUE + char + RESET
            else:
                colored_line += char
        swirl_frames.append(colored_line)

        clear_screen()

@safe_execute()
def animate_item_selection(item: MenuItem, index: int, width: int) -> None:
    """
    Highlight selected item with animation.
    
    Args:
        item: MenuItem being selected
        index: Index of the item
        width: Available width for rendering
    """
    # Skip if animations disabled
    if not get_config_value("animations_enabled", True):
        return
        
    # Skip if terminal doesn't support ANSI colors
    if not supports_ansi_color():
        return
        
    # Get item text
    item_text = item.render(width, selected=False)
    
    # Simple pulse animation
    highlight_colors = ["cyan", "blue", "cyan"]
    
    for color in highlight_colors:
        # Create highlighted version
        highlighted = color_text(f"{BOLD}{item_text}{RESET}", color)
        
        # Print the highlighted item
        sys.stdout.write(f"\r{highlighted}")
        sys.stdout.flush()
        
        # Short delay
        time.sleep(0.05)
        
    # Restore normal selection
    final_text = item.render(width, selected=True)
    sys.stdout.write(f"\r{final_text}")
    sys.stdout.flush()

@safe_execute()
def animate_typing(text: str, speed: float = None, variations: bool = True) -> None:
    """
    Show typing animation for text.
    
    Args:
        text: Text to display
        speed: Base typing speed in seconds per character (uses TYPING_SPEED if None)
        variations: Whether to vary typing speed for natural effect
    """
    # Use default typing speed if not specified
    speed = TYPING_SPEED if speed is None else speed
    
    # Skip if animations disabled
    if not get_config_value("animations_enabled", True):
        print(text)
        return
    
    # Add random burps if this is a Rick message
    if random.random() < 0.3 and "*burp*" not in text:
        parts = text.split()
        if len(parts) > 3:
            burp_index = random.randint(1, len(parts) - 2)
            parts.insert(burp_index, "*burp*")
            text = " ".join(parts)
    
    # Character by character output
    for char in text:
        # Print the character without newline
        sys.stdout.write(char)
        sys.stdout.flush()
        
        # Vary speed if requested
        if variations:
            if char == '.':
                time.sleep(speed * 3)
            elif char == ',' or char == ';':
                time.sleep(speed * 2)
            elif char == ' ':
                time.sleep(speed)
            else:
                time.sleep(speed)
        else:
            time.sleep(speed)
    
    print()  # End with newline

@safe_execute()
def create_spinner(message: str = "Processing", spinner_type: str = "portal", 
                   duration: float = None, fps: int = 10) -> None:
    """
    Show loading spinner animation.
    
    Args:
        message: Message to display alongside spinner
        spinner_type: Type of spinner ('portal', 'dots', 'bar')
        duration: How long to run spinner (None = manual stop required)
        fps: Frames per second
    
    Returns:
        Callable: Function to stop the spinner
    """
    # Skip if animations disabled or terminal doesn't support it
    if not get_config_value("animations_enabled", True) or not supports_ansi_color():
        print(f"{message}...")
        return lambda: None
    
    # Different spinner styles
    spinners = {
        "portal": ["◐", "◓", "◑", "◒"],
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "bar": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
    }
    
    # Use dots as fallback if requested type isn't available
    frames = spinners.get(spinner_type, spinners["dots"])
    
    # Setup for spinner
    import threading
    import itertools
    
    # Flag to control the spinner
    stop_spinner = threading.Event()
    
    def spin():
        # Loop through spinner frames
        for frame in itertools.cycle(frames):
            if stop_spinner.is_set():
                break
                
            # Print the spinner frame
            sys.stdout.write(f"\r{PORTAL_GREEN}{frame}{RESET} {message}... ")
            sys.stdout.flush()
            
            # Wait for next frame
            time.sleep(1.0 / fps)
            
        # Clear the line when done
        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
        sys.stdout.flush()
    
    # Start spinner in a separate thread
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.daemon = True
    spinner_thread.start()
    
    # If duration specified, sleep and then stop
    if duration is not None:
        def auto_stop():
            time.sleep(duration)
            stop_spinner.set()
            
        auto_stop_thread = threading.Thread(target=auto_stop)
        auto_stop_thread.daemon = True
        auto_stop_thread.start()
    
    # Return function to stop the spinner
    return lambda: stop_spinner.set()

# =====================================================================
# Visual Elements
# =====================================================================

@safe_execute()
def create_menu_border(width: int, height: int, style: str = "portal") -> List[str]:
    """
    Create Rick-themed border for menus.
    
    Args:
        width: Width of the border
        height: Height of the border
        style: Border style ('portal', 'simple', 'double')
        
    Returns:
        List[str]: Lines of the border
    """
    logger.debug(f"Creating menu border with style: {style}")
    
    # Ensure minimum dimensions
    width = max(width, 20)
    height = max(height, 5)
    
    # Available border styles
    styles = {
        "portal": {
            "top_left": "╭",
            "top_right": "╮",
            "bottom_left": "╰",
            "bottom_right": "╯",
            "horizontal": "─",
            "vertical": "│"
        },
        "simple": {
            "top_left": "+",
            "top_right": "+",
            "bottom_left": "+",
            "bottom_right": "+",
            "horizontal": "-",
            "vertical": "|"
        },
        "double": {
            "top_left": "╔",
            "top_right": "╗",
            "bottom_left": "╚",
            "bottom_right": "╝",
            "horizontal": "═",
            "vertical": "║"
        }
    }
    
    # Use simple style if unicode not supported
    if not supports_unicode():
        style = "simple"
        
    # Get border characters for the style
    border = styles.get(style, styles["simple"])
    
    # Create border lines
    top = border["top_left"] + border["horizontal"] * (width - 2) + border["top_right"]
    middle = border["vertical"] + " " * (width - 2) + border["vertical"]
    bottom = border["bottom_left"] + border["horizontal"] * (width - 2) + border["bottom_right"]
    
    # Colorize if supported
    if supports_ansi_color():
        top = color_text(top, "cyan")
        middle = color_text(middle, "cyan")
        bottom = color_text(bottom, "cyan")
    
    # Create all lines
    lines = [top]
    for _ in range(height - 2):
        lines.append(middle)
    lines.append(bottom)
    
    return lines

@safe_execute()
def create_portal_background(width: int, height: int, density: float = 0.05) -> List[str]:
    """
    Create portal background effect.
    
    Args:
        width: Width of the background
        height: Height of the background
        density: Density of portal elements (0.0-1.0)
        
    Returns:
        List[str]: Lines of the background
    """
    logger.debug("Creating portal background")
    
    # Portal elements
    elements = ["*", "~", ".", "°", "·"]
    
    # Create background
    lines = []
    for _ in range(height):
        line = ""
        for _ in range(width):
            # Add portal element based on density
            if random.random() < density:
                element = random.choice(elements)
                # Colorize if supported
                if supports_ansi_color():
                    if element in "*°":
                        element = color_text(element, "green")
                    elif element in "~":
                        element = color_text(element, "blue")
                    else:
                        element = color_text(element, "cyan")
                line += element
            else:
                line += " "
        lines.append(line)
        
    return lines

@safe_execute()
def create_menu_header(title: str, width: int, with_quote: bool = True) -> List[str]:
    """
    Create styled menu header with title.
    
    Args:
        title: Menu title
        width: Available width
        with_quote: Whether to include a Rick quote
        
    Returns:
        List[str]: Lines of the header
    """
    logger.debug(f"Creating menu header for: {title}")
    
    # Make sure title fits within width
    max_title_width = width - 10
    if len(title) > max_title_width:
        title = title[:max_title_width-3] + "..."
    
    # Create header separator
    separator = "═" * width if supports_unicode() else "=" * width
    
    # Format title
    formatted_title = title.center(width)
    if supports_ansi_color():
        formatted_title = color_text(BOLD + formatted_title + RESET, "green")
        separator = color_text(separator, "blue")
    
    # Add Rick quote if requested
    lines = [formatted_title, separator]
    
    if with_quote and random.random() < 0.7:
        # Add a random Rick menu comment
        quote = random.choice(RICK_MENU_COMMENTS)
        
        if supports_ansi_color():
            quote = color_text(quote, "yellow")
            
        lines.append(quote.center(width))
        lines.append("")
    else:
        lines.append("")
        
    return lines

@safe_execute()
def create_menu_footer(controls: Dict[str, str], width: int) -> List[str]:
    """
    Create footer with key controls and system metrics if enabled.
    
    Args:
        controls: Dict mapping keys to actions
        width: Available width
        
    Returns:
        List[str]: Lines of the footer
    """
    logger.debug("Creating menu footer")
    
    # Check if metrics should be displayed
    show_metrics = get_config_value("ui.show_metrics", None)
    # Try alternate format if not found
    if show_metrics is None:
        show_metrics = get_config_value("ui___show_metrics", True)
    else:
        # Convert to boolean if needed
        show_metrics = str(show_metrics).lower() == "true"
    
    # Create separator
    separator = "─" * width if supports_unicode() else "-" * width
    if supports_ansi_color():
        separator = color_text(separator, "blue")
    
    # Format controls
    control_parts = []
    for key, action in controls.items():
        if supports_ansi_color():
            formatted = f"{color_text(key, 'cyan')}: {action}"
        else:
            formatted = f"{key}: {action}"
        control_parts.append(formatted)
    
    # Join controls with separators
    control_text = " | ".join(control_parts)
    
    # Ensure control text fits
    if len(control_text) > width:
        # Create multiple lines of controls if needed
        control_lines = []
        current_line = []
        current_width = 0
        
        for part in control_parts:
            part_width = len(part) + 3  # +3 for the separator
            if current_width + part_width > width and current_line:
                control_lines.append(" | ".join(current_line))
                current_line = [part]
                current_width = part_width
            else:
                current_line.append(part)
                current_width += part_width
                
        if current_line:
            control_lines.append(" | ".join(current_line))
        
        footer_lines = [separator] + [line.center(width) for line in control_lines]
    else:
        # Single line of controls
        footer_lines = [separator, control_text.center(width)]
    
    # Add system metrics if enabled
    if show_metrics:
        try:
            # Get current menu implementation
            use_python_impl = get_config_value("ui.menu.use_python_implementation", True)
            impl_indicator = "PY-MENU" if use_python_impl else "ZSH-MENU"
            
            # Try to get system metrics
            import psutil
            
            # Get CPU usage
            cpu_usage = f"{psutil.cpu_percent(interval=0.1)}%" if hasattr(psutil, 'cpu_percent') else "??%"
            
            # Get RAM usage
            mem_usage = f"{psutil.virtual_memory().percent}%" if hasattr(psutil, 'virtual_memory') else "??%"
            
            # Get temperature (platform specific)
            temperature = "??"
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps and 'coretemp' in temps:
                        temperature = f"{temps['coretemp'][0].current}°C"
                    elif temps and 'cpu_thermal' in temps:
                        temperature = f"{temps['cpu_thermal'][0].current}°C"
            except:
                pass
                
            # Create metrics line
            metrics_text = f"CPU: {cpu_usage} | RAM: {mem_usage} | TEMP: {temperature} | {impl_indicator}"
            
            # Add Rick quote if there's space
            rick_quotes = [
                "Wubba lubba dub dub!",
                "I'm not drunk! *burp*",
                "I've got a portal gun and a bad attitude!",
                "Science isn't about why, it's about why not!",
                "Nobody exists on purpose. Nobody belongs anywhere."
            ]
            
            # Select random quote
            import random
            rick_quote = random.choice(rick_quotes)
            
            # Add quote to metrics if there's space
            if len(metrics_text) + len(rick_quote) + 5 < width:
                metrics_text = f"{metrics_text} | {rick_quote}"
                
            # Add metrics line to footer
            metrics_line = metrics_text.center(width)
            if supports_ansi_color():
                metrics_line = color_text(metrics_line, "blue")
                
            footer_lines.insert(1, metrics_line)
        except Exception as e:
            logger.error(f"Error displaying system metrics in footer: {str(e)}")
    
    return footer_lines

@safe_execute()
def highlight_selection(item: MenuItem, selected: bool = True, width: int = 80) -> str:
    """
    Highlight current item with Rick-themed styling.
    
    Args:
        item: MenuItem to highlight
        selected: Whether item is selected
        width: Available width
        
    Returns:
        str: Highlighted item text
    """
    # Get base rendering from the item
    item_text = item.render(width, selected)
    
    # For selected items, add additional styling
    if selected and supports_ansi_color():
        # Add arrow indicator
        arrow = MENU_SYMBOLS["arrow"] + " "
        item_text = arrow + item_text
        
        # Add portal icon for extra flair
        if random.random() < 0.1:  # Occasional portal decoration
            portal = " " + MENU_SYMBOLS["portal"]
            item_text += portal
    
    return item_text

@safe_execute()
def highlight_category(category: MenuCategory, selected: bool = True, width: int = 80) -> str:
    """
    Highlight current category with Rick-themed styling.
    
    Args:
        category: MenuCategory to highlight
        selected: Whether category is selected
        width: Available width
        
    Returns:
        str: Highlighted category text
    """
    # Get base rendering from the category
    category_text = category.render(width, selected)
    
    # For selected categories, add additional styling
    if selected and supports_ansi_color():
        # Add arrow indicator
        arrow = MENU_SYMBOLS["arrow"] + " "
        category_text = arrow + category_text
    
    return category_text

@safe_execute()
def create_rick_menu_comment() -> str:
    """
    Create a random Rick-styled menu comment.
    
    Returns:
        str: Random Rick comment
    """
    comment = random.choice(RICK_MENU_COMMENTS)
    
    # Add burp if not already present
    if "*burp*" not in comment and random.random() < 0.3:
        parts = comment.split()
        if len(parts) > 2:
            burp_index = random.randint(1, len(parts) - 1)
            parts.insert(burp_index, "*burp*")
            comment = " ".join(parts)
    
    # Colorize if supported
    if supports_ansi_color():
        comment = color_text(comment, "yellow")
        
    return comment

# =====================================================================
# Core Menu Functions
# =====================================================================

@safe_execute()
def display_menu(title: str, items: List[Union[MenuItem, str]], width: int = None, 
                 height: int = None, border_style: str = "portal", 
                 with_portal_bg: bool = False) -> Optional[Tuple[int, Any]]:
    """
    Show a menu with items and get user selection.
    
    Args:
        title: Menu title
        items: List of MenuItems or strings
        width: Menu width (uses terminal width if None)
        height: Menu height (uses terminal height if None)
        border_style: Border style ('portal', 'simple', 'double')
        with_portal_bg: Whether to show portal background
        
    Returns:
        Optional[Tuple[int, Any]]: Selected index and item value, or None if cancelled
    """
    logger.debug(f"Displaying menu: {title} with {len(items)} items")
    
    # Convert string items to MenuItems
    menu_items = []
    for item in items:
        if isinstance(item, str):
            menu_items.append(MenuItem(text=item, value=item))
        else:
            menu_items.append(item)
    
    # Create menu object
    menu = Menu(title=title, items=menu_items, width=width, height=height)
    
    # Display the menu
    return navigate_menu(menu, border_style=border_style, with_portal_bg=with_portal_bg)

@safe_execute()
def navigate_menu(menu: Menu, parent_menu: Menu = None, border_style: str = "portal",
                  with_portal_bg: bool = False) -> Optional[Tuple[int, Any]]:
    """
    Handle menu navigation and selection.
    
    Args:
        menu: Menu object to navigate
        parent_menu: Parent menu (for back navigation)
        border_style: Border style to use
        with_portal_bg: Whether to show portal background
        
    Returns:
        Optional[Tuple[int, Any]]: Selected index and item value, or None if cancelled
    """
    logger.debug(f"Navigating menu: {menu.title}")
    
    # Get terminal dimensions
    term_width = get_terminal_width()
    term_height = get_terminal_height()
    
    # Set menu width and height
    menu.width = menu.width or term_width
    menu.height = menu.height or term_height
    
    # Ensure menu is within terminal bounds
    menu.width = min(menu.width, term_width - 2)
    menu.height = min(menu.height, term_height - 2)
    
    # Set up key controls
    controls = {
        "↑/↓": "Navigate", 
        "Enter": "Select",
        "Esc": "Exit"
    }
    
    # Add back control if there's a parent menu
    if parent_menu:
        controls["B"] = "Back"
    
    # Add help control
    controls["?"] = "Help"
    
    # Show portal entry animation
    animate_transition(to_menu=menu)
    
    # Main menu navigation loop
    while not menu.exit_requested:
        # Clear screen
        clear_screen()
        
        # Create menu elements
        border = create_menu_border(menu.width, menu.height, style=border_style)
        header = create_menu_header(menu.title, menu.width)
        footer = create_menu_footer(controls, menu.width)
        
        # Get visible items
        visible_items = menu.get_visible_items()
        
        # Calculate available space for items
        available_height = menu.height - len(header) - len(footer) - 2
        
        # Handle scrolling if needed
        total_items = len(visible_items)
        if total_items > available_height:
            # Adjust scroll offset if needed
            if menu.selected_index < menu.scroll_offset:
                menu.scroll_offset = menu.selected_index
            elif menu.selected_index >= menu.scroll_offset + available_height:
                menu.scroll_offset = menu.selected_index - available_height + 1
                
            # Get visible items after scrolling
            visible_range = visible_items[menu.scroll_offset:menu.scroll_offset + available_height]
            
            # Add scroll indicators
            has_scroll_up = menu.scroll_offset > 0
            has_scroll_down = menu.scroll_offset + available_height < total_items
            
            # Update controls for scrolling
            if has_scroll_up:
                controls["PgUp"] = "Scroll Up"
            elif "PgUp" in controls:
                del controls["PgUp"]
                
            if has_scroll_down:
                controls["PgDn"] = "Scroll Down"
            elif "PgDn" in controls:
                del controls["PgDn"]
        else:
            visible_range = visible_items
            menu.scroll_offset = 0
        
        # Portal background (if requested)
        background = None
        if with_portal_bg and supports_ansi_color():
            background = create_portal_background(menu.width - 2, menu.height - 2)
        
        # Start rendering
        content = []
        
        # Add header
        for line in header:
            content.append(line)
        
        # Add items
        for i, item in enumerate(visible_range):
            # Get global index (accounting for scroll)
            global_index = i + menu.scroll_offset
            
            # Format the item
            if isinstance(item, MenuCategory):
                formatted = highlight_category(item, global_index == menu.selected_index, menu.width)
            else:
                formatted = highlight_selection(item, global_index == menu.selected_index, menu.width)
                
            content.append(formatted)
        
        # Add padding if needed
        padding_needed = available_height - len(visible_range)
        for _ in range(padding_needed):
            content.append("")
        
        # Add footer
        for line in footer:
            content.append(line)
        
        # Render the menu
        print(border[0])  # Top border
        
        for i, line in enumerate(content):
            # Add background if available
            if background and 0 <= i < len(background):
                bg_line = background[i]
                padded_line = line.ljust(menu.width - 2)
                # Print with border
                print(f"{border[1][0]}{padded_line}{border[1][-1]}")
            else:
                # Print with border
                print(f"{border[1][0]}{line.ljust(menu.width - 2)}{border[1][-1]}")
        
        print(border[-1])  # Bottom border
        
        # Get user input
        key = get_single_key()
        
        # Process key input
        if key in ('\x1b', 'q', 'Q'):  # Escape or q
            # Exit the menu
            menu.exit()
            animate_portal_close()
            return None
            
        elif key in ('b', 'B') and parent_menu:  # Back
            # Go back to parent menu
            animate_transition(from_menu=menu, to_menu=parent_menu)
            return (-1, "BACK")
            
        elif key in ('?', 'h', 'H'):  # Help
            show_menu_help(menu, controls)
            
        elif key in ('\r', '\n', ' '):  # Enter or space
            # Activate the selected item
            result = menu.activate_selected()
            
            # If it's a category, just redraw
            current_item = menu.get_current_item()
            if isinstance(current_item, MenuCategory):
                continue
            
            # Otherwise return the result
            if result is not None:
                animate_portal_close()
                return (menu.selected_index, result)
                
        elif key in ('j', 'J', '\x1b[B'):  # Down arrow or j
            menu.select_next()
            
        elif key in ('k', 'K', '\x1b[A'):  # Up arrow or k
            menu.select_previous()
            
        elif key in ('g', 'G', 'Home'):  # Home or g
            # Go to first item
            menu.selected_index = 0
            
        elif key in ('G', 'End'):  # End or G
            # Go to last item
            menu.selected_index = len(visible_items) - 1
            
        elif key in ('PgDn', '\x1b[6~'):  # Page Down
            # Page down (move multiple items)
            new_index = min(menu.selected_index + available_height, len(visible_items) - 1)
            menu.selected_index = new_index
            
        elif key in ('PgUp', '\x1b[5~'):  # Page Up
            # Page up (move multiple items)
            new_index = max(menu.selected_index - available_height, 0)
            menu.selected_index = new_index
    
    # Menu was exited
    animate_portal_close()
    return None

@safe_execute()
def get_selection(items: List[Union[str, Dict[str, Any], MenuItem]], prompt: str = "Select an option", 
                  default: int = None, numbered: bool = True) -> Optional[int]:
    """
    Get user selection from a list of options.
    
    Args:
        items: List of items (strings, dicts, or MenuItems)
        prompt: Text to display above the menu
        default: Default selection index
        numbered: Whether to show item numbers
        
    Returns:
        Optional[int]: Selected index or None if cancelled
    """
    logger.debug(f"Getting selection from {len(items)} items")
    
    # Convert items to proper format
    menu_items = []
    for i, item in enumerate(items):
        if isinstance(item, MenuItem):
            menu_items.append(item)
        elif isinstance(item, dict) and 'text' in item:
            # Convert dict to MenuItem
            text = item['text']
            value = item.get('value', text)
            enabled = item.get('enabled', True)
            icon = item.get('icon', None)
            menu_items.append(MenuItem(text=text, value=value, enabled=enabled, icon=icon))
        else:
            # Add number prefix if requested
            prefix = f"{i+1}. " if numbered else ""
            text = prefix + str(item)
            menu_items.append(MenuItem(text=text, value=item))
    
    # Set default selection
    menu = Menu(title=prompt, items=menu_items)
    if default is not None and 0 <= default < len(menu_items):
        menu.selected_index = default
    
    # Display menu and get selection
    result = navigate_menu(menu)
    
    # Return just the index
    if result:
        return result[0]
    return None

@safe_execute()
def show_message(text: str, title: str = "Message", with_animation: bool = True,
                 message_type: str = "info") -> None:
    """
    Display message with animation.
    
    Args:
        text: Message text
        title: Message title
        with_animation: Whether to show typing animation
        message_type: Type of message ('info', 'error', 'warning', 'success')
    """
    logger.debug(f"Showing {message_type} message: {text}")
    
    # Clear the screen
    clear_screen()
    
    # Get terminal dimensions
    width = get_terminal_width()
    height = get_terminal_height()
    
    # Create border
    border = create_menu_border(width, 10, style="portal")
    
    # Format title based on message type
    if message_type == "error":
        formatted_title = format_error(title)
    elif message_type == "warning":
        formatted_title = format_warning(title)
    elif message_type == "success":
        formatted_title = format_success(title)
    else:
        formatted_title = format_info(title)
    
    # Center the title
    centered_title = formatted_title.center(width - 4)
    
    # Format the message text
    formatted_text = format_text(text, width=width - 8)
    
    # Add Rick's touch to messages
    if message_type == "error" and random.random() < 0.7:
        formatted_text += "\n\n" + color_text("Nice job breaking things, *burp* genius.", "red")
    elif message_type == "warning" and random.random() < 0.7:
        formatted_text += "\n\n" + color_text("You're being warned for a reason, Einstein.", "yellow")
    elif message_type == "success" and random.random() < 0.7:
        formatted_text += "\n\n" + color_text("Wow, something actually went right for once!", "green")
        
    # Print the message
    print(border[0])
    print(f"{border[1][0]}{centered_title.center(width-2)}{border[1][-1]}")
    print(border[1])
    
    # Print the message text with or without animation
    for line in formatted_text.split('\n'):
        # Calculate padding for center alignment
        padding = (width - 2 - len(line)) // 2
        padded_line = " " * padding + line
        
        if with_animation:
            print(f"{border[1][0]}", end="")
            animate_typing(padded_line.ljust(width-2), speed=0.01)
            print(f"{border[1][-1]}")
        else:
            print(f"{border[1][0]}{padded_line.ljust(width-2)}{border[1][-1]}")
    
    # Add empty space and prompt
    for _ in range(2):
        print(f"{border[1][0]}{' ' * (width-2)}{border[1][-1]}")
        
    print(f"{border[1][0]}{color_text('Press any key to continue...', 'cyan').center(width-2)}{border[1][-1]}")
    print(border[-1])
    
    # Wait for key press
    get_single_key()

@safe_execute()
def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Get yes/no confirmation from user.
    
    Args:
        prompt: Confirmation prompt text
        default: Default response (True for yes, False for no)
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    logger.debug(f"Asking for confirmation: {prompt}")
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Create border
    border = create_menu_border(width, 7, style="portal")
    
    # Format the prompt with Rick's flair
    if random.random() < 0.3 and "*burp*" not in prompt:
        parts = prompt.split()
        burp_index = random.randint(1, len(parts) - 1)
        parts.insert(burp_index, "*burp*")
        prompt = " ".join(parts)
    
    formatted_prompt = format_text(prompt, width=width - 8)
    
    # Show default in the options
    yes_text = "[Y]es" if default else "[y]es"
    no_text = "[n]o" if not default else "[N]o"
    options_text = f"{yes_text} / {no_text}"
    
    # Print confirmation dialog
    clear_screen()
    print(border[0])
    print(f"{border[1][0]}{color_text('Confirmation', 'yellow').center(width-2)}{border[1][-1]}")
    print(border[1])
    
    # Print the prompt text
    for line in formatted_prompt.split('\n'):
        # Calculate padding for center alignment
        padding = (width - 2 - len(line)) // 2
        padded_line = " " * padding + line
        print(f"{border[1][0]}{padded_line.ljust(width-2)}{border[1][-1]}")
    
    print(border[1])
    print(f"{border[1][0]}{options_text.center(width-2)}{border[1][-1]}")
    print(border[-1])
    
    # Get user response
    while True:
        key = get_single_key().lower()
        
        if key in ('y', 'Y', '\r', '\n') and default:
            return True
        elif key == 'y':
            return True
        elif key in ('n', 'N', '\x1b'):  # n, N, or Escape
            return False
        elif key in ('\r', '\n'):  # Enter
            return default

@safe_execute()
def show_progress(operation: str, total_steps: int, with_portal: bool = True,
                  cancel_allowed: bool = True) -> Callable[[int, str], bool]:
    """
    Show progress indicator for an operation.
    
    Args:
        operation: Name of the operation
        total_steps: Total number of steps
        with_portal: Whether to use portal-themed progress
        cancel_allowed: Whether the operation can be cancelled
        
    Returns:
        Callable: Function to update progress
    """
    logger.debug(f"Creating progress indicator for: {operation}")
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Setup progress state
    progress_state = {
        'current': 0,
        'total': total_steps,
        'status': 'Starting...',
        'cancelled': False
    }
    
    # Create the progress bar width (account for text and borders)
    bar_width = width - 20
    
    # Portal animation characters
    portal_chars = ['◢', '◣', '◤', '◥'] if supports_unicode() else ['>', 'v', '<', '^']
    portal_index = 0
    
    # Function to update the progress display
    def update_progress():
        # Calculate percentage
        if progress_state['total'] <= 0:
            percent = 100
        else:
            percent = int((progress_state['current'] / progress_state['total']) * 100)
        
        # Create progress bar
        completed_width = int((bar_width * percent) / 100)
        
        if with_portal and supports_ansi_color():
            # Portal-themed progress bar
            bar = ""
            for i in range(bar_width):
                if i < completed_width:
                    if i == completed_width - 1:
                        # Add portal character at the end of progress
                        char = portal_chars[portal_index]
                        bar += color_text(char, "green")
                    else:
                        # Alternate colors for completed section
                        if i % 3 == 0:
                            bar += color_text("■", "green")
                        elif i % 3 == 1:
                            bar += color_text("■", "cyan")
                        else:
                            bar += color_text("■", "blue")
                else:
                    # Empty section
                    bar += "□"
        else:
            # Simple progress bar
            bar = "[" + "■" * completed_width + "□" * (bar_width - completed_width) + "]"
        
        # Format status line
        status_line = f"{percent:3d}% {bar} {progress_state['status']}"
        
        # Add cancel instruction if allowed
        if cancel_allowed:
            cancel_text = "Press 'Esc' to cancel"
            if supports_ansi_color():
                cancel_text = color_text(cancel_text, "red")
            status_line += f" ({cancel_text})"
        
        # Clear line and print
        sys.stdout.write("\r" + " " * width)  # Clear the line
        sys.stdout.write("\r" + status_line)
        sys.stdout.flush()
    
    # Function for the caller to update progress
    def update(step: int, status: str) -> bool:
        """
        Update the progress indicator.
        
        Args:
            step: Current step (0 to total_steps)
            status: Status message
            
        Returns:
            bool: False if cancelled, True otherwise
        """
        nonlocal portal_index
        
        # Update state
        progress_state['current'] = step
        progress_state['status'] = status
        
        # Rotate portal character
        portal_index = (portal_index + 1) % len(portal_chars)
        
        # Update display
        update_progress()
        
        # Check for cancellation if allowed
        if cancel_allowed and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == '\x1b':  # Escape key
                progress_state['cancelled'] = True
                print("\nOperation cancelled by user.")
                return False
        
        return not progress_state['cancelled']
    
    # Initial display
    print(f"\n{color_text(operation, 'cyan')}\n")
    update_progress()
    
    return update

@safe_execute()
def show_menu_help(menu: Menu, controls: Dict[str, str]) -> None:
    """
    Show help information about menu controls.
    
    Args:
        menu: Current menu
        controls: Control key mappings
    """
    logger.debug("Showing menu help")
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Create help content
    help_content = [
        "=== Rick Assistant Menu Help ===",
        "",
        "Navigation Controls:",
        "  ↑/k: Move selection up",
        "  ↓/j: Move selection down",
        "  Home/g: Go to first item",
        "  End/G: Go to last item",
        "  PgUp: Move up one page",
        "  PgDn: Move down one page",
        "",
        "Action Controls:",
        "  Enter/Space: Select item",
        "  b: Go back to previous menu",
        "  Esc/q: Exit current menu",
        "  ?: Show this help"
    ]
    
    # Add Rick's commentary
    rick_comments = [
        "Look at you needing help with a simple *burp* menu. Pathetic.",
        "It's just a menu, not interdimensional rocket science.",
        "I've trained lab rats that learned menus faster than you.",
        "Oh great, you found the help section. What an achievement.",
        "Yes, you press keys and things happen. Revolutionary concept."
    ]
    
    help_content.append("")
    help_content.append(random.choice(rick_comments))
    
    # Format and display as a message
    formatted_help = "\n".join(help_content)
    show_message(formatted_help, title="Menu Help", with_animation=False)

# =====================================================================
# Integration with Existing Components
# =====================================================================

@safe_execute()
def get_menu_key() -> str:
    """
    Get keyboard input specific for menu navigation.
    
    This function extends get_single_key to better handle special keys
    like arrows and function keys in menu context.
    
    Returns:
        str: Key pressed by user
    """
    # Use input system's single key function
    key = get_single_key()
    
    # Process special key sequences
    if key == '\x1b':  # Escape sequence
        # Check if there's more input (arrow keys, etc.)
        if hasattr(sys.stdin, 'fileno') and select.select([sys.stdin], [], [], 0.1)[0]:
            seq = sys.stdin.read(2)
            
            # Arrow keys
            if seq == '[A':
                return 'UP'
            elif seq == '[B':
                return 'DOWN'
            elif seq == '[C':
                return 'RIGHT'
            elif seq == '[D':
                return 'LEFT'
            elif seq == '[5':  # PgUp
                # Consume trailing ~
                sys.stdin.read(1)
                return 'PGUP'
            elif seq == '[6':  # PgDn
                # Consume trailing ~
                sys.stdin.read(1)
                return 'PGDN'
            elif seq == '[H':  # Home
                return 'HOME'
            elif seq == '[F':  # End
                return 'END'
        
        # Just Escape key
        return 'ESC'
    
    # Regular key - return as is
    return key

@safe_execute()
def process_menu_input(key: str, menu: Menu, selection: int) -> Tuple[bool, int, Any]:
    """
    Process key input for menu navigation.
    
    Args:
        key: Key pressed by user
        menu: Current menu
        selection: Current selection index
        
    Returns:
        Tuple[bool, int, Any]:
            - Whether the menu should exit
            - New selection index
            - Result value if item selected, or None
    """
    logger.debug(f"Processing menu input: {key}")
    
    # Get visible items
    visible_items = menu.get_visible_items()
    total_items = len(visible_items)
    
    # Exit keys
    if key in ('ESC', 'q', 'Q'):
        return True, selection, None
        
    # Selection keys
    elif key in ('ENTER', '\r', '\n', ' '):
        # Get the item
        if 0 <= selection < total_items:
            item = visible_items[selection]
            
            # If it's a category, just toggle expansion
            if isinstance(item, MenuCategory):
                item.expanded = not item.expanded
                return False, selection, None
                
            # If it's a toggle, toggle it
            elif isinstance(item, MenuToggle):
                result = item.toggle()
                return False, selection, None
                
            # Otherwise, execute the item
            else:
                result = item.execute()
                return True, selection, result
                
    # Navigation keys
    elif key in ('DOWN', 'j', 'J'):
        # Move selection down
        return False, min(selection + 1, total_items - 1), None
        
    elif key in ('UP', 'k', 'K'):
        # Move selection up
        return False, max(selection - 1, 0), None
        
    elif key in ('HOME', 'g'):
        # Go to first item
        return False, 0, None
        
    elif key in ('END', 'G'):
        # Go to last item
        return False, total_items - 1, None
        
    elif key in ('PGDN',):
        # Page down (move 10 items)
        return False, min(selection + 10, total_items - 1), None
        
    elif key in ('PGUP',):
        # Page up (move 10 items)
        return False, max(selection - 10, 0), None
    
    # For other keys, no change
    return False, selection, None

@safe_execute()
def get_animation_preferences() -> dict:
    """
    Get user animation preferences from configuration.
    
    Returns:
        dict: Animation settings
    """
    # Get configuration values or use defaults
    return {
        'enabled': get_config_value('animations_enabled', True),
        'speed': get_config_value('animation_speed', 1.0),
        'portal_effects': get_config_value('portal_effects', True),
        'typing_speed': get_config_value('typing_speed', 0.03),
        'transitions': get_config_value('menu_transitions', True)
    }

@safe_execute()
def should_animate() -> bool:
    """
    Check if animations should be displayed.
    
    Returns:
        bool: True if animations are enabled
    """
    # Check configuration and terminal capabilities
    return (get_config_value('animations_enabled', True) and 
            supports_ansi_color() and 
            not get_config_value('disable_all_animations', False))

@safe_execute(default_return=None)
def handle_menu_action(action_item: MenuItem, show_animations: bool = True) -> Any:
    """
    Execute menu action with visual feedback.
    
    Args:
        action_item: MenuItem to execute
        show_animations: Whether to show animations
        
    Returns:
        Any: Result of the action
    """
    logger.debug(f"Handling menu action: {action_item.text}")
    
    # Skip animations if disabled
    if not show_animations or not should_animate():
        return action_item.execute()
    
    # Show spinner while executing
    spinner_stop = create_spinner(f"Executing: {action_item.text}", spinner_type="portal")
    
    try:
        # Execute the action
        result = action_item.execute()
        
        # Stop spinner
        spinner_stop()
        
        # Show success message
        if action_item.text:
            show_message(f"Successfully executed: {action_item.text}", 
                         title="Action Complete", message_type="success")
            
        return result
    except Exception as e:
        # Stop spinner
        spinner_stop()
        
        # Show error message
        error_msg = f"Error executing '{action_item.text}': {str(e)}"
        show_message(error_msg, title="Action Failed", message_type="error")
        
        # Re-raise the exception
        raise

@safe_execute(default_return=None)
def handle_toggle(toggle_item: MenuToggle, show_animations: bool = True) -> bool:
    """
    Toggle a menu item with visual feedback.
    
    Args:
        toggle_item: MenuToggle to toggle
        show_animations: Whether to show animations
        
    Returns:
        bool: New toggle state
    """
    logger.debug(f"Handling menu toggle: {toggle_item.text}")
    
    # Skip animations if disabled
    if not show_animations or not should_animate():
        return toggle_item.toggle()
    
    # Toggle the item with visual feedback
    old_state = toggle_item.state
    new_state = toggle_item.toggle()
    
    # If state changed, show brief feedback
    if old_state != new_state:
        state_text = "ON" if new_state else "OFF"
        color = "green" if new_state else "red"
        
        # Flash brief status (at bottom of terminal to avoid disrupting menu)
        term_width = get_terminal_width()
        message = f"'{toggle_item.text}' is now {state_text}"
        
        # Save cursor position
        sys.stdout.write("\033[s")
        
        # Move to bottom of screen
        sys.stdout.write(f"\033[{get_terminal_height()};0H")
        
        # Print message
        sys.stdout.write(color_text(message.center(term_width), color))
        sys.stdout.flush()
        
        # Wait briefly
        time.sleep(0.5)
        
        # Clear line
        sys.stdout.write("\r" + " " * term_width)
        
        # Restore cursor position
        sys.stdout.write("\033[u")
        sys.stdout.flush()
    
    return new_state

@safe_execute()
def register_menu_with_powerlevel10k() -> bool:
    """
    Register menu system with Powerlevel10k if available.
    
    Returns:
        bool: True if registration was successful
    """
    logger.debug("Attempting to register menu with Powerlevel10k")
    
    # Check if powerlevel10k integration is enabled
    if not get_config_value('powerlevel10k_integration', True):
        logger.debug("Powerlevel10k integration is disabled in config")
        return False
    
    # Define function to be called by Powerlevel10k
    def prompt_rick_menu_segment():
        # This would be called by Powerlevel10k to show menu status
        # Return appropriate format for Powerlevel10k
        menu_enabled = get_config_value('menu_enabled', True)
        
        if menu_enabled:
            return "%F{green}🧪 MENU%f"
        else:
            return ""
    
    # We would need to save this function somewhere accessible to ZSH
    # This is just a placeholder - actual implementation would depend
    # on how Powerlevel10k integration is set up
    
    # For demonstration purposes, we'll just log that it was registered
    logger.info("Menu system registered with Powerlevel10k")
    return True

@safe_execute()
def format_menu_for_p10k(menu_title: str, is_active: bool = True) -> str:
    """
    Format menu information for Powerlevel10k segment.
    
    Args:
        menu_title: Title of the current menu
        is_active: Whether the menu system is active
        
    Returns:
        str: Formatted string for Powerlevel10k
    """
    logger.debug(f"Formatting menu for P10k: {menu_title}")
    
    # Format for Powerlevel10k segment
    if is_active:
        # Active menu - show portal icon and title
        return f"%F{{green}}🧪%f %F{{cyan}}{menu_title}%f"
    else:
        # Inactive menu - just show icon
        return "%F{gray}🧪%f"

# =====================================================================
# Advanced Features
# =====================================================================

@safe_execute()
def create_submenu(parent: Menu, title: str, items: List[MenuItem] = None) -> Menu:
    """
    Create a submenu under a parent menu.
    
    Args:
        parent: Parent menu
        title: Submenu title
        items: List of menu items
        
    Returns:
        Menu: The created submenu
    """
    logger.debug(f"Creating submenu: {title} under {parent.title}")
    
    # Create submenu with parent reference
    submenu = Menu(title=title, items=items or [], parent=parent)
    
    # Inherit width and height from parent
    submenu.width = parent.width
    submenu.height = parent.height
    
    return submenu

@safe_execute()
def navigate_hierarchy(root_menu: Menu) -> Optional[Tuple[Menu, int, Any]]:
    """
    Navigate through menu hierarchy.
    
    Args:
        root_menu: Root menu to start navigation
        
    Returns:
        Optional[Tuple[Menu, int, Any]]:
            - Menu where selection was made
            - Selected index
            - Selected value or None if cancelled
    """
    logger.debug(f"Starting hierarchical navigation from: {root_menu.title}")
    
    # Start with root menu
    current_menu = root_menu
    menu_stack = []
    
    # Show portal open animation for root menu
    animate_portal_open()
    
    while True:
        # Display current menu
        result = navigate_menu(current_menu, 
                              parent_menu=menu_stack[-1] if menu_stack else None)
        
        # Check result
        if result is None:
            # Menu was exited/cancelled
            if not menu_stack:
                # At root menu, exit completely
                animate_portal_close()
                return None
            else:
                # Go back to parent menu
                current_menu = menu_stack.pop()
                continue
                
        if result[0] == -1 and result[1] == "BACK":
            # Explicit "back" navigation
            if menu_stack:
                current_menu = menu_stack.pop()
                continue
            else:
                # At root menu, exit completely
                animate_portal_close()
                return None
                
        # Get selected item
        index, value = result
        selected_item = current_menu.get_item_at_index(index)
        
        # Check if it's a submenu (either old direct Menu format or new typed dict format)
        if isinstance(selected_item, Menu):
            # Direct Menu object - old format (shouldn't happen anymore but keep for backwards compatibility)
            menu_stack.append(current_menu)
            current_menu = selected_item
            continue
        elif isinstance(value, dict) and value.get("type") == "submenu" and "menu" in value:
            # New typed format with menu in a dict
            submenu = value.get("menu")
            if isinstance(submenu, Menu):
                menu_stack.append(current_menu)
                current_menu = submenu
                continue
            else:
                logger.error(f"Invalid submenu object: {submenu}")
                # Skip this invalid item
                continue
            
        # Regular item selection - return result
        animate_portal_close()
        return (current_menu, index, value)

@safe_execute()
def create_hierarchical_menu(title: str, structure: Dict, width: int = None, 
                            height: int = None) -> Menu:
    """
    Create a hierarchical menu from a dictionary structure.
    
    Args:
        title: Root menu title
        structure: Dictionary defining menu structure
        width: Menu width
        height: Menu height
        
    Example structure:
    {
        "General": {  # Category
            "items": [
                {"text": "Option 1", "value": "opt1"},
                {"text": "Option 2", "value": "opt2", "enabled": False}
            ]
        },
        "Advanced": {  # Category
            "items": [
                {"text": "Advanced 1", "value": "adv1"},
                {"text": "Submenu", "submenu": {  # Submenu
                    "items": [
                        {"text": "Sub Option 1", "value": "sub1"}
                    ]
                }}
            ]
        },
        "Toggle Options": {  # Category
            "items": [
                {"text": "Feature 1", "type": "toggle", "key": "feature1", "default": True}
            ]
        }
    }
    
    Returns:
        Menu: Root menu of the hierarchy
    """
    logger.debug(f"Creating hierarchical menu: {title}")
    
    # Create root menu
    root_menu = Menu(title=title, width=width, height=height)
    
    # Process structure
    for category_name, category_data in structure.items():
        # Create category
        category = root_menu.add_category(category_name)
        
        # Add items to category
        for item_data in category_data.get("items", []):
            # Check item type
            item_type = item_data.get("type", "action")
            
            if item_type == "toggle":
                # Toggle item
                toggle = MenuToggle(
                    text=item_data["text"],
                    key=item_data.get("key"),
                    default=item_data.get("default", False),
                    callback=item_data.get("callback"),
                    enabled=item_data.get("enabled", True)
                )
                category.add_item(toggle)
                
            elif "submenu" in item_data:
                # Submenu - recursively create
                submenu_structure = {
                    "items": item_data["submenu"].get("items", [])
                }
                submenu = create_hierarchical_menu(
                    title=item_data["text"],
                    structure={"Items": submenu_structure},
                    width=width,
                    height=height
                )
                submenu.parent = root_menu
                
                # Create a special submenu item with a typed value instead of storing
                # the Menu object directly in value
                item = MenuItem(
                    text=item_data["text"],
                    value={"type": "submenu", "menu": submenu},  # Use a dict with metadata instead of raw Menu
                    enabled=item_data.get("enabled", True),
                    icon=MENU_SYMBOLS["folder"]
                )
                category.add_item(item)
                
            else:
                # Regular action item
                item = MenuItem(
                    text=item_data["text"],
                    value=item_data.get("value"),
                    enabled=item_data.get("enabled", True),
                    callback=item_data.get("callback"),
                    icon=item_data.get("icon")
                )
                category.add_item(item)
    
    return root_menu

@safe_execute()
def save_menu_state(menu: Menu) -> Dict:
    """
    Save current menu state.
    
    Args:
        menu: Menu to save state for
        
    Returns:
        Dict: Saved state
    """
    logger.debug(f"Saving state for menu: {menu.title}")
    
    # Create state dictionary
    state = {
        "title": menu.title,
        "selected_index": menu.selected_index,
        "scroll_offset": menu.scroll_offset,
        "categories": {}
    }
    
    # Save category expansion states
    for i, item in enumerate(menu.items):
        if isinstance(item, MenuCategory):
            state["categories"][i] = {
                "expanded": item.expanded
            }
    
    return state

@safe_execute()
def restore_menu_state(menu: Menu, state: Dict) -> bool:
    """
    Restore saved menu state.
    
    Args:
        menu: Menu to restore state for
        state: Previously saved state
        
    Returns:
        bool: True if state was restored successfully
    """
    logger.debug(f"Restoring state for menu: {menu.title}")
    
    # Verify this is the correct menu
    if state.get("title") != menu.title:
        logger.warning(f"Menu title mismatch: {menu.title} != {state.get('title')}")
        return False
    
    # Restore selection
    if "selected_index" in state:
        menu.selected_index = state["selected_index"]
        
    # Restore scroll offset
    if "scroll_offset" in state:
        menu.scroll_offset = state["scroll_offset"]
    
    # Restore category expansion states
    for i_str, cat_state in state.get("categories", {}).items():
        try:
            i = int(i_str)
            if 0 <= i < len(menu.items) and isinstance(menu.items[i], MenuCategory):
                menu.items[i].expanded = cat_state.get("expanded", False)
        except (ValueError, IndexError):
            continue
    
    return True

@safe_execute()
def create_context_menu(items: List[Union[str, Dict, MenuItem]], x: int = None, 
                      y: int = None, title: str = "Context Menu") -> Optional[Any]:
    """
    Create and display a context menu at specified position.
    
    Args:
        items: List of menu items
        x: X position (uses current cursor position if None)
        y: Y position (uses current cursor position if None)
        title: Menu title
        
    Returns:
        Optional[Any]: Selected value or None if cancelled
    """
    logger.debug(f"Creating context menu: {title} with {len(items)} items")
    
    # Convert items to MenuItems if needed
    menu_items = []
    for item in items:
        if isinstance(item, MenuItem):
            menu_items.append(item)
        elif isinstance(item, dict) and "text" in item:
            if item.get("type") == "toggle":
                # Toggle item
                menu_items.append(MenuToggle(
                    text=item["text"],
                    key=item.get("key"),
                    default=item.get("default", False),
                    callback=item.get("callback"),
                    enabled=item.get("enabled", True)
                ))
            else:
                # Regular item
                menu_items.append(MenuItem(
                    text=item["text"],
                    value=item.get("value", item["text"]),
                    callback=item.get("callback"),
                    enabled=item.get("enabled", True),
                    icon=item.get("icon")
                ))
        else:
            # String item
            menu_items.append(MenuItem(text=str(item), value=item))
    
    # Create menu
    menu = Menu(title=title, items=menu_items)
    
    # Calculate dimensions
    max_item_width = max(len(item.text) for item in menu_items) if menu_items else 20
    width = max(max_item_width + 10, len(title) + 10)
    height = len(menu_items) + 6  # Header + border + padding
    
    # Adjust to fit terminal
    term_width = get_terminal_width()
    term_height = get_terminal_height()
    
    width = min(width, term_width - 4)
    height = min(height, term_height - 4)
    
    menu.width = width
    menu.height = height
    
    # Position menu if coordinates provided
    # This would require custom terminal control that is beyond the scope
    # of this implementation. In a real implementation, we would position
    # the menu using terminal control sequences.
    
    # Display menu
    result = navigate_menu(menu, border_style="portal", with_portal_bg=True)
    
    # Return selected value or None if cancelled
    if result:
        return result[1]  # Return value
    return None

@safe_execute()
def create_wizard(steps: List[Dict], title: str = "Rick's Wizard") -> Optional[Dict]:
    """
    Create a multi-step wizard.
    
    Args:
        steps: List of step definitions
        title: Wizard title
        
    Returns:
        Optional[Dict]: Collected data or None if cancelled
    
    Example step:
    {
        "title": "Step 1: Basic Information",
        "fields": [
            {"name": "username", "prompt": "Enter your username", "default": "morty"},
            {"name": "enable_portal", "type": "toggle", "prompt": "Enable portal gun", "default": True}
        ],
        "text": "Welcome to the first step of the wizard."
    }
    """
    logger.debug(f"Creating wizard: {title} with {len(steps)} steps")
    
    # Initialize result dictionary
    result = {}
    
    # Show wizard
    animate_portal_open()
    
    # Process each step
    for i, step in enumerate(steps):
        # Format step title
        step_title = f"{title} - {step['title']} ({i+1}/{len(steps)})"
        
        # Show step intro if provided
        if "text" in step:
            show_message(step["text"], title=step_title, with_animation=True)
        
        # Process fields for this step
        for field in step.get("fields", []):
            field_name = field["name"]
            field_prompt = field.get("prompt", field_name)
            field_type = field.get("type", "input")
            field_default = field.get("default")
            
            # Add Rick's touch to the prompt
            if random.random() < 0.3 and "*burp*" not in field_prompt:
                parts = field_prompt.split()
                burp_index = random.randint(1, len(parts) - 1)
                parts.insert(burp_index, "*burp*")
                field_prompt = " ".join(parts)
            
            # Get input based on field type
            if field_type == "toggle":
                # Toggle field
                result[field_name] = confirm_action(field_prompt, default=field_default)
                
            elif field_type == "selection":
                # Selection from options
                options = field.get("options", [])
                if not options:
                    continue
                    
                # Convert options to proper format
                menu_items = []
                for opt in options:
                    if isinstance(opt, dict) and "text" in opt:
                        menu_items.append(MenuItem(
                            text=opt["text"],
                            value=opt.get("value", opt["text"]),
                            enabled=opt.get("enabled", True)
                        ))
                    else:
                        menu_items.append(MenuItem(text=str(opt), value=opt))
                
                # Create selection menu
                menu = Menu(title=field_prompt, items=menu_items)
                
                # Set default if provided
                if field_default is not None:
                    for i, item in enumerate(menu_items):
                        if item.value == field_default:
                            menu.selected_index = i
                            break
                
                # Display menu
                select_result = navigate_menu(menu)
                
                if select_result:
                    result[field_name] = select_result[1]  # Get value
                else:
                    # Selection cancelled
                    animate_portal_close()
                    return None
            
            else:
                # Regular input field
                value = get_input(prompt=field_prompt, default=field_default)
                
                if value is None:
                    # Input cancelled
                    animate_portal_close()
                    return None
                    
                result[field_name] = value
        
        # Show progress
        progress = (i + 1) / len(steps)
        progress_bar = "[" + "█" * int(20 * progress) + "░" * (20 - int(20 * progress)) + "]"
        
        # Show confirmation for this step
        if i < len(steps) - 1:  # Not the last step
            if not confirm_action(f"Step {i+1} complete! {progress_bar} Continue to next step?", default=True):
                animate_portal_close()
                return None
    
    # Show completion message
    completion_message = "Wizard completed! Here's what you entered:\n\n"
    
    for key, value in result.items():
        completion_message += f"• {key}: {value}\n"
        
    show_message(completion_message, title=f"{title} - Complete", message_type="success")
    
    # Close wizard
    animate_portal_close()
    
    return result

# =====================================================================
# Testing & Example Usage
# =====================================================================

@safe_execute()
def run_test_menu():
    """
    Run a test menu to demonstrate functionality.
    
    This function is for development and testing purposes.
    """
    # Create a test menu structure
    menu_structure = {
        "General Options": {
            "items": [
                {"text": "Show Information", "value": "info"},
                {"text": "Run Diagnostics", "value": "diag"},
                {"text": "Check System Status", "value": "status"}
            ]
        },
        "Portal Settings": {
            "items": [
                {"text": "Enable Portal Gun", "type": "toggle", "key": "portal_enabled", "default": True},
                {"text": "Set Portal Destination", "value": "set_dest"},
                {"text": "Advanced Settings", "submenu": {
                    "items": [
                        {"text": "Power Level", "value": "power"},
                        {"text": "Portal Fluid", "value": "fluid"},
                        {"text": "Dimensional Calibration", "value": "calibration"}
                    ]
                }}
            ]
        },
        "About": {
            "items": [
                {"text": "Version Information", "value": "version"},
                {"text": "License", "value": "license"},
                {"text": "Exit", "value": "exit"}
            ]
        }
    }
    
    # Create the menu
    main_menu = create_hierarchical_menu(
        title="Rick's Portal Menu System",
        structure=menu_structure
    )
    
    # Navigate the menu
    result = navigate_hierarchy(main_menu)
    
    # Show result
    if result:
        menu, index, value = result
        print(f"\nSelected: {value} from {menu.title}")
    else:
        print("\nMenu cancelled")

@safe_execute()
def display_static_portal_open() -> None:
    """
    Display a static open portal image, properly centered in the terminal.
    Used when animations are disabled or static portal is enabled.
    """
    clear_screen()
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Select the appropriate portal art
    portal_art = STATIC_PORTAL_ART_OPEN.strip().split('\n')
    
    # Center each line of the portal art
    centered_portal = []
    for line in portal_art:
        centered_line = line.center(width)
        centered_portal.append(centered_line)
    
    # Print the centered portal art with proper spacing
    print("\n" * 2)  # Add some spacing at the top
    for line in centered_portal:
        print(line)
    print("\n" * 2)  # Add some spacing at the bottom

@safe_execute()
def display_static_portal_closed() -> None:
    """
    Display a static closed portal image, properly centered in the terminal.
    Used when animations are disabled or static portal is enabled.
    """
    clear_screen()
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Select the appropriate portal art
    portal_art = STATIC_PORTAL_ART_CLOSED.strip().split('\n')
    
    # Center each line of the portal art
    centered_portal = []
    for line in portal_art:
        centered_line = line.center(width)
        centered_portal.append(centered_line)
    
    # Print the centered portal art with proper spacing
    print("\n" * 2)  # Add some spacing at the top
    for line in centered_portal:
        print(line)
    print("\n" * 2)  # Add some spacing at the bottom

# =====================================================================
# Module Exports
# =====================================================================

__all__ = [
    # Core menu classes
    'Menu',
    'MenuItem',
    'MenuCategory',
    'MenuAction',
    'MenuToggle',
    
    # Basic menu functions
    'display_menu',
    'navigate_menu',
    'get_selection',
    'show_message',
    'confirm_action',
    'show_progress',
    
    # Animation functions
    'animate_portal_open',
    'animate_portal_close',
    'animate_transition',
    'animate_item_selection',
    'animate_typing',
    'create_spinner',
    
    # Visual elements
    'create_menu_border',
    'create_portal_background',
    'create_menu_header',
    'create_menu_footer',
    'highlight_selection',
    'highlight_category',
    
    # Integration functions
    'get_menu_key',
    'process_menu_input',
    'get_animation_preferences',
    'should_animate',
    'handle_menu_action',
    'handle_toggle',
    
    # Advanced features
    'create_submenu',
    'navigate_hierarchy',
    'create_hierarchical_menu',
    'save_menu_state',
    'restore_menu_state',
    'create_context_menu',
    'create_wizard',
    
    # Test function
    'run_test_menu'
]

# If this module is run directly, execute test function
if __name__ == "__main__":
    run_test_menu()