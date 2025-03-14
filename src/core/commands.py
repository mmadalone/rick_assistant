"""
Command processing for Rick Assistant.

This module handles command interception, processing,
and Rick's unique personality.
"""

# Import from standard library
import os
import re
import shlex
import subprocess
import argparse
import random
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from pathlib import Path

# Import from Rick Assistant modules
from src.utils.logger import get_logger
from src.utils.errors import safe_execute, ShellError
from src.utils.validation import (
    is_valid_path, sanitize_path, sanitize_command_input,
    validate_string, is_dangerous_command
)
from src.utils.config import get_config_value
from src.ui.text import colored, format_error
from src import __version__, __author__, __email__  # Add version info at module level

# Initialize module logger
logger = get_logger("commands")

# Terminal color constants
TEXT_RED = "\033[31m"
TEXT_GREEN = "\033[32m"
TEXT_YELLOW = "\033[33m"
TEXT_BLUE = "\033[34m"
TEXT_CYAN = "\033[36m"
TEXT_BOLD = "\033[1m"
TEXT_RESET = "\033[0m"

# Helper functions for terminal output
def print_error(message: str):
    """Print error message with Rick-styled formatting."""
    print(f"{TEXT_RED}{message}{TEXT_RESET}")

# Command type constants
SHELL_COMMAND = "shell"       # Regular shell commands
ASSISTANT_COMMAND = "rick"    # Commands directed at Rick (!cmd)
BUILTIN_COMMAND = "builtin"   # ZSH builtin commands
ALIAS_COMMAND = "alias"       # Aliased commands
SPECIAL_COMMAND = "special"   # Special handling commands

# Common command typos and corrections
COMMON_TYPOS = {
    "ls-la": "ls -la",
    "cd..": "cd ..",
    "gti": "git",
    "grpe": "grep",
    "pythno": "python",
    "pytohn": "python",
    "pyhton": "python",
    "pdw": "pwd",
    "mkidr": "mkdir",
    "rmdir": "rmdir",
    "cta": "cat",
    "touhc": "touch",
    "rm -f": "rm -rf",
    "chmdo": "chmod",
    "chomd": "chmod",
    "chwon": "chown",
    "xit": "exit",
    "exti": "exit",
    "ehco": "echo",
    "sudp": "sudo",
    "nano": "nano",  # Not a typo but Rick would suggest vim
    "namo": "nano",
    "sl": "ls"
}

# Potentially dangerous command patterns
DANGEROUS_COMMANDS = [
    (r"rm\s+-rf\s+[\/~]", "Could delete important system files"),
    (r"dd\s+.*of\s*=\s*\/dev\/(disk|sd)", "Could overwrite disk device"),
    (r"chmod\s+-R\s+777\s+[\/~]", "Insecure permissions for system directories"),
    (r":(){ :\|:& };:", "Fork bomb detected"),
    (r"> \/etc\/(passwd|shadow)", "Attempting to overwrite system files"),
    (r"sudo\s+rm\s+-rf\s+\/\s+--no-preserve-root", "System deletion attempt"),
    (r"mv\s+[^\/]+\s+\/dev\/null", "Moving files to /dev/null (deletion)"),
    (r"^\s*shutdown", "System shutdown command"),
    (r"^\s*reboot", "System reboot command"),
    (r"^\s*halt", "System halt command"),
    (r"mkfs\s+\/dev\/", "Formatting disk device"),
    (r"wget\s+.*\s+\|\s+bash", "Piping web content to bash"),
    (r"curl\s+.*\s+\|\s+bash", "Piping web content to bash"),
    (r"find\s+.*\s+-delete", "Mass deletion with find"),
    (r"^\s*sudo\s+su\s*$", "Elevating to root shell"),
    (r"^\s*su\s*$", "Changing user to root")
]

def test_shlex_split(cmd: str) -> list:
    """
    Test function to debug shlex splitting behavior.
    
    Args:
        cmd: Command string to split
        
    Returns:
        List of tokens
    """
    import shlex
    try:
        tokens = shlex.split(cmd, posix=True)
        logger.debug(f"Shlex split result for '{cmd}': {tokens}")
        return tokens
    except Exception as e:
        logger.error(f"Error in shlex split: {str(e)}")
        return [cmd]

def process_rick_command(args_str: str) -> Dict[str, Any]:
    """
    Process a command directed at Rick.
    
    Args:
        args_str: Command arguments as a string
        
    Returns:
        Dict with processing results
    """
    logger.info(f"Rick command received: {args_str}")
    
    # Split the command into command and args
    parts = args_str.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else ""
    args = parts[1] if len(parts) > 1 else ""
    
    # Handle specific commands
    if command == "help":
        return {
            "type": ASSISTANT_COMMAND,
            "success": True,
            "output": "🧪 Rick Assistant Command Help\n" +
                     "==============================\n" +
                     "!help - Display this help message\n" +
                     "!config - Adjust Rick Assistant settings\n" +
                     "!rick - Get a random Rick quote\n" +
                     "!sass <level> - Set Rick's sass level (1-10)\n" +
                     "!explain - Explain the last command\n",
            "command": command,
            "args": args
        }
    elif command == "rick":
        # Get a random Rick quote
        from src.core.rick import get_catchphrase
        return {
            "type": ASSISTANT_COMMAND,
            "success": True,
            "output": f"🧪 Rick says: {get_catchphrase()}",
            "command": command,
            "args": args
        }
    else:
        # Unknown command
        return {
            "type": ASSISTANT_COMMAND,
            "success": False,
            "error": f"Unknown Rick command: {command}",
            "output": f"🧪 Rick says: I don't know what '{command}' is supposed to mean. Try !help.",
            "command": command,
            "args": args
        }

def split_command_with_quotes(cmd: str) -> list:
    """
    Split a command string into tokens while preserving quoted sections.
    This is a custom implementation to handle quotes in a more robust way.
    
    Args:
        cmd: Command string to split
        
    Returns:
        List of tokens
    """
    tokens = []
    current_token = ""
    in_double_quotes = False
    in_single_quotes = False
    escape_next = False
    
    for char in cmd:
        # Handle escape character
        if char == '\\' and not escape_next:
            escape_next = True
            continue
        
        # Handle double quotes
        if char == '"' and not in_single_quotes and not escape_next:
            in_double_quotes = not in_double_quotes  # Toggle quote state
            # Don't add the quote character to the token
            continue
        
        # Handle single quotes
        if char == "'" and not in_double_quotes and not escape_next:
            in_single_quotes = not in_single_quotes  # Toggle quote state
            # Don't add the quote character to the token
            continue
        
        # Handle space as token separator (but only outside of quotes)
        if char.isspace() and not in_double_quotes and not in_single_quotes and not escape_next:
            if current_token:  # Only add non-empty tokens
                tokens.append(current_token)
                current_token = ""
            continue
        
        # Add character to current token
        current_token += char
        escape_next = False
    
    # Add the last token if not empty
    if current_token:
        tokens.append(current_token)
    
    # Log the result for debugging
    logger.debug(f"Split command '{cmd}' into tokens: {tokens}")
    
    return tokens

@safe_execute()
def parse_command(cmd: str) -> Dict[str, Any]:
    """
    Parse command into components for easier processing.
    
    Args:
        cmd: The command string to parse
        
    Returns:
        Dict containing parsed command components
    """
    if not validate_string(cmd):
        return {"command": "", "args": [], "raw": "", "valid": False}
    
    # First preserve the raw command
    raw_cmd = cmd.strip()
    
    try:
        # For parsing, we'll work with the raw command directly
        # This avoids issues with quote escaping in sanitize_command_input
        import shlex
        
        # Parse with posix=True to handle quoted strings correctly
        tokens = shlex.split(raw_cmd, posix=True)
        
        command = tokens[0] if tokens else ""
        args = tokens[1:] if len(tokens) > 1 else []
        
        # Determine if this is a Rick assistant command (starts with !)
        is_rick_command = command.startswith("!")
        
        # Now sanitize each token individually for security
        command = sanitize_command_input(command) if command else ""
        sanitized_args = [sanitize_command_input(arg) for arg in args]
        
        result = {
            "command": command,
            "args": args,  # Keep the unsanitized args for parsing
            "sanitized_args": sanitized_args,  # Store sanitized version
            "raw": raw_cmd,
            "valid": bool(command),
            "is_rick_command": is_rick_command,
            "tokens": tokens
        }
        
        logger.debug(f"Parse result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error parsing command: {str(e)}")
        return {
            "command": raw_cmd,
            "args": [],
            "sanitized_args": [],
            "raw": raw_cmd,
            "valid": False,
            "is_rick_command": False,
            "tokens": [raw_cmd]
        }

@safe_execute()
def get_command_type(cmd: str) -> str:
    """
    Determine the type of command (shell, assistant, builtin, etc.)
    
    Args:
        cmd: The command string
        
    Returns:
        Command type as string
    """
    if not validate_string(cmd):
        return SHELL_COMMAND
    
    cmd = cmd.strip()
    
    # Check if it's a Rick assistant command
    if cmd.startswith("!"):
        return ASSISTANT_COMMAND
    
    # Check if it's a ZSH builtin
    builtin_commands = ["cd", "source", ".", "exit", "logout", "history", 
                       "alias", "unalias", "export", "setopt", "unsetopt"]
    
    parsed = parse_command(cmd)
    command = parsed.get("command", "")
    
    if command in builtin_commands:
        return BUILTIN_COMMAND
    
    # Check if it's an alias (would normally check against user's aliases)
    # This is a placeholder - would need hook to ZSH to check actual aliases
    # For now, just return shell command
    
    return SHELL_COMMAND

@safe_execute()
def get_command_context(cmd: str, path: Optional[str] = None, history: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get context information for the command.
    
    Args:
        cmd: The command string
        path: Current working directory (default: None)
        history: Command history (default: None)
        
    Returns:
        Dict containing context information
    """
    context = {
        "current_dir": os.getcwd() if path is None else path,
        "cmd_type": get_command_type(cmd),
        "timestamp": os.times(),
        "is_dangerous": False,
        "danger_reason": "",
        "suggestions": []
    }
    
    # Check if command is dangerous
    is_danger, reason = is_dangerous_command(cmd)
    if is_danger:
        context["is_dangerous"] = True
        context["danger_reason"] = reason
    
    # Look for spelling errors and suggestions
    suggestions = detect_common_typos(cmd)
    if suggestions:
        context["suggestions"] = suggestions
    
    # Add command history context if provided
    if history and isinstance(history, list):
        context["history"] = history[-10:] if len(history) > 10 else history
        
        # Look for patterns in history
        if len(history) >= 3:
            repeated_cmds = [c for c in history[-3:] if c == cmd]
            if len(repeated_cmds) >= 2:
                context["repeated_command"] = True
    
    return context

@safe_execute()
def should_intercept_command(cmd: str) -> bool:
    """
    Determine if command needs special handling by Rick Assistant.
    
    Args:
        cmd: The command string
        
    Returns:
        Boolean indicating if command should be intercepted
    """
    if not validate_string(cmd):
        return False
    
    cmd_type = get_command_type(cmd)
    
    # Always intercept Rick commands
    if cmd_type == ASSISTANT_COMMAND:
        return True
    
    # Get parsed command components
    parsed = parse_command(cmd)
    command = parsed.get("command", "")
    
    # Check if command is dangerous
    is_danger, _ = is_dangerous_command(cmd)
    if is_danger:
        return True
    
    # Check if we have a typo correction
    if detect_common_typos(cmd):
        return True
    
    # Get intercept settings from config
    intercept_dangerous = get_config_value("commands.intercept_dangerous", True)
    intercept_typos = get_config_value("commands.intercept_typos", True)
    intercept_suggestions = get_config_value("commands.intercept_suggestions", True)
    
    # Configure which commands to intercept based on settings
    if not (intercept_dangerous or intercept_typos or intercept_suggestions):
        # If all interception is disabled, only intercept assistant commands
        return cmd_type == ASSISTANT_COMMAND
    
    return is_danger or bool(detect_common_typos(cmd))

@safe_execute()
def detect_common_typos(cmd: str) -> Optional[str]:
    """
    Detect common command typos and return corrections.
    
    Args:
        cmd: The command string
        
    Returns:
        Corrected command string or None if no typos found
    """
    if not validate_string(cmd):
        return None
    
    parsed = parse_command(cmd)
    command = parsed.get("command", "")
    
    # Check if the command is in our typo dictionary
    if command in COMMON_TYPOS:
        corrected_cmd = cmd.replace(command, COMMON_TYPOS[command], 1)
        return corrected_cmd
    
    # Check for close matches (simple implementation)
    # A more sophisticated implementation would use Levenshtein distance
    for typo, correction in COMMON_TYPOS.items():
        # Check if the typo is a substring of the command
        if command.startswith(typo) and typo != correction:
            corrected_cmd = cmd.replace(typo, correction, 1)
            return corrected_cmd
    
    return None

@safe_execute()
def process_command(cmd: str) -> Dict[str, Any]:
    """
    Main entry point for command processing
    
    Args:
        cmd: Command string to process
        
    Returns:
        Dict with processing results
    """
    result = {
        "original_command": cmd,
        "processed_command": cmd,  # Default to original command
        "type": SHELL_COMMAND,
        "intercepted": False,
        "dangerous": False,
        "has_suggestion": False,
        "suggestion": None,
        "output": None,
        "error": None,
        "success": True
    }
    
    # Guard against empty commands
    if not validate_string(cmd):
        result["success"] = False
        result["error"] = "Empty or invalid command"
        return result
    
    # Clean and parse the command
    cleaned_cmd = sanitize_command_input(cmd.strip())
    parsed = parse_command(cleaned_cmd)
    
    # Set command type
    cmd_type = get_command_type(cleaned_cmd)
    result["type"] = cmd_type
    
    # Handle Rick Assistant command
    if cmd_type == ASSISTANT_COMMAND:
        result["intercepted"] = True
        
        # Extract command without the ! prefix
        rick_cmd = cleaned_cmd[1:].strip() if cleaned_cmd.startswith("!") else cleaned_cmd
        
        # Process Rick command
        if rick_cmd:
            rick_result = process_rick_command(rick_cmd)
            result.update(rick_result)
        else:
            result["error"] = "Empty Rick command"
            result["success"] = False
        
        return result
    
    # Get command context
    context = get_command_context(cleaned_cmd)
    
    # Check for dangerous commands
    if context.get("is_dangerous", False):
        result["dangerous"] = True
        result["danger_reason"] = context.get("danger_reason", "")
        
        # Get user preference for interception
        intercept_dangerous = get_config_value("commands.intercept_dangerous", True)
        if intercept_dangerous:
            result["intercepted"] = True
            result["output"] = create_warning_message(
                cleaned_cmd, 
                context.get("danger_reason", "potentially dangerous command")
            )
    
    # Check for typos and suggestions
    suggestion = detect_common_typos(cleaned_cmd)
    if suggestion:
        result["has_suggestion"] = True
        result["suggestion"] = suggestion
        
        # Get user preference for interception
        intercept_typos = get_config_value("commands.intercept_typos", True)
        if intercept_typos:
            result["intercepted"] = True
            result["output"] = format_suggestion(cleaned_cmd, suggestion)
    
    # If we should show a suggestion, don't execute the command yet
    if result["intercepted"]:
        return result
    
    # We're not intercepting, so just pass the original command through
    result["processed_command"] = cleaned_cmd
    return result

def create_warning_message(cmd: str, reason: str) -> str:
    """
    Create Rick-styled warning message for dangerous commands.
    
    Args:
        cmd: The command string
        reason: The reason why the command is dangerous
        
    Returns:
        Formatted warning message
    """
    messages = [
        f"Whoa there, genius! That command could {reason}! Are you *burp* trying to break something?",
        f"Hold up! That command might {reason}. Even I'm not that reckless, and I destroy planets for fun!",
        f"Nice try! That command could {reason}. What are you, some kind of Jerry? *burp*",
        f"You want to {reason}? That's a level of stupid I didn't think was possible! *burp*",
        f"Seriously? That command might {reason}. Do you want a medal for being dangerously incompetent?",
    ]
    
    # Select a random message
    import random
    message = random.choice(messages)
    
    # Format the full warning
    return f"🧪 Rick says: {message}\n🛑 Command: {cmd}"

def format_suggestion(original: str, suggestion: str) -> str:
    """
    Format command correction with Rick's sarcasm.
    
    Args:
        original: Original command with typo
        suggestion: Suggested correction
        
    Returns:
        Formatted suggestion message
    """
    messages = [
        f"Did you mean '{suggestion}'? Your typing is worse than Jerry's job prospects! *burp*",
        f"Wow, you meant '{suggestion}', genius. I've seen Mortys with better typing skills!",
        f"Let me fix that for you: '{suggestion}'. It's like watching a Blargian try to use Earth tech. Pathetic.",
        f"'{suggestion}' is what you wanted. Maybe spend less time watching interdimensional cable and more time learning to type!",
        f"You meant '{suggestion}'. *burp* Your typing accuracy is right up there with Morty's dating success rate.",
    ]
    
    # Select a random message
    import random
    message = random.choice(messages)
    
    # Format the full suggestion
    return f"🧪 Rick says: {message}"

@safe_execute()
def check_rm_rf_command(cmd: str) -> Tuple[bool, Optional[str]]:
    """
    Check for dangerous recursive deletion commands.
    
    Args:
        cmd: The command string
        
    Returns:
        Tuple of (is_dangerous, reason)
    """
    try:
        if not validate_string(cmd):
            return False, None
        
        # Patterns for dangerous rm -rf commands
        patterns = [
            (r"rm\s+-rf\s+\/", "delete your entire filesystem"),
            (r"rm\s+-rf\s+\/home", "delete home directories"),
            (r"rm\s+-rf\s+\/usr", "delete system binaries"),
            (r"rm\s+-rf\s+\/etc", "delete system configuration"),
            (r"rm\s+-rf\s+\/var", "delete system variable data"),
            (r"rm\s+-rf\s+[\/~]\s+--no-preserve-root", "forcefully delete protected directories"),
            (r"rm\s+-rf\s+\.\.", "delete parent directory"),
            (r"rm\s+-rf\s+\*", "delete all files in current directory"),
            (r"rm\s+-rf\s+\.", "delete current directory")
        ]
        
        for pattern, reason in patterns:
            if re.search(pattern, cmd):
                return True, reason
        
        return False, None
    except Exception as e:
        logger.error(f"Error checking for dangerous rm command: {str(e)}")
        return False, None

@safe_execute()
def check_destructive_redirect(cmd: str) -> Tuple[bool, Optional[str]]:
    """
    Check for dangerous redirections that might overwrite important files.
    
    Args:
        cmd: The command string
        
    Returns:
        Tuple of (is_dangerous, reason)
    """
    try:
        if not validate_string(cmd):
            return False, None
        
        # Patterns for dangerous redirections
        patterns = [
            (r">\s*\/etc\/passwd", "overwrite system password file"),
            (r">\s*\/etc\/shadow", "overwrite system shadow password file"),
            (r">\s*\/etc\/sudoers", "overwrite sudo configuration"),
            (r">\s*\/etc\/hosts", "overwrite hosts file"),
            (r">\s*\/boot\/", "overwrite boot files"),
            (r">\s*\/bin\/", "overwrite system binaries"),
            (r">\s*\/dev\/sd[a-z]", "write directly to disk device"),
            (r">\s*\/dev\/null\s+<", "attempt to read from /dev/null (will produce empty output)"),
        ]
        
        for pattern, reason in patterns:
            if re.search(pattern, cmd):
                return True, reason
        
        return False, None
    except Exception as e:
        logger.error(f"Error checking for dangerous redirect: {str(e)}")
        return False, None

@safe_execute()
def confirm_dangerous_command(cmd: str, reason: str) -> Dict[str, Any]:
    """
    Prepare a confirmation request for risky commands.
    
    Args:
        cmd: The dangerous command
        reason: Why the command is dangerous
        
    Returns:
        Dict with confirmation data
    """
    warning = create_warning_message(cmd, reason)
    
    return {
        "original_command": cmd,
        "needs_confirmation": True,
        "warning": warning,
        "danger_reason": reason,
        "suggested_alternative": suggest_safer_alternative(cmd),
        "confirmation_message": "Are you SURE you want to run this command? [y/N]: "
    }

@safe_execute()
def suggest_safer_alternative(cmd: str) -> Optional[str]:
    """
    Suggest safer alternatives for dangerous commands.
    
    Args:
        cmd: The dangerous command
        
    Returns:
        Safer alternative command or None
    """
    # Define patterns and their safer alternatives
    alternatives = [
        # rm -rf / alternatives
        (r"rm\s+-rf\s+\/", "# DON'T DO THIS! Be more specific about what you want to delete"),
        
        # Safer rm alternatives
        (r"rm\s+-rf\s+\*", "ls -la  # List files first to see what would be deleted"),
        (r"rm\s+-rf\s+\.", "cd .. && rm -rf dirname  # Delete from parent directory instead"),
        
        # Add --preserve-root
        (r"rm\s+-rf\s+\/(?!.*--preserve-root)", "rm -rf / --preserve-root  # Added protection flag"),
        
        # Use trash instead of rm
        (r"rm\s+([^-].*)", "mv \\1 ~/.trash/  # Use trash instead of permanent deletion"),
        
        # For dd, suggest adding status=progress
        (r"dd\s+if=(\S+)\s+of=(\S+)", "dd if=\\1 of=\\2 status=progress  # Added progress indicator"),
        
        # For chmod 777, suggest more restrictive permissions
        (r"chmod\s+-R\s+777\s+(\S+)", "chmod -R 755 \\1  # More secure permissions"),
        
        # For wget/curl piping to bash, suggest downloading first
        (r"(wget|curl)\s+(\S+)\s+\|\s+bash", "\\1 \\2 -O script.sh && less script.sh  # Review before executing"),
    ]
    
    for pattern, alternative in alternatives:
        if re.search(pattern, cmd):
            return alternative
    
    return None

@safe_execute()
def suggest_correction(cmd: str) -> Optional[Dict[str, Any]]:
    """
    Offer corrections for command typos.
    
    Args:
        cmd: The command string
        
    Returns:
        Dict with correction suggestion or None
    """
    if not validate_string(cmd):
        return None
    
    # First check for simple typos
    correction = detect_common_typos(cmd)
    if correction:
        return {
            "original": cmd,
            "suggestion": correction,
            "type": "typo",
            "confidence": "high",
            "message": format_suggestion(cmd, correction)
        }
    
    # Look for more complex typos using command similarity
    parsed = parse_command(cmd)
    command = parsed.get("command", "")
    
    # List of common commands to check similarity against
    common_commands = [
        "ls", "cd", "pwd", "mkdir", "touch", "rm", "cp", "mv",
        "cat", "less", "grep", "find", "chmod", "chown", "tar",
        "gzip", "gunzip", "ssh", "scp", "rsync", "wget", "curl",
        "git", "python", "pip", "npm", "node", "java", "javac",
        "make", "gcc", "g++", "docker", "kubectl", "aws", "az"
    ]
    
    # Simple Levenshtein distance (character-based edit distance)
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    # Only process single-word commands to avoid false positives
    if len(command) >= 2 and " " not in command:
        # Find closest match
        closest = None
        min_distance = float('inf')
        
        for cmd_option in common_commands:
            distance = levenshtein(command, cmd_option)
            # Use a threshold based on command length
            threshold = max(1, min(2, len(command) // 3))
            
            if distance <= threshold and distance < min_distance:
                min_distance = distance
                closest = cmd_option
        
        if closest:
            # Replace the command portion with the closest match
            correction = cmd.replace(command, closest, 1)
            return {
                "original": cmd,
                "suggestion": correction,
                "type": "typo",
                "confidence": "medium" if min_distance == 1 else "low",
                "message": format_suggestion(cmd, correction)
            }
    
    return None

@safe_execute()
def suggest_command_improvement(cmd: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Suggest better command options or flags.
    
    Args:
        cmd: The command string
        context: Command context information
        
    Returns:
        Dict with improvement suggestion or None
    """
    if not validate_string(cmd):
        return None
    
    parsed = parse_command(cmd)
    command = parsed.get("command", "")
    args = parsed.get("args", [])
    
    # Command-specific improvements
    improvements = {
        # ls improvements
        "ls": [
            (lambda a: len(a) == 0, "ls -la", "Show all files with details"),
            (lambda a: "-l" in a and "-h" not in a, lambda c: c + " -h", "Add human-readable sizes"),
            (lambda a: "-a" not in a and "-l" in a, lambda c: c.replace("-l", "-la"), "Show hidden files too"),
        ],
        
        # cd improvements
        "cd": [
            (lambda a: len(a) == 0, "cd ~", "Go to home directory"),
            (lambda a: a[0] == "..", "cd -", "Return to previous directory"),
        ],
        
        # mkdir improvements
        "mkdir": [
            (lambda a: len(a) > 0 and "-p" not in a, lambda c: c.replace("mkdir", "mkdir -p"), "Create parent directories"),
        ],
        
        # cp improvements
        "cp": [
            (lambda a: len(a) >= 2 and "-r" not in a and "-R" not in a, lambda c: c.replace("cp", "cp -r"), 
             "Add recursive flag for directories"),
            (lambda a: len(a) >= 2 and "-v" not in a, lambda c: c + " -v", "Show progress"),
        ],
        
        # rm improvements
        "rm": [
            (lambda a: len(a) > 0 and "-i" not in a, lambda c: c.replace("rm", "rm -i"), 
             "Add interactive flag for safety"),
        ],
        
        # grep improvements
        "grep": [
            (lambda a: len(a) >= 2 and "-i" not in a, lambda c: c.replace("grep", "grep -i"), 
             "Add case-insensitive search"),
            (lambda a: len(a) >= 2 and "-r" not in a and "-R" not in a, lambda c: c.replace("grep", "grep -r"), 
             "Add recursive search"),
        ],
        
        # find improvements
        "find": [
            (lambda a: len(a) >= 2 and "-type" not in " ".join(a), lambda c: c + " -type f", 
             "Add file type filter"),
        ],
        
        # ps improvements
        "ps": [
            (lambda a: len(a) == 0, "ps aux", "Show all processes"),
        ],
        
        # wget improvements
        "wget": [
            (lambda a: len(a) > 0 and "-c" not in a, lambda c: c.replace("wget", "wget -c"), 
             "Add continue flag for resuming"),
        ],
    }
    
    # Check if command has improvements
    if command in improvements:
        for condition, improvement, reason in improvements[command]:
            if condition(args):
                # Apply improvement (either string or function)
                if callable(improvement):
                    improved_cmd = improvement(cmd)
                else:
                    improved_cmd = improvement
                
                return {
                    "original": cmd,
                    "suggestion": improved_cmd,
                    "type": "improvement",
                    "reason": reason,
                    "message": format_improvement_suggestion(cmd, improved_cmd, reason),
                    "confidence": "medium"
                }
    
    return None

def format_improvement_suggestion(original: str, suggestion: str, reason: str) -> str:
    """
    Format command improvement suggestion with Rick's style.
    
    Args:
        original: Original command
        suggestion: Improved command
        reason: Reason for improvement
        
    Returns:
        Formatted improvement message
    """
    messages = [
        f"Try '{suggestion}' instead. {reason}, you *burp* amateur!",
        f"A smarter person would use '{suggestion}'. {reason}, obviously!",
        f"Even Jerry would use '{suggestion}'. {reason}, you know?",
        f"Use '{suggestion}' next time. {reason}. *burp* Just saying.",
        f"*burp* I can't watch this. Use '{suggestion}'. {reason}. You're welcome.",
    ]
    
    # Select a random message
    import random
    message = random.choice(messages)
    
    # Format the full suggestion
    return f"🧪 Rick says: {message}"

@safe_execute()
def remember_user_preference(cmd: str, accept_suggestion: bool) -> None:
    """
    Track user preferences for suggestions.
    
    Args:
        cmd: The command string
        accept_suggestion: Whether user accepted the suggestion
    """
    try:
        # Get the current user preferences
        from src.utils.config import load_config, save_config
        
        config = load_config()
        if 'commands' not in config:
            config['commands'] = {}
        
        if 'preferences' not in config['commands']:
            config['commands']['preferences'] = {
                'accepted_suggestions': 0,
                'rejected_suggestions': 0,
                'suggestion_history': []
            }
        
        # Update counters
        prefs = config['commands']['preferences']
        if accept_suggestion:
            prefs['accepted_suggestions'] = prefs.get('accepted_suggestions', 0) + 1
        else:
            prefs['rejected_suggestions'] = prefs.get('rejected_suggestions', 0) + 1
        
        # Store command in history (limited to last 20)
        cmd_history = prefs.get('suggestion_history', [])
        cmd_entry = {
            'command': cmd,
            'accepted': accept_suggestion,
            'timestamp': str(os.times())
        }
        
        cmd_history.append(cmd_entry)
        # Keep only the last 20 entries
        if len(cmd_history) > 20:
            cmd_history = cmd_history[-20:]
        
        prefs['suggestion_history'] = cmd_history
        
        # Save the updated preferences
        save_config(config)
        
        # Adjust suggestion frequency based on acceptance rate
        acceptance_rate = prefs['accepted_suggestions'] / (
            prefs['accepted_suggestions'] + prefs['rejected_suggestions']
        ) if (prefs['accepted_suggestions'] + prefs['rejected_suggestions']) > 0 else 0.5
        
        # If acceptance rate is low, reduce suggestion frequency
        if acceptance_rate < 0.3 and config['commands'].get('intercept_typos', True):
            logger.info("Low suggestion acceptance rate, reducing suggestion frequency")
            config['commands']['suggestion_frequency'] = 'low'
        elif acceptance_rate > 0.7:
            logger.info("High suggestion acceptance rate, increasing suggestion frequency")
            config['commands']['suggestion_frequency'] = 'high'
        else:
            config['commands']['suggestion_frequency'] = 'medium'
        
        save_config(config)
        
    except Exception as e:
        logger.error(f"Error remembering user preference: {str(e)}")

@safe_execute()
def execute_assistant_cmd(cmd: str) -> Dict[str, Any]:
    """
    Handle assistant-specific commands.
    
    Args:
        cmd: The command string (without the ! prefix)
        
    Returns:
        Dict with command results
    """
    if not validate_string(cmd):
        return {
            "success": False,
            "error": "Empty or invalid command",
            "output": "🧪 Rick says: What do you expect me to do with *burp* nothing?"
        }
    
    # Parse the command
    parts = shlex.split(cmd)
    command = parts[0].lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    
    # Command handlers
    handlers = {
        "help": handle_help_command,
        "rick": handle_rick_quote_command,
        "config": handle_config_command,
        "version": handle_version_command,
        "stats": handle_stats_command,
        "clear": handle_clear_command,
        "status": handle_status_command,
        "about": handle_about_command,
        "tip": handle_tip_command,
        "toggle": handle_toggle_command,
    }
    
    # Check if command exists
    if command in handlers:
        return handlers[command](args)
    
    # Unknown command
    valid_commands = ", ".join(["!" + cmd for cmd in handlers.keys()])
    return {
        "success": False,
        "error": f"Unknown Rick command: {command}",
        "output": f"🧪 Rick says: What the *burp* is '{command}'? Try one of these instead: {valid_commands}"
    }

# Rick command handlers
@safe_execute()
def handle_help_command(args: List[str]) -> Dict[str, Any]:
    """Handle !help command"""
    help_text = """
🧪 Rick Assistant Command Help 🧪

Available commands:
!help         - Show this help message
!rick         - Show a random Rick quote
!config       - Open Rick Assistant configuration
!version      - Show Rick Assistant version
!stats        - Show command statistics
!clear        - Clear command history
!status       - Show Rick Assistant status
!about        - About Rick Assistant
!tip          - Show a random command tip
!toggle       - Toggle feature on/off

Rick will also help with:
- Command typos and corrections
- Dangerous command warnings
- Command improvements

For more help, visit: https://github.com/user/rick_assistant
"""
    return {
        "success": True,
        "output": help_text.strip()
    }

@safe_execute()
def handle_rick_quote_command(args: List[str]) -> Dict[str, Any]:
    """Handle !rick command to show a random Rick quote"""
    quotes = [
        "Wubba lubba dub dub!",
        "I'm not a hero. I'm a high-functioning alcoholic.",
        "Sometimes science is more art than science, Morty.",
        "What, so everyone's supposed to sleep every single night now?",
        "I don't do magic, Morty, I do science. One takes brains, the other takes dark eye liner.",
        "I'm sorry, but your opinion means very little to me.",
        "I'm not driven by avenging my dead family, I'm driven by finding that McNugget sauce.",
        "I'm Mr. Meeseeks, look at me! Just kidding, I'm Rick.",
        "The universe is basically an animal. It grazes on the ordinary.",
        "To live is to risk it all; otherwise you're just an inert chunk of randomly assembled molecules.",
        "If I let you make me nervous, then we can't get schwifty.",
        "I turned myself into a pickle, Morty!",
        "Life is effort and I'll stop when I die!",
        "There's a lesson here, and I'm not going to be the one to figure it out.",
        "I'm a scientist; because I invent, transform, create, and destroy for a living."
    ]
    
    import random
    quote = random.choice(quotes)
    
    return {
        "success": True,
        "output": f"🧪 Rick says: \"{quote}\""
    }

@safe_execute()
def handle_config_command(args: List[str]) -> Dict[str, Any]:
    """Handle !config command to manage configuration"""
    from src.utils.config import get_config_path, load_config
    
    config_path = get_config_path()
    
    # If args provided, try to set config values
    if args:
        # TODO: Implement config setting functionality - planned for phase 4 (Command Processing & Safety Features)
        # Will support: rick config set key value, rick config get key, rick config list
        return {
            "success": False,
            "output": f"🧪 Rick says: Config editing not implemented yet. *burp* Edit the file manually at {config_path}"
        }
    
    # Otherwise just show config location
    return {
        "success": True,
        "output": f"🧪 Rick says: Config file located at: {config_path}\nEdit it with your favorite text editor, genius."
    }

@safe_execute()
def handle_version_command(args: List[str]) -> Dict[str, Any]:
    """Handle !version command"""
    # Import version info from main package
    from src import __version__, __author__, __email__
    
    version_info = f"""
Rick Assistant v{__version__}
Author: {__author__}
Email: {__email__}

"The *burp* newest version of my genius!"
"""
    return {
        "success": True,
        "output": version_info.strip()
    }

@safe_execute()
def handle_stats_command(args: List[str]) -> Dict[str, Any]:
    """Handle !stats command to show usage statistics"""
    from src.utils.config import load_config
    
    config = load_config()
    stats = config.get("stats", {})
    
    if not stats:
        return {
            "success": True,
            "output": "🧪 Rick says: No statistics available yet. *burp* Use me more!"
        }
    
    commands_run = stats.get("commands_run", 0)
    corrections_made = stats.get("corrections_made", 0)
    dangerous_commands = stats.get("dangerous_commands", 0)
    
    stats_text = f"""
🧪 Rick Assistant Statistics 🧪

Commands run: {commands_run}
Corrections made: {corrections_made}
Dangerous commands caught: {dangerous_commands}

"Numbers don't lie, but I do. *burp* Frequently."
"""
    return {
        "success": True,
        "output": stats_text.strip()
    }

# Placeholder handlers for other commands
def handle_clear_command(args: List[str]) -> Dict[str, Any]:
    """Handle !clear command to clear history"""
    return {
        "success": True,
        "output": "🧪 Rick says: History cleared. *burp* Your shameful commands are gone!"
    }
    
def handle_status_command(args: List[str]) -> Dict[str, Any]:
    """Handle !status command"""
    from src.utils.config import load_config
    
    config = load_config()
    enabled = config.get("general", {}).get("enabled", True)
    status = "active" if enabled else "disabled"
    
    return {
        "success": True,
        "output": f"🧪 Rick says: Rick Assistant is currently {status}. {'Ready to judge your commands!' if enabled else 'Taking a break from your stupidity.'}"
    }
    
def handle_about_command(args: List[str]) -> Dict[str, Any]:
    """Handle !about command"""
    about_text = """
🧪 Rick Assistant 🧪

A Rick Sanchez-themed ZSH assistant that helps (and insults) you
while you're using the command line.

Features:
- Command correction
- Shell command improvements
- Dangerous command detection
- Rick's unique personality

"It's like having me *burp* looking over your shoulder all day!"
"""
    return {
        "success": True,
        "output": about_text.strip()
    }
    
def handle_tip_command(args: List[str]) -> Dict[str, Any]:
    """Handle !tip command to show a random tip"""
    tips = [
        "Use 'cd -' to return to your previous directory.",
        "Press Ctrl+R to search through command history.",
        "Use 'sudo !!' to repeat the last command with sudo.",
        "Use 'ls -la' to see hidden files and directories.",
        "Create directory trees with 'mkdir -p parent/child/grandchild'.",
        "Use 'find . -name \"*.txt\"' to find all .txt files.",
        "Use 'history | grep keyword' to find commands in history.",
        "The 'head' and 'tail' commands show the beginning and end of files.",
        "Press Tab twice to show all completion possibilities.",
        "Use 'ps aux | grep process' to find running processes.",
        "Add 'time' before a command to see how long it takes to run.",
        "Use 'df -h' to check disk space in human-readable format.",
        "Use 'du -sh *' to see the size of directories.",
        "Use 'man command' to read the manual for a command.",
        "Use 'alias' to create shortcuts for commands."
    ]
    
    import random
    tip = random.choice(tips)
    
    return {
        "success": True,
        "output": f"🧪 Rick says: Here's a tip, *burp* genius!\n\n{tip}\n\nNot that you'll remember it..."
    }
    
def handle_toggle_command(args: List[str]) -> Dict[str, Any]:
    """Handle !toggle command to turn features on/off"""
    if not args:
        return {
            "success": False,
            "output": "🧪 Rick says: Toggle what exactly? Try !toggle [feature] where feature is one of: typos, dangerous, suggestions, all"
        }
    
    feature = args[0].lower()
    valid_features = ["typos", "dangerous", "suggestions", "all"]
    
    if feature not in valid_features:
        features_list = ", ".join(valid_features)
        return {
            "success": False,
            "output": f"🧪 Rick says: Invalid feature '{feature}'. *burp* Choose from: {features_list}"
        }
    
    from src.utils.config import load_config, save_config
    
    config = load_config()
    if "commands" not in config:
        config["commands"] = {}
    
    # Toggle the selected feature
    if feature == "all":
        # Get current state (default to True if not set)
        current = config["commands"].get("intercept_typos", True)
        
        # Toggle all features to the opposite state
        config["commands"]["intercept_typos"] = not current
        config["commands"]["intercept_dangerous"] = not current
        config["commands"]["intercept_suggestions"] = not current
        
        state = "enabled" if not current else "disabled"
        message = f"All features {state}"
    else:
        # Map feature names to config keys
        feature_map = {
            "typos": "intercept_typos",
            "dangerous": "intercept_dangerous",
            "suggestions": "intercept_suggestions"
        }
        
        key = feature_map[feature]
        current = config["commands"].get(key, True)
        config["commands"][key] = not current
        
        state = "enabled" if not current else "disabled"
        message = f"Feature '{feature}' {state}"
    
    # Save the updated config
    save_config(config)
    
    response_text = "Now I can *burp* annoy you properly!" if state == "enabled" else "Fine, I'll shut up about it."
    
    return {
        "success": True,
        "output": f"🧪 Rick says: {message}. {response_text}"
    }

@safe_execute()
def format_command_output(result: Dict[str, Any]) -> str:
    """
    Format command output with Rick's style.
    
    Args:
        result: Command result dictionary
        
    Returns:
        Formatted output string
    """
    if not result or not isinstance(result, dict):
        return "🧪 Rick says: Got some *burp* garbage data. Can't work with this!"
    
    # If there's already output, just return it
    if "output" in result and result["output"]:
        return result["output"]
    
    # Format output based on command type and result state
    cmd_type = result.get("type", SHELL_COMMAND)
    success = result.get("success", True)
    original_cmd = result.get("original_command", "")
    
    # Handle errors
    if not success and "error" in result and result["error"]:
        error_msg = result["error"]
        return f"🧪 Rick says: {get_error_message(error_msg)}"
    
    # Handle different command types
    if cmd_type == ASSISTANT_COMMAND:
        return format_assistant_output(result)
    elif cmd_type == SHELL_COMMAND:
        if "intercepted" in result and result["intercepted"]:
            # Command was intercepted (dangerous or has suggestion)
            if result.get("dangerous", False):
                return create_warning_message(
                    original_cmd, 
                    result.get("danger_reason", "potentially dangerous command")
                )
            elif result.get("has_suggestion", False):
                return format_suggestion(
                    original_cmd, 
                    result.get("suggestion", "")
                )
        
        # Generic success message for non-intercepted command
        return f"🧪 Rick says: Running command, *burp* obviously!"
    
    # Default fallback
    return "🧪 Rick says: Command processed. Don't ask me how it went."

@safe_execute()
def format_assistant_output(result: Dict[str, Any]) -> str:
    """
    Format output for Rick assistant commands.
    
    Args:
        result: Command result dictionary
        
    Returns:
        Formatted output string
    """
    if "output" in result and result["output"]:
        return result["output"]
    
    command = result.get("command", "")
    success = result.get("success", True)
    
    if not success:
        error = result.get("error", "unknown error")
        return f"🧪 Rick says: Couldn't process '{command}'. {error}"
    
    # Generic success message
    return f"🧪 Rick says: Processed '{command}'. What do you want, a medal?"

@safe_execute()
def get_error_message(error: str) -> str:
    """
    Create a Rick-styled error message.
    
    Args:
        error: Error message or description
        
    Returns:
        Rick-styled error message
    """
    messages = [
        f"Great job breaking everything! *burp* Error: {error}",
        f"You really screwed that up, didn't you? {error}",
        f"That's about as functional as Jerry's *burp* career. {error}",
        f"Wow, you really know how to mess things up! {error}",
        f"Congratulations, you've achieved peak incompetence! {error}",
    ]
    
    import random
    return random.choice(messages)

@safe_execute()
def log_command_execution(cmd: str, result: Dict[str, Any]) -> None:
    """
    Log command execution for history.
    
    Args:
        cmd: The command string
        result: Command result dictionary
    """
    # Get the current stats
    from src.utils.config import load_config, save_config
    
    config = load_config()
    if "stats" not in config:
        config["stats"] = {
            "commands_run": 0,
            "corrections_made": 0,
            "dangerous_commands": 0,
            "last_commands": []
        }
    
    stats = config["stats"]
    
    # Update command count
    stats["commands_run"] = stats.get("commands_run", 0) + 1
    
    # If a correction was made, update count
    if result.get("has_suggestion", False) and result.get("accepted_suggestion", False):
        stats["corrections_made"] = stats.get("corrections_made", 0) + 1
    
    # If a dangerous command was caught, update count
    if result.get("dangerous", False):
        stats["dangerous_commands"] = stats.get("dangerous_commands", 0) + 1
    
    # Store command in history (limited to last 20)
    cmd_history = stats.get("last_commands", [])
    cmd_entry = {
        "command": cmd,
        "timestamp": str(os.times()),
        "type": result.get("type", SHELL_COMMAND),
        "success": result.get("success", True)
    }
    
    cmd_history.append(cmd_entry)
    # Keep only the last 20 entries
    if len(cmd_history) > 20:
        cmd_history = cmd_history[-20:]
    
    stats["last_commands"] = cmd_history
    
    # Save the updated stats
    save_config(config)
    
    # Also log to the actual logger
    cmd_type = result.get("type", SHELL_COMMAND)
    success = result.get("success", True)
    
    if cmd_type == ASSISTANT_COMMAND:
        logger.info(f"Executed Rick command: {cmd}")
    elif result.get("dangerous", False):
        logger.warning(f"Dangerous command detected: {cmd}")
    elif result.get("has_suggestion", False):
        logger.info(f"Command suggestion: {cmd} -> {result.get('suggestion', '')}")
    else:
        logger.debug(f"Executed shell command: {cmd}")
    
    if not success:
        logger.error(f"Command failed: {cmd}, Error: {result.get('error', 'Unknown error')}")

def register_with_hook_system() -> None:
    """
    Register command processor with ZSH hook system.
    This would connect the command processor to the ZSH hooks.
    """
    # Placeholder for now - actual implementation would depend on the hook system
    logger.info("Command processor registered with ZSH hook system")
    pass

@safe_execute()
def handle_empty_command() -> Dict[str, Any]:
    """
    Handle case when command is empty.
    
    Returns:
        Dict with empty command result
    """
    messages = [
        "You gonna type something or just sit there mouth-breathing?",
        "I don't speak telepathically. Try using actual *burp* commands.",
        "Oh great, I'm stuck in a shell with someone who can't even type.",
        "Empty command? That's like Jerry trying to contribute to a conversation.",
        "Use your words. Preferably ones that form a *burp* command.",
    ]
    
    import random
    message = random.choice(messages)
    
    return {
        "success": False,
        "error": "Empty command",
        "output": f"🧪 Rick says: {message}",
        "type": SHELL_COMMAND,
        "intercepted": True
    }

@safe_execute()
def handle_very_long_command(cmd: str) -> Dict[str, Any]:
    """
    Handle extremely long commands.
    
    Args:
        cmd: Very long command string
        
    Returns:
        Dict with long command result
    """
    # Truncate the command for logging and display
    max_length = 100
    truncated = cmd[:max_length] + "..." if len(cmd) > max_length else cmd
    
    messages = [
        f"Whoa, that command is longer than one of Rick's monologues!",
        f"What is this, a command or your life story?",
        f"Did you just paste your entire *burp* PhD thesis into the terminal?",
        f"I've seen shorter instructions for building a portal gun!",
        f"Are you trying to break the terminal with that novel you call a command?",
    ]
    
    import random
    message = random.choice(messages)
    
    # Check if the command is actually dangerous (might be a script injection attempt)
    is_danger, reason = is_dangerous_command(cmd)
    
    result = {
        "original_command": truncated,
        "processed_command": cmd,
        "type": SHELL_COMMAND,
        "intercepted": True,
        "long_command": True,
        "output": f"🧪 Rick says: {message}"
    }
    
    if is_danger:
        result["dangerous"] = True
        result["danger_reason"] = reason
        result["output"] = create_warning_message(truncated, reason)
    
    return result

@safe_execute()
def handle_special_command(cmd: str) -> Dict[str, Any]:
    """
    Handle special cases like "sudo !!" history expansion.
    
    Args:
        cmd: Command string
        
    Returns:
        Dict with special command result
    """
    if cmd.startswith("sudo !!"):
        return {
            "original_command": cmd,
            "processed_command": cmd,
            "type": SPECIAL_COMMAND,
            "intercepted": True,
            "output": "🧪 Rick says: Ah, the classic 'sudo !!' move. Trying to compensate for something?"
        }
    
    if cmd == "cd -":
        return {
            "original_command": cmd,
            "processed_command": cmd,
            "type": SPECIAL_COMMAND,
            "intercepted": True,
            "output": "🧪 Rick says: Going back, huh? Can't blame you for wanting to *burp* escape your current mistakes."
        }
    
    if cmd == "cd ~" or cmd == "cd":
        return {
            "original_command": cmd,
            "processed_command": cmd,
            "type": SPECIAL_COMMAND,
            "intercepted": True,
            "output": "🧪 Rick says: Scurrying back to your home directory like a scared little mouse?"
        }
    
    # Handle exit/logout with a goodbye message
    if cmd in ["exit", "logout"]:
        return {
            "original_command": cmd,
            "processed_command": cmd,
            "type": SPECIAL_COMMAND,
            "intercepted": True,
            "output": "🧪 Rick says: Running away already? Typical. *burp* See ya later, loser!"
        }
    
    return {
        "original_command": cmd,
        "processed_command": cmd,
        "type": SHELL_COMMAND,
        "intercepted": False
    }

@safe_execute()
def run_self_test() -> Dict[str, Any]:
    """
    Run a self-test of the command processor functionality.
    
    Returns:
        Dict with test results
    """
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    def run_test(name, func, expected=True):
        """Helper to run a single test"""
        test_results["total_tests"] += 1
        result = func()
        passed = result == expected
        
        if passed:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        test_results["test_details"].append({
            "name": name,
            "passed": passed,
            "expected": expected,
            "actual": result
        })
        
        return passed
    
    # Test parsing functionality
    run_test("Parse simple command", 
             lambda: parse_command("ls -la").get("command") == "ls")
    
    run_test("Parse command args", 
             lambda: parse_command("ls -la").get("args") == ["-la"])
    
    run_test("Parse Rick command", 
             lambda: parse_command("!help").get("is_rick_command"))
    
    run_test("Command type detection - shell", 
             lambda: get_command_type("ls -la") == SHELL_COMMAND)
    
    run_test("Command type detection - assistant", 
             lambda: get_command_type("!help") == ASSISTANT_COMMAND)
    
    run_test("Command type detection - builtin", 
             lambda: get_command_type("cd /tmp") == BUILTIN_COMMAND)
    
    # Test typo detection
    run_test("Common typo detection", 
             lambda: detect_common_typos("gti status") == "git status")
    
    # Test dangerous command detection
    run_test("Dangerous command detection", 
             lambda: is_dangerous_command("rm -rf /")[0])
    
    # Test Rick commands
    run_test("Rick help command", 
             lambda: handle_help_command([]).get("success"))
    
    run_test("Rick quote command", 
             lambda: handle_rick_quote_command([]).get("success"))
    
    # Test suggestion formatting
    run_test("Suggestion formatting", 
             lambda: "Rick says" in format_suggestion("gti", "git"))
    
    # Test empty command handling
    run_test("Empty command handling", 
             lambda: not handle_empty_command().get("success"))
    
    return test_results

if __name__ == "__main__":
    # Only run test if module is executed directly
    print("Running Rick Assistant Command Processor self-test...")
    results = run_self_test()
    
    # Print test summary
    print(f"\nTest Summary:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    
    if results['failed_tests'] > 0:
        print("\nFailed tests:")
        for test in results['test_details']:
            if not test['passed']:
                print(f"  - {test['name']}: expected {test['expected']}, got {test['actual']}")
    
    print("\nCommand processor test complete.")

def run_command_diagnose(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run diagnostics for Rick Assistant.
    
    Checks for dependencies, configuration, and integration status.
    """
    
    # Set up diagnostics environment
    logger.info("Running diagnostics")
    logger.debug(f"Diagnostics args: {args}")
    
    # Parse arguments
    arg_parser = argparse.ArgumentParser(description="Rick Assistant Diagnostics")
    arg_parser.add_argument("--p10k", action="store_true", help="Run p10k integration diagnostics")
    arg_parser.add_argument("--metrics", action="store_true", help="Run system metrics diagnostics")
    arg_parser.add_argument("--all", action="store_true", help="Run all diagnostics")
    arg_parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    # Parse args if provided
    if args and len(args) > 0:
        try:
            parsed_args = arg_parser.parse_args(args)
        except SystemExit:
            # Handle argparse's internal exit
            return 1
    else:
        # Default to running all diagnostics
        parsed_args = argparse.Namespace(p10k=False, metrics=False, all=True, verbose=False)
    
    # Determine what to run
    run_p10k = parsed_args.p10k or parsed_args.all
    run_metrics = parsed_args.metrics or parsed_args.all
    verbose = parsed_args.verbose
    
    # If only specific tests selected, update the all flag
    if parsed_args.p10k or parsed_args.metrics:
        parsed_args.all = False
    
    # Header
    print(f"\n{TEXT_CYAN}Rick Assistant Diagnostics{TEXT_RESET}")
    print(f"{TEXT_BLUE}=================================={TEXT_RESET}\n")
    
    # Run metrics diagnostics if requested
    if run_metrics:
        print(f"{TEXT_CYAN}System Metrics Check{TEXT_RESET}")
        print(f"{TEXT_BLUE}------------------{TEXT_RESET}")
        
        try:
            # Import metric functions
            from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
            
            # Test CPU metrics
            cpu_info = get_cpu_usage()
            cpu_usage = cpu_info.get('usage', 0)
            cpu_state = cpu_info.get('state', 'normal')
            print(f"CPU Usage:      {TEXT_BOLD}{cpu_usage:.1f}%{TEXT_RESET} ({cpu_state})")
            if verbose:
                print(f"  Full CPU Info: {cpu_info}")
            
            # Test RAM metrics
            ram_info = get_ram_info()
            ram_percent = ram_info.get('percent', 0)
            ram_used = ram_info.get('used', 0) / (1024 * 1024)  # Convert to MB
            ram_total = ram_info.get('total', 0) / (1024 * 1024)  # Convert to MB
            ram_state = ram_info.get('state', 'normal')
            print(f"RAM Usage:      {TEXT_BOLD}{ram_percent:.1f}%{TEXT_RESET} ({ram_state})")
            print(f"RAM Used:       {TEXT_BOLD}{ram_used:.1f} MB{TEXT_RESET} / {ram_total:.1f} MB")
            if verbose:
                print(f"  Full RAM Info: {ram_info}")
            
            # Test temperature metrics
            temp_info = get_cpu_temperature()
            temp_available = temp_info.get('available', False)
            if temp_available:
                temp_value = temp_info.get('temperature', 0)
                temp_state = temp_info.get('state', 'normal')
                print(f"CPU Temperature: {TEXT_BOLD}{temp_value:.1f}°C{TEXT_RESET} ({temp_state})")
            else:
                print(f"CPU Temperature: {TEXT_YELLOW}Not available{TEXT_RESET}")
            if verbose:
                print(f"  Full Temperature Info: {temp_info}")
            
            print(f"\nMetrics Collection: {TEXT_GREEN}Working{TEXT_RESET}")
            print(f"Metrics Commentary: \"{temp_info.get('commentary', 'None')}\"")
            
        except Exception as e:
            logger.error(f"Error testing system metrics: {e}")
            print(f"{TEXT_RED}Error testing system metrics: {e}{TEXT_RESET}")
            print(f"\nMetrics Collection: {TEXT_RED}Error{TEXT_RESET}")
            
            # Check for psutil
            try:
                import psutil
                print(f"psutil: {TEXT_GREEN}Installed{TEXT_RESET}")
            except ImportError:
                print(f"psutil: {TEXT_RED}Not installed{TEXT_RESET}")
                print("Run 'pip install psutil' to enable system metrics")
        
        print("")  # Empty line
    
    # Run p10k diagnostics if requested
    if run_p10k:
        # Execute the p10k diagnostics script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "core", "integrations", "p10k_diagnostics.zsh"
        )
        
        # Log the script path for debugging
        logger.debug(f"P10k diagnostics script path: {script_path}")
        
        # Check if the script exists
        if not os.path.exists(script_path):
            logger.error(f"P10k diagnostics script not found at {script_path}")
            print(f"{TEXT_RED}P10k diagnostics script not found.{TEXT_RESET}")
            print(f"Expected path: {script_path}")
            return 1
        
        # Run the diagnostics script
        try:
            subprocess.call(["zsh", script_path])
        except Exception as e:
            logger.error(f"Error running p10k diagnostics: {e}")
            print(f"{TEXT_RED}Error running p10k diagnostics: {e}{TEXT_RESET}")
            return 1
    
    # If running all diagnostics, show a summary
    if parsed_args.all:
        print(f"\n{TEXT_CYAN}Summary{TEXT_RESET}")
        print(f"{TEXT_BLUE}-------{TEXT_RESET}")
        print(f"To run specific diagnostics, use:")
        print(f"  {TEXT_YELLOW}rick diagnose --p10k{TEXT_RESET}    - Test Powerlevel10k integration")
        print(f"  {TEXT_YELLOW}rick diagnose --metrics{TEXT_RESET} - Test system metrics collection")
        print(f"  {TEXT_YELLOW}rick diagnose --verbose{TEXT_RESET} - Show detailed diagnostic information")
        print(f"  {TEXT_YELLOW}rick diagnose --all{TEXT_RESET}     - Run all diagnostics (default)")
        print("")
        print(f"To fix P10k integration issues, run: {TEXT_YELLOW}rick p10k [right|left|dir]{TEXT_RESET}")
        print(f"To test metrics directly, run: {TEXT_YELLOW}rick metrics{TEXT_RESET}")
        print("")
    
    return 0

def run_command_metrics(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Display current system metrics.
    
    This command shows CPU usage, RAM usage, and temperature if available.
    Useful for verifying that system metrics collection is working.
    """
    logger.info("Displaying system metrics")
    
    try:
        # Import here to avoid circular imports
        from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
        
        # Get CPU usage
        cpu_info = get_cpu_usage()
        cpu_usage = cpu_info.get('usage', 0)
        
        # Get RAM info
        ram_info = get_ram_info()
        ram_usage = ram_info.get('percent', 0)
        ram_used = ram_info.get('used', 0)
        ram_total = ram_info.get('total', 0)
        
        # Get CPU temperature
        temp_info = get_cpu_temperature()
        temp_available = temp_info.get('available', False)
        temp_value = temp_info.get('temperature', 0)
        temp_state = temp_info.get('state', 'normal')
        
        # Print the metrics with nice formatting
        print("\n🧪 Rick Assistant System Metrics 🧪")
        print("=================================")
        print(f"🖥️  CPU Usage:      {cpu_usage:.1f}%")
        print(f"🔧  RAM Usage:      {ram_usage:.1f}% ({ram_used/1024/1024:.1f} MB / {ram_total/1024/1024:.1f} MB)")
        
        if temp_available:
            # Color coding for temperature
            temp_color = "\033[32m"  # Green
            if temp_state == 'warning':
                temp_color = "\033[33m"  # Yellow
            elif temp_state == 'critical':
                temp_color = "\033[31m"  # Red
                
            print(f"🌡️  CPU Temperature: {temp_color}{temp_value:.1f}°C\033[0m")
            print(f"    Temperature State: {temp_color}{temp_state.upper()}\033[0m")
        else:
            print(f"🌡️  CPU Temperature: Not available")
        
        # Get a Rick comment
        comments = temp_info.get('commentary', '*burp* This is fine.')
        print(f"\nRick says: \"{comments}\"")
        
        return 0
    except Exception as e:
        logger.error(f"Error displaying metrics: {e}")
        print_error(f"Error displaying metrics: {e}")
        
        # Check if psutil is installed
        try:
            import psutil
            print("psutil is installed, but something else went wrong.")
        except ImportError:
            print("\npsutil is not installed. Install it with:")
            print("  pip install psutil")
            print("Then try again.")
        
        return 1

def run_command_p10k(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Configure Powerlevel10k integration.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    
    # Set up p10k integration
    logger.info("Setting up p10k integration")
    logger.debug(f"p10k args: {args}")
    
    # If no args, default to showing help
    if not args:
        args = ["help"]
    
    # Check if we should run the test
    if args and args[0] == "--test":
        return run_p10k_test()
    
    # Get the position
    position = args[0] if args else "help"
    
    try:
        # Find the integration script
        integration_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "core", "integrations", "p10k_integration.zsh"
        )
        
        # Check if the script exists
        if not os.path.exists(integration_script):
            logger.error(f"p10k integration script not found at {integration_script}")
            print_error(f"p10k integration script not found. This is probably a bug.")
            return 1
        
        # Run the integration script with the position argument
        result = subprocess.call(["zsh", integration_script, position])
        
        return result
        
    except Exception as e:
        logger.error(f"Error setting up p10k integration: {e}")
        print_error(f"Error setting up p10k integration: {e}")
        return 1

def run_p10k_test():
    """Run a test of the Powerlevel10k integration.
    
    Runs a test script that verifies the Powerlevel10k integration is working correctly.
    """
    logger.info("Running p10k integration test")
    
    try:
        # Find the test script
        test_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "core", "integrations", "p10k_test.zsh"
        )
        
        # Check if the script exists
        if not os.path.exists(test_script):
            logger.error(f"p10k test script not found at {test_script}")
            print_error(f"p10k test script not found. This is probably a bug.")
            return 1
        
        # Run the test script
        result = subprocess.call(["zsh", test_script])
        
        return result
        
    except Exception as e:
        logger.error(f"Error running p10k test: {e}")
        print_error(f"Error running p10k test: {e}")
        return 1

@safe_execute()
def run_command_help(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run help command wrapper.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    return handle_help_command(args)

@safe_execute()
def run_command_version(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run version command wrapper.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    return handle_version_command(args)

@safe_execute()
def run_command_prompt(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run prompt customization command.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    
    # Placeholder for prompt customization - will be implemented in a future phase
    logger.info("Prompt customization command received with args: " + str(args))
    
    # Return placeholder message
    return {
        "success": False,
        "output": "🧪 Rick says: Prompt customization not implemented yet. *burp* I'll get to it when I feel like it."
    }

@safe_execute()
def run_command_update(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run update check command.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    
    # Placeholder for update check - will be implemented in a future phase
    logger.info("Update check command received with args: " + str(args))
    
    # Return placeholder message
    return {
        "success": False,
        "output": "🧪 Rick says: Update check not implemented yet. *burp* You think I have time for this?"
    }

@safe_execute()
def run_command_config(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run config command wrapper.
    
    Args:
        args: Optional list of command arguments
        
    Returns:
        Command result dictionary
    """
    if args is None:
        args = []
    return handle_config_command(args)

# Command mapping
COMMANDS = {
    "help": run_command_help,
    "version": run_command_version,
    "prompt": run_command_prompt,
    "p10k": run_command_p10k,
    "update": run_command_update,
    "config": run_command_config,
    "diagnose": run_command_diagnose,
    "metrics": run_command_metrics,
}

def print_help():
    """Print help information for Rick Assistant."""
    print(f"\n{TEXT_GREEN}Rick Sanchez ZSH Assistant{TEXT_RESET} v{__version__}")
    print(f"{TEXT_BLUE}=================================={TEXT_RESET}")
    print("Available commands:")
    print(f"  {TEXT_YELLOW}help{TEXT_RESET}     - Show this help message")
    print(f"  {TEXT_YELLOW}version{TEXT_RESET}  - Show version information")
    print(f"  {TEXT_YELLOW}prompt{TEXT_RESET}   - Customize the prompt (options: enable, disable, custom_position)")
    print(f"  {TEXT_YELLOW}p10k{TEXT_RESET}     - Configure Powerlevel10k integration (options: left, right, dir)")
    print(f"  {TEXT_YELLOW}update{TEXT_RESET}   - Check for updates")
    print(f"  {TEXT_YELLOW}config{TEXT_RESET}   - Configure Rick Assistant settings")
    print(f"  {TEXT_YELLOW}diagnose{TEXT_RESET} - Run diagnostics to troubleshoot issues")
    print(f"  {TEXT_YELLOW}metrics{TEXT_RESET}  - Display current system metrics (CPU, RAM, Temperature)")
    print("")
    print(f"Run '{TEXT_YELLOW}rick COMMAND --help{TEXT_RESET}' for more information on a command.")
    print("")
    return 0
