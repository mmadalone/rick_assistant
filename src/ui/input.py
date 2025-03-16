#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Input Handling Module for Rick Assistant.

This module provides robust terminal input handling capabilities with Rick's personality,
including single key input, selection menus, and tab completion. All functions
include proper terminal state management to prevent shell crashes.

Example usage:
    from src.ui.input import get_input, get_single_key, get_selection
    
    # Get text input from user
    name = get_input("Enter your name")
    
    # Get a single keypress
    key = get_single_key("Press any key to continue")
    
    # Get a selection from options
    options = ["Option 1", "Option 2", "Option 3"]
    index = get_selection(options)
"""

import os
import sys
import re
import signal
import logging
import random
import time
import shutil
from typing import List, Dict, Any, Optional, Union, Tuple, Callable

# Platform-specific imports
try:
    import termios
    import tty
    import fcntl
    import select
    HAS_UNIX_TERMINAL = True
except ImportError:
    HAS_UNIX_TERMINAL = False

# Try to import for Windows support
try:
    import msvcrt
    HAS_WINDOWS_TERMINAL = True
except ImportError:
    HAS_WINDOWS_TERMINAL = False

# Check if terminal is available
if not (HAS_UNIX_TERMINAL or HAS_WINDOWS_TERMINAL):
    print("Warning: Neither Unix nor Windows terminal capabilities detected. Input handling will be limited.")

# Import the new completion system
try:
    from src.ui.completion import (
        complete_command, 
        complete_path, 
        complete_option, 
        format_completions, 
        get_completion_context
    )
    HAS_COMPLETION_SYSTEM = True
except ImportError:
    HAS_COMPLETION_SYSTEM = False
    # We'll use our built-in completers if the dedicated module isn't available yet

# Import utility functions
from src.utils.logger import get_logger
from src.utils.errors import safe_execute

# Import from other Rick Assistant modules
try:
    from src.utils.errors import safe_execute, RickAssistantError, handle_exception
    from src.utils.logger import get_logger
    from src.ui.text import (
        color_text, format_text, stream_text, 
        format_error, format_warning, format_success, format_info,
        get_terminal_width, get_terminal_height, supports_ansi_color, supports_unicode
    )
    from src.core.prompt import format_rick_prompt, format_user_prompt
except ImportError as e:
    # Fallback for when importing as standalone
    print(f"Warning: Could not import all Rick Assistant modules: {e}")
    # Define minimal versions of required functions
    def safe_execute(default_return=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}")
                    return default_return
            return wrapper
        return decorator
    
    def handle_exception(e): print(f"Error: {e}")
    def get_logger(name): 
        return logging.getLogger(name)
    def color_text(text, color): return text
    def format_text(text, width=80): return text
    def stream_text(text, speed=0.03): print(text)
    def format_error(message): return f"Error: {message}"
    def format_warning(message): return f"Warning: {message}"
    def format_success(message): return f"Success: {message}"
    def format_info(message): return f"Info: {message}"
    def get_terminal_width(): return 80
    def get_terminal_height(): return 24
    def supports_ansi_color(): return False
    def supports_unicode(): return False
    def format_rick_prompt():
        return "🧪 Rick> "
    
    def format_user_prompt(username=None):
        return f"👹 {username or 'User'}> "

# Set up logger
logger = get_logger("input")

# Constants
CTRL_C = b'\x03' if sys.platform == 'win32' else '\x03'
ENTER = b'\r' if sys.platform == 'win32' else '\r'
BACKSPACE = b'\x08' if sys.platform == 'win32' else '\x7f'
TAB = b'\t' if sys.platform == 'win32' else '\t'
ESC = b'\x1b' if sys.platform == 'win32' else '\x1b'
UP_ARROW = b'\xe0H' if sys.platform == 'win32' else '\x1b[A'
DOWN_ARROW = b'\xe0P' if sys.platform == 'win32' else '\x1b[B'

# Rick's input style comments
RICK_INPUT_PROMPTS = [
    "Well? I'm waiting, *burp* genius: ",
    "Type something already: ",
    "Don't just sit there, *burp* type something: ",
    "Input required, even from your primitive brain: ",
    "Your thoughts, if you have any: "
]

# Add a new constant for command history
HISTORY_MAX_SIZE = 100  # Maximum number of commands to store in history

# Add a global to store command history
_command_history = []
_history_index = -1

# Move aliases and __all__ to end of file after all functions are defined

# Terminal state management functions
@safe_execute(default_return=None)
def save_term_state():
    """
    Save the current terminal state so it can be restored later.
    
    Returns:
        Optional[Any]: The saved terminal state or None if not supported
    """
    logger.debug("Saving terminal state")
    
    if HAS_UNIX_TERMINAL:
        try:
            fd = sys.stdin.fileno()
            # Save terminal attributes
            old_settings = termios.tcgetattr(fd)
            # Save flags for non-blocking mode
            old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            return (old_settings, old_flags)
        except Exception as e:
            logger.error(f"Error saving terminal state: {e}")
            return None
    elif HAS_WINDOWS_TERMINAL:
        # Windows doesn't have a direct equivalent - just return a placeholder
        return True
    else:
        logger.warning("Terminal state management not supported on this platform")
        return None

@safe_execute(default_return=False)
def restore_term_state(saved_state):
    """
    Restore terminal state from a previously saved state.
    
    Args:
        saved_state: The terminal state from save_term_state()
        
    Returns:
        bool: True if successful, False if failed
    """
    logger.debug("Restoring terminal state")
    
    if saved_state is None:
        logger.warning("No saved state to restore")
        return False
        
    if HAS_UNIX_TERMINAL and isinstance(saved_state, tuple):
        try:
            old_settings, old_flags = saved_state
            fd = sys.stdin.fileno()
            # Restore terminal attributes
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # Restore flags
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
            return True
        except Exception as e:
            logger.error(f"Error restoring terminal state: {e}")
            return False
    elif HAS_WINDOWS_TERMINAL:
        # Windows has no direct equivalent
        return True
    else:
        logger.warning("Terminal state management not supported on this platform")
        return False

@safe_execute(default_return=False)
def enable_raw_mode():
    """
    Set the terminal to raw mode for immediate key reading without buffering.
    
    Raw mode allows reading single keypresses without requiring the user to press Enter.
    This function handles the platform-specific differences between Unix and Windows.
    The terminal state MUST be restored with disable_raw_mode() when finished.
    
    Returns:
        Any: The previous terminal state (to be passed to disable_raw_mode)
            - Unix: tuple of (terminal_settings, file_descriptor_flags)
            - Windows: True (no special state needed)
            - None if an error occurred or platform not supported
    
    Example:
        >>> saved_state = enable_raw_mode()
        >>> try:
        ...     key = sys.stdin.read(1)  # Read a single key
        ... finally:
        ...     disable_raw_mode(saved_state)  # Important to restore!
    """
    logger.debug("Enabling raw mode")
    
    if HAS_UNIX_TERMINAL:
        try:
            fd = sys.stdin.fileno()
            # Save current terminal settings
            old_settings = termios.tcgetattr(fd)
            old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            
            # Set terminal to raw mode
            tty.setraw(fd)
            
            return (old_settings, old_flags)
        except Exception as e:
            logger.error(f"Error enabling raw mode: {e}")
            return None
    elif HAS_WINDOWS_TERMINAL:
        # Windows doesn't need special handling for raw mode as msvcrt.getch()
        # already behaves like raw mode
        return True
    else:
        logger.warning("Raw mode not supported on this platform")
        return None

@safe_execute(default_return=False)
def disable_raw_mode(saved_state):
    """
    Restore terminal to normal mode after using raw mode.
    
    This function reverts the changes made by enable_raw_mode() and
    must be called to restore proper terminal functionality.
    
    Args:
        saved_state: Terminal state returned by enable_raw_mode()
            - Unix: tuple of (terminal_settings, file_descriptor_flags)
            - Windows: any value (ignored)
    
    Returns:
        bool: True if restored successfully, False if failed
        
    Example:
        >>> saved_state = enable_raw_mode()
        >>> try:
        ...     # Read input in raw mode
        ... finally:
        ...     disable_raw_mode(saved_state)  # Always restore terminal state
    """
    return restore_term_state(saved_state)

@safe_execute(default_return=False)
def flush_input_buffer():
    """
    Clear the input buffer to prevent unwanted keystrokes being processed.
    
    Returns:
        bool: True if successful, False if failed
    """
    logger.debug("Flushing input buffer")
    
    if HAS_UNIX_TERMINAL:
        try:
            # Use termios to flush input
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
            
            # As a backup, also try non-blocking read loop
            old_flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
            try:
                # Set stdin to non-blocking
                fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
                
                # Read until no more data
                while True:
                    try:
                        data = os.read(sys.stdin.fileno(), 1024)
                        if not data:
                            break
                    except BlockingIOError:
                        break
            finally:
                # Restore blocking mode
                fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, old_flags)
                
            return True
        except Exception as e:
            logger.error(f"Error flushing input buffer: {e}")
            return False
    elif HAS_WINDOWS_TERMINAL:
        try:
            # Flush input by reading all available input
            while msvcrt.kbhit():
                msvcrt.getch()
            return True
        except Exception as e:
            logger.error(f"Error flushing input buffer on Windows: {e}")
            return False
    else:
        logger.warning("Input buffer flushing not supported on this platform")
        return False

@safe_execute(default_return=(80, 24))
def get_terminal_dimensions():
    """
    Get the current terminal dimensions (width, height).
    
    Returns:
        Tuple[int, int]: (width, height) of the terminal
    """
    try:
        # Try to use stty to get dimensions
        if HAS_UNIX_TERMINAL:
            import struct
            import subprocess
            
            # First method: Use ioctl if available
            try:
                h, w = struct.unpack('HHHH', 
                    fcntl.ioctl(sys.stdout.fileno(), 
                                termios.TIOCGWINSZ, 
                                struct.pack('HHHH', 0, 0, 0, 0))
                )[:2]
                if w > 0 and h > 0:
                    return w, h
            except:
                pass
                
            # Second method: Try using stty command
            try:
                with subprocess.Popen(['stty', 'size'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE) as process:
                    output, _ = process.communicate()
                    h, w = map(int, output.decode().split())
                    if w > 0 and h > 0:
                        return w, h
            except:
                pass
        
        # Fallback methods
        if hasattr(shutil, 'get_terminal_size'):
            # Python 3.3+ has this function
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        
        # Last resort: environment variables or defaults
        width = int(os.environ.get('COLUMNS', 80))
        height = int(os.environ.get('LINES', 24))
        return width, height
    except Exception as e:
        logger.error(f"Error getting terminal dimensions: {e}")
        return 80, 24  # Default fallback

@safe_execute()
def handle_terminal_resize(callback=None):
    """
    Set up a handler for terminal resize events (SIGWINCH).
    
    This function registers a signal handler that updates internal terminal
    dimensions when the terminal is resized, and optionally calls a user-provided
    callback function.
    
    Args:
        callback (Callable, optional): Function to call when terminal is resized.
            The callback will receive two arguments: (width, height)
    
    Returns:
        Callable: The previous signal handler (if any) for later restoration
        
    Example:
        >>> def on_resize(width, height):
        ...     print(f"Terminal resized to {width}x{height}")
        >>> 
        >>> original_handler = handle_terminal_resize(on_resize)
        >>> # Later, to restore:
        >>> import signal
        >>> signal.signal(signal.SIGWINCH, original_handler)
    """
    if not HAS_UNIX_TERMINAL:
        logger.warning("Terminal resize handling not supported on this platform")
        return

    def handle_resize(signum, frame):
        """Signal handler for SIGWINCH (window change)."""
        if callback:
            dims = get_terminal_dimensions()
            callback(dims)
    
    # Set up signal handler for SIGWINCH (terminal resize)
    if hasattr(signal, 'SIGWINCH'):
        signal.signal(signal.SIGWINCH, handle_resize)
        logger.debug("Set up terminal resize handler") 

# Basic input handler functions
@safe_execute(default_return=None)
def get_input(prompt=None, default=None, use_rick_style=True):
    """
    Get user input with formatted prompt and Rick's personality.
    
    This function displays a prompt (with optional Rick Sanchez flair) and
    returns the user's input. It supports default values and handles
    interruptions gracefully.
    
    Args:
        prompt (str, optional): The prompt to display. If None, a random Rick prompt is used.
        default (str, optional): Default value if user enters nothing.
        use_rick_style (bool): Whether to use Rick's sarcastic style.
        
    Returns:
        Optional[str]: The user input or None if error occurred.
        
    Examples:
        >>> name = get_input("Enter your name")
        >>> location = get_input("Where are you?", default="Earth C-137")
        >>> answer = get_input(None, use_rick_style=True)  # Uses a random Rick prompt
    """
    try:
        # Format the prompt with Rick's style if requested
        if prompt is None and use_rick_style:
            prompt = random.choice(RICK_INPUT_PROMPTS)
        elif prompt is not None and use_rick_style:
            # Add Rick's touch to custom prompts
            if random.random() < 0.3 and not prompt.endswith(('*burp*', ':')):
                prompt = prompt.rstrip() + ", *burp* "
            if not prompt.endswith(': ') and not prompt.endswith(':\n'):
                prompt = prompt.rstrip() + ': '
        
        # Add default value to prompt if provided
        if default is not None:
            if prompt.endswith(': '):
                prompt = prompt[:-2] + f" [{default}]: "
            else:
                prompt = prompt + f" [{default}]: "
                
        # Display the prompt and get input
        if supports_ansi_color():
            formatted_prompt = color_text(prompt, "cyan")
        else:
            formatted_prompt = prompt
            
        user_input = input(formatted_prompt)
        
        # Return default if input is empty
        if not user_input and default is not None:
            return default
            
        return user_input
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInput cancelled.")
        return None
    except Exception as e:
        logger.error(f"Error getting input: {e}")
        return None

@safe_execute(default_return=None)
def get_single_key(prompt=None, timeout=None):
    """
    Get a single keypress without Enter key and with optional timeout.
    
    This function sets the terminal to raw mode to read a single keypress
    without requiring the Enter key to be pressed. It handles special keys
    (like arrow keys) and timeout functionality.
    
    Args:
        prompt (str, optional): Text to display as prompt. If None, no prompt is shown.
        timeout (float, optional): Maximum time to wait for input in seconds.
            If None, wait indefinitely.
        
    Returns:
        Optional[str]: 
            - Single character pressed by user
            - None if error occurred or timeout expired
            - CTRL_C constant if Ctrl+C was pressed
            
    Examples:
        >>> key = get_single_key("Press any key to continue")
        >>> direction = get_single_key("Choose direction (arrow keys)")
        >>> response = get_single_key("Press Y/N within 5 seconds", timeout=5.0)
    """
    # Display prompt if provided
    if prompt:
        if supports_ansi_color():
            print(color_text(prompt, "cyan"), end='', flush=True)
        else:
            print(prompt, end='', flush=True)
    
    key = None
    saved_state = None
    
    try:
        if HAS_UNIX_TERMINAL:
            # Save terminal state and set to raw mode
            saved_state = enable_raw_mode()
            
            # Set up timeout using select if requested
            if timeout is not None:
                ready, _, _ = select.select([sys.stdin], [], [], timeout)
                if not ready:
                    return None  # Timeout
            
            # Read a single character
            key = os.read(sys.stdin.fileno(), 1).decode('utf-8', errors='replace')
            
            # Handle escape sequences for arrow keys, etc.
            if key == ESC:
                # Check if we can read more bytes (for escape sequences)
                if timeout is not None:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if not ready:
                        return key  # Just ESC key
                
                # Try to read the rest of the escape sequence
                try:
                    rest = os.read(sys.stdin.fileno(), 2).decode('utf-8', errors='replace')
                    key = key + rest
                except:
                    pass  # Just return ESC if we can't read more
                    
        elif HAS_WINDOWS_TERMINAL:
            # Windows doesn't need raw mode
            if timeout is not None:
                # Implement timeout for Windows
                start_time = time.time()
                while (time.time() - start_time) < timeout:
                    if msvcrt.kbhit():
                        key_bytes = msvcrt.getch()
                        # Handle special keys (arrow keys, etc.)
                        if key_bytes == b'\xe0':
                            key_bytes += msvcrt.getch()
                        key = key_bytes.decode('utf-8', errors='replace')
                        break
                    time.sleep(0.01)  # Small sleep to prevent CPU hogging
            else:
                # Wait indefinitely
                key_bytes = msvcrt.getch()
                # Handle special keys (arrow keys, etc.)
                if key_bytes == b'\xe0':
                    key_bytes += msvcrt.getch()
                key = key_bytes.decode('utf-8', errors='replace')
        else:
            # Fallback for systems without raw input support
            logger.warning("Single key input not fully supported on this platform")
            key = input().strip()
            if key:
                key = key[0]  # Take just the first character
                
        return key
    except KeyboardInterrupt:
        return CTRL_C
    except Exception as e:
        logger.error(f"Error getting single key: {e}")
        return None
    finally:
        # Restore terminal state
        if saved_state:
            disable_raw_mode(saved_state)
        
        # Print newline for cleaner output
        if key and key not in (CTRL_C, '\r', '\n'):
            print()

@safe_execute(default_return=None)
def get_confirmation(prompt="Are you sure?", default=False, yes_key='y', no_key='n'):
    """
    Get a yes/no confirmation from the user with Rick-style commentary.
    
    Args:
        prompt (str): The confirmation prompt
        default (bool): Default response if user just presses Enter
        yes_key (str): Key for "yes" (default: 'y')
        no_key (str): Key for "no" (default: 'n')
        
    Returns:
        Optional[bool]: True for yes, False for no, None on error/interrupt
    """
    # Format the confirmation prompt with Rick's style and color
    yes_char = yes_key.upper() if default else yes_key.lower()
    no_char = no_key.upper() if not default else no_key.lower()
    
    rick_comments = [
        "Like you have a choice...",
        "As if your answer matters...",
        "This better be good...",
        "Try not to mess this up...",
        "*burp* Think carefully..."
    ]
    
    # Add Rick's commentary 50% of the time
    if random.random() < 0.5:
        comment = random.choice(rick_comments)
        prompt = f"{prompt} {comment}"
    
    # Format the prompt with yes/no options
    full_prompt = f"{prompt} [{yes_char}/{no_char}] "
    
    while True:
        if supports_ansi_color():
            formatted_prompt = color_text(full_prompt, "yellow")
        else:
            formatted_prompt = full_prompt
            
        # Get a single key response
        response = get_single_key(formatted_prompt)
        
        # Handle response
        if response is None:
            return None  # Error occurred
        elif response.lower() == yes_key.lower() or (response in ('\r', '\n') and default):
            return True
        elif response.lower() == no_key.lower() or (response in ('\r', '\n') and not default):
            return False
        elif response == CTRL_C:
            print("\nOperation cancelled.")
            return None

@safe_execute(default_return=None)
def get_password(prompt="Enter password"):
    """
    Get masked password input for secure entries.
    
    Args:
        prompt (str): The prompt to display
        
    Returns:
        Optional[str]: The password entered or None on error/interrupt
    """
    full_prompt = f"{prompt}: "
    
    if supports_ansi_color():
        formatted_prompt = color_text(full_prompt, "cyan")
    else:
        formatted_prompt = full_prompt
    
    # Handle password input based on platform
    try:
        if HAS_UNIX_TERMINAL:
            # Use getpass if available (Unix systems)
            try:
                import getpass
                return getpass.getpass(formatted_prompt)
            except ImportError:
                # Manual implementation if getpass not available
                print(formatted_prompt, end='', flush=True)
                
                fd = sys.stdin.fileno()
                saved_state = termios.tcgetattr(fd)
                
                try:
                    # Disable echo
                    new_settings = termios.tcgetattr(fd)
                    new_settings[3] = new_settings[3] & ~termios.ECHO
                    termios.tcsetattr(fd, termios.TCSANOW, new_settings)
                    
                    # Read password
                    password = input()
                    return password
                finally:
                    # Restore terminal settings
                    termios.tcsetattr(fd, termios.TCSADRAIN, saved_state)
                    
        elif HAS_WINDOWS_TERMINAL:
            # Manual implementation for Windows
            print(formatted_prompt, end='', flush=True)
            
            password = ""
            while True:
                char = msvcrt.getch()
                
                # Handle Enter, Backspace and Ctrl+C
                if char in (b'\r', b'\n'):
                    print()
                    break
                elif char == b'\b':  # Backspace
                    if password:
                        password = password[:-1]
                        # Erase character on screen
                        print('\b \b', end='', flush=True)
                elif char == b'\x03':  # Ctrl+C
                    print('^C')
                    return None
                else:
                    password += char.decode('utf-8', errors='replace')
                    # Print asterisk for each character
                    print('*', end='', flush=True)
                    
            return password
        else:
            # Fallback for unsupported platforms - WARNING: shows password
            logger.warning("Secure password input not supported on this platform")
            return input(formatted_prompt)
    except KeyboardInterrupt:
        print("\nPassword entry cancelled.")
        return None

@safe_execute(default_return=None)
def get_selection(options, prompt="Select an option", default=None):
    """
    Get a selection from a list of options with Rick-style commentary.
    
    This function displays a numbered list of options and prompts the user
    to select one by number. It includes Rick's sarcastic comments and handles
    invalid selections with appropriate error messages.
    
    Args:
        options (List[str]): List of options to select from.
        prompt (str): Prompt to display above the list of options.
        default (int, optional): Default option index if user presses Enter.
            Note: this is a zero-based index, but displayed to user as 1-based.
        
    Returns:
        Optional[int]: 
            - Zero-based index of selected option
            - None on error/interruption
    
    Examples:
        >>> options = ["Run simulation", "Configure portal gun", "Exit"]
        >>> choice = get_selection(options)
        >>> 
        >>> planets = ["Earth", "Blips and Chitz", "Gazorpazorp"]
        >>> planet_idx = get_selection(planets, "Choose destination", default=0)
    """
    if not options:
        logger.error("No options provided for selection")
        return None
        
    # Rick's selection commentaries
    rick_comments = [
        "Try not to pick the worst one...",
        "Let's see how bad your choice is...",
        "Prepare to disappoint me with your selection...",
        "*burp* Pick one already!",
        "Oh boy, another terrible decision coming up..."
    ]
    
    # Add Rick's commentary sometimes
    if random.random() < 0.4:
        prompt = f"{prompt} {random.choice(rick_comments)}"
    
    # Display options with indices
    print()
    print(color_text(prompt, "cyan"))
    for i, option in enumerate(options):
        # Highlight default option if set
        if default is not None and i == default:
            print(color_text(f"[{i+1}] {option} (default)", "green"))
        else:
            print(f"[{i+1}] {option}")
    
    # Get user selection with validation
    while True:
        try:
            selection = get_input("Enter number", None, use_rick_style=True)
            
            # Handle empty input
            if not selection and default is not None:
                return default
                
            # Validate input is a number
            if not selection or not selection.isdigit():
                print(color_text("Enter a valid number. Even Jerry could do that.", "red"))
                continue
                
            # Convert to index
            index = int(selection) - 1
            
            # Validate in range
            if index < 0 or index >= len(options):
                print(color_text(f"Number must be between 1 and {len(options)}. *burp* Try again.", "red"))
                continue
                
            return index
        except KeyboardInterrupt:
            print("\nSelection cancelled.")
            return None 

# Completion functions
@safe_execute(default_return=[])
def complete_command(partial, shell_path=None):
    """
    Complete partial shell commands using available system commands.
    
    This function attempts to find matches for a partial command by checking
    common executable paths. It works across platforms and supports completing
    both commands and their arguments.
    
    Args:
        partial (str): Partial command to complete.
        shell_path (str, optional): Override for PATH environment variable.
            If None, uses the system PATH.
    
    Returns:
        List[str]: List of matching command completions (empty if none found).
        
    Examples:
        >>> complete_command("py")  # Might return ["python", "python3", "pyenv"]
        >>> complete_command("git ")  # Might complete git subcommands
    """
    if not partial:
        return []
        
    # Determine platform-appropriate shell path
    if shell_path is None:
        if sys.platform == 'win32':
            # Use cmd.exe on Windows by default
            shell_path = os.environ.get('COMSPEC', 'cmd.exe')
        else:
            # Use user's default shell on Unix, fallback to /bin/sh
            shell_path = os.environ.get('SHELL', '/bin/sh')
    
    logger.debug(f"Using shell: {shell_path} for command completion")
        
    try:
        # Use appropriate completion mechanism based on platform
        import subprocess
        import tempfile
        
        if sys.platform == 'win32':
            # Windows implementation - use dir to find executables
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
        else:
            # Unix implementation - use shell's completion mechanism
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
    except Exception as e:
        logger.error(f"Error completing command: {e}")
        
        # Fallback: Try finding executables in PATH
        try:
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            completions = []
            
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
        except Exception as inner_e:
            logger.error(f"Fallback command completion failed: {inner_e}")
            return []

@safe_execute(default_return=[])
def complete_path(partial):
    """
    Complete partial file paths with tab.
    
    This function handles path completion with proper expansion of
    home directory references (~) and relative paths.
    
    Args:
        partial (str): Partial path to complete.
            
    Returns:
        List[str]: List of matching path completions (empty if none found).
        
    Examples:
        >>> complete_path("~/Doc")  # Might return ["~/Documents/"]
        >>> complete_path("./src/")  # Might return subdirectories and files
    """
    if partial == '':
        partial = '.'
        
    try:
        # Expand ~ in path
        expanded_path = os.path.expanduser(partial)
        
        # Split into directory and prefix
        if os.path.isdir(expanded_path):
            directory = expanded_path
            prefix = ''
        else:
            directory = os.path.dirname(expanded_path) or '.'
            prefix = os.path.basename(expanded_path)
        
        # Get matching files in directory
        if os.path.isdir(directory):
            matches = []
            try:
                for entry in os.listdir(directory):
                    if entry.startswith(prefix):
                        full_path = os.path.join(directory, entry)
                        # Add trailing slash for directories
                        if os.path.isdir(full_path):
                            entry += os.path.sep
                        matches.append(entry)
            except PermissionError:
                logger.warning(f"Permission denied when accessing directory: {directory}")
                
            return sorted(matches)
        else:
            return []
    except Exception as e:
        logger.error(f"Error completing path: {e}")
        return []

@safe_execute(default_return=[])
def complete_option(partial, options):
    """
    Complete from a list of options.
    
    Args:
        partial (str): Partial string to match
        options (List[str]): List of available options
        
    Returns:
        List[str]: List of matching options
    """
    if not options:
        return []
        
    # Simple prefix matching
    matches = [opt for opt in options if opt.startswith(partial)]
    
    # If no matches, try case-insensitive matching
    if not matches:
        matches = [opt for opt in options if opt.lower().startswith(partial.lower())]
        
    return sorted(matches)

@safe_execute(default_return='')
def format_completions(options, prompt="", partial="", max_width=None):
    """
    Format completion display with Rick-style commentary.
    
    Args:
        options (List[str]): Completion options to display
        prompt (str): Current prompt
        partial (str): Partial text being completed
        max_width (int, optional): Maximum width for formatting
        
    Returns:
        str: Formatted completions with Rick's commentary
    """
    if not options:
        return ""
        
    # Get terminal width
    if max_width is None:
        width, _ = get_terminal_dimensions()
    else:
        width = max_width
        
    # Rick's completion commentaries
    rick_comments = [
        "Here are some options, *burp* try not to pick the worst one:",
        "Look at all these choices you'll probably mess up:",
        "Even Jerry could pick one of these:",
        "Your limited options:",
        "Try one of these, genius:"
    ]
    
    # Format the header with Rick's commentary
    header = random.choice(rick_comments)
    if supports_ansi_color():
        header = color_text(header, "yellow")
        
    # Calculate column width for display
    if options:
        col_width = max(len(opt) for opt in options) + 2
    else:
        col_width = 20
        
    # Calculate number of columns that fit
    num_cols = max(1, width // col_width)
    
    # Format the completions in columns
    rows = []
    for i in range(0, len(options), num_cols):
        row = options[i:i+num_cols]
        row_text = "".join(opt.ljust(col_width) for opt in row)
        rows.append(row_text)
        
    # Build the final result
    result = f"\n{header}\n" + "\n".join(rows)
    
    return result

@safe_execute(default_return=None)
def handle_tab_key(current_text="", context=None):
    """
    Process tab key for completion based on context.
    
    This function handles tab completion for commands, file paths, or custom options.
    It attempts to auto-detect the context if not specified. When multiple 
    completions are possible, it finds the common prefix for partial completion.
    
    Args:
        current_text (str): The current input text to complete.
        context (str or dict, optional): Context to determine completion type:
            - "command": Complete shell commands
            - "path": Complete file paths
            - "option": Complete from custom options list (requires context["options"])
            - None: Auto-detect based on input (default)
            
    Returns:
        Tuple[str, List[str]]: 
            - First element: Completed text (or original if no completion)
            - Second element: List of possible completions (empty if none)
            
    Examples:
        >>> completed, options = handle_tab_key("ls -")  # Command completion
        >>> completed, options = handle_tab_key("~/Doc")  # Path completion
        >>> completed, options = handle_tab_key("ap", {"options": ["apple", "apricot"]})
    """
    if not current_text:
        return current_text, []
        
    # Use the new completion system if available
    if HAS_COMPLETION_SYSTEM:
        # Auto-detect context if not provided
        if context is None:
            completion_context = get_completion_context(current_text)
            context = completion_context
        
        # Get completions based on context
        options = []
        if context == "command":
            options = complete_command(current_text)
        elif context == "path":
            options = complete_path(current_text)
        elif context == "directory":
            options = complete_path(current_text)
            # Filter to directories only
            options = [opt for opt in options if opt.endswith('/')]
        elif context == "git" and current_text.startswith('git '):
            options = complete_command(current_text)  # The command completer handles git commands
        elif context == "rick" and (current_text.startswith('rick-') or current_text.startswith('r-')):
            options = complete_command(current_text)  # The command completer handles Rick commands
        elif context == "option" and isinstance(context, dict) and "options" in context:
            options = complete_option(current_text, context["options"])
    else:
        # Legacy completion (fallback)
        # Auto-detect context if not provided
        if context is None:
            if current_text.startswith('git '):
                context = "git"
            elif current_text.startswith('/') or current_text.startswith('./') or current_text.startswith('~/') or '/' in current_text:
                context = "path"
            elif os.path.isdir(os.path.expanduser(current_text.split()[0]) if ' ' in current_text else current_text):
                context = "directory"
            else:
                context = "command"
        
        # Get completions using legacy methods
        options = []
        if context == "command":
            options = _legacy_complete_command(current_text)
        elif context == "path":
            options = _legacy_complete_path(current_text)
        elif context == "directory":
            options = _legacy_complete_path(current_text)
            # Filter to directories only
            options = [opt for opt in options if opt.endswith('/')]
        elif context == "git" and current_text.startswith('git '):
            # Special handling for git commands
            git_part = current_text[4:].strip()
            
            # Common git commands for completion
            git_commands = [
                'add', 'branch', 'checkout', 'clone', 'commit', 'diff', 'fetch', 
                'init', 'log', 'merge', 'pull', 'push', 'rebase', 'reset', 
                'status', 'tag'
            ]
            
            if not git_part:
                # Complete the git command itself
                options = ['git ' + cmd for cmd in git_commands]
            elif not ' ' in git_part:
                # Complete the first level git subcommand
                options = ['git ' + cmd for cmd in git_commands if cmd.startswith(git_part)]
            else:
                # For git commands with arguments, fall back to path completion
                cmd_parts = git_part.split(' ', 1)
                if cmd_parts[0] in ['add', 'checkout', 'diff']:
                    path_part = cmd_parts[1] if len(cmd_parts) > 1 else ''
                    path_options = _legacy_complete_path(path_part)
                    options = [f'git {cmd_parts[0]} {path}' for path in path_options]
        elif isinstance(context, dict) and "options" in context:
            options = _legacy_complete_option(current_text, context["options"])
    
    # If only one option, auto-complete
    if len(options) == 1:
        return options[0], options
    elif len(options) > 1:
        # Find common prefix for partial completion
        common_prefix = os.path.commonprefix(options)
        if common_prefix and len(common_prefix) > len(current_text):
            return common_prefix, options
    
    # Return original text with options for display
    return current_text, options

# Safety and error handling features
@safe_execute()
def handle_ctrl_c(original_handler=None):
    """
    Set up a signal handler for Ctrl+C (SIGINT) that doesn't crash the terminal.
    
    This function installs a custom signal handler that properly cleans up
    terminal state when Ctrl+C is pressed, preventing the terminal from 
    remaining in an unusable state.
    
    Args:
        original_handler (Callable, optional): Original signal handler to restore on cleanup.
            If None, captures the current handler automatically.
        
    Returns:
        Callable: The original handler for later restoration with restore_ctrl_c_handler()
        
    Example:
        >>> original = handle_ctrl_c()
        >>> try:
        ...     # Your code that might be interrupted
        ... finally:
        ...     restore_ctrl_c_handler(original)
    """
    if original_handler is None:
        original_handler = signal.getsignal(signal.SIGINT)
    
    def safe_interrupt_handler(signum, frame):
        """Safe interrupt handler that won't crash the terminal."""
        # Print newline for cleaner output
        print("\nOperation interrupted by user", file=sys.stderr)
        
        # If we're in raw mode, try to restore terminal
        if HAS_UNIX_TERMINAL:
            try:
                # Try to restore terminal to a sane state
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, 
                               termios.tcgetattr(sys.stdin.fileno()))
            except:
                pass
                
        # Re-raise KeyboardInterrupt for proper handling
        raise KeyboardInterrupt("User interrupted operation")
    
    # Set the handler
    signal.signal(signal.SIGINT, safe_interrupt_handler)
    
    return original_handler

@safe_execute()
def restore_ctrl_c_handler(original_handler):
    """
    Restore the original Ctrl+C handler.
    
    Args:
        original_handler: The original handler to restore
    """
    if original_handler:
        signal.signal(signal.SIGINT, original_handler)

@safe_execute(default_return=False)
def recover_from_input_errors():
    """
    Recover from input-related errors by resetting terminal state.
    
    This function attempts to restore the terminal to a working state
    after input-related errors occur. It's especially useful when
    raw mode might have been left active due to an exception.
    
    Returns:
        bool: True if recovery was successful, False otherwise
        
    Example:
        >>> # After an exception in raw mode
        >>> recover_from_input_errors()
        >>> print("Terminal should be usable again")
    """
    logger.info("Attempting to recover from input errors")
    
    try:
        # Print a newline to ensure clean output
        print()
        
        if HAS_UNIX_TERMINAL:
            # Try to get current terminal settings
            try:
                current_attrs = termios.tcgetattr(sys.stdin.fileno())
                
                # Reset ECHO and ICANON flags to restore normal behavior
                current_attrs[3] = current_attrs[3] | termios.ECHO | termios.ICANON
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, current_attrs)
            except:
                # If that fails, try more aggressive methods
                try:
                    # Use stty to reset terminal
                    os.system("stty sane")
                except:
                    pass
                    
            # Also try to flush input buffer
            try:
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
            except:
                pass
                
        # For both platforms, print something to ensure terminal is working
        print(color_text("Terminal reset after error. *burp* You're welcome.", "yellow"))
        
        return True
    except Exception as e:
        logger.error(f"Failed to recover from input errors: {e}")
        return False

@safe_execute(default_return=(None, "Input timeout"))
def get_input_with_timeout(prompt=None, timeout=30.0, default=None, use_rick_style=True):
    """
    Get user input with a timeout, returning default value if timer expires.
    
    This function builds on get_input() but adds a timeout feature.
    If the user doesn't respond within the specified timeout period,
    it returns the default value (or None) with a timeout message.
    
    Args:
        prompt (str, optional): The prompt to display. If None, a random Rick prompt is used.
        timeout (float): Maximum time to wait for input in seconds.
        default (str, optional): Default value if user enters nothing or timeout expires.
        use_rick_style (bool): Whether to use Rick's sarcastic style.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: 
            - First element: User input, default value, or None if error
            - Second element: Error/timeout message or None if input was successful
            
    Examples:
        >>> value, error = get_input_with_timeout("Your answer", timeout=10.0, default="42")
        >>> if error:
        ...     print(f"Timeout or error: {error}")
        >>> else:
        ...     print(f"You entered: {value}")
    """
    if not HAS_UNIX_TERMINAL:
        # Fallback for non-Unix systems - doesn't support timeout
        logger.warning("Input timeout not supported on this platform")
        result = get_input(prompt, default, use_rick_style)
        return result, None
    
    # Format the prompt
    if prompt is None and use_rick_style:
        prompt = random.choice(RICK_INPUT_PROMPTS)
    elif prompt is not None and use_rick_style:
        # Add Rick's touch to custom prompts
        if random.random() < 0.3 and not prompt.endswith(('*burp*', ':')):
            prompt = prompt.rstrip() + ", *burp* "
        if not prompt.endswith(': ') and not prompt.endswith(':\n'):
            prompt = prompt.rstrip() + ': '
    
    # Add timeout information to prompt
    timeout_info = f" [{timeout}s timeout]"
    if prompt.endswith(': '):
        prompt = prompt[:-2] + timeout_info + ": "
    else:
        prompt = prompt + timeout_info
    
    # Add default value to prompt if provided
    if default is not None:
        if prompt.endswith(': '):
            prompt = prompt[:-2] + f" [{default}]: "
        else:
            prompt = prompt + f" [{default}]: "
    
    # Set up the input capturing in a separate thread
    import threading
    import queue
    
    input_queue = queue.Queue()
    
    def input_thread():
        try:
            # Display the prompt and get input
            if supports_ansi_color():
                formatted_prompt = color_text(prompt, "cyan")
            else:
                formatted_prompt = prompt
                
            user_input = input(formatted_prompt)
            input_queue.put(user_input)
        except Exception as e:
            input_queue.put(e)
    
    # Start the input thread
    thread = threading.Thread(target=input_thread)
    thread.daemon = True
    thread.start()
    
    # Wait for input or timeout
    try:
        result = input_queue.get(block=True, timeout=timeout)
        
        # Handle exceptions from input thread
        if isinstance(result, Exception):
            if isinstance(result, KeyboardInterrupt):
                return None, "Input cancelled"
            else:
                logger.error(f"Error in input thread: {result}")
                return None, f"Input error: {result}"
        
        # Return default if input is empty
        if not result and default is not None:
            return default, None
            
        return result, None
    except queue.Empty:
        # Timeout occurred
        if use_rick_style:
            timeout_msgs = [
                "Wow, *burp* you're slow even for a human.",
                "Did you fall asleep? Using the default.",
                "Time's up, genius. I've got better things to do.",
                "Some of us don't live forever, you know. Moving on.",
                "Ugh, waiting for you is like waiting for Jerry to be useful."
            ]
            print(color_text(random.choice(timeout_msgs), "yellow"))
        else:
            print(color_text("Input timeout. Using default value.", "yellow"))
            
        return default, "Input timeout"

@safe_execute(default_return="Enter something useful") 
def provide_input_help(context):
    """
    Show context-sensitive help for different input types.
    
    Args:
        context (str): Context identifier ("command", "path", "confirmation", etc.)
        
    Returns:
        str: Help message appropriate for the context
    """
    # Base help messages
    help_messages = {
        "command": "Enter a command to execute. Use TAB for completion.",
        "path": "Enter a file path. Use TAB to complete paths.",
        "confirmation": "Enter Y for yes or N for no.",
        "selection": "Enter the number of your selection.",
        "password": "Enter your password (input will be hidden).",
        "text": "Enter text and press ENTER when done.",
        "number": "Enter a numerical value.",
        "default": "Enter your input or press ENTER for default."
    }
    
    # Rick-styled help messages
    rick_help = {
        "command": "Type a command, genius. Even Jerry could figure this out. Use TAB if your memory's failing you.",
        "path": "It's a *burp* file path. You know, those things with slashes? Hit TAB if you're lost.",
        "confirmation": "It's a simple Y or N question! What part of that is confusing your primitive brain?",
        "selection": "See those numbers? Pick one. It's not quantum physics.",
        "password": "Enter a password, and no, I won't look. Not that I'd care about your pathetic secrets.",
        "text": "Use your words. If you still remember how to form coherent sentences.",
        "number": "A number. You know, those things you count with? 1, 2, 3... ring any bells?",
        "default": "Enter something or don't. The default is probably better than what you'd choose anyway."
    }
    
    # Get the appropriate help message
    context = context.lower() if context else "text"
    if context not in help_messages:
        context = "text"
        
    # 75% chance of Rick's sassy help, 25% chance of normal help
    if random.random() < 0.75:
        return rick_help.get(context, rick_help["text"])
    else:
        return help_messages.get(context, help_messages["text"])

@safe_execute(default_return=(False, "Validation failed"))
def validate_input(input_value, validator, error_message=None):
    """
    Validate user input with custom validator function.
    
    This function applies a validation function to user input and returns
    whether the validation passed, along with an optional error message.
    The validator can either return True/False or raise an exception on invalid input.
    
    Args:
        input_value (Any): The input value to validate.
        validator (Callable): Function that returns True/False or throws exception on invalid input.
            The validator should accept a single parameter (the input) and return:
            - True: Input is valid
            - False: Input is invalid
            - str: Input is invalid with custom error message
        error_message (str, optional): Custom error message on validation failure.
        
    Returns:
        Tuple[bool, str]: A tuple containing:
            - First element: Boolean indicating if validation passed (True) or failed (False)
            - Second element: Error message if validation failed, None otherwise
    
    Examples:
        >>> # Simple validation
        >>> is_valid, msg = validate_input("42", lambda x: x.isdigit())
        >>> 
        >>> # Validator with custom error message
        >>> def validate_age(age):
        ...     if not age.isdigit():
        ...         return "Age must be a number, even Jerry knows that."
        ...     if int(age) < 0 or int(age) > 130:
        ...         return "Enter a *burp* realistic age."
        ...     return True
        >>> 
        >>> is_valid, msg = validate_input(user_age, validate_age)
    """
    if not validator:
        return True, None
        
    try:
        result = validator(input_value)
        if result is True:
            return True, None
        elif result is False:
            return False, error_message or "Invalid input. Like, seriously bad."
        elif isinstance(result, str):
            # Validator returned error message
            return False, result
        else:
            # Treat any other return as pass
            return True, None
    except Exception as e:
        logger.debug(f"Input validation error: {e}")
        if error_message:
            return False, error_message
        else:
            return False, f"Invalid input: {str(e)}" 

# Main API function aliases for better naming
get_text = get_input
get_key = get_single_key
confirm = get_confirmation
select = get_selection
get_with_timeout = get_input_with_timeout

# Add module exports
__all__ = [
    # Input handling
    'get_input', 'get_single_key', 'get_selection', 'get_confirmation', 'get_password',
    'get_text', 'get_key', 'confirm', 'select', 'get_with_timeout',
    
    # Terminal state management
    'save_term_state', 'restore_term_state', 'enable_raw_mode', 'disable_raw_mode',
    'flush_input_buffer', 'get_terminal_dimensions', 'handle_terminal_resize',
    
    # Completion
    'complete_command', 'complete_path', 'complete_option', 
    'format_completions', 'handle_tab_key',
    
    # Safety features
    'handle_ctrl_c', 'restore_ctrl_c_handler', 'recover_from_input_errors',
    'validate_input', 'provide_input_help',
]

# Module initialization function
def _initialize_module():
    """Initialize the input module on import."""
    logger.debug("Initializing input module")
    
    # Check if terminal is a TTY
    if not sys.stdin.isatty():
        logger.warning("stdin is not a TTY. Some input features will be limited.")
    
    # Log platform detection results
    if HAS_UNIX_TERMINAL:
        logger.debug("Unix terminal capabilities detected")
    elif HAS_WINDOWS_TERMINAL:
        logger.debug("Windows terminal capabilities detected")
    else:
        logger.warning("No specialized terminal capabilities detected")
        
    # We'll perform terminal-specific setup after the module is fully loaded
    return {
        "unix_terminal": HAS_UNIX_TERMINAL,
        "windows_terminal": HAS_WINDOWS_TERMINAL,
        "isatty": sys.stdin.isatty(),
        "supports_ansi": supports_ansi_color() if 'supports_ansi_color' in globals() else False,
        "supports_unicode": supports_unicode() if 'supports_unicode' in globals() else False
    }

# Placeholder to be filled in with actual terminal capabilities
_terminal_capabilities = _initialize_module()

# This function will be called at the end of the module to perform initialization
# that requires all functions to be defined first
def _late_init():
    """Complete initialization after all functions are defined."""
    global _terminal_capabilities
    
    try:
        # Get terminal dimensions now that the function is defined
        width, height = get_terminal_dimensions()
        _terminal_capabilities["terminal_dimensions"] = (width, height)
        logger.debug(f"Terminal dimensions: {width}x{height}")
        
        # Set up terminal resize handler if supported
        if HAS_UNIX_TERMINAL and hasattr(signal, 'SIGWINCH'):
            handle_terminal_resize(lambda dims: logger.debug(f"Terminal resized to {dims[0]}x{dims[1]}"))
    except Exception as e:
        logger.error(f"Error during late initialization: {e}")
        _terminal_capabilities["terminal_dimensions"] = (80, 24)  # Fallback dimensions

# Add this function after validate_input
@safe_execute(default_return=None)
def get_input_with_history(prompt=None, default=None, use_rick_style=True):
    """
    Get user input with command history support using arrow keys.
    
    This enhanced version of get_input adds support for navigating
    command history using the up and down arrow keys. It requires
    raw mode terminal support.
    
    Args:
        prompt (str, optional): The prompt to display.
        default (str, optional): Default value if user enters nothing.
        use_rick_style (bool): Whether to use Rick's sarcastic style.
        
    Returns:
        Optional[str]: The user input or None if error occurred.
        
    Examples:
        >>> command = get_input_with_history("Enter command: ")
        >>> # Use up/down arrows to navigate through previous commands
    """
    global _command_history, _history_index
    
    # Reset history navigation index
    _history_index = len(_command_history)
    
    # Format the prompt with Rick's style if requested
    formatted_prompt = _format_input_prompt(prompt, default, use_rick_style)
    
    # Current input buffer
    buffer = ""
    cursor_pos = 0
    
    # Print the prompt
    if supports_ansi_color():
        sys.stdout.write(color_text(formatted_prompt, "cyan"))
    else:
        sys.stdout.write(formatted_prompt)
    sys.stdout.flush()
    
    # Save terminal state
    saved_state = save_term_state()
    
    try:
        # Set terminal to raw mode for direct key handling
        enable_raw_mode()
        
        while True:
            # Read a key
            key = _read_single_key()
            
            # Handle special keys
            if key == '\r' or key == '\n':
                # Enter key - accept input
                sys.stdout.write('\n')
                sys.stdout.flush()
                
                # Add command to history if not empty and not a duplicate of last entry
                if buffer and (not _command_history or buffer != _command_history[-1]):
                    _command_history.append(buffer)
                    # Trim history if it gets too large
                    if len(_command_history) > HISTORY_MAX_SIZE:
                        _command_history.pop(0)
                
                # Return the buffer or default if empty
                if not buffer and default:
                    return default
                return buffer
                
            elif key == '\x7f' or key == '\x08':
                # Backspace key - delete character before cursor
                if cursor_pos > 0:
                    buffer = buffer[:cursor_pos-1] + buffer[cursor_pos:]
                    cursor_pos -= 1
                    # Redraw the line
                    _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                    
            elif key == '\x1b':
                # Escape sequence - check for arrow keys
                seq = _read_escape_sequence()
                
                if seq == '[A':  # Up arrow
                    if _command_history and _history_index > 0:
                        _history_index -= 1
                        buffer = _command_history[_history_index]
                        cursor_pos = len(buffer)
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                        
                elif seq == '[B':  # Down arrow
                    if _history_index < len(_command_history) - 1:
                        _history_index += 1
                        buffer = _command_history[_history_index]
                        cursor_pos = len(buffer)
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                    elif _history_index == len(_command_history) - 1:
                        # At the end of history, clear buffer
                        _history_index = len(_command_history)
                        buffer = ""
                        cursor_pos = 0
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                        
                elif seq == '[C':  # Right arrow
                    if cursor_pos < len(buffer):
                        cursor_pos += 1
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                        
                elif seq == '[D':  # Left arrow
                    if cursor_pos > 0:
                        cursor_pos -= 1
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                
                elif seq == '[H':  # Home key
                    cursor_pos = 0
                    _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                
                elif seq == '[F':  # End key
                    cursor_pos = len(buffer)
                    _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                
            elif key == '\t':  # Tab key - auto-completion
                if buffer:
                    completed, options = handle_tab_key(buffer)
                    if completed != buffer:
                        buffer = completed
                        cursor_pos = len(buffer)
                        _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                    elif options:
                        # Display completion options below the current line
                        print('\n' + format_completions(options, partial=buffer))
                        # Redraw prompt and buffer
                        sys.stdout.write(color_text(formatted_prompt, "cyan") if supports_ansi_color() else formatted_prompt)
                        sys.stdout.write(buffer)
                        sys.stdout.flush()
                        cursor_pos = len(buffer)
                    
            elif key == CTRL_C:
                # Ctrl+C - cancel input
                sys.stdout.write('\n')
                sys.stdout.flush()
                return None
                
            elif key.isprintable():
                # Regular character - add to buffer at cursor position
                buffer = buffer[:cursor_pos] + key + buffer[cursor_pos:]
                cursor_pos += 1
                _redraw_input_line(formatted_prompt, buffer, cursor_pos)
                
    finally:
        # Restore terminal state
        restore_term_state(saved_state)

# Helper functions for get_input_with_history
def _read_single_key():
    """Read a single key from stdin without blocking."""
    if HAS_UNIX_TERMINAL:
        try:
            if select.select([sys.stdin], [], [], 0)[0]:
                return os.read(sys.stdin.fileno(), 1).decode('utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Error reading key: {e}")
            return ''
    return ''

def _read_escape_sequence():
    """Read an escape sequence from stdin."""
    seq = ''
    if HAS_UNIX_TERMINAL:
        try:
            # Wait for up to 50ms to read the full escape sequence
            start = time.time()
            while time.time() - start < 0.05:
                if select.select([sys.stdin], [], [], 0)[0]:
                    char = os.read(sys.stdin.fileno(), 1).decode('utf-8', errors='replace')
                    seq += char
                    # If we collected a complete sequence, return it
                    if seq == '[A' or seq == '[B' or seq == '[C' or seq == '[D' or \
                       seq == '[H' or seq == '[F':
                        return seq
                else:
                    time.sleep(0.001)
        except Exception as e:
            logger.error(f"Error reading escape sequence: {e}")
    return seq

def _redraw_input_line(prompt, buffer, cursor_pos):
    """Redraw the input line with the buffer and cursor at the specified position."""
    # Calculate prompt length (without ANSI color codes)
    prompt_len = len(prompt)
    if supports_ansi_color():
        # Attempt to strip ANSI color codes for width calculation
        prompt_len = len(re.sub(r'\x1b\[[0-9;]*[mK]', '', prompt))
    
    # Get terminal width to ensure we don't exceed it
    term_width = get_terminal_width()
    
    # Clear the line and return to beginning
    sys.stdout.write('\r' + ' ' * (prompt_len + len(buffer) + 5) + '\r')
    
    # Redraw prompt
    if supports_ansi_color():
        sys.stdout.write(color_text(prompt, "cyan"))
    else:
        sys.stdout.write(prompt)
    
    # Redraw buffer
    sys.stdout.write(buffer)
    
    # Move cursor to position
    if cursor_pos < len(buffer):
        sys.stdout.write('\r' + ' ' * (prompt_len + cursor_pos))
    
    sys.stdout.flush()

def _format_input_prompt(prompt, default, use_rick_style):
    """Format the input prompt with consistent styling."""
    if prompt is None and use_rick_style:
        # Use Rick's prompt style
        try:
            prompt = format_rick_prompt()
        except Exception:
            prompt = random.choice(RICK_INPUT_PROMPTS)
    elif prompt is not None and use_rick_style:
        # Add Rick's touch to custom prompts
        if random.random() < 0.3 and not prompt.endswith(('*burp*', ':')):
            prompt = prompt.rstrip() + ", *burp* "
        if not prompt.endswith(': ') and not prompt.endswith(':\n'):
            prompt = prompt.rstrip() + ': '
    
    # Add default value to prompt if provided
    if default is not None:
        if prompt.endswith(': '):
            prompt = prompt[:-2] + f" [{default}]: "
        else:
            prompt = prompt + f" [{default}]: "
            
    return prompt

# Add this function for context-aware tab completion
@safe_execute(default_return=(None, []))
def context_aware_complete(text, context=None):
    """
    Provide context-aware tab completion based on input context.
    
    This enhances the handle_tab_key function by adding more specific
    context detection and completion options.
    
    Args:
        text (str): The text to complete.
        context (str or dict, optional): Additional context for completion.
            - "command": Shell command completion
            - "path": File path completion
            - "option": Custom option list completion (requires context["options"])
            - "git": Git command completion
            - "directory": Directory-only completion
            - None: Auto-detect context (default)
            
    Returns:
        Tuple[str, List[str]]: A tuple containing:
            - Completed text (or original if no completion)
            - List of possible completions (empty if none)
            
    Examples:
        >>> completed, options = context_aware_complete("git ", "git")
        >>> completed, options = context_aware_complete("~/Doc", "path")
    """
    if not text:
        return text, []
    
    # Use the new completion system if available
    if HAS_COMPLETION_SYSTEM:
        # Auto-detect context using the completion system
        completion_context = get_completion_context(text) if context is None else context
        
        # Get completions based on context
        options = []
        
        if completion_context == "command":
            options = complete_command(text)
        elif completion_context == "path":
            options = complete_path(text)
        elif completion_context == "directory":
            options = complete_path(text)
            # Filter to directories only
            options = [opt for opt in options if opt.endswith('/')]
        elif completion_context == "git" and text.startswith('git '):
            # Handle git commands using the command completer which has special git handling
            options = complete_command(text)
        elif completion_context == "rick" and (text.startswith('rick ') or text.startswith('r-')):
            # Handle Rick commands using the command completer which has special Rick handling
            options = complete_command(text)
        elif isinstance(context, dict) and "options" in context:
            options = complete_option(text, context["options"])
    else:
        # Legacy completion (fallback)
        # Auto-detect context
        if context is None:
            if text.startswith('git '):
                context = "git"
            elif text.startswith('/') or text.startswith('./') or text.startswith('~/') or '/' in text:
                context = "path"
            elif os.path.isdir(os.path.expanduser(text.split()[0]) if ' ' in text else text):
                context = "directory"
            else:
                context = "command"
        
        # Get completions using legacy methods
        options = []
        
        if context == "command":
            options = _legacy_complete_command(text)
        elif context == "path":
            options = _legacy_complete_path(text)
        elif context == "directory":
            options = _legacy_complete_path(text)
            # Filter to directories only
            options = [opt for opt in options if opt.endswith('/')]
        elif context == "git" and text.startswith('git '):
            # Special handling for git commands
            git_part = text[4:].strip()
            
            # Common git commands for completion
            git_commands = [
                'add', 'branch', 'checkout', 'clone', 'commit', 'diff', 'fetch', 
                'init', 'log', 'merge', 'pull', 'push', 'rebase', 'reset', 
                'status', 'tag'
            ]
            
            if not git_part:
                # Complete the git command itself
                options = ['git ' + cmd for cmd in git_commands]
            elif not ' ' in git_part:
                # Complete the first level git subcommand
                options = ['git ' + cmd for cmd in git_commands if cmd.startswith(git_part)]
            else:
                # For git commands with arguments, fall back to path completion
                cmd_parts = git_part.split(' ', 1)
                if cmd_parts[0] in ['add', 'checkout', 'diff']:
                    path_part = cmd_parts[1] if len(cmd_parts) > 1 else ''
                    path_options = _legacy_complete_path(path_part)
                    options = [f'git {cmd_parts[0]} {path}' for path in path_options]
        elif isinstance(context, dict) and "options" in context:
            options = _legacy_complete_option(text, context["options"])
    
    # If only one option, auto-complete
    if len(options) == 1:
        return options[0], options
    elif len(options) > 1:
        # Find common prefix for partial completion
        common_prefix = os.path.commonprefix(options)
        if common_prefix and len(common_prefix) > len(text):
            return common_prefix, options
    
    # Return original text with options for display
    return text, options

# Menu system integration helpers
@safe_execute(default_return=(None, []))
def get_menu_selection(items, prompt="Select an option", default=None, numbered=True):
    """
    Display a menu and get user selection.
    
    This function is designed to work with the upcoming menu system
    by providing a consistent interface for menu selection.
    
    Args:
        items (List[str or dict]): Menu items to display.
            If dict, should have 'text' key for display text.
        prompt (str): Text to display above the menu.
        default (int, optional): Default selection index.
        numbered (bool): Whether to show item numbers.
        
    Returns:
        Tuple[int, any]: A tuple containing:
            - Selected index or None if cancelled
            - Selected item or None if cancelled
            
    Examples:
        >>> options = ["Option 1", "Option 2", "Option 3"]
        >>> index, selected = get_menu_selection(options)
        >>> 
        >>> menu_items = [
        ...    {"text": "Option 1", "value": "opt1"},
        ...    {"text": "Option 2", "value": "opt2"}
        ... ]
        >>> index, selected = get_menu_selection(menu_items)
    """
    if not items:
        return None, None
    
    # Convert items to display format
    display_items = []
    for item in items:
        if isinstance(item, dict) and 'text' in item:
            display_items.append(item['text'])
        else:
            display_items.append(str(item))
    
    # Get selection
    index = get_selection(display_items, prompt, default)
    
    if index is None:
        return None, None
    
    # Return selected item
    selected_item = items[index]
    return index, selected_item

# Add to __all__ list
__all__.extend([
    'get_input_with_history',
    'context_aware_complete',
    'get_menu_selection'
])

# Call the late initialization function after all functions are defined
_late_init()

# Legacy completion functions for fallback when the new system isn't available
@safe_execute(default_return=[])
def _legacy_complete_command(partial):
    """Legacy command completion function for fallback use."""
    return complete_command(partial)

@safe_execute(default_return=[])
def _legacy_complete_path(partial):
    """Legacy path completion function for fallback use."""
    return complete_path(partial)

@safe_execute(default_return=[])
def _legacy_complete_option(partial, options):
    """Legacy option completion function for fallback use."""
    return complete_option(partial, options) 