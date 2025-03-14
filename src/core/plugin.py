"""
Rick Assistant Plugin Core Module

This module provides the central RickAssistant class that coordinates
the functionality of the Rick Assistant ZSH plugin.

"Look Morty, I've turned myself into a *burp* Python class!
Pickle Riiiick! But more maintainable and object-oriented!"
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import core utilities
from src.utils.logger import get_logger
from src.utils.config import get_config_value, save_config
from src.utils.errors import safe_execute, RickAssistantError

# Get logger for this module
logger = get_logger(__name__)

class RickAssistant:
    """
    Main plugin class that coordinates Rick Assistant functionality.
    
    This class serves as the central controller for the Rick Assistant,
    coordinating between the ZSH shell, Python modules, and user interactions.
    """
    
    def __init__(self):
        """Initialize the Rick Assistant plugin."""
        self.initialized = False
        self.hooks_registered = False
        self.config = {}
        self._initialize()
        
    @safe_execute(default_return=False)
    def _initialize(self) -> bool:
        """Internal initialization method."""
        logger.info("Initializing Rick Assistant plugin...")
        
        # Load configuration
        try:
            from src.utils.config import load_config
            self.config = load_config()
            logger.debug("Configuration loaded successfully")
        except ImportError:
            logger.warning("Could not load configuration module")
            self.config = {}
        
        # Register hooks if available
        try:
            from src.core.hooks import initialize_hooks
            initialize_hooks()
            self.hooks_registered = True
            logger.debug("Hooks registered successfully")
        except ImportError:
            logger.debug("Hooks module not available yet")
        
        self.initialized = True
        logger.info("Rick Assistant plugin initialized")
        return True
    
    @property
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled in configuration."""
        return get_config_value("general.enabled", True)
    
    def execute_command(self, command: str) -> str:
        """
        Execute a Rick Assistant command.
        
        Args:
            command: The command to execute
            
        Returns:
            Response message from command execution
        """
        logger.debug(f"Executing command: {command}")
        
        # Placeholder for command execution logic
        return f"Rick acknowledges your command: {command}\n*burp* I'll implement this properly later."
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current plugin status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "initialized": self.initialized,
            "enabled": self.is_enabled,
            "hooks_registered": self.hooks_registered,
            "version": get_config_value("version", "0.1.0")
        }
    
    def cleanup(self) -> None:
        """Perform cleanup operations when plugin is unloaded."""
        logger.info("Cleaning up Rick Assistant plugin...")
        # Placeholder for cleanup logic 