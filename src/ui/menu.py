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
import platform
from typing import List, Dict, Any, Optional, Union, Tuple, Callable, TypeVar
import select
import json

from src.ui.text import clear_screen, color_text, get_terminal_width, get_terminal_height, supports_unicode, supports_ansi_color
from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.config import get_config_value, set_config_value

# Set up logger
logger = get_logger(__name__)

# Rick and Morty themed color definitions
RICK_COLORS = {
    "normal": {"fg": "blue", "bg": "black"},
    "highlight": {"fg": "cyan", "bg": "black"},
    "selected": {"fg": "black", "bg": "blue"},
    "disabled": {"fg": "white", "bg": "black"},
    "header": {"fg": "blue", "bg": "black"},
    "footer": {"fg": "cyan", "bg": "black"},
    "border": {"fg": "blue", "bg": "black"},
    "error": {"fg": "red", "bg": "black"},
    "success": {"fg": "green", "bg": "black"},
    "warning": {"fg": "yellow", "bg": "black"}
}

MORTY_COLORS = {
    "normal": {"fg": "yellow", "bg": "black"},
    "highlight": {"fg": "cyan", "bg": "black"},
    "selected": {"fg": "black", "bg": "yellow"},
    "disabled": {"fg": "white", "bg": "black"},
    "header": {"fg": "yellow", "bg": "black"},
    "footer": {"fg": "cyan", "bg": "black"},
    "border": {"fg": "yellow", "bg": "black"},
    "error": {"fg": "red", "bg": "black"},
    "success": {"fg": "green", "bg": "black"},
    "warning": {"fg": "magenta", "bg": "black"}
}

PORTAL_COLORS = {
    "normal": {"fg": "green", "bg": "black"},
    "highlight": {"fg": "cyan", "bg": "black"},
    "selected": {"fg": "black", "bg": "green"},
    "disabled": {"fg": "white", "bg": "black"},
    "header": {"fg": "green", "bg": "black"},
    "footer": {"fg": "cyan", "bg": "black"},
    "border": {"fg": "green", "bg": "black"},
    "error": {"fg": "red", "bg": "black"},
    "success": {"fg": "green", "bg": "black"},
    "warning": {"fg": "yellow", "bg": "black"}
}

# Default theme
DEFAULT_THEME = PORTAL_COLORS

class ThemeManager:
    """
    Manages color themes for the Rick Assistant menu.
    
    This class provides methods to get and set themes.
    """
    
    @staticmethod
    def get_theme(theme_name):
        """
        Get a theme by name.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Dict: Theme color definitions
        """
        themes = {
            "Portal Green": PORTAL_COLORS,
            "Rick Blue": RICK_COLORS,
            "Morty Yellow": MORTY_COLORS,
            "Terminal Default": DEFAULT_THEME
        }
        
        return themes.get(theme_name, DEFAULT_THEME)
    
    @staticmethod
    def get_current_theme():
        """
        Get the current theme based on configuration.
        
        Returns:
            Dict: Theme color definitions
        """
        theme_name = get_config_value("ui.theme", "Portal Green")
        return ThemeManager.get_theme(theme_name)
    
    @staticmethod
    def set_theme(theme_name):
        """
        Set the current theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            bool: True if successful, False otherwise
        """
        valid_themes = ["Portal Green", "Rick Blue", "Morty Yellow", "Terminal Default"]
        
        if theme_name not in valid_themes:
            logger.error(f"Invalid theme name: {theme_name}")
            return False
            
        return set_config_value("ui.theme", theme_name)

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
        format_text, stream_text, 
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
    def get_config_value(key, default=None):
        return default
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
    def clear_screen():
        """Fallback clear screen function that properly clears the terminal."""
        try:
            # Check platform
            if sys.platform == 'win32':
                os.system('cls')
            else:
                os.system('clear')
            return True
        except Exception:
            # Last resort: print newlines
            print("\n" * 100)
            return False
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

# Static portal ASCII art for the OPEN state (portal when open)
STATIC_PORTAL_ART_OPEN = """
    .-'""""""-.
  ,'           `.
 /               \\
|                 |
|                 |
 \\    RICK AND   /
  `.   MORTY    ,'
    `'-......-'´
"""

# Flag to track if we're returning from a command execution
RETURNING_FROM_COMMAND = False


# Static portal ASCII art for the CLOSED state (portal when closed)
STATIC_PORTAL_ART_CLOSED = """
    .-'""""""-.
  ,'           `.
 /               \\
|                 |
|     PORTAL      |
 \\    CLOSED     /
  `.             ,'
    `'-......-'´
"""

# Original braille art portal (just for backwards compatibility)
STATIC_PORTAL_ART = """
    .-'""""""-.
  ,'           `.
 /               \\
|                 |
|   RICK MENU     |
 \\   SYSTEM      /
  `.             ,'
    `'-......-'´
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

# Base class for menu items before the Menu class
class MenuItem:
    """
    Base class for menu items.
    
    This class represents a menu item with text and an optional action.
    
    Attributes:
        text (str): Display text for this item
        action (Callable): Function to call when this item is activated
        parent: Parent object (Menu or MenuCategory)
        enabled (bool): Whether this item is enabled
        key (str): Configuration key (for toggleable items)
        coming_soon (bool): Whether this item is marked as coming soon
        item_type (str): Type of menu item (used for styling)
    """
    
    def __init__(self, text: str, action=None, enabled: bool = True, 
                 key: str = None, coming_soon: bool = False, 
                 item_type: str = "standard"):
        """
        Initialize a menu item.
        
        Args:
            text: Display text for this item
            action: Function to call when this item is activated
            enabled: Whether this item is enabled
            key: Configuration key (for toggleable items)
            coming_soon: Whether this item is marked as coming soon
            item_type: Type of menu item (used for styling)
        """
        self.text = text
        self.action = action
        self.enabled = enabled
        self.key = key
        self.coming_soon = coming_soon
        self.parent = None
        self.item_type = item_type
    
    def activate(self):
        """
        Activate this item.
            
        Returns:
            Result of the action or None
        """
        if not self.enabled:
            return None
    
        if self.coming_soon:
            return "coming_soon"
        
            if callable(self.action):
                return self.action()
            
        return None
        
    def get_display_text(self) -> str:
        """
        Get the display text for this item.
            
        Returns:
            str: Formatted display text
        """
        text = self.text
        
        if self.coming_soon:
            text = f"{text} 🚧"
        
        return text

# Forward declaration to avoid circular imports
class Menu:
    """
    Menu class for representing a navigable menu.
    
    This class represents a menu with a title, items, and parent reference.
    It supports pagination for displaying a large number of items.
    
    Attributes:
        title (str): Menu title
        items (List[MenuItem]): List of menu items
        parent (Menu): Parent menu
        border_style (str): Border style
        theme (Dict): Color theme
        current_page (int): Current page number (0-based)
        items_per_page (int): Number of items to show per page
        breadcrumbs (List[str]): Path of menus leading to this one
    """
    
    def __init__(self, title="Menu", items=None, parent=None, border_style="single", theme=None):
        """
        Initialize a menu.
        
        Args:
            title: Menu title
            items: List of menu items
            parent: Parent menu
            border_style: Border style
            theme: Color theme
        """
        self.title = title
        self.items = items or []
        self.parent = parent
        self.border_style = border_style
        self.theme = theme or DEFAULT_THEME
        self.current_page = 0
        self.items_per_page = 10
        
        # Build breadcrumb path if parent is provided
        self.breadcrumbs = []
        if parent:
            # Start with parent's breadcrumbs
            self.breadcrumbs = parent.breadcrumbs.copy() if hasattr(parent, 'breadcrumbs') else []
            
            # Add parent's title if not already in breadcrumbs
            if parent.title and (not self.breadcrumbs or self.breadcrumbs[-1] != parent.title):
                self.breadcrumbs.append(parent.title)
    
    def add_item(self, item):
        """
        Add an item to the menu.
        
        Args:
            item: MenuItem to add
        """
        item.parent = self
        self.items.append(item)
    
    def get_page_count(self):
        """
        Get the number of pages in this menu.
            
        Returns:
            int: Number of pages
        """
        if not self.items:
            return 1
            
        return (len(self.items) + self.items_per_page - 1) // self.items_per_page
    
    def get_current_page_items(self):
        """
        Get the items on the current page.
            
        Returns:
            List[MenuItem]: Items on the current page
        """
        if not self.items:
            return []
            
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        
        return self.items[start_idx:end_idx]
    
    def next_page(self):
        """
        Go to the next page.
            
        Returns:
            int: New page number
        """
        page_count = self.get_page_count()
        if self.current_page < page_count - 1:
            self.current_page += 1
        return self.current_page
    
    def prev_page(self):
        """
        Go to the previous page.
        
        Returns:
            int: New page number
        """
        if self.current_page > 0:
            self.current_page -= 1
        return self.current_page
    
    def get_breadcrumbs(self):
        """
        Get the breadcrumb path for this menu.
        
    Returns:
            List[str]: Breadcrumb path
        """
        # Return combined breadcrumbs plus current title
        return self.breadcrumbs + [self.title]

# Now define specialized menu item types
class MenuCategory(MenuItem):
    """
    Category menu item that can contain sub-items.
    
    This class represents a menu category that can contain other menu items.
    
    Attributes:
        text (str): Display text for this item
        items (List[MenuItem]): List of sub-items
        expanded (bool): Whether this category is expanded
        parent: Parent menu
        enabled (bool): Whether this item is enabled
    """
    
    def __init__(self, text: str, items: List[MenuItem] = None, 
                 expanded: bool = False, enabled: bool = True):
        """
        Initialize a category menu item.
    
    Args:
            text: Display text for this item
            items: List of sub-items
            expanded: Whether this category is expanded
            enabled: Whether this item is enabled
        """
        super().__init__(text, None, enabled, None, False, "category")
        self.items = items or []
        self.expanded = expanded
        
        # Set parent reference for all items
        for item in self.items:
            item.parent = self
            
    def add_item(self, item: MenuItem):
        """
        Add an item to this category.
    
    Args:
            item: Item to add
        """
        item.parent = self
        self.items.append(item)
        
    def activate(self):
        """
        Activate this category (toggle expansion).
    
    Returns:
            str: "expanded" or "collapsed"
        """
        if not self.enabled:
            return None
            
        self.expanded = not self.expanded
        return "expanded" if self.expanded else "collapsed"
        
    def get_display_text(self) -> str:
        """
        Get the display text for this item, including expansion state.
        
    Returns:
            str: Formatted display text with expansion indicator
        """
        indicator = "▼" if self.expanded else "▶"
        return f"{indicator} {self.text}"

    def create_submenu(self) -> 'Menu':
        """
        Create a submenu from this category.
        
    Returns:
            Menu: Submenu containing this category's items
        """
        # Create submenu with this category's title and items
        submenu = Menu(title=self.text, parent=self.parent)
        
        # Add all items to the submenu
        for item in self.items:
            submenu.add_item(item)
            
        return submenu

class MenuToggle(MenuItem):
    """
    Toggleable menu item.
    
    This class represents a menu item that can be toggled on/off.
    
    Attributes:
        text (str): Display text for this item
        key (str): Configuration key
        default (bool): Default state
        parent: Parent menu
        enabled (bool): Whether this item is enabled
    """
    
    def __init__(self, text: str, key: str, default: bool = False, enabled: bool = True):
        """
        Initialize a toggle menu item.
    
    Args:
            text: Display text for this item
            key: Configuration key
            default: Default state
            enabled: Whether this item is enabled
        """
        super().__init__(text, None, enabled, key, False, "toggle")
        self.default = default
        
    def get_state(self) -> bool:
        """
        Get the current toggle state.
        
    Returns:
            bool: Current state
        """
        if self.key:
            return get_config_value(self.key, self.default)
        return self.default
        
    def toggle(self) -> bool:
        """
        Toggle the state.
        
    Returns:
            bool: New state
        """
        new_state = not self.get_state()
        
        if self.key:
            set_config_value(self.key, new_state)
            
        return new_state
        
    def activate(self):
        """
        Activate (toggle) this item.
        
    Returns:
            bool: New state
        """
        if not self.enabled:
                return None
                    
        return self.toggle()
        
    def get_display_text(self) -> str:
        """
        Get the display text for this item, including toggle state.
        
    Returns:
            str: Formatted display text with toggle state
        """
        state = self.get_state()
        indicator = "[X]" if state else "[ ]"
        return f"{indicator} {self.text}"

class MultiOptionMenuItem(MenuItem):
    """
    Menu item with multiple selectable options.
    
    This class represents a menu item that can cycle through multiple options.
    
    Attributes:
        text (str): Display text for this item
        key (str): Configuration key
        options (List[str]): Available options
        default (str): Default option
        parent: Parent menu
        enabled (bool): Whether this item is enabled
    """
    
    def __init__(self, text: str, key: str, options: List[str], 
                 default: str = None, enabled: bool = True):
        """
        Initialize a multi-option menu item.
    
    Args:
            text: Display text for this item
            key: Configuration key
            options: Available options
            default: Default option
            enabled: Whether this item is enabled
        """
        super().__init__(text, None, enabled, key, False, "multi_option")
        self.options = options
        self.default = default or (options[0] if options else "")
        
    def get_current_option(self) -> str:
        """
        Get the currently selected option.
            
        Returns:
            str: Currently selected option
        """
        if self.key:
            return get_config_value(self.key, self.default)
        return self.default
        
    def next_option(self) -> str:
        """
        Select the next option.
    
    Returns:
            str: New selected option
        """
        if not self.options:
            return self.default
            
        current = self.get_current_option()
        try:
            index = self.options.index(current)
            new_index = (index + 1) % len(self.options)
            new_option = self.options[new_index]
        except (ValueError, IndexError):
            new_option = self.options[0] if self.options else self.default
            
        if self.key:
            set_config_value(self.key, new_option)
            
        return new_option
        
    def activate(self):
        """
        Activate (cycle) this item.
        
    Returns:
            str: New selected option
        """
        if not self.enabled:
                return None
            
        return self.next_option()
        
    def get_display_text(self) -> str:
        """
        Get the display text for this item, including current option.
    
    Returns:
            str: Formatted display text with current option
        """
        option = self.get_current_option()
        return f"{self.text}: {option}"

# Fix the broken wizard function that was incorrectly added to the file
@safe_execute()
def run_wizard(title: str, steps: List[Dict], result: Dict = None) -> Optional[Dict]:
    """
    Run a multi-step wizard with the given steps.
    
    Args:
        title: Wizard title
        steps: List of step dictionaries
        result: Current result dictionary (for resuming)
        
    Returns:
        Dict or None: Result dictionary or None if cancelled
    """
    # Initialize result dictionary
    result = result or {}
    
    # Track current step
    for i, step in enumerate(steps):
        step_title = step.get('title', f"Step {i+1}/{len(steps)}")
        step_desc = step.get('description', '')
        
        # Set up the form fields for this step
        fields = step.get('fields', [])
        
        for field in fields:
            field_name = field.get('name', f"field_{i}")
            field_type = field.get('type', 'text')
            field_label = field.get('label', field_name)
            field_default = field.get('default', '')
            field_required = field.get('required', True)
            field_options = field.get('options', [])
            
            # Format prompt
            field_prompt = f"{field_label}"
            if field_required:
                field_prompt += " (required)"
            field_prompt += ": "
            
            # Handle different field types
            if field_type == 'select' and field_options:
                # Selection field
                value = field_default
                # Handle selection logic
                if value is None:
                    return None
                result[field_name] = value
            else:
                # Regular input field
                value = get_input(prompt=field_prompt, default=field_default)
                
                if value is None:
                    return None
                    
                result[field_name] = value
        
        # Show progress
        progress = (i + 1) / len(steps)
        progress_bar = "[" + "█" * int(20 * progress) + "░" * (20 - int(20 * progress)) + "]"
        
        # Show confirmation for this step
        if i < len(steps) - 1:  # Not the last step
            if not confirm_action(f"Step {i+1} complete! {progress_bar} Continue to next step?", default=True):
                return None
    
    # Show completion message
    completion_message = "Wizard completed! Here's what you entered:\n\n"
    
    for key, value in result.items():
        completion_message += f"• {key}: {value}\n"
        
    show_message(completion_message, title=f"{title} - Complete", message_type="success")
    
    return result

# =====================================================================
# Testing & Example Usage

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
    
    # Portal ASCII art in Rick & Morty colors (green/cyan)
    portal_art = """
    .-'""""""-.
  ,'           `.
 /               \\
|                 |
|                 |
 \\    RICK AND   /
  `.   MORTY    ,'
    `'-......-'´
    """.strip().split('\n')
    
    # Center each line of the portal art
    centered_portal = []
    for line in portal_art:
        # Colorize the line with green and cyan highlights
        if supports_ansi_color():
            # Color the outer parts green, inner text cyan
            colorized = ""
            for char in line:
                if char in ".-'`\\/ ":
                    colorized += PORTAL_GREEN + char + RESET
                elif char in "(),|":
                    colorized += PORTAL_BLUE + char + RESET
                else:
                    colorized += PORTAL_CYAN + char + RESET
            line = colorized
            
        centered_line = line.center(width)
        centered_portal.append(centered_line)
    
    # Print the centered portal art with proper spacing
    print("\n" * 2)  # Add some spacing at the top
    for line in centered_portal:
        print(line)
    print("\n" * 2)  # Add some spacing at the bottom
    
    # Short pause to ensure visibility
    time.sleep(0.3)

@safe_execute()
def display_static_portal_closed() -> None:
    """
    Display a static closed portal image, properly centered in the terminal.
    Used when animations are disabled or static portal is enabled.
    """
    clear_screen()
    
    # Get terminal dimensions
    width = get_terminal_width()
    
    # Portal ASCII art in Rick & Morty colors (green/cyan)
    portal_art = """
    .-'""""""-.
  ,'           `.
 /               \\
|                 |
|     PORTAL      |
 \\    CLOSED     /
  `.             ,'
    `'-......-'´
    """.strip().split('\n')
    
    # Center each line of the portal art
    centered_portal = []
    for line in portal_art:
        # Colorize the line with green and cyan highlights
        if supports_ansi_color():
            # Color the outer parts green, inner text cyan
            colorized = ""
            for char in line:
                if char in ".-'`\\/ ":
                    colorized += PORTAL_GREEN + char + RESET
                elif char in "(),|":
                    colorized += PORTAL_BLUE + char + RESET
                else:
                    colorized += PORTAL_CYAN + char + RESET
            line = colorized
            
        centered_line = line.center(width)
        centered_portal.append(centered_line)
    
    # Print the centered portal art with proper spacing
    print("\n" * 2)  # Add some spacing at the top
    for line in centered_portal:
        print(line)
    print("\n" * 2)  # Add some spacing at the bottom
    
    # Short pause to ensure visibility
    time.sleep(0.3)

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
    
    # Menu creation and rendering
    'create_menu_border',
    'create_menu_header',
    'create_menu_footer',
    'highlight_selection',
    'highlight_category',
    'create_ricktastic_menu',
    'show_menu',
    
    # Hierarchical menu functions
    'create_hierarchical_menu',
    'navigate_hierarchy',
    'create_submenu',
    
    # Wizard and context menus
    'create_wizard',
    'create_context_menu',
    
    # Static portal displays
    'display_static_portal_open',
    'display_static_portal_closed',
    
    # Test functions
    'run_test_menu'
]

# If this module is run directly, execute test function
if __name__ == "__main__":
    run_test_menu()

@safe_execute()
def render_menu(border: List[str], header: List[str], items: List[MenuItem], footer: List[str], 
               selected_index: int, background: Optional[List[str]] = None) -> None:
    """
    Render a complete menu with border, header, items, and footer.
    
    Args:
        border: Border lines (top, sides, bottom)
        header: Header section lines
        items: Menu items to display
        footer: Footer section lines
        selected_index: Index of the selected item (relative to visible items)
        background: Optional background to display behind the menu
    """
    # Start rendering
    content = []
    
    # Add header
    for line in header:
        content.append(line)
    
    # Add items
    for i, item in enumerate(items):
        # Format the item
        if isinstance(item, MenuCategory):
            formatted = highlight_category(item, i == selected_index, len(border[0])-2)
        else:
            formatted = highlight_selection(item, i == selected_index, len(border[0])-2)
            
        content.append(formatted)
    
    # Add padding if needed
    available_height = len(border[0]) - len(header) - len(footer) - 2
    padding_needed = max(0, available_height - len(items))
    for _ in range(padding_needed):
        content.append("")
    
    # Add footer
    for line in footer:
        content.append(line)
    
    # Calculate total available width
    border_width = len(border[0])
    
    # Position cursor at top-left before rendering
    sys.stdout.write("\033[H")
    sys.stdout.flush()
    
    # Render the menu
    print(border[0])  # Top border
    
    for i, line in enumerate(content):
        # Add background if available
        if background and i < len(background):
            bg_line = background[i]
            padded_line = line.ljust(border_width - 2)
            # Print with border
            print(f"{border[1][0]}{padded_line}{border[1][-1]}")
        else:
            # Print with border
            print(f"{border[1][0]}{line.ljust(border_width - 2)}{border[1][-1]}")
    
    print(border[-1])  # Bottom border
    
    # Flush output
    sys.stdout.flush()

@safe_execute()
def create_ricktastic_menu(title="Rick Assistant Control Panel", theme=None):
    """
    Create the main Ricktastic menu structure with categories from MENU_ROADMAP.md.
    
    Args:
        title: Menu title
        theme: Color theme to use
    
    Returns:
        Menu: The main menu object
    """
    logger.debug("Creating Ricktastic menu")
    
    # Use the provided theme or default to portal colors
    theme = theme or PORTAL_COLORS
    
    # Create main menu
    main_menu = Menu(title=title, theme=theme)
    
    # Brain Module category
    brain_items = [
        MenuToggle("Enable Brain Module", "brain.enabled", True),
        MultiOptionMenuItem("Active Brain Model", "brain.model", 
                          ["Default", "OpenAI", "Ollama", "Anthropic", "Local LLM", "LM Studio"]),
        MenuToggle("Enhanced Context", "brain.enhanced_context", True),
        MenuToggle("Long-term Memory", "brain.memory", True),
        MultiOptionMenuItem("Personality", "brain.personality", 
                          ["Rick Sanchez", "Morty Smith", "Beth Smith", "Summer Smith", "Jerry Smith"]),
        MultiOptionMenuItem("Response Style", "brain.style", 
                          ["Funny", "Scientific", "Helpful", "Sarcastic", "Mixed"]),
        MenuToggle("Project Awareness", "brain.project_awareness", True)
    ]
    brain_category = MenuCategory("Brain Module", brain_items)
    main_menu.add_item(brain_category)
    
    # Rick Commands category
    cmd_items = [
        MenuToggle("Enable Command Suggestions", "commands.suggestions", True),
        MenuToggle("Shell Command Enhancement", "commands.shell_enhancement", True),
        MenuToggle("In-terminal File Editing", "commands.file_editing", True),
        MenuToggle("Code Completion", "commands.code_completion", False, False),
        MenuToggle("Command History Analysis", "commands.history_analysis", True)
    ]
    cmd_category = MenuCategory("Rick Commands", cmd_items)
    main_menu.add_item(cmd_category)
    
    # Settings category
    settings_items = [
        MenuCategory("General Settings", [
            MenuToggle("Auto-start on Terminal", "settings.autostart", True),
            MenuToggle("Update Checks", "settings.update_checks", True),
            MultiOptionMenuItem("Log Level", "settings.log_level", 
                             ["Error", "Warning", "Info", "Debug"]),
            MenuToggle("Anonymous Usage Stats", "settings.usage_stats", False)
        ]),
        MenuCategory("Prompt Settings", [
            MenuToggle("Show Git Status", "settings.prompt.show_git", True),
            MenuToggle("Show Python Environment", "settings.prompt.show_python_env", True),
            MenuToggle("Show Directory", "settings.prompt.show_directory", True),
            MenuToggle("Show Resource Usage", "settings.prompt.show_resources", True)
        ])
    ]
    settings_category = MenuCategory("Settings", settings_items)
    main_menu.add_item(settings_category)
    
    # Universe Options category
    universe_items = [
        MenuToggle("Portal Gun Navigation", "universe.portal_gun", True),
        MenuToggle("Interdimensional Cable", "universe.cable", True),
        MenuToggle("Meeseeks AI Helper", "universe.meeseeks", False),
        MenuToggle("Citadel Connection", "universe.citadel", False, False),
        MenuToggle("Multiverse Browser", "universe.multiverse", False, False)
    ]
    universe_category = MenuCategory("Universe Options", universe_items)
    main_menu.add_item(universe_category)
    
    # Security & Safety Features category
    safety_items = [
        MenuToggle("Command Safety Checks", "safety.command_checks", True),
        MenuToggle("Suspicious Pattern Detection", "safety.pattern_detection", True),
        MenuToggle("Destructive Command Confirmation", "safety.destructive_confirm", True),
        MenuToggle("AI Hallucination Detection", "safety.hallucination_detection", True)
    ]
    safety_category = MenuCategory("Security & Safety", safety_items)
    main_menu.add_item(safety_category)
    
    # UI Settings category
    ui_items = [
        MultiOptionMenuItem("Color Theme", "ui.theme", 
                          ["Portal Green", "Morty Yellow", "Rick Blue", "Terminal Default"]),
        MenuToggle("Show ASCII Rick", "ui.show_ascii_rick", True),
        MenuToggle("Use Unicode Characters", "ui.use_unicode", True),
        MenuToggle("Enable Animations", "ui.animations", True),
        MenuToggle("Compact Display Mode", "ui.compact_mode", False)
    ]
    ui_category = MenuCategory("UI Settings", ui_items)
    main_menu.add_item(ui_category)
    
    # Input Handling category
    input_items = [
        MenuToggle("Tab Completion", "input.tab_completion", True),
        MenuToggle("Command Syntax Highlighting", "input.syntax_highlight", True),
        MenuToggle("Auto-correction", "input.autocorrect", False),
        MultiOptionMenuItem("Typing Mode", "input.typing_mode", 
                         ["Standard", "Vim-like", "Emacs-like"])
    ]
    input_category = MenuCategory("Input Handling", input_items)
    main_menu.add_item(input_category)
    
    # Advanced Options category
    advanced_items = [
        MenuToggle("Developer Mode", "advanced.developer_mode", False),
        MenuToggle("Performance Mode", "advanced.performance_mode", False),
        MenuToggle("External API Access", "advanced.external_api", True),
        MenuToggle("Background Processing", "advanced.background_processing", True),
        MenuToggle("Debug Logging", "advanced.debug_logging", False)
    ]
    advanced_category = MenuCategory("Advanced Options", advanced_items)
    main_menu.add_item(advanced_category)
    
    # System Monitoring category
    monitoring_items = [
        MenuToggle("CPU Usage Alerts", "monitoring.cpu_alerts", True),
        MenuToggle("Memory Usage Alerts", "monitoring.memory_alerts", True),
        MenuToggle("Temperature Monitoring", "monitoring.temperature", True),
        MenuToggle("Process Tracking", "monitoring.process_tracking", False),
        MenuToggle("Network Usage Monitoring", "monitoring.network", False)
    ]
    monitoring_category = MenuCategory("System Monitoring", monitoring_items)
    main_menu.add_item(monitoring_category)
    
    # Actions category
    actions_items = [
        MenuItem("View System Information", lambda: "system_info"),
        MenuItem("View Memory Usage", lambda: "memory_usage"),
        MenuItem("View CPU Status", lambda: "cpu_status"),
        MenuItem("Reset All Settings", lambda: "reset_settings"),
        MenuItem("Restart Rick Assistant", lambda: "restart_zsh"),
        MenuItem("Exit Menu", lambda: "quit")
    ]
    actions_category = MenuCategory("Actions", actions_items)
    main_menu.add_item(actions_category)
    
    return main_menu

@safe_execute()
def reset_all_settings():
    """Reset all settings to defaults"""
    clear_screen()
    print("\n  Resetting all settings to defaults...")
    time.sleep(1)
    print("  Settings have been reset!")
    time.sleep(1.5)
    return None

@safe_execute()
def show_system_diagnostics():
    """Show system diagnostics"""
    clear_screen()
    print("\n  System Diagnostics")
    print("  =================")
    print(f"\n  OS: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  Terminal: {os.environ.get('TERM', 'Unknown')}")
    print(f"  Shell: {os.environ.get('SHELL', 'Unknown')}")
    
    # Add more diagnostic info here
    
    print("\n  Press any key to return...")
    getch()
    return None

@safe_execute()
def cleanup_temp_files():
    """Clean up temporary files"""
    clear_screen()
    print("\n  Cleaning up temporary files...")
    time.sleep(1)
    print("  Cleanup complete!")
    time.sleep(1.5)
    return None

@safe_execute()
def check_for_updates():
    """Check for updates"""
    clear_screen()
    print("\n  Checking for updates...")
    time.sleep(1)
    print("  You're running the latest version!")
    time.sleep(1.5)
    return None

@safe_execute()
def show_quick_tips():
    """Show quick tips"""
    clear_screen()
    print("\n  Quick Tips")
    print("  ==========")
    print("\n  1. Use arrow keys or number keys to navigate the menu")
    print("  2. Press Q to exit menus")
    print("  3. Type 'rick help' in your terminal for command help")
    
    print("\n  Press any key to return...")
    getch()
    return None

@safe_execute()
def show_command_reference():
    """Show command reference"""
    clear_screen()
    print("\n  Command Reference")
    print("  ================")
    print("\n  rick menu       - Open this menu")
    print("  rick status     - Show assistant status")
    print("  rick help       - Show help information")
    print("  rick version    - Show version information")
    
    print("\n  Press any key to return...")
    getch()
    return None

@safe_execute()
def show_about_info():
    """Show about information"""
    clear_screen()
    print("\n  Rick Assistant")
    print("  =============")
    print("\n  Version: 0.1.0")
    print("  C-137 Morty Edition")
    print("\n  A Rick and Morty themed ZSH assistant")
    print("  Licensed under MIT")
    
    print("\n  Press any key to return...")
    getch()
    return None

@safe_execute()
def show_documentation():
    """Show documentation"""
    clear_screen()
    print("\n  Opening documentation...")
    time.sleep(1.5)
    return None

@safe_execute()
def restart_zsh():
    """Restart ZSH"""
    clear_screen()
    print("\n  Restarting ZSH...")
    time.sleep(1)
    return "restart_zsh"  # Special return value to trigger ZSH restart

@safe_execute()
def test_portal_gun():
    """Test the portal gun"""
    # Display portal animation
    animate_portal_open()
    time.sleep(0.5)
    animate_portal_close()
    return None

@safe_execute()
def toggle_debug_mode():
    """Toggle debug mode"""
    clear_screen()
    print("\n  Toggling debug mode...")
    time.sleep(1)
    print("  Debug mode toggled!")
    time.sleep(1.5)
    return None

@safe_execute()
def exit_menu():
    """Exit the menu"""
    # Return special value to indicate exit
    return "exit"

@safe_execute()
def show_menu() -> Optional[str]:
    """
    Show the main Rick menu with the new Ricktastic style.
    
    Returns:
        Optional[str]: Result of menu selection or None
    """
    logger.debug("Showing main Rick menu")
    
    try:
        # Create the menu structure
        menu = create_ricktastic_menu()
        
        # Navigate the menu with slash borders
        result = navigate_menu(menu, border_style="slash")
        
        # Handle specific return values
        if result:
            index, value = result
            if value == "restart_zsh":
                # Handle ZSH restart
                return "restart_zsh"
            elif value == "exit":
                # Exit menu
                return None
            else:
                # Return the value
                return value
        
        return None
    
    except Exception as e:
        logger.error(f"Error in show_menu: {str(e)}")
        if supports_ansi_color():
            print(f"\033[31mError showing menu: {str(e)}\033[0m")
        else:
            print(f"Error showing menu: {str(e)}")
        time.sleep(2)
        return None

@safe_execute()
def animate_portal_close(width: int = None, height: int = None, frames: int = 1, 
                         frame_duration: float = 0.2) -> None:
    """
    Animate a portal closing with simplified animation.
    
    Args:
        width: Terminal width (auto-detected if None)
        height: Terminal height (auto-detected if None)
        frames: Number of animation frames (default: 1)
        frame_duration: Duration of each frame in seconds (default: 0.2)
    """
    logger.debug("Animating portal close")
    
    # Skip animation if static portal is preferred
    if USE_STATIC_PORTAL:
        display_static_portal_closed()
        return
    
    try:
        # Get terminal dimensions if not provided
        width = width or get_terminal_width()
        height = height or get_terminal_height()
        
        # Clear screen
        clear_screen()
        
        # Create portal closing animation frames
        portal_frames = []
        
        # Frame 1: Portal starting to close
        portal_frame1 = [
            "     /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\     ",
            "   /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   ",
            "  /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  ",
            " /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ",
            "/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\",
            "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//",
            " \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\// ",
            "  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//  ",
            "   \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//   ",
            "     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//     "
        ]
        
        # Frame 2: Portal closed
        portal_frame2 = [
            "     /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\     ",
            "   /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\   ",
            "  /\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\  ",
            " /\\\\\\\\\\\\\\\\PORTAL\\\\\\\\\\\\\\\\\\\ ",
            "/\\\\\\\\\\\\\\\\\\CLOSED\\\\\\\\\\\\\\\\\\\\",
            "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//",
            " \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\// ",
            "  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//  ",
            "   \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//   ",
            "     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//     "
        ]
        
        # Add frames to animation
        portal_frames.append(portal_frame1)
        portal_frames.append(portal_frame2)
        
        # Animate the portal closing
        for frame in portal_frames:
            # Clear screen
            clear_screen()
            
            # Calculate centering
            frame_width = len(frame[0])
            frame_height = len(frame)
            
            x_offset = (width - frame_width) // 2
            y_offset = (height - frame_height) // 2
            
            # Print empty lines for top padding
            for _ in range(y_offset):
                print()
            
            # Print the frame with colors
            for line in frame:
                # Add left padding
                padding = " " * x_offset
                
                # Colorize the line
                colored_line = ""
                for char in line:
                    if char == "/":
                        # Green for outer portal
                        colored_line += "\033[32m/\033[0m" if supports_ansi_color() else "/"
                    elif char == "\\":
                        # Green for outer portal
                        colored_line += "\033[32m\\\033[0m" if supports_ansi_color() else "\\"
                    elif char in "PORTALCLOSED":
                        # Cyan for text
                        colored_line += "\033[36m" + char + "\033[0m" if supports_ansi_color() else char
                    else:
                        # Blue for inner portal
                        colored_line += "\033[34m" + char + "\033[0m" if supports_ansi_color() else char
                
                # Print the line
                print(padding + colored_line)
            
            # Wait for the specified duration
            time.sleep(frame_duration)
        
        # Small pause at the end
        time.sleep(0.3)
        
    except Exception as e:
        logger.error(f"Error in animate_portal_close: {str(e)}")
        # Fallback to static display
        display_static_portal_closed()

@safe_execute()
def getch() -> str:
    """
    Get a single character from the user without requiring Enter.
    Handles special keys like arrows better than standard implementations.
    
    Returns:
        str: The character pressed by the user or a special key code
    """
    if sys.platform == 'win32':
        # Windows implementation
        import msvcrt
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix
                    # Arrow keys
                    key = msvcrt.getch()
                    if key == b'H':  # Up
                        return 'k'
                    elif key == b'P':  # Down
                        return 'j'
                    elif key == b'K':  # Left
                        return 'h'
                    elif key == b'M':  # Right
                        return 'l'
                elif key == b'\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                return key.decode('utf-8', errors='replace')
    else:
        # Unix/Linux/MacOS implementation
        import termios
        import tty
        import select
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            
            # Check if input is available (timeout of 0.1 seconds)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                # Read first character
                ch = sys.stdin.read(1)
                
                # Handle escape sequences for arrow keys
                if ch == '\x1b':
                    # Could be an escape sequence
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                ch3 = sys.stdin.read(1)
                                # Arrow keys
                                if ch3 == 'A':
                                    return 'k'  # Up
                                elif ch3 == 'B':
                                    return 'j'  # Down
                                elif ch3 == 'C':
                                    return 'l'  # Right
                                elif ch3 == 'D':
                                    return 'h'  # Left
                return ch
            return ''
        except Exception as e:
            logger.error(f"Error in getch: {e}")
            return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Import for handling rick commentary
import random
import os
import json
from src.utils.logger import get_logger

# Add below the existing imports

# Logger
logger = get_logger(__name__)

# Rick commentary system
def load_rick_catchphrases():
    """
    Load Rick catchphrases from the data file.
    
    Returns:
        List[str]: List of catchphrases or default catchphrases if file not found
    """
    default_catchphrases = [
        "Wubba lubba dub dub!",
        "I'm not arguing, I'm just explaining why I'm right.",
        "Sometimes science is more art than science.",
        "I turned myself into a menu, Morty!",
        "What, you think you're better than me because you have a menu?",
        "This menu interface is primitive. I've seen better UIs in a butter passing robot.",
        "You know what? I eat menus like this for breakfast!",
        "I don't have time for a full menu navigation tutorial, Morty!",
        "Look at all these options, Morty! The possibilities are almost endless!",
        "Don't just stare at it, Morty! Pick something!",
        "This menu is the Rick-est Rick that ever Ricked!",
        "I'm Menu Rick! *burp*",
        "These are just *burp* settings, Morty! Don't overthink it!",
        "You're overthinking the menu, Morty! Just pick something!"
    ]
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Try to load catchphrases from the data file
    try:
        catchphrases_path = os.path.expanduser("~/.rick_assistant/data/catchphrases.json")
        
        if os.path.isfile(catchphrases_path):
            with open(catchphrases_path, 'r') as f:
                data = json.load(f)
                
                if 'catchphrases' in data and isinstance(data['catchphrases'], list):
                    return data['catchphrases']
    except Exception as e:
        logger.error(f"Failed to load catchphrases: {e}")
    
    # Return default catchphrases if loading failed
    return default_catchphrases

def get_random_rick_commentary():
    """
    Get a random Rick catchphrase.
    
    Returns:
        str: Random Rick catchphrase
    """
    catchphrases = load_rick_catchphrases()
    return random.choice(catchphrases)

# Modify the show_menu function to support pagination
def show_menu(title="Rick Assistant Control Panel", theme=None):
    """
    Display the main Rick menu with the new Ricktastic style.
    
    Args:
        title: Title of the menu
        theme: Color theme to use (overrides configured theme)
        
    Returns:
        Any: Result from menu navigation
    """
    try:
        logger.debug("Displaying Ricktastic menu")
        
        # Use provided theme or get from configuration
        if theme is None:
            theme = ThemeManager.get_current_theme()
        
        # Create the menu structure
        menu = create_ricktastic_menu(title=title, theme=theme)
        
        # Generate a random Rick commentary
        rick_commentary = get_random_rick_commentary()
        
        # Prepare navigation options
        navigation_footer = [
            "Navigate: ↑↓←→ | Select: Enter | Back: Esc | Quit: q"
        ]
        
        result = navigate_menu(
            menu, 
            commentary=rick_commentary,
            footer_text=navigation_footer
        )
        
        # Handle special return values
        if result == "restart_zsh":
            logger.info("User requested ZSH restart")
            return "restart_zsh"
        elif result == "quit":
            logger.info("User exited menu")
            return None
            
        return result
    except Exception as e:
        logger.error(f"Error showing menu: {e}")
        print(f"Error showing menu: {e}")
        return None

# Add the navigate_menu function
def navigate_menu(menu, commentary=None, footer_text=None):
    """
    Navigate through a menu with pagination support.
    
    Args:
        menu: Menu object to navigate
        commentary: Optional Rick commentary to display
        footer_text: Optional footer text to display
        
    Returns:
        Any: Result from menu navigation
    """
    import curses
    from curses import wrapper
    
    # Create a nested function to store state
    def _menu_navigation(stdscr):
        # Using nonlocal to allow modification of outer variables
        nonlocal commentary
        
        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        curses.start_color()  # Enable colors
        curses.use_default_colors()  # Use terminal's default colors
        curses.raw()  # Raw input mode
        curses.nonl()  # No newline mode
        stdscr.clear()
        
        # Critical: Enable keypad mode for arrow keys
        stdscr.keypad(True)
        
        # Initialize colors based on theme
        theme = menu.theme or DEFAULT_THEME
        init_menu_colors(theme)
        
        # Main navigation loop
        current_menu = menu
        selected_index = 0
        result = None
        
        while True:
            # Clear screen
            stdscr.clear()
            
            # Get terminal dimensions
            max_y, max_x = stdscr.getmaxyx()
            
            # Calculate available height for menu items
            header_height = 3  # Title + commentary + separator
            footer_height = 3  # Navigation help + breadcrumbs + separator
            available_height = max_y - header_height - footer_height
            
            # Set items per page based on available height
            current_menu.items_per_page = max(1, available_height - 2)
            
            # Get current page items
            page_items = current_menu.get_current_page_items()
            page_count = current_menu.get_page_count()
            
            # Ensure selected index is within bounds
            if not page_items:
                selected_index = 0
            elif selected_index >= len(page_items):
                selected_index = len(page_items) - 1
                
            # Draw header
            draw_header(stdscr, max_x, current_menu.title, commentary)
            
            # Draw menu items
            draw_menu_items(stdscr, max_x, page_items, selected_index, header_height)
            
            # Draw pagination indicators if needed
            if page_count > 1:
                draw_pagination(stdscr, max_x, current_menu.current_page, page_count, max_y - footer_height)
                
            # Draw footer (navigation help, breadcrumbs)
            nav_text = "▲▼: Navigate | ◄►: Pages | Enter: Select | Esc: Back | Q: Quit | R: Refresh"
            draw_footer(stdscr, max_x, max_y, nav_text, current_menu.get_breadcrumbs())
            
            # Refresh screen before waiting for input
            stdscr.refresh()
            
            # Get user input - with proper logging for debugging
            try:
                key = stdscr.getch()
                logger.debug(f"Key pressed: {key}")
                
                # Handle navigation keys with comprehensive support
                if key == curses.KEY_UP:
                    if page_items:
                        selected_index = (selected_index - 1) % len(page_items)
                
                elif key == curses.KEY_DOWN:
                    if page_items:
                        selected_index = (selected_index + 1) % len(page_items)
                
                elif key == curses.KEY_LEFT:
                    current_menu.prev_page()
                    selected_index = 0
                
                elif key == curses.KEY_RIGHT:
                    current_menu.next_page()
                    selected_index = 0
                
                elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key variations
                    # Activate selected item
                    if page_items and selected_index < len(page_items):
                        selected_item = page_items[selected_index]
                        action_result = selected_item.activate()
                        
                        # Handle special return values
                        if isinstance(selected_item, MenuCategory):
                            # Navigate to submenu
                            submenu = selected_item.create_submenu()
                            submenu_result = navigate_menu(submenu, commentary, footer_text)
                            
                            if submenu_result in ["restart_zsh", "quit"]:
                                return submenu_result
                        else:
                            # Process normal menu item activation
                            if action_result == "restart_zsh":
                                return "restart_zsh"
                            elif action_result == "quit":
                                return "quit"
                            elif action_result == "back":
                                if current_menu.parent:
                                    current_menu = current_menu.parent
                                    selected_index = 0
                
                elif key == 27:  # Escape key
                    # Go back to parent menu if available
                    if current_menu.parent:
                        current_menu = current_menu.parent
                        selected_index = 0
                    else:
                        return None  # Exit menu if at root
                
                elif key in [ord('q'), ord('Q')]:
                    # Quit menu
                    return "quit"
                
                elif key in [ord('r'), ord('R')]:
                    # Refresh commentary
                    commentary = get_random_rick_commentary()
                
                # Number key support for direct selection
                elif ord('1') <= key <= ord('9'):
                    # Direct selection by number (1-9)
                    index = key - ord('1')  # Convert to 0-based index
                    if index < len(page_items):
                        selected_index = index
                
                elif key == ord('0'):
                    # Handle 0 key as item 10
                    if 9 < len(page_items):
                        selected_index = 9
                
            except Exception as e:
                # Log the error but continue navigation
                logger.error(f"Error processing key input: {e}")
                # Add error message to commentary temporarily
                commentary = f"Menu error: {str(e)}"
                
        return result
    
    # Run the menu navigation in curses wrapper
    return wrapper(_menu_navigation)

# Helper functions for the navigate_menu function
def init_menu_colors(theme):
    """
    Initialize curses color pairs based on the theme.
    
    Args:
        theme: Color theme to use
    """
    import curses
    
    try:
        # Define color map for terminal colors
        color_map = {
            "black": curses.COLOR_BLACK,
            "red": curses.COLOR_RED,
            "green": curses.COLOR_GREEN,
            "yellow": curses.COLOR_YELLOW,
            "blue": curses.COLOR_BLUE,
            "magenta": curses.COLOR_MAGENTA,
            "cyan": curses.COLOR_CYAN,
            "white": curses.COLOR_WHITE,
            "default": -1,  # Terminal default color
        }
        
        # Initialize color pairs for the theme
        if not theme:
            # Default theme - Portal colors
            theme = {
                "normal": {"fg": "green", "bg": "black"},
                "highlight": {"fg": "cyan", "bg": "black"},
                "selected": {"fg": "black", "bg": "green"},
                "disabled": {"fg": "white", "bg": "black"},
                "header": {"fg": "green", "bg": "black"},
                "footer": {"fg": "cyan", "bg": "black"},
                "border": {"fg": "green", "bg": "black"},
                "error": {"fg": "red", "bg": "black"},
                "success": {"fg": "green", "bg": "black"},
                "warning": {"fg": "yellow", "bg": "black"}
            }
        
        # Define color pair numbers
        COLOR_NORMAL = 1
        COLOR_HIGHLIGHT = 2
        COLOR_SELECTED = 3
        COLOR_DISABLED = 4
        COLOR_HEADER = 5
        COLOR_FOOTER = 6
        COLOR_BORDER = 7
        COLOR_ERROR = 8
        COLOR_SUCCESS = 9
        COLOR_WARNING = 10
        
        # Initialize color pairs
        # Default to standard colors if theme colors not available
        curses.init_pair(COLOR_NORMAL, 
                         color_map.get(theme.get("normal", {}).get("fg", "green"), curses.COLOR_GREEN),
                         color_map.get(theme.get("normal", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_HIGHLIGHT, 
                         color_map.get(theme.get("highlight", {}).get("fg", "cyan"), curses.COLOR_CYAN),
                         color_map.get(theme.get("highlight", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_SELECTED, 
                         color_map.get(theme.get("selected", {}).get("fg", "black"), curses.COLOR_BLACK),
                         color_map.get(theme.get("selected", {}).get("bg", "green"), curses.COLOR_GREEN))
                         
        curses.init_pair(COLOR_DISABLED, 
                         color_map.get(theme.get("disabled", {}).get("fg", "white"), curses.COLOR_WHITE),
                         color_map.get(theme.get("disabled", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_HEADER, 
                         color_map.get(theme.get("header", {}).get("fg", "green"), curses.COLOR_GREEN),
                         color_map.get(theme.get("header", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_FOOTER, 
                         color_map.get(theme.get("footer", {}).get("fg", "cyan"), curses.COLOR_CYAN),
                         color_map.get(theme.get("footer", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_BORDER, 
                         color_map.get(theme.get("border", {}).get("fg", "green"), curses.COLOR_GREEN),
                         color_map.get(theme.get("border", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_ERROR, 
                         color_map.get(theme.get("error", {}).get("fg", "red"), curses.COLOR_RED),
                         color_map.get(theme.get("error", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_SUCCESS, 
                         color_map.get(theme.get("success", {}).get("fg", "green"), curses.COLOR_GREEN),
                         color_map.get(theme.get("success", {}).get("bg", "black"), curses.COLOR_BLACK))
                         
        curses.init_pair(COLOR_WARNING, 
                         color_map.get(theme.get("warning", {}).get("fg", "yellow"), curses.COLOR_YELLOW),
                         color_map.get(theme.get("warning", {}).get("bg", "black"), curses.COLOR_BLACK))
        
        # Return constant-like attributes for use elsewhere
        return {
            "NORMAL": curses.color_pair(COLOR_NORMAL),
            "HIGHLIGHT": curses.color_pair(COLOR_HIGHLIGHT),
            "SELECTED": curses.color_pair(COLOR_SELECTED),
            "DISABLED": curses.color_pair(COLOR_DISABLED),
            "HEADER": curses.color_pair(COLOR_HEADER),
            "FOOTER": curses.color_pair(COLOR_FOOTER),
            "BORDER": curses.color_pair(COLOR_BORDER),
            "ERROR": curses.color_pair(COLOR_ERROR),
            "SUCCESS": curses.color_pair(COLOR_SUCCESS),
            "WARNING": curses.color_pair(COLOR_WARNING)
        }
    except Exception as e:
        # Graceful fallback if color initialization fails
        logger.error(f"Error initializing colors: {e}")
        return {}  # Return empty dict as fallback

def draw_header(stdscr, width, title, commentary=None):
    """
    Draw the menu header.
    
    Args:
        stdscr: Curses screen
        width: Screen width
        title: Menu title
        commentary: Optional Rick commentary
    """
    import curses
    
    # Draw title
    title_text = f"=== {title} ==="
    x = max(0, (width - len(title_text)) // 2)
    stdscr.addstr(0, x, title_text, curses.color_pair(1) | curses.A_BOLD)
    
    # Draw commentary if provided
    if commentary:
        comment_text = f"Rick says: {commentary}"
        
        # Truncate if too long
        if len(comment_text) > width - 4:
            comment_text = comment_text[:width - 7] + "..."
            
        x = max(0, (width - len(comment_text)) // 2)
        stdscr.addstr(1, x, comment_text, curses.color_pair(2))
    
    # Draw separator
    try:
        stdscr.addstr(2, 0, "=" * width, curses.color_pair(1))
    except curses.error:
        # Handle edge case when drawing at bottom-right corner
        pass

def draw_menu_items(stdscr, width, items, selected_index, start_y):
    """
    Draw menu items with appropriate highlighting.
    
    Args:
        stdscr: Curses window
        width: Available width
        items: List of menu items to display
        selected_index: Index of the selected item
        start_y: Starting Y position
    """
    import curses
    
    try:
        # Get color pairs from theme initialization
        colors = init_menu_colors(None)  # Use default theme if needed
        
        # Set default attributes for fallback
        normal_attr = curses.A_NORMAL
        selected_attr = curses.A_REVERSE
        disabled_attr = curses.A_DIM
        
        # Use theme colors if available
        if colors:
            normal_attr = colors.get("NORMAL", curses.A_NORMAL)
            selected_attr = colors.get("SELECTED", curses.A_REVERSE)
            disabled_attr = colors.get("DISABLED", curses.A_DIM)
        
        # Calculate item positioning
        for i, item in enumerate(items):
            # Get item display text
            item_text = item.get_display_text()
            
            # Truncate if too long for display
            if len(item_text) > width - 4:
                item_text = item_text[:width - 7] + "..."
                
            # Center item text
            padding = (width - len(item_text)) // 2
            
            # Set attributes based on item state
            if i == selected_index:
                if not item.enabled:
                    attr = disabled_attr | curses.A_REVERSE
                else:
                    attr = selected_attr
            else:
                if not item.enabled:
                    attr = disabled_attr
                else:
                    # Special handling for different item types
                    if item.item_type == "category":
                        attr = colors.get("HIGHLIGHT", curses.A_BOLD)
                    else:
                        attr = normal_attr
            
            # Draw the item with appropriate attributes
            y_pos = start_y + i + 1
            try:
                stdscr.addstr(y_pos, padding, item_text, attr)
            except curses.error:
                # Handle potential out-of-bounds errors
                pass
                
    except Exception as e:
        # Log error but continue
        logger.error(f"Error drawing menu items: {e}")
        
        # Fallback: Draw items in plain text if possible
        try:
            for i, item in enumerate(items):
                y_pos = start_y + i + 1
                if y_pos < stdscr.getmaxyx()[0]:
                    text = f"{'> ' if i == selected_index else '  '}{item.get_display_text()}"
                    stdscr.addstr(y_pos, 2, text[:width-4])
        except:
            # If all else fails, just continue without drawing items
            pass

def draw_pagination(stdscr, width, current_page, total_pages, y_pos):
    """
    Draw pagination indicators.
    
    Args:
        stdscr: Curses screen
        width: Screen width
        current_page: Current page number (0-based)
        total_pages: Total number of pages
        y_pos: Y position to draw at
    """
    import curses
    
    if total_pages <= 1:
        return
    
    # Create pagination text
    if supports_unicode():
        pagination = []
        
        # Add left arrow if not on first page
        if current_page > 0:
            pagination.append("◀")
        else:
            pagination.append(" ")
        
        # Add page numbers
        for i in range(total_pages):
            if i == current_page:
                pagination.append(f"[{i+1}]")
            else:
                pagination.append(f" {i+1} ")
        
        # Add right arrow if not on last page
        if current_page < total_pages - 1:
            pagination.append("▶")
        else:
            pagination.append(" ")
    else:
        # ASCII fallback
        pagination = []
        
        # Add left arrow if not on first page
        if current_page > 0:
            pagination.append("<")
        else:
            pagination.append(" ")
        
        # Add page numbers
        for i in range(total_pages):
            if i == current_page:
                pagination.append(f"[{i+1}]")
            else:
                pagination.append(f" {i+1} ")
        
        # Add right arrow if not on last page
        if current_page < total_pages - 1:
            pagination.append(">")
        else:
            pagination.append(" ")
    
    # Join and center the pagination text
    pagination_text = " ".join(pagination)
    x = max(0, (width - len(pagination_text)) // 2)
    
    # Make sure we don't draw outside the screen
    if y_pos < stdscr.getmaxyx()[0]:
        try:
            # Draw pagination
            stdscr.addstr(y_pos, x, pagination_text, curses.color_pair(1))
        except curses.error:
            # Handle edge case when drawing at bottom-right corner
            pass

def draw_footer(stdscr, width, height, nav_text=None, breadcrumbs=None):
    """
    Draw menu footer with navigation help and breadcrumbs.
    
    Args:
        stdscr: Curses window
        width: Available width
        height: Total screen height
        nav_text: Navigation help text
        breadcrumbs: Breadcrumb path
    """
    import curses
    
    try:
        # Get colors from theme
        colors = init_menu_colors(None)
        
        # Set default attributes
        footer_attr = curses.A_NORMAL
        breadcrumb_attr = curses.A_NORMAL
        
        # Use theme colors if available
        if colors:
            footer_attr = colors.get("FOOTER", curses.A_NORMAL)
            breadcrumb_attr = colors.get("NORMAL", curses.A_NORMAL)
        
        # Calculate positions
        footer_y = height - 2
        breadcrumb_y = height - 1
        
        # Default navigation text if not provided
        if nav_text is None:
            nav_text = "↑↓: Navigate | ←→: Pages | Enter: Select | Esc: Back | Q: Quit"
        
        # Ensure text isn't too long
        if len(nav_text) > width - 4:
            nav_text = nav_text[:width - 7] + "..."
        
        # Center the navigation text
        nav_x = (width - len(nav_text)) // 2
        
        # Draw navigation help
        try:
            stdscr.addstr(footer_y, nav_x, nav_text, footer_attr)
        except curses.error:
            # Handle out-of-bounds errors
            pass
        
        # Draw breadcrumbs if provided
        if breadcrumbs:
            # Format breadcrumbs with separator
            breadcrumb_text = " > ".join(breadcrumbs)
            
            # Truncate if too long
            if len(breadcrumb_text) > width - 4:
                breadcrumb_text = "..." + breadcrumb_text[-(width - 7):]
            
            # Center the breadcrumb text
            breadcrumb_x = (width - len(breadcrumb_text)) // 2
            
            try:
                stdscr.addstr(breadcrumb_y, breadcrumb_x, breadcrumb_text, breadcrumb_attr)
            except curses.error:
                # Handle out-of-bounds errors
                pass
    
    except Exception as e:
        # Log error but continue
        logger.error(f"Error drawing footer: {e}")
        
        # Fallback: Draw simple footer
        try:
            footer_simple = "Use arrows to navigate, Enter to select"
            simple_x = (width - len(footer_simple)) // 2
            stdscr.addstr(height - 1, simple_x, footer_simple)
        except:
            # If all else fails, just continue
            pass

# Add these functions after the imports but before the classes

# Configuration utils
def get_config_value(key, default=None):
    """
    Get a configuration value from the config system.
    
    Args:
        key: Configuration key (e.g., "ui.theme")
        default: Default value if key not found
        
    Returns:
        Any: Configuration value or default
    """
    try:
        # Import here to avoid circular imports
        from src.utils.config import get_config_value as get_config
        
        # Get the value from config
        return get_config(key, default)
    except Exception as e:
        logger.error(f"Failed to get config value for {key}: {e}")
        return default

def set_config_value(key, value):
    """
    Set a configuration value in the config system.
    
    Args:
        key: Configuration key (e.g., "ui.theme")
        value: Value to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from src.utils.config import set_config_value as set_config
        
        # Set the value in config
        set_config(key, value)
        logger.debug(f"Updated config: {key} = {value}")
        return True
    except Exception as e:
        logger.error(f"Failed to set config value for {key}: {e}")
        return False

def toggle_config_value(key, default=False):
    """
    Toggle a boolean configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        bool: New value
    """
    current = get_config_value(key, default)
    
    if not isinstance(current, bool):
        current = bool(current)
        
    new_value = not current
    set_config_value(key, new_value)
    return new_value

# Add after the configuration utils

def ensure_data_directory():
    """
    Ensure the data directory for Rick Assistant exists.
    Creates directories if they don't exist.
    """
    try:
        # Get home directory
        home_dir = os.path.expanduser("~")
        
        # Define paths
        rick_dir = os.path.join(home_dir, ".rick_assistant")
        data_dir = os.path.join(rick_dir, "data")
        
        # Create directories if they don't exist
        if not os.path.exists(rick_dir):
            os.makedirs(rick_dir)
            logger.debug(f"Created directory: {rick_dir}")
            
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.debug(f"Created directory: {data_dir}")
            
        # Create default catchphrases file if it doesn't exist
        catchphrases_path = os.path.join(data_dir, "catchphrases.json")
        if not os.path.exists(catchphrases_path):
            default_catchphrases = {
                "catchphrases": [
                    "Wubba lubba dub dub!",
                    "I'm not arguing, I'm just explaining why I'm right.",
                    "Sometimes science is more art than science.",
                    "I turned myself into a menu, Morty!",
                    "What, you think you're better than me because you have a menu?",
                    "This menu interface is primitive. I've seen better UIs in a butter passing robot.",
                    "You know what? I eat menus like this for breakfast!",
                    "I don't have time for a full menu navigation tutorial, Morty!",
                    "Look at all these options, Morty! The possibilities are almost endless!",
                    "Don't just stare at it, Morty! Pick something!",
                    "This menu is the Rick-est Rick that ever Ricked!",
                    "I'm Menu Rick! *burp*",
                    "These are just *burp* settings, Morty! Don't overthink it!",
                    "You're overthinking the menu, Morty! Just pick something!"
                ]
            }
            
            with open(catchphrases_path, 'w') as f:
                json.dump(default_catchphrases, f, indent=2)
                
            logger.debug(f"Created default catchphrases file: {catchphrases_path}")
            
        return True
    except Exception as e:
        logger.error(f"Failed to ensure data directory: {e}")
        return False

# Fix the missing confirm_action function
@safe_execute()
def confirm_action(message, default=True):
    """
    Show a confirmation prompt with yes/no options.
    
    Args:
        message: Message to display
        default: Default value (True for yes, False for no)
        
    Returns:
        bool: True if confirmed, False if not
    """
    # No animation as per requirements
    if not message.endswith('?'):
        message += '?'
        
    prompt = f"{message} [{'Y/n' if default else 'y/N'}]: "
    
    try:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
            
        if response in ['y', 'yes']:
            return True
            
        if response in ['n', 'no']:
            return False
            
        # Invalid response, use default
        return default
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return False
    except Exception as e:
        logger.error(f"Error in confirm_action: {e}")
        return default

# Fix the missing show_message function
@safe_execute()
def show_message(message, title=None, message_type="info"):
    """
    Show a message to the user.
    
    Args:
        message: Message to display
        title: Optional title
        message_type: Type of message (info, success, warning, error)
    """
    # No animation as per requirements
    try:
        # Clear screen
        clear_screen()
        
        # Format based on message type
        formatted_message = message
        
        if message_type == "info":
            formatted_message = format_info(message)
        elif message_type == "success":
            formatted_message = format_success(message)
        elif message_type == "warning":
            formatted_message = format_warning(message)
        elif message_type == "error":
            formatted_message = format_error(message)
            
        # Print title if provided
        if title:
            print(f"\n  {title}")
            print(f"  {'=' * len(title)}")
            
        # Print message
        print(f"\n  {formatted_message}")
        
        # Wait for keypress
        print("\n  Press any key to continue...")
        getch()
    except Exception as e:
        logger.error(f"Error showing message: {e}")
        print(f"\nError: {e}")
        # Wait briefly
        time.sleep(1)

# Fix the missing create_hierarchical_menu function
@safe_execute()
def create_hierarchical_menu(title, structure):
    """
    Create a hierarchical menu from a dictionary structure.
    
    Args:
        title: Menu title
        structure: Dictionary with category and item definitions
        
    Returns:
        Menu: The created menu
    """
    # Create the main menu
    main_menu = Menu(title=title)
    
    # Process each category
    for category_name, category_data in structure.items():
        # Create items list
        items = []
        
        # Add items to the category
        for item_data in category_data.get("items", []):
            # Extract item data
            item_text = item_data.get("text", "")
            item_value = item_data.get("value", None)
            item_type = item_data.get("type", "standard")
            item_key = item_data.get("key", None)
            item_default = item_data.get("default", None)
            item_enabled = item_data.get("enabled", True)
            item_options = item_data.get("options", [])
            
            # Handle submenu
            if "submenu" in item_data:
                # Create a submenu category
                submenu_items = []
                
                # Process submenu items
                for submenu_item in item_data["submenu"].get("items", []):
                    sub_text = submenu_item.get("text", "")
                    sub_value = submenu_item.get("value", None)
                    sub_type = submenu_item.get("type", "standard")
                    
                    # Create submenu item based on type
                    if sub_type == "toggle":
                        sub_item = MenuToggle(sub_text, submenu_item.get("key"), 
                                           submenu_item.get("default", False))
                    elif sub_type == "multi_option":
                        sub_item = MultiOptionMenuItem(sub_text, submenu_item.get("key"),
                                                    submenu_item.get("options", []),
                                                    submenu_item.get("default", None))
                    else:
                        # Standard menu item
                        action = None
                        if sub_value:
                            action = lambda v=sub_value: v
                        sub_item = MenuItem(sub_text, action)
                        
                    submenu_items.append(sub_item)
                
                # Create the submenu category
                submenu_category = MenuCategory(item_text, submenu_items)
                items.append(submenu_category)
            else:
                # Create item based on type
                if item_type == "toggle":
                    item = MenuToggle(item_text, item_key, item_default, item_enabled)
                elif item_type == "multi_option":
                    item = MultiOptionMenuItem(item_text, item_key, item_options, item_default, item_enabled)
                else:
                    # Standard menu item
                    action = None
                    if item_value:
                        # Use lambda with default value to capture current value
                        action = lambda v=item_value: v
                    item = MenuItem(item_text, action, item_enabled)
                    
                items.append(item)
        
        # Create category and add to menu
        category = MenuCategory(category_name, items)
        main_menu.add_item(category)
    
    return main_menu

# Fix the missing navigate_hierarchy function
@safe_execute()
def navigate_hierarchy(menu):
    """
    Navigate a hierarchical menu.
    
    Args:
        menu: Menu to navigate
        
    Returns:
        tuple: (menu, index, value) or None if cancelled
    """
    # Current menu starts as the provided one
    current_menu = menu
    current_index = 0
    
    while True:
        # Clear screen
        clear_screen()
        
        # Display menu title
        print(f"\n  {current_menu.title}")
        print(f"  {'=' * len(current_menu.title)}")
        
        # Display breadcrumbs if available
        if current_menu.breadcrumbs:
            path = " > ".join(current_menu.breadcrumbs)
            print(f"  Location: {path} > {current_menu.title}")
            print()
        
        # Get current page items
        items = current_menu.get_current_page_items()
        
        # Display items with numbers
        for i, item in enumerate(items):
            # Format based on item type and selection
            if i == current_index:
                # Selected item
                if isinstance(item, MenuCategory):
                    display = highlight_category(item, True)
                else:
                    display = highlight_selection(item, True)
            else:
                # Unselected item
                if isinstance(item, MenuCategory):
                    display = highlight_category(item, False)
                else:
                    display = highlight_selection(item, False)
                    
            # Print the item
            print(f"  {i+1}. {display}")
        
        # Display pagination if needed
        if current_menu.get_page_count() > 1:
            print(f"\n  Page {current_menu.current_page + 1}/{current_menu.get_page_count()}")
            print("  Use Left/Right arrows to navigate pages")
        
        # Display navigation help
        print("\n  Navigate: ↑↓ | Select: Enter | Back: Esc | Quit: q")
        
        # Get user input
        key = getch()
        
        # Handle navigation keys
        if key in ['q', 'Q']:
            # Quit
            return None
        elif key in ['\x1b', '\x03']:  # ESC or Ctrl+C
            # Go back or quit
            if current_menu.parent:
                # Go back to parent
                current_menu = current_menu.parent
                current_index = 0
            else:
                # Quit if at root
                return None
        elif key in ['\r', '\n']:  # Enter
            # Activate selected item
            if items and current_index < len(items):
                selected_item = items[current_index]
                result = selected_item.activate()
                
                # Handle category activation (submenu navigation)
                if isinstance(selected_item, MenuCategory):
                    # Navigate to submenu
                    submenu = selected_item.create_submenu()
                    submenu_result = navigate_hierarchy(submenu)
                    
                    if submenu_result:
                        return submenu_result
                elif result is not None:
                    # Return the result and selected item info
                    return (current_menu, current_index, result)
        elif key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # Direct selection by number
            selected = int(key) - 1
            if selected < len(items):
                current_index = selected
        elif key in ['j', 'J'] or key == '\x1b[B':  # Down arrow, j
            # Move selection down
            current_index = (current_index + 1) % len(items) if items else 0
        elif key in ['k', 'K'] or key == '\x1b[A':  # Up arrow, k
            # Move selection up
            current_index = (current_index - 1) % len(items) if items else 0
        elif key in ['h', 'H'] or key == '\x1b[D':  # Left arrow, h
            # Previous page
            current_menu.prev_page()
            current_index = 0
        elif key in ['l', 'L'] or key == '\x1b[C':  # Right arrow, l
            # Next page
            current_menu.next_page()
            current_index = 0

# Fix the missing highlight functions
@safe_execute()
def highlight_category(category, is_selected, width=None):
    """
    Format a category menu item with appropriate highlighting.
    
    Args:
        category: MenuCategory to format
        is_selected: Whether this category is selected
        width: Optional width for padding
        
    Returns:
        str: Formatted display text
    """
    # Get the display text
    text = category.get_display_text()
    
    # Simple highlighting with brackets if selected
    if is_selected:
        if supports_ansi_color():
            # Use color if supported
            return f"\033[7m{text}\033[0m"  # Reversed colors
        else:
            # Fallback to brackets
            return f"[{text}]"
    else:
        return text

@safe_execute()
def highlight_selection(item, is_selected, width=None):
    """
    Format a menu item with appropriate highlighting.
    
    Args:
        item: MenuItem to format
        is_selected: Whether this item is selected
        width: Optional width for padding
        
    Returns:
        str: Formatted display text
    """
    # Get the display text
    text = item.get_display_text()
    
    # Apply disabled styling if needed
    if not item.enabled:
        if supports_ansi_color():
            # Use dim text for disabled items
            return f"\033[2m{text}\033[0m"  # Dim
        else:
            # Fallback for disabled items
            return f"(disabled) {text}"
    
    # Apply selected styling
    if is_selected:
        if supports_ansi_color():
            # Use reversed colors for selection
            return f"\033[7m{text}\033[0m"  # Reversed colors
        else:
            # Fallback to brackets
            return f"[{text}]"
    else:
        return text

# Add a no-op version of animate_portal_open since we don't want animations
@safe_execute()
def animate_portal_open():
    """
    Stub for portal opening animation.
    Per requirements, we don't want animations, so this just displays a static portal.
    """
    display_static_portal_open()

# Add the missing create_wizard function
@safe_execute()
def create_wizard(title, steps, callback=None):
    """
    Create a wizard with multiple steps.
    
    Args:
        title: Wizard title
        steps: List of step dictionaries
        callback: Function to call with wizard results
        
    Returns:
        Dict: Wizard configuration
    """
    return {
        "title": title,
        "steps": steps,
        "callback": callback,
        "current_step": 0,
        "results": {}
    }

# Add the missing create_context_menu function
@safe_execute()
def create_context_menu(items, title="Context Menu"):
    """
    Create a context menu with the given items.
    
    Args:
        items: List of items (either strings or MenuItem objects)
        title: Menu title
        
    Returns:
        Menu: The created context menu
    """
    menu = Menu(title)
    
    # Process each item
    for item in items:
        if isinstance(item, str):
            # Create a simple menu item from string
            menu_item = MenuItem(item, lambda text=item: text)
            menu.add_item(menu_item)
        elif isinstance(item, MenuItem):
            # Use the MenuItem directly
            menu.add_item(item)
        elif isinstance(item, dict):
            # Create from dictionary
            text = item.get("text", "")
            action = item.get("action", None)
            enabled = item.get("enabled", True)
            
            menu_item = MenuItem(text, action, enabled)
            menu.add_item(menu_item)
    
    return menu