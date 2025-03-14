"""
ZSH Hooks Module for Rick Assistant

This module manages ZSH hooks integration, handling events like
precmd (before prompt), preexec (before command execution), and
chpwd (when changing directories).

"I turned myself into a shell hook, Morty! *burp* I'm Hook Riiiick!"
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Union, Dict, List, Any, Tuple, Callable

# Import utils
from src.utils.logger import get_logger
from src.utils.errors import safe_execute, ShellError
from src.utils.validation import sanitize_command_input, is_dangerous_command
from src.utils.path_safety import (
    normalize_path,
    is_path_within_safe_directories,
    validate_path_permissions,
    resolve_path
)

# Get logger for this module
logger = get_logger(__name__)

# Store registered hook callbacks
_PRECMD_HOOKS: List[Callable] = []
_PREEXEC_HOOKS: List[Callable[[str], None]] = []
_CHPWD_HOOKS: List[Callable[[Optional[str]], None]] = []
_HOOKS_INITIALIZED = False

def _log_error(message: str) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message to log
    """
    logger.error(message)
    # Print directly to stderr for critical shell integration issues
    print(f"Rick Assistant Error: {message}", file=sys.stderr)

@safe_execute(show_user_message=False)
def precmd_hook() -> None:
    """
    Hook executed before the prompt is displayed.
    
    This function is called by ZSH's precmd hook before each prompt display.
    It's responsible for setting up the prompt environment, checking system
    status, and preparing for user input.
    """
    logger.debug("Executing precmd hook")
    
    # Get current working directory for context
    try:
        # Use Path object for better cross-platform support
        cwd = Path.cwd()
        cwd_path = normalize_path(cwd)
        if cwd_path:
            logger.debug(f"Current working directory: {cwd_path}")
        else:
            logger.warning("Could not normalize current working directory")
    except Exception as e:
        logger.warning(f"Could not get current working directory: {str(e)}")
    
    # Execute registered precmd hooks
    for hook in _PRECMD_HOOKS:
        try:
            hook()
        except Exception as e:
            logger.error(f"Error executing custom precmd hook: {str(e)}")

@safe_execute(show_user_message=False)
def preexec_hook(command: str) -> None:
    """
    Hook executed before command execution.
    
    This function is called by ZSH's preexec hook before executing a command.
    It's responsible for logging commands, checking for dangerous operations,
    and providing command suggestions.
    
    Args:
        command: Command string to be executed
    """
    # Validate and sanitize the command input to prevent injection
    if not command or not isinstance(command, str):
        logger.warning("Invalid command passed to preexec_hook")
        return
        
    # Sanitize the command for logging
    safe_command = sanitize_command_input(command)
    logger.debug(f"Executing preexec hook for command: {safe_command}")
    
    # Check if the command is potentially dangerous
    is_dangerous, reason = is_dangerous_command(command)
    if is_dangerous:
        logger.warning(f"Potentially dangerous command detected: {safe_command} - {reason}")
        # Could display warning to user here
    
    # Execute registered preexec hooks
    for hook in _PREEXEC_HOOKS:
        try:
            hook(command)
        except Exception as e:
            logger.error(f"Error executing custom preexec hook: {str(e)}")

@safe_execute(show_user_message=False)
def chpwd_hook(directory: Optional[str] = None) -> None:
    """
    Hook executed when changing directories.
    
    This function is called by ZSH's chpwd hook when the directory changes.
    It's responsible for updating context, checking the new directory,
    and loading directory-specific configurations.
    
    Args:
        directory: New directory path (uses current directory if None)
    """
    # Validate and normalize the directory path
    if directory is None:
        try:
            directory = Path.cwd()
        except Exception as e:
            logger.warning(f"Could not get current working directory: {str(e)}")
            return
    
    # Ensure directory is valid
    if isinstance(directory, str):
        # Convert string to Path
        dir_path = Path(directory)
    elif isinstance(directory, Path):
        dir_path = directory
    else:
        logger.warning(f"Invalid directory type passed to chpwd_hook: {type(directory)}")
        return
        
    # Normalize and validate the directory path
    normalized_path = normalize_path(dir_path)
    if not normalized_path:
        logger.warning(f"Could not normalize directory path: {directory}")
        return
    
    # Log the directory change using the normalized path
    logger.debug(f"Directory changed to: {normalized_path}")
    
    # Validate the directory exists, is accessible, and has appropriate permissions
    if not normalized_path.exists():
        logger.warning(f"Directory does not exist: {normalized_path}")
        return
        
    if not normalized_path.is_dir():
        logger.warning(f"Path is not a directory: {normalized_path}")
        return
        
    if not validate_path_permissions(normalized_path):
        logger.warning(f"Directory has insufficient permissions: {normalized_path}")
        return
        
    # Check if directory is within safe boundaries
    if not is_path_within_safe_directories(normalized_path):
        logger.warning(f"Directory is outside safe boundaries: {normalized_path}")
        # Could add additional safety measures here
    
    # Execute registered chpwd hooks
    for hook in _CHPWD_HOOKS:
        try:
            hook(str(normalized_path))
        except Exception as e:
            logger.error(f"Error executing custom chpwd hook: {str(e)}")

def validate_directory(directory: Union[str, Path]) -> Tuple[Optional[Path], Optional[str]]:
    """
    Validate a directory path for safety and accessibility.
    
    Args:
        directory: Directory path to validate
        
    Returns:
        Tuple of (normalized path or None, error message or None)
    """
    # Convert to Path if string
    if isinstance(directory, str):
        dir_path = Path(directory)
    elif isinstance(directory, Path):
        dir_path = directory
    else:
        return None, f"Invalid directory type: {type(directory)}"
    
    # Normalize the path
    normalized_path = normalize_path(dir_path)
    if not normalized_path:
        return None, f"Could not normalize directory path: {directory}"
    
    # Check existence
    if not normalized_path.exists():
        return None, f"Directory does not exist: {normalized_path}"
    
    # Check if it's a directory
    if not normalized_path.is_dir():
        return None, f"Path is not a directory: {normalized_path}"
    
    # Check permissions
    if not validate_path_permissions(normalized_path):
        return None, f"Directory has insufficient permissions: {normalized_path}"
    
    # Check safety boundaries
    if not is_path_within_safe_directories(normalized_path):
        return normalized_path, f"Warning: Directory is outside safe boundaries: {normalized_path}"
    
    # All checks passed
    return normalized_path, None

# Hook Registration Functions

def register_precmd_hook(callback: Callable[[], None]) -> bool:
    """
    Register a function to run before the prompt is displayed.
    
    Args:
        callback: Function to call before prompt display
        
    Returns:
        True if registration successful, False otherwise
    """
    if not callable(callback):
        logger.error("Precmd hook must be callable")
        return False
        
    if callback not in _PRECMD_HOOKS:
        _PRECMD_HOOKS.append(callback)
        logger.debug(f"Registered precmd hook: {callback.__name__}")
        return True
    else:
        logger.debug(f"Precmd hook already registered: {callback.__name__}")
        return False

def register_preexec_hook(callback: Callable[[str], None]) -> bool:
    """
    Register a function to run before command execution.
    
    Args:
        callback: Function to call before command execution,
                 should accept the command string as parameter
                 
    Returns:
        True if registration successful, False otherwise
    """
    if not callable(callback):
        logger.error("Preexec hook must be callable")
        return False
        
    if callback not in _PREEXEC_HOOKS:
        _PREEXEC_HOOKS.append(callback)
        logger.debug(f"Registered preexec hook: {callback.__name__}")
        return True
    else:
        logger.debug(f"Preexec hook already registered: {callback.__name__}")
        return False

def register_chpwd_hook(callback: Callable[[Optional[str]], None]) -> bool:
    """
    Register a function to run when directory changes.
    
    Args:
        callback: Function to call when directory changes,
                 should accept the directory string as parameter
                 
    Returns:
        True if registration successful, False otherwise
    """
    if not callable(callback):
        logger.error("Chpwd hook must be callable")
        return False
        
    if callback not in _CHPWD_HOOKS:
        _CHPWD_HOOKS.append(callback)
        logger.debug(f"Registered chpwd hook: {callback.__name__}")
        return True
    else:
        logger.debug(f"Chpwd hook already registered: {callback.__name__}")
        return False

def is_hook_registered(hook_type: str, callback: Callable) -> bool:
    """
    Check if a hook is already registered.
    
    Args:
        hook_type: Type of hook ('precmd', 'preexec', or 'chpwd')
        callback: Function to check
        
    Returns:
        True if hook is registered, False otherwise
    """
    if not callable(callback):
        return False
        
    if hook_type == 'precmd':
        return callback in _PRECMD_HOOKS
    elif hook_type == 'preexec':
        return callback in _PREEXEC_HOOKS
    elif hook_type == 'chpwd':
        return callback in _CHPWD_HOOKS
    else:
        logger.error(f"Unknown hook type: {hook_type}")
        return False

@safe_execute(default_return=False)
def initialize_hooks() -> bool:
    """
    Set up all hook registrations.
    
    Returns:
        True if initialization was successful
    """
    global _HOOKS_INITIALIZED
    
    if _HOOKS_INITIALIZED:
        logger.debug("Hooks already initialized")
        return True
    
    try:
        logger.info("Initializing ZSH hooks")
        # Currently, there's no additional setup beyond creating the hook lists,
        # which happens at module import time. This function exists for future
        # extensibility and to match the expected interface from plugin.py.
        _HOOKS_INITIALIZED = True
        return True
    except Exception as e:
        logger.error(f"Failed to initialize hooks: {str(e)}")
        return False

@safe_execute(default_return=False)
def cleanup_hooks() -> bool:
    """
    Clean up hooks on plugin deactivation.
    
    Returns:
        True if cleanup was successful
    """
    global _PRECMD_HOOKS, _PREEXEC_HOOKS, _CHPWD_HOOKS, _HOOKS_INITIALIZED
    
    try:
        logger.info("Cleaning up ZSH hooks")
        _PRECMD_HOOKS.clear()
        _PREEXEC_HOOKS.clear()
        _CHPWD_HOOKS.clear()
        _HOOKS_INITIALIZED = False
        return True
    except Exception as e:
        logger.error(f"Failed to clean up hooks: {str(e)}")
        return False

# Initialize hooks at module import time
if not _HOOKS_INITIALIZED:
    initialize_hooks()
