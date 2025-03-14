#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Completion Utilities for Rick Assistant

This module provides utility functions for the tab completion system,
including detecting completion contexts and handling common operations.
"""

import os
import sys
import re
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.path_safety import is_safe_path

# Initialize logger
logger = get_logger(__name__)

# Constants for completion types
COMPLETION_COMMAND = "command"
COMPLETION_PATH = "path" 
COMPLETION_DIRECTORY = "directory"
COMPLETION_OPTION = "option"
COMPLETION_GIT = "git"
COMPLETION_RICK = "rick"  # Rick Assistant specific commands

# Rick-themed rejection messages for unsafe paths
UNSAFE_PATH_MESSAGES = [
    "Nice try, *buuurp* but I'm not touching that path with a ten-foot portal gun.",
    "That path looks shadier than a deal with the Galactic Federation.",
    "Trying to get me to complete system paths? What's next, making me pass butter?",
    "I don't think so, Morty. That path could destroy the whole universe... or worse.",
    "Let me put this in terms you'll understand: NO.",
]

@safe_execute(default_return=COMPLETION_COMMAND)
def get_completion_context(text: str) -> str:
    """
    Determine the completion context based on input text.
    
    This analyzes the text to determine what type of completion should be used:
    command, path, directory, git commands, or Rick assistant commands.
    
    Args:
        text: The input text to analyze
        
    Returns:
        str: The detected completion context type
    """
    if not text:
        return COMPLETION_COMMAND
        
    # Check for path-like inputs
    if text.startswith('/') or text.startswith('./') or text.startswith('~/') or '/' in text:
        # Check if it's specifically looking for directories (ends with /)
        if text.endswith('/'):
            return COMPLETION_DIRECTORY
        return COMPLETION_PATH
    
    # Check for git command completion
    if text.startswith('git '):
        return COMPLETION_GIT
    
    # Check for Rick assistant commands (rick prefix or r-)
    if text.startswith('rick ') or text.startswith('r-'):
        return COMPLETION_RICK
        
    # Default to command completion
    return COMPLETION_COMMAND

@safe_execute(default_return="")
def find_common_prefix(options: List[str]) -> str:
    """
    Find the longest common prefix in a list of strings.
    
    Args:
        options: List of strings to find common prefix
        
    Returns:
        str: The longest common prefix, or empty string if none
    """
    if not options:
        return ""
    
    if len(options) == 1:
        return options[0]
        
    # Find common prefix
    prefix = os.path.commonprefix(options)
    return prefix

@safe_execute(default_return=False)
def is_wsl() -> bool:
    """
    Detect if running in Windows Subsystem for Linux.
    
    Returns:
        bool: True if running in WSL, False otherwise
    """
    # Method 1: Check for /proc/version containing Microsoft
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                return True
    except:
        pass
    
    # Method 2: Check for WSL environment variable
    if 'WSL_DISTRO_NAME' in os.environ:
        return True
    
    # Method 3: Check for Windows-specific paths in PATH
    path = os.environ.get('PATH', '')
    if '/mnt/c/' in path:
        return True
        
    return False

@safe_execute(default_return=None)
def check_zsh_version() -> Optional[str]:
    """
    Get the installed ZSH version.
    
    Returns:
        Optional[str]: ZSH version string, or None if not found
    """
    try:
        # Try to get zsh version using zsh command
        import subprocess
        result = subprocess.run(
            ['zsh', '--version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=1.0
        )
        
        if result.returncode == 0:
            version_match = re.search(r'zsh (\d+\.\d+(?:\.\d+)?)', result.stdout)
            if version_match:
                return version_match.group(1)
    except Exception as e:
        logger.debug(f"Error checking ZSH version: {e}")
    
    return None

@safe_execute(default_return=[])
def get_rick_completer_message() -> List[str]:
    """
    Get a random Rick-themed message about completion.
    
    Returns:
        List[str]: List of Rick-themed completion messages
    """
    import random
    
    messages = [
        "Completing stuff like a *burp* pro, Morty!",
        "Oh, you need me to finish your thoughts for you? Typical.",
        "Look at Mr. Lazy here, can't even finish typing commands.",
        "Tab completion: for when your brain is too small to remember full paths.",
        "Wubba lubba tab tab!",
        "In some dimension, you're smart enough to type the whole thing yourself.",
        "You're welcome for saving you those precious keystrokes.",
        "I could complete quantum equations, but here I am completing your basic commands.",
    ]
    
    return messages 