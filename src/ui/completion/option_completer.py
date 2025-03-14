#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Option Completion Module for Rick Assistant

This module handles completion from custom option lists,
including formatting and presentation of completions.
"""

import os
import sys
import re
import shutil
import random
from typing import List, Dict, Any, Optional, Union, Tuple

from src.utils.logger import get_logger
from src.utils.errors import safe_execute

# Initialize logger
logger = get_logger(__name__)

@safe_execute(default_return=[])
def complete_option(partial: str, options: List[str]) -> List[str]:
    """
    Complete input from a custom list of options.
    
    This finds matches from a list of predefined options,
    useful for custom command arguments and choices.
    
    Args:
        partial: Partial text to complete
        options: List of possible options to match against
        
    Returns:
        List of matching option completions
        
    Examples:
        >>> complete_option("ap", ["apple", "apricot", "banana"])
        ["apple", "apricot"]
    """
    if not partial or not options:
        return []
        
    # Find all options that start with the partial text
    matches = [opt for opt in options if opt.startswith(partial)]
    
    # Sort alphabetically
    matches.sort()
    
    return matches

@safe_execute(default_return="")
def format_completions(completions: List[str], partial: str = "", 
                       columns: int = 0, add_rick_comment: bool = True) -> str:
    """
    Format a list of completions for display.
    
    This creates a formatted multi-column display of completions
    with optional Rick personality touches.
    
    Args:
        completions: List of completions to display
        partial: The partial text being completed
        columns: Number of columns (0 for auto-detect)
        add_rick_comment: Whether to add Rick's personality
        
    Returns:
        Formatted string ready for display
    """
    if not completions:
        return ""
    
    try:
        # Auto-detect terminal width if columns is 0
        if columns <= 0:
            terminal_width = shutil.get_terminal_size().columns
        else:
            terminal_width = columns
            
        # Find the longest completion for padding
        max_length = max(len(comp) for comp in completions) + 2
        
        # Calculate number of columns that will fit
        num_columns = max(1, terminal_width // max_length)
        
        # Sort completions alphabetically
        completions = sorted(completions)
        
        # Build the formatted output row by row
        output = []
        
        # Add Rick-themed header if requested
        if add_rick_comment and completions:
            rick_headers = [
                f"*Burp* Here are {len(completions)} options for '{partial}':",
                f"What do you want, {len(completions)} choices not enough?",
                f"Behold my genius - {len(completions)} completions for your tiny brain:",
                f"Choose wisely from these {len(completions)} options, or don't, I don't care:",
                f"The multiverse gives you {len(completions)} possibilities:",
            ]
            output.append(random.choice(rick_headers))
            output.append("")
            
        # Build the rows for display
        rows = []
        row = []
        for i, comp in enumerate(completions):
            if partial and comp.startswith(partial):
                # Highlight the matching part if applicable
                match_part = comp[:len(partial)]
                rest_part = comp[len(partial):]
                formatted_comp = f"\033[1m{match_part}\033[0m{rest_part}"
            else:
                formatted_comp = comp
                
            row.append(formatted_comp.ljust(max_length))
            
            # Start a new row when we reach the column limit
            if (i + 1) % num_columns == 0:
                rows.append("".join(row))
                row = []
                
        # Add the last partial row if any
        if row:
            rows.append("".join(row))
            
        # Combine all rows and add to output
        output.extend(rows)
        
        # Add Rick-themed footer if requested
        if add_rick_comment and len(completions) > 5:
            rick_footers = [
                "Too many options? Well, that's your problem.",
                "Just pick one already! *burp*",
                "In infinite universes, all of these are the wrong choice.",
                "Or just keep hitting tab like a mindless drone.",
                "I could've solved the entropy crisis in the time it takes you to decide.",
            ]
            output.append("")
            output.append(random.choice(rick_footers))
            
        return "\n".join(output)
    except Exception as e:
        logger.error(f"Error formatting completions: {e}")
        # Fallback to simple format
        return "\n".join(completions)

@safe_execute(default_return=[])
def filter_options_by_prefix(partial: str, options: List[str]) -> List[str]:
    """
    Filter options by prefix with case insensitivity.
    
    Args:
        partial: Prefix to match
        options: List of options to filter
        
    Returns:
        Filtered list of options
    """
    if not partial:
        return options
        
    # Case insensitive prefix matching
    return [opt for opt in options if opt.lower().startswith(partial.lower())]

@safe_execute(default_return=[])
def filter_options_fuzzy(partial: str, options: List[str]) -> List[str]:
    """
    Filter options with fuzzy matching.
    
    Args:
        partial: Text to fuzzy match
        options: List of options to filter
        
    Returns:
        Filtered list of options sorted by match quality
    """
    if not partial:
        return options
        
    # Convert partial to lowercase for matching
    partial_lower = partial.lower()
    
    # Build regex pattern for fuzzy matching
    pattern = '.*'.join(re.escape(char) for char in partial_lower)
    regex = re.compile(pattern)
    
    # Find all matches
    matches = []
    for opt in options:
        match = regex.search(opt.lower())
        if match:
            # Calculate match quality (lower is better)
            # Based on position and match length
            quality = match.start() + (match.end() - match.start()) / len(opt)
            matches.append((opt, quality))
    
    # Sort by match quality (best first)
    matches.sort(key=lambda x: x[1])
    
    # Return just the options
    return [m[0] for m in matches] 