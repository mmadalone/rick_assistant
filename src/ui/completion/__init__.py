#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rick Assistant ZSH Completion Module

This module provides a comprehensive tab completion system for the Rick Assistant,
extending ZSH's built-in completion with Rick-themed features and enhanced safety.

Examples:
    from src.ui.completion import setup_completion, complete_command, complete_path
"""

import os
import sys
import importlib
from typing import List, Dict, Any, Optional, Union, Tuple

# Re-export completers for easy access
from .zsh_integration import setup_zsh_completion
from .command_completer import complete_command, get_command_description
from .path_completer import complete_path, complete_directory
from .option_completer import complete_option, format_completions
from .utils import get_completion_context, find_common_prefix

__all__ = [
    'setup_zsh_completion',
    'complete_command',
    'complete_path',
    'complete_directory',
    'complete_option',
    'format_completions',
    'get_completion_context',
    'find_common_prefix',
    'get_command_description',
] 