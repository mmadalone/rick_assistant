"""
Rick Assistant Main Module

This is the main entry point for the Rick Assistant ZSH plugin.

"Listen Morty, *burp* this is where the magic happens - the central nervous system 
of this whole operation. Don't mess with it unless you know what you're doing!"
"""

import os
import sys
from typing import Dict, Any, Optional, Union, List, Tuple, Callable

# Import core modules in order of dependency
from src.utils.logger import get_logger, setup_logger
from src.utils.errors import safe_execute, RickAssistantError
from src.utils.config import (
    get_config_value, set_config_value, 
    load_config, save_config, get_default_config
)
from src.core.setup import initialize as setup_initialize

# Initialize logger
logger = get_logger(__name__)

# Version information
__version__ = "0.1.0"
__author__ = "Rick Assistant Contributors"
__description__ = "Rick Sanchez-themed ZSH assistant"

# Constants
DEFAULT_CONFIG = {
    "general": {
        "enabled": True,
        "log_level": "INFO",
        "show_welcome_message": True,
        "show_exit_message": True
    }
}

def initialize() -> bool:
    """
    Initialize the Rick Assistant.
    
    This is the main initialization function called by the ZSH plugin.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info("Main module initializing Rick Assistant")
    
    # Delegate to the setup module for actual initialization
    return setup_initialize()

def is_enabled() -> bool:
    """
    Check if Rick Assistant is enabled.
    
    Returns:
        bool: True if enabled, False otherwise
    """
    return get_config_value("general.enabled", True)

def get_status() -> Dict[str, Any]:
    """
    Get the current status of Rick Assistant.
    
    Returns:
        Dict[str, Any]: Status information including version, 
                        enabled state, and integration modes
    """
    return {
        "version": __version__,
        "enabled": is_enabled(),
        "config_path": get_config_value("config_path", "~/.rick_assistant/config.json"),
        # Include key integration statuses based on current phase
        "prompt_integration": {
            "mode": get_config_value("prompt_integration.mode", "auto"),
            "display_style": get_config_value("prompt_integration.display_style", "command_output")
        }
    }

# Phase 4: Command Processing & Safety Features
def process_command(cmd: str) -> Dict[str, Any]:
    """
    Process a command through Rick Assistant.
    
    Placeholder for Phase 4 implementation.
    
    Args:
        cmd: The command to process
        
    Returns:
        Dict containing result information
    """
    logger.debug(f"Command processing requested (but not implemented yet): {cmd}")
    return {"status": "not_implemented", "message": "Command processing coming soon"}

# Phase 5-7: Additional features
def get_version_info() -> Dict[str, Any]:
    """
    Get detailed version information.
    
    Returns:
        Dict containing version details
    """
    return {
        "version": __version__,
        "description": __description__,
        "phase": "3.4",  # Current implementation phase
        "build_date": "2024-03-09",
        "compatibility": {
            "python_min": "3.6.0",
            "zsh_min": "5.0",
            "oh_my_zsh": "compatible"
        }
    }

if __name__ == "__main__":
    """
    Command-line interface for Rick Assistant.
    
    This allows direct invocation of the Rick Assistant module,
    primarily for testing and debugging purposes.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Rick Assistant Control")
    parser.add_argument("--status", action="store_true", help="Show Rick Assistant status")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--enable", action="store_true", help="Enable Rick Assistant")
    parser.add_argument("--disable", action="store_true", help="Disable Rick Assistant")
    parser.add_argument("--debug", action="store_true", help="Toggle debug mode")
    
    args = parser.parse_args()
    
    if args.status:
        status = get_status()
        print(f"Rick Assistant v{status['version']}")
        print(f"Status: {'Enabled' if status['enabled'] else 'Disabled'}")
        print(f"Prompt Mode: {status['prompt_integration']['display_style']}")
    elif args.version:
        info = get_version_info()
        print(f"Rick Assistant v{info['version']}")
        print(f"Phase: {info['phase']}")
        print(f"Build Date: {info['build_date']}")
    elif args.enable:
        set_config_value("general.enabled", True)
        print("Rick Assistant enabled")
    elif args.disable:
        set_config_value("general.enabled", False)
        print("Rick Assistant disabled")
    elif args.debug:
        current = get_config_value("general.log_level", "INFO")
        new_level = "DEBUG" if current != "DEBUG" else "INFO"
        set_config_value("general.log_level", new_level)
        print(f"Debug mode {'enabled' if new_level == 'DEBUG' else 'disabled'}")
    else:
        parser.print_help() 