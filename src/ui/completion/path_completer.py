#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Path Completion Module for Rick Assistant

This module handles completion for file paths, including safety checks
to prevent accessing sensitive or dangerous paths.
"""

import os
import sys
import re
import glob
import random
from typing import List, Dict, Any, Optional, Union, Tuple

from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.path_safety import is_safe_path

from .utils import UNSAFE_PATH_MESSAGES, is_wsl

# Initialize logger
logger = get_logger(__name__)

# Special directories to prioritize in completions
PRIORITY_DIRS = [
    "Documents",
    "Downloads",
    "Desktop",
    "Projects",
    "src",
    "data",
    "tests",
]

@safe_execute(default_return=[])
def complete_path(partial: str) -> List[str]:
    """
    Complete partial file paths with safety checks.
    
    This function finds matching file paths for a given partial path,
    expanding ~ to home directory and applying safety checks to prevent
    access to sensitive system paths.
    
    Args:
        partial: Partial path to complete
        
    Returns:
        List of matching path completions (empty if none found or unsafe)
        
    Examples:
        >>> complete_path("~/Doc")  # Might return ["~/Documents/"]
        >>> complete_path("./src/")  # Might return files/dirs in ./src/
    """
    if not partial:
        return []
    
    # Expand ~ to home directory
    expanded_partial = os.path.expanduser(partial)
    
    # Safety check - don't complete unsafe paths
    if not is_safe_path(expanded_partial):
        logger.warning(f"Unsafe path completion attempt: {partial}")
        return []
    
    # Handle special case for WSL - convert Windows paths
    if is_wsl() and partial.startswith('/mnt/'):
        return _complete_wsl_path(partial)
    
    # Get the directory to search in and the prefix to match
    if os.path.isdir(expanded_partial):
        # If the partial path is a directory, list its contents
        search_dir = expanded_partial
        prefix = ""
    else:
        # Otherwise, get the directory and filename prefix
        search_dir = os.path.dirname(expanded_partial) or "."
        prefix = os.path.basename(expanded_partial)
    
    # Ensure search_dir exists and is accessible
    if not os.path.exists(search_dir) or not os.access(search_dir, os.R_OK):
        return []
    
    try:
        # Get all matching entries in the directory
        entries = os.listdir(search_dir)
        matches = [entry for entry in entries if entry.startswith(prefix)]
        
        # Prioritize directories and common file types
        matches = _prioritize_completions(matches, search_dir)
        
        # Format the results
        if os.path.dirname(expanded_partial):
            # If there was a directory part, preserve it
            base_dir = os.path.dirname(partial)
            if not base_dir.endswith('/'):
                base_dir += '/'
            completions = [base_dir + match for match in matches]
        else:
            # Otherwise, just return the matches
            completions = matches
        
        # Add trailing slash to directories for easier navigation
        completions = [f"{comp}/" if os.path.isdir(os.path.expanduser(comp)) else comp 
                       for comp in completions]
                       
        return completions
    except Exception as e:
        logger.error(f"Error completing path '{partial}': {e}")
        return []

@safe_execute(default_return=[])
def complete_directory(partial: str) -> List[str]:
    """
    Complete partial paths, returning only directories.
    
    Similar to complete_path but filters results to only include directories.
    
    Args:
        partial: Partial path to complete
        
    Returns:
        List of matching directory completions (empty if none found or unsafe)
    """
    # Get all path completions
    all_completions = complete_path(partial)
    
    # Filter to only directories (ending with /)
    return [comp for comp in all_completions if comp.endswith('/')]

@safe_execute(default_return=[])
def _complete_wsl_path(partial: str) -> List[str]:
    """
    Handle path completion specifically for WSL paths.
    
    Args:
        partial: Partial path to complete (WSL format)
        
    Returns:
        List of matching path completions
    """
    # Special handling for /mnt/ paths in WSL
    try:
        # Convert /mnt/c/... to C:\...
        if partial.startswith('/mnt/') and len(partial) >= 6:
            drive_letter = partial[5].upper()
            windows_path = f"{drive_letter}:{partial[6:]}"
            
            # Safety check for Windows path
            if not is_safe_path(windows_path):
                logger.warning(f"Unsafe Windows path completion attempt: {windows_path}")
                return []
                
            # Use glob to find matches
            if os.path.isdir(partial):
                matches = glob.glob(f"{partial}/*")
            else:
                matches = glob.glob(f"{partial}*")
                
            # Convert back to WSL paths
            return sorted([path for path in matches])
            
        # Regular WSL path
        return complete_path(partial)
    except Exception as e:
        logger.error(f"Error completing WSL path: {e}")
        return []

@safe_execute(default_return=[])
def _prioritize_completions(matches: List[str], search_dir: str) -> List[str]:
    """
    Prioritize completions by type and relevance.
    
    Args:
        matches: List of matching filenames
        search_dir: Directory these matches are from
        
    Returns:
        Sorted list with priorities applied
    """
    # Create buckets for different types
    directories = []
    priority_files = []
    regular_files = []
    
    # Sort matches into appropriate buckets
    for match in matches:
        full_path = os.path.join(search_dir, match)
        
        if os.path.isdir(full_path):
            if match in PRIORITY_DIRS:
                # Priority directories go first
                directories.insert(0, match)
            else:
                # Other directories
                directories.append(match)
        elif any(match.endswith(ext) for ext in ['.py', '.sh', '.zsh', '.json', '.txt', '.md']):
            # Common file types given priority
            priority_files.append(match)
        else:
            # Everything else
            regular_files.append(match)
    
    # Sort each group alphabetically
    directories.sort()
    priority_files.sort()
    regular_files.sort()
    
    # Combine the groups in priority order
    return directories + priority_files + regular_files

@safe_execute(default_return=False)
def path_exists_safely(path: str) -> bool:
    """
    Check if a path exists with additional safety checks.
    
    Args:
        path: Path to check
        
    Returns:
        True if path exists and is safe, False otherwise
    """
    # Expand user directory
    expanded_path = os.path.expanduser(path)
    
    # First check if it's safe
    if not is_safe_path(expanded_path):
        return False
    
    # Then check if it exists
    return os.path.exists(expanded_path)

@safe_execute(default_return=None)
def get_path_description(path: str) -> Optional[str]:
    """
    Get a description for a path.
    
    Args:
        path: Path to describe
        
    Returns:
        Description of the path, or None if unavailable
    """
    try:
        expanded_path = os.path.expanduser(path)
        
        # Safety check
        if not is_safe_path(expanded_path):
            return random.choice(UNSAFE_PATH_MESSAGES)
        
        if not os.path.exists(expanded_path):
            return "Path does not exist"
        
        # Get basic info
        if os.path.isdir(expanded_path):
            try:
                item_count = len(os.listdir(expanded_path))
                return f"Directory with {item_count} items"
            except:
                return "Directory (cannot access contents)"
        else:
            # It's a file
            try:
                size = os.path.getsize(expanded_path)
                if size < 1024:
                    size_str = f"{size} bytes"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                
                return f"File, {size_str}"
            except:
                return "File (cannot access details)"
    except Exception as e:
        logger.error(f"Error getting path description: {e}")
        return None 