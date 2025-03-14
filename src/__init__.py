"""
Rick Assistant ZSH Plugin Package

This package provides a Rick Sanchez-themed assistant for ZSH with various
features including enhanced prompts, command suggestions, and Rick's signature
personality.

"Listen up, M-Morty! This *burp* package is gonna revolutionize your terminal!
You're welcome, you ungrateful universe."
"""

__version__ = "0.1.0"
__author__ = "Rick Assistant Developer"
__description__ = "Rick Sanchez-themed ZSH assistant"

# Package metadata dictionary for easy access
METADATA = {
    "name": "rick_assistant",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "github": "https://github.com/yourusername/rick_assistant"
}

# Rick ASCII Art
RICK_ASCII = r"""
                      .-.
                     (   )
                      '-'
                      J L
                      | |
                     J   L
                     |   |
                    J     L
                  .-'.___.'-.
                 /___________\
            _.-""'           '""-._
          .'                       '.
        /                             \
       /                               \
      /_______                   _______\
      (       )                 (       )
      (       )                 (       )
      (       )                 (       )
      (       )                 (       )
       (______)                 (______)
"""

# Import core utilities
import os
import sys
from pathlib import Path
import logging

# Add project root to path if not already there
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Initialize logging system
try:
    from src.utils.logger import get_logger, configure_root_logger
    
    # Configure root logger
    configure_root_logger(level="INFO")
    
    # Get package logger
    logger = get_logger(__name__)
    logger.info(f"Initializing Rick Assistant v{__version__}")
    
except ImportError:
    # Fallback logging if main logger is unavailable
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Initializing Rick Assistant v{__version__} (basic logging)")

# Plugin instance placeholder
_plugin_instance = None
_initialization_successful = False

def get_plugin_instance():
    """Get the active plugin instance."""
    global _plugin_instance
    if _plugin_instance is None:
        try:
            # Import lazily to avoid circular imports
            from src.core.plugin import RickAssistant
            _plugin_instance = RickAssistant()
            logger.debug("Created new plugin instance")
        except ImportError as e:
            logger.warning(f"Could not create plugin instance: {str(e)}")
            return None
    return _plugin_instance

# Import core modules for easier access
try:
    from src.utils.config import get_config_value, save_config
    from src.utils.errors import safe_execute, RickAssistantError
    from src.utils.path_safety import normalize_path, is_path_within_safe_directories
    
    # Mark initialization as successful
    _initialization_successful = True
    logger.info("Rick Assistant core modules loaded successfully")
    
except ImportError as e:
    _initialization_successful = False
    logger.error(f"Failed to import core modules: {str(e)}")

def is_ready():
    """Check if the plugin is ready to use."""
    return _initialization_successful

def version():
    """Return package version string."""
    return f"Rick Assistant v{__version__}"

def display_welcome():
    """Display welcome message with Rick ASCII art."""
    print(RICK_ASCII)
    print(f"Rick Assistant v{__version__} initialized and ready to *burp* serve!")
    print(f"Created by: {__author__}")
    print("Type '!rick help' for assistance")

# Display welcome message if this module is run directly
if __name__ == "__main__":
    display_welcome()
