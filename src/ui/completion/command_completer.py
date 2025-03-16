#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Completion Module for Rick Assistant

This module handles completion for shell commands, supporting both native and 
Rick Assistant commands with rich descriptions and context-aware filtering.
"""

import os
import sys
import re
import shutil
import random
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union, Tuple

from src.utils.logger import get_logger
from src.utils.errors import safe_execute

from .utils import is_wsl

# Initialize logger
logger = get_logger(__name__)

# Rick-specific commands for completion
RICK_COMMANDS = {
    "rick-config": "Configure Rick Assistant settings",
    "rick-help": "Display help about Rick Assistant commands",
    "rick-enable": "Enable a specific Rick Assistant feature",
    "rick-disable": "Disable a specific Rick Assistant feature",
    "rick-info": "Show information about Rick Assistant",
    "rick-universe": "Switch to a different universe designation",
    "rick-status": "Show current status of Rick Assistant",
    "rick-quote": "Display a random Rick quote",
    "rick-reload": "Reload Rick Assistant configuration",
    "rick-debug": "Enable debug mode for Rick Assistant",
}

# Rick subcommands for the main 'rick' command
RICK_SUBCOMMANDS = {
    "help": "Show Rick Assistant help message",
    "version": "Show Rick Assistant version",
    "status": "Check Rick's status",
    "debug": "Toggle debug mode",
    "burp": "Make Rick burp",
    "cleanup": "Clean up temporary files",
    "prompt": "Configure prompt integration",
    "p10k": "Update Rick's Powerlevel10k integration",
    "diagnose": "Run diagnostics to troubleshoot setup",
    "menu": "Open Rick's interactive menu"
}

# Subcommands for 'rick prompt'
RICK_PROMPT_SUBCOMMANDS = {
    "segment": "Add Rick as a Powerlevel10k segment",
    "right_prompt": "Place Rick in the right side prompt",
    "command_output": "Show Rick's comments between commands",
    "custom_position": "Place Rick at a custom position in your prompt",
    "auto": "Automatically select the best mode for your terminal",
    "status": "Show current prompt integration mode"
}

# Common command categories - will be populated later
COMMAND_CATEGORIES = {}

@safe_execute(default_return={})
def _build_command_categories() -> Dict[str, List[str]]:
    """
    Build dictionary of command categories for organization.
    
    Returns:
        Dict[str, List[str]]: Command categories and their commands
    """
    categories = {
        "file": ["ls", "cat", "cp", "mv", "rm", "mkdir", "touch", "chmod", "chown", "find"],
        "process": ["ps", "top", "htop", "kill", "pkill", "bg", "fg", "jobs"],
        "network": ["ping", "curl", "wget", "ssh", "netstat", "ifconfig", "ip", "nmap"],
        "system": ["sudo", "su", "systemctl", "service", "reboot", "shutdown"],
        "text": ["grep", "sed", "awk", "cut", "sort", "uniq", "wc", "diff"],
        "package": ["apt", "apt-get", "yum", "dnf", "pacman", "brew", "dpkg"],
        "archive": ["tar", "zip", "unzip", "gzip", "gunzip"],
        "development": ["git", "make", "gcc", "g++", "python", "python3", "npm", "cargo"],
        "rick": list(RICK_COMMANDS.keys()),
    }
    
    return categories

# Build command categories
COMMAND_CATEGORIES = _build_command_categories()

@safe_execute(default_return=[])
def complete_command(partial: str, shell_path: Optional[str] = None) -> List[str]:
    """
    Complete partial shell commands using available system commands.
    
    This function attempts to find matches for a partial command by checking
    common executable paths. It works across platforms and supports completing
    both commands and their arguments.
    
    Args:
        partial: Partial command to complete.
        shell_path: Override for PATH environment variable.
            If None, uses the system PATH.
    
    Returns:
        List of matching command completions (empty if none found).
        
    Examples:
        >>> complete_command("py")  # Might return ["python", "python3", "pyenv"]
        >>> complete_command("git ")  # Might complete git subcommands
    """
    if not partial:
        return []
        
    # Check for Rick Assistant commands first
    if partial.startswith("rick-") or partial.startswith("r-"):
        return _complete_rick_command(partial)
    
    # Check for rick subcommands if input starts with "rick "
    if partial.startswith("rick "):
        return _complete_rick_subcommand(partial[5:])  # Remove "rick " prefix
        
    # Check git subcommands if input starts with "git "
    if partial.startswith("git "):
        return _complete_git_command(partial)

    # Determine platform-appropriate shell path
    if shell_path is None:
        if sys.platform == 'win32':
            # Use cmd.exe on Windows by default
            shell_path = os.environ.get('COMSPEC', 'cmd.exe')
        else:
            # Use user's default shell on Unix, fallback to /bin/sh
            shell_path = os.environ.get('SHELL', '/bin/sh')
    
    logger.debug(f"Using shell: {shell_path} for command completion")
        
    # Special handling for WSL to handle path issues
    if is_wsl():
        return _complete_command_wsl(partial)
    
    try:
        # Use appropriate completion mechanism based on platform
        if sys.platform == 'win32':
            return _complete_command_windows(partial)
        else:
            return _complete_command_unix(partial, shell_path)
    except Exception as e:
        logger.error(f"Error completing command: {e}")
        
        # Fallback: Try finding executables in PATH
        return _complete_command_fallback(partial)

@safe_execute(default_return=[])
def _complete_command_unix(partial: str, shell_path: str) -> List[str]:
    """
    Complete commands on Unix-like systems.
    
    Args:
        partial: Partial command to complete
        shell_path: Path to shell executable
        
    Returns:
        List of matching completions
    """
    import subprocess
    import tempfile
    
    # Create a temporary file with appropriate permissions
    fd, temp_path = tempfile.mkstemp(suffix='.sh', prefix='rick_completion_')
    try:
        with os.fdopen(fd, 'w') as f:
            # Use compgen for bash or zsh compatible shells
            # Add safeguards against command injection
            safe_partial = partial.replace('"', '\\"')
            
            if os.path.basename(shell_path) in ('zsh', 'bash'):
                f.write(f"""
#!/usr/bin/env {os.path.basename(shell_path)}
compgen -c "{safe_partial}" 2>/dev/null || echo "__NO_COMPLETIONS__"
""")
            else:
                # Fallback for other shells
                f.write(f"""
#!/bin/sh
echo $(ls -1 /usr/bin | grep "^{safe_partial}" 2>/dev/null)
""")
        
        # Set as executable
        os.chmod(temp_path, 0o700)
        
        # Run the completion command with timeout to prevent hanging
        try:
            output = subprocess.check_output(
                [shell_path, temp_path],
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=2.0  # Add timeout to prevent hanging
            )
        except subprocess.TimeoutExpired:
            logger.warning("Command completion timed out")
            return []
            
        # Process the output
        if "__NO_COMPLETIONS__" in output:
            return []
            
        completions = output.strip().split('\n')
        return [c for c in completions if c and c.startswith(partial)]
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

@safe_execute(default_return=[])
def _complete_command_windows(partial: str) -> List[str]:
    """
    Complete commands on Windows systems.
    
    Args:
        partial: Partial command to complete
        
    Returns:
        List of matching completions
    """
    completions = []
    
    # Check commands in PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for directory in path_dirs:
        try:
            if not os.path.isdir(directory):
                continue
                
            for file in os.listdir(directory):
                # Check for executables and batch files
                if (file.startswith(partial) and 
                    (file.lower().endswith(('.exe', '.bat', '.cmd')) or 
                     os.access(os.path.join(directory, file), os.X_OK))):
                    completions.append(file)
        except (PermissionError, FileNotFoundError):
            pass
            
    return sorted(set(completions))

@safe_execute(default_return=[])
def _complete_command_wsl(partial: str) -> List[str]:
    """
    Complete commands specifically for WSL environment.
    
    Args:
        partial: Partial command to complete
        
    Returns:
        List of matching completions
    """
    completions = []
    
    # First check Linux paths (prioritize these)
    for directory in ['/usr/bin', '/bin', '/usr/local/bin']:
        try:
            if not os.path.isdir(directory):
                continue
            
            for file in os.listdir(directory):
                if file.startswith(partial) and os.access(os.path.join(directory, file), os.X_OK):
                    completions.append(file)
        except (PermissionError, FileNotFoundError):
            pass
    
    # Add system-specific commands from PATH but avoid Windows executables
    for directory in os.environ.get('PATH', '').split(os.pathsep):
        # Skip Windows paths to avoid duplicates and Windows-specific commands
        if '/mnt/' in directory:
            continue
            
        try:
            if not os.path.isdir(directory):
                continue
            
            for file in os.listdir(directory):
                if file.startswith(partial) and os.access(os.path.join(directory, file), os.X_OK):
                    completions.append(file)
        except (PermissionError, FileNotFoundError):
            pass
    
    return sorted(set(completions))

@safe_execute(default_return=[])
def _complete_command_fallback(partial: str) -> List[str]:
    """
    Fallback method for command completion that works across platforms.
    
    Args:
        partial: Partial command to complete
        
    Returns:
        List of matching completions
    """
    completions = []
    
    # Check commands in PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for directory in path_dirs:
        try:
            if not os.path.isdir(directory):
                continue
                
            for file in os.listdir(directory):
                if file.startswith(partial) and os.access(os.path.join(directory, file), os.X_OK):
                    completions.append(file)
        except (PermissionError, FileNotFoundError):
            pass
            
    return sorted(set(completions))

@safe_execute(default_return=[])
def _complete_rick_command(partial: str) -> List[str]:
    """
    Complete Rick Assistant specific commands.
    
    Args:
        partial: Partial Rick command to complete
        
    Returns:
        List of matching Rick command completions
    """
    # Handle both "rick-" and "r-" prefixes
    if partial.startswith("r-"):
        # Convert to rick- format for matching, then convert back for results
        rick_partial = "rick-" + partial[2:]
        rick_commands = [cmd for cmd in RICK_COMMANDS.keys() if cmd.startswith(rick_partial)]
        return ["r-" + cmd[5:] for cmd in rick_commands]  # Convert back to r- format
        
    # Standard rick- prefix
    rick_commands = [cmd for cmd in RICK_COMMANDS.keys() if cmd.startswith(partial)]
    return rick_commands

@safe_execute(default_return=[])
def _complete_git_command(partial: str) -> List[str]:
    """
    Complete git subcommands.
    
    Args:
        partial: Partial git command to complete
        
    Returns:
        List of matching git command completions
    """
    git_cmd = partial[4:].strip()  # Remove "git " prefix
    
    # Common git commands for completion
    git_commands = [
        'add', 'branch', 'checkout', 'clone', 'commit', 'diff', 'fetch', 
        'init', 'log', 'merge', 'pull', 'push', 'rebase', 'reset', 
        'status', 'tag'
    ]
    
    if not git_cmd:
        # Complete the git command itself
        return ['git ' + cmd for cmd in git_commands]
    elif not ' ' in git_cmd:
        # Complete the first level git subcommand
        return ['git ' + cmd for cmd in git_commands if cmd.startswith(git_cmd)]
    else:
        # For git commands with arguments, we would handle differently based on subcommand
        # This could be expanded for specific git subcommands
        return []

@safe_execute(default_return=[])
def _complete_rick_subcommand(partial: str) -> List[str]:
    """
    Complete subcommands for the main 'rick' command.
    
    Args:
        partial: Partial subcommand to complete (without the 'rick ' prefix)
        
    Returns:
        List of matching rick subcommand completions
    """
    # Handle nested subcommands
    if partial.startswith("prompt "):
        # Handle rick prompt subcommands
        prompt_partial = partial[7:].strip()  # Remove "prompt " prefix
        prompt_subcommands = [f"prompt {cmd}" for cmd in RICK_PROMPT_SUBCOMMANDS.keys() 
                             if cmd.startswith(prompt_partial)]
        return prompt_subcommands
    elif partial.startswith("menu "):
        # Handle rick menu subcommands
        menu_partial = partial[5:].strip()  # Remove "menu " prefix
        menu_options = ["main", "test", "settings", "tools"]
        return [f"menu {opt}" for opt in menu_options if opt.startswith(menu_partial)]
    
    # Handle first-level subcommands
    subcommands = []
    for cmd in RICK_SUBCOMMANDS.keys():
        if cmd.startswith(partial):
            subcommands.append(cmd)
    
    return subcommands

@safe_execute(default_return=None)
def get_command_description(command: str) -> Optional[str]:
    """
    Get the description for a command.
    
    Args:
        command: Command to get description for
        
    Returns:
        Optional description of the command, or None if not found
    """
    # Check if it's a Rick command with rick- prefix
    if command in RICK_COMMANDS:
        return RICK_COMMANDS[command]
    
    # Check if it's a rick subcommand (format: "rick help")
    if command.startswith("rick "):
        subcommand = command[5:]  # Remove "rick " prefix
        
        # Handle nested subcommands
        if subcommand.startswith("prompt "):
            prompt_subcommand = subcommand[7:]  # Remove "prompt " prefix
            if prompt_subcommand in RICK_PROMPT_SUBCOMMANDS:
                return RICK_PROMPT_SUBCOMMANDS[prompt_subcommand]
        
        # Handle first-level subcommands
        if subcommand in RICK_SUBCOMMANDS:
            return RICK_SUBCOMMANDS[subcommand]
    
    # Try to find command category
    for category, commands in COMMAND_CATEGORIES.items():
        if command in commands:
            return f"{category.capitalize()} command: {command}"
    
    # Try to get description from man pages (Unix/Linux only)
    if sys.platform != 'win32':
        try:
            result = subprocess.run(
                ['man', '-f', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=1.0
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    
    # Default description
    return f"Shell command: {command}" 