#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Menu Launcher for Rick Assistant.

This script serves as the entry point for the menu system,
handling different menu types and configurations.
"""

import sys
import os
import argparse
import shutil
import subprocess
import re
import locale
from typing import Optional, List, Dict, Any, Tuple

# Add parent directory to path to allow importing from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import menu system
try:
    from src.ui.menu import (
        create_hierarchical_menu, navigate_hierarchy, run_test_menu,
        create_wizard, show_message, create_context_menu, Menu
    )
    from src.utils.logger import get_logger
    from src.utils.errors import safe_execute
    from src.utils.config import get_config_value, set_config_value
    from src.ui.text import supports_unicode, supports_ansi_color, color_text
except ImportError as e:
    print(f"Error importing Rick Assistant modules: {e}")
    sys.exit(1)

# Set up logger
logger = get_logger("menu_launcher")

# Define menu symbols dictionary for icons used in diagnostics
MENU_SYMBOLS = {
    "folder": "📁",  # Folder icon
    "status": "ℹ️",   # Status/info icon
    "debug": "🔧",    # Debug/tools icon
    "help": "❓",     # Help icon
    "config": "⚙️",   # Configuration icon
    "toggle_on": "✅",  # Toggle on icon
    "toggle_off": "❌"   # Toggle off icon
}

@safe_execute()
def execute_rick_command(command: str, *args) -> Tuple[bool, str]:
    """
    Execute a Rick command and return the result.
    
    Args:
        command: The command to execute
        
    Returns:
        Tuple[bool, str]: Success status and output
    """
    # Safety check for invalid command inputs
    if not command or not isinstance(command, str):
        # Handle Menu objects or submenu dictionaries being incorrectly passed
        if isinstance(command, dict) and command.get("type") == "submenu":
            return False, "Cannot execute a submenu as a command - this is a menu navigation error"
        elif str(command).startswith("<src.ui.menu.Menu "):
            return False, "Cannot execute a Menu object as a command - this is a menu navigation error"
        else:
            return False, f"Invalid command input: {type(command).__name__}"
    
    # Get command components
    cmd_parts = command.split()
    if len(cmd_parts) < 2 or cmd_parts[0] != "rick":
        return False, f"Invalid Rick command format: {command}"
    
    # Get the base command (without 'rick')
    base_cmd = cmd_parts[1]
    
    # Handle special commands with custom processing
    if base_cmd == "status":
        return execute_status_command()
    elif base_cmd == "debug":
        return execute_debug_command()
    elif base_cmd == "version":
        return execute_version_command()
    elif base_cmd == "help":
        return execute_help_command()
        
    # For other commands, execute directly with rick wrapper or in ZSH
    try:
        # Check if the rick wrapper is available in PATH
        rick_wrapper = shutil.which("rick")
        
        if rick_wrapper:
            # Execute command with the rick wrapper
            logger.debug(f"Executing command via rick wrapper: {command}")
            
            try:
                # Execute with a timeout to prevent hanging
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15  # Timeout after 15 seconds
                )
                
                # Process output
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                
                # Format the output
                formatted_output = filter_command_output(stdout, stderr, base_cmd)
                
                # Return success based on return code
                return result.returncode == 0, formatted_output
                
            except subprocess.TimeoutExpired:
                return False, f"Command timed out after 15 seconds: {command}"
                
        else:
            # Rick wrapper not found, try to execute in ZSH directly
            logger.warning("Rick wrapper not found, falling back to ZSH execution")
            
            # Build ZSH command to source the plugin and execute the command
            rick_command = f"zsh -c 'source \"$RICK_ASSISTANT_SCRIPT_DIR/rick_assistant.plugin.zsh\" && {command}'"
            
            try:
                # Execute with a timeout to prevent hanging
                result = subprocess.run(
                    rick_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15  # Timeout after 15 seconds
                )
                
                # Process output
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                
                # Format the output
                formatted_output = filter_command_output(stdout, stderr, base_cmd)
                
                # Return success based on return code
                return result.returncode == 0, formatted_output
                
            except subprocess.TimeoutExpired:
                return False, f"Command timed out after 15 seconds: {command}"
        
    except Exception as e:
        error_msg = f"Error executing Rick command: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@safe_execute(default_return=(False, "Error executing status command"))
def execute_status_command() -> Tuple[bool, str]:
    """Execute the status command with simplified output."""
    try:
        # Try to get Rick's status directly without executing the command
        rick_dir = os.environ.get('RICK_ASSISTANT_SCRIPT_DIR', os.getcwd())
        sys.path.insert(0, rick_dir)
        
        try:
            from src.utils.config import get_config_value
            enabled = get_config_value("general.enabled", True)
            status = "enabled" if enabled else "disabled"
            return True, f"Rick is {status}"
        except ImportError:
            # Fall back to command execution
            result = subprocess.run(
                "rick status", 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                # Extract just the status line
                status_line = result.stdout.strip()
                return True, status_line
            else:
                return False, "Could not determine Rick's status"
    except Exception as e:
        logger.error(f"Error executing status command: {e}")
        return False, "Error retrieving Rick's status"

@safe_execute(default_return=(False, "Error executing debug command"))
def execute_debug_command() -> Tuple[bool, str]:
    """Execute the debug command with simplified output."""
    try:
        # Execute the command and capture output
        result = subprocess.run(
            "rick debug", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Filter to just the important status message
        if result.returncode == 0:
            output = result.stdout.strip()
            # Extract just the debug mode status message
            match = re.search(r"Rick is now .*? \(debug mode (?:on|off)\)", output)
            if match:
                return True, match.group(0)
            else:
                return True, "Debug mode toggled successfully"
        else:
            return False, "Failed to toggle debug mode"
    except Exception as e:
        logger.error(f"Error executing debug command: {e}")
        return False, "Error toggling debug mode"

@safe_execute(default_return=(False, "Error executing version command"))
def execute_version_command() -> Tuple[bool, str]:
    """Execute the version command with simplified output."""
    try:
        # Execute the command and capture output
        result = subprocess.run(
            "rick version", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            # Just return the version line
            return True, result.stdout.strip()
        else:
            return False, "Could not retrieve version information"
    except Exception as e:
        logger.error(f"Error executing version command: {e}")
        return False, "Error retrieving version information"

@safe_execute(default_return=(False, "Error executing help command"))
def execute_help_command() -> Tuple[bool, str]:
    """Execute the help command with simplified output for menu context."""
    try:
        # Execute the command and capture output
        result = subprocess.run(
            "rick help", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            # Return a summary of available commands
            help_text = "Available Rick Commands:\n"
            
            # Extract command list from help output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "rick " in line and " - " in line:
                    help_text += "• " + line.strip() + "\n"
            
            return True, help_text
        else:
            return False, "Could not retrieve help information"
    except Exception as e:
        logger.error(f"Error executing help command: {e}")
        return False, "Error retrieving help information"

@safe_execute(default_return="Error filtering command output")
def filter_command_output(output: str, error_output: str, command: str) -> str:
    """
    Filter and format command output for menu display.
    
    Args:
        output: Command standard output
        error_output: Command standard error
        command: The command that was executed
        
    Returns:
        str: Formatted output suitable for menu display
    """
    # Combine output and error if needed
    if error_output and not output:
        output = error_output
    elif error_output:
        output += "\n" + error_output
    
    # Strip ANSI color codes which can cause display issues
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    # Filter common command outputs
    if command == "status":
        # Just extract the status line
        match = re.search(r"Rick is (enabled|disabled)", output)
        if match:
            return match.group(0)
    elif command == "debug":
        # Extract just the debug mode message
        match = re.search(r"Rick is now .*? \(debug mode (?:on|off)\)", output)
        if match:
            return match.group(0)
    elif command == "version":
        # For version, just return the first line that contains version info
        for line in output.split('\n'):
            if "version" in line.lower():
                return line.strip()
        # Fallback to original output
        return output
    elif command == "help":
        # Format the help output to be more readable
        lines = output.split('\n')
        formatted_help = "Available Rick Commands:\n\n"
        command_found = False
        
        for line in lines:
            # Clean the line
            line = line.strip()
            
            # Only include command descriptions
            if "rick " in line and " - " in line:
                command_found = True
                # Extract the command and description
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    cmd, desc = parts
                    # Format nicely with bullet point
                    formatted_help += f"• {cmd.strip()}\n  {desc.strip()}\n\n"
                else:
                    # Fallback if parsing fails
                    formatted_help += f"• {line.strip()}\n\n"
        
        # If no commands were found, just use a trimmed version of the original output
        if not command_found:
            formatted_help = "Rick Assistant Help:\n\n"
            # Add up to 15 lines of the original output
            for line in lines[:15]:
                if line.strip():
                    formatted_help += line.strip() + "\n"
            
        return formatted_help
    
    # Truncate very long output
    if len(output) > 2000:
        lines = output.split('\n')
        if len(lines) > 30:
            # Show first 20 lines and last 10
            output = '\n'.join(lines[:20]) + "\n\n[...output truncated...]\n\n" + '\n'.join(lines[-10:])
    
    # Try to get terminal width
    try:
        term_width = shutil.get_terminal_size((80, 24)).columns
        # Set a reasonable width for the output box (80% of terminal width)
        width = min(int(term_width * 0.8), 100)
    except Exception:
        # Fallback width
        width = 76
        
    # Calculate border
    border = "─" * (width - 2)
    
    # Create a nicely formatted output
    formatted_output = f"┌{border}┐\n"
    
    # Add command title
    title = f" Command: rick {command} "
    padding_left = (width - len(title) - 2) // 2
    padding_right = width - padding_left - len(title) - 2
    formatted_output += f"│{' ' * padding_left}{title}{' ' * padding_right}│\n"
    formatted_output += f"├{border}┤\n"
    
    # Add command output with line wrapping
    lines = output.split('\n')
    
    # Process each line with proper wrapping
    for line in lines:
        # Skip processing if the line is empty
        if not line.strip():
            formatted_output += f"│{' ' * (width - 2)}│\n"
            continue
            
        # Handle long lines by wrapping them
        remaining = line
        while remaining:
            # Calculate how much of the current line we can include
            display_width = width - 4  # Allow for padding on both sides
            
            # Take a chunk of the right size
            if len(remaining) <= display_width:
                # This chunk fits completely
                chunk = remaining
                remaining = ""
            else:
                # Need to wrap; try to break at word boundary
                chunk = remaining[:display_width]
                # Look for last space in this chunk to break at word boundary
                last_space = chunk.rfind(' ')
                if last_space > display_width // 2:  # Only if the space is reasonably positioned
                    chunk = chunk[:last_space]
                    remaining = remaining[last_space+1:]
                else:
                    # No good breakpoint found, just split at the max size
                    remaining = remaining[display_width:]
            
            # Add the chunk with proper padding
            padding = width - len(chunk) - 4
            formatted_output += f"│ {chunk}{' ' * padding} │\n"
    
    # Add bottom border
    formatted_output += f"└{border}┘\n"
    
    return formatted_output

@safe_execute()
def launch_main_menu():
    """Launch the main Rick Assistant menu."""
    # Create the main menu structure
    menu_structure = {
        "Rick Commands": {
            "items": [
                {"text": "Status", "value": "rick status"},
                {"text": "Debug Mode", "value": "rick debug"},
                {"text": "Version Info", "value": "rick version"},
                {"text": "Show Help", "value": "rick help"}
            ]
        },
        "Configuration": {
            "items": [
                {"text": "Prompt Integration", "value": "rick prompt"},
                {"text": "Powerlevel10k Setup", "value": "rick p10k"},
                {"text": "Run Diagnostics", "value": "rick diagnose"},
                {"text": "Display Settings", "submenu": {
                    "items": [
                        {"text": "Show Welcome Message", "type": "toggle", "key": "general.show_welcome_message", "default": True},
                        {"text": "Theme Settings 🚧", "value": "theme_settings_placeholder"},
                        {"text": "Color Scheme 🚧", "value": "color_settings_placeholder"}
                    ]
                }},
                {"text": "Menu Settings", "submenu": {
                    "items": [
                        {"text": "Use Python Implementation", "type": "toggle", "key": "menu.use_python_implementation", "default": False},
                        {"text": "Enable Animations", "type": "toggle", "key": "menu.animations_enabled", "default": False},
                        {"text": "Use Static Portal", "type": "toggle", "key": "menu.use_static_portal", "default": True},
                        {"text": "Terminal Compatibility Mode", "type": "toggle", "key": "menu.terminal_compatibility_mode", "default": False}
                    ]
                }},
                {"text": "Prompt Settings", "submenu": {
                    "items": [
                        {"text": "Prompt Mode", "value": "rick prompt"},
                        {"text": "Catchphrases 🚧", "value": "catchphrases_placeholder"},
                        {"text": "System Info 🚧", "value": "system_info_placeholder"},
                        {"text": "Exit Code 🚧", "value": "exit_code_placeholder"}
                    ]
                }},
                {"text": "System Monitoring", "submenu": {
                    "items": [
                        {"text": "Temperature Settings 🚧", "value": "temperature_placeholder"},
                        {"text": "CPU Monitoring 🚧", "value": "cpu_placeholder"},
                        {"text": "RAM Monitoring 🚧", "value": "ram_placeholder"}
                    ]
                }},
                {"text": "Error Message Style", "submenu": {
                    "items": [
                        {"text": "Rick Style", "value": {"type": "error_style", "style": "rick"}},
                        {"text": "Simple", "value": {"type": "error_style", "style": "simple"}},
                        {"text": "Technical", "value": {"type": "error_style", "style": "technical"}}
                    ]
                }}
            ]
        },
        "Tools": {
            "items": [
                {"text": "Clean Up Files", "value": "rick cleanup"},
                {"text": "Setup Wizard", "value": "setup_wizard"},
                {"text": "Terminal Info", "value": "terminal_info"},
                {"text": "Menu Diagnostics", "value": "menu_diagnostics"}
            ]
        }
    }
    
    # Create and navigate the menu
    main_menu = create_hierarchical_menu(
        title="Rick Assistant Menu",
        structure=menu_structure
    )
    
    result = navigate_hierarchy(main_menu)
    
    # Handle the result
    if result:
        menu, index, value = result
        
        # Special handling for certain actions
        if value == "setup_wizard":
            run_setup_wizard()
            return launch_main_menu()  # Return to main menu when done
        elif value == "terminal_info":
            show_terminal_info()
            return launch_main_menu()  # Return to main menu when done
        elif value == "menu_diagnostics":
            show_menu_diagnostics()
            return launch_main_menu()  # Return to main menu when done
        elif isinstance(value, dict) and value.get("type") == "toggle":
            # Handle toggle items
            key = value.get("key")
            default = value.get("default")
            if key:
                success, message = handle_toggle_setting(key, default)
                
                # Show feedback to the user
                if success:
                    show_message("Setting Updated", message, "success")
                else:
                    show_message("Error", message, "error")
                    
                # If toggling the menu implementation, ask if user wants to restart
                if key == "menu.use_python_implementation":
                    # Get the new setting value
                    use_python = get_config_value("menu.use_python_implementation", False)
                    impl_name = "Python" if use_python else "Native ZSH"
                    
                    # Ask if user wants to restart menu with new implementation
                    restart = confirm_action(
                        f"Switch to {impl_name} Implementation?",
                        f"Would you like to restart the menu using the {impl_name} implementation?",
                        "Yes, restart now", "No, continue with current implementation"
                    )
                    
                    if restart and not use_python:
                        # User wants to restart with Native ZSH
                        return None  # Exit Python menu to fall back to Native ZSH
                
                # Return to the same menu
                return launch_main_menu()
        elif isinstance(value, dict) and value.get("type") == "error_style":
            # Handle error style setting
            style = value.get("style")
            if style:
                success = set_config_value("general.error_style", style)
                if success:
                    style_name = "Rick-style" if style == "rick" else style.capitalize()
                    show_message("Setting Updated", f"Error messages will now use {style_name} format.", "success")
                else:
                    show_message("Error", "Failed to update error style setting.", "error")
                
                # Return to the same menu
                return launch_main_menu()
        elif value in ["theme_settings_placeholder", "color_settings_placeholder", 
                      "catchphrases_placeholder", "system_info_placeholder", 
                      "exit_code_placeholder", "temperature_placeholder", 
                      "cpu_placeholder", "ram_placeholder"]:
            # Handle placeholder items
            show_message("Work in Progress", 
                        "Wh-what do you think I am, Morty? A miracle worker?\nThis feature isn't implemented yet! *burp*", 
                        "warning")
            return launch_main_menu()  # Return to main menu
        elif isinstance(value, Menu):
            # This is a submenu object - we should never get here because
            # navigate_hierarchy should handle submenu navigation internally
            logger.warning("Received Menu object as value - this should not happen")
            # Just return to the main menu
            return launch_main_menu()
        else:
            # Execute Rick command
            success, output = execute_rick_command(value)
            
            # Show results
            if success:
                show_message("Command Output", output, "info")
            else:
                show_message("Command Error", output, "error")
            
            # Set flag to indicate we're returning from a command execution
            # This will prevent unnecessary animations when going back to the menu
            try:
                # Import the menu module and set the flag directly
                import src.ui.menu as menu_module
                
                # Set the flag to True to skip animations
                menu_module.RETURNING_FROM_COMMAND = True
                logger.debug("Set animation skip flag for returning from command")
            except (ImportError, AttributeError) as e:
                logger.debug(f"Could not set animation skip flag: {e}")
            
            # Return to main menu when done
            return launch_main_menu()
    
    return None

@safe_execute()
def run_setup_wizard():
    """Run the setup wizard."""
    # Simple example wizard
    steps = [
        {
            "title": "Basic Settings",
            "text": "Welcome to the Rick Assistant Setup Wizard. Let's configure some basic settings.",
            "fields": [
                {
                    "name": "username",
                    "prompt": "What should Rick call you?",
                    "default": os.environ.get("USER", "Morty")
                },
                {
                    "name": "enable_sass",
                    "type": "toggle",
                    "prompt": "Enable Rick's sass?",
                    "default": True
                }
            ]
        },
        {
            "title": "Display Settings",
            "text": "Now let's configure how Rick appears in your terminal.",
            "fields": [
                {
                    "name": "prompt_style",
                    "type": "selection",
                    "prompt": "Choose prompt style",
                    "options": [
                        {"text": "Right Prompt", "value": "right_prompt"},
                        {"text": "Left Prompt", "value": "left_prompt"},
                        {"text": "Command Output", "value": "command_output"}
                    ],
                    "default": "right_prompt"
                },
                {
                    "name": "animation_speed",
                    "type": "selection",
                    "prompt": "Animation speed",
                    "options": [
                        {"text": "Fast", "value": 0.5},
                        {"text": "Normal", "value": 1.0},
                        {"text": "Slow", "value": 1.5},
                        {"text": "Very Slow", "value": 2.0}
                    ],
                    "default": 1.0
                }
            ]
        },
        {
            "title": "Menu Features",
            "text": "Configure menu behavior options.",
            "fields": [
                {
                    "name": "menu_animations",
                    "type": "toggle",
                    "prompt": "Enable menu animations?",
                    "default": True
                },
                {
                    "name": "menu_commentary",
                    "type": "toggle",
                    "prompt": "Enable Rick's menu commentary?",
                    "default": True
                }
            ]
        }
    ]
    
    # Run the wizard
    result = create_wizard(steps, title="Rick Assistant Setup")
    
    if result:
        # Save the settings
        try:
            # Import configuration module
            rick_dir = os.environ.get('RICK_ASSISTANT_SCRIPT_DIR', os.getcwd())
            sys.path.insert(0, rick_dir)
            
            try:
                from src.utils.config import set_config_value
                
                # Save each setting
                for key, value in result.items():
                    if key == "username":
                        set_config_value("general.username", value)
                    elif key == "enable_sass":
                        set_config_value("general.sass_enabled", value)
                    elif key == "prompt_style":
                        set_config_value("prompt_integration.display_style", value)
                    elif key == "animation_speed":
                        set_config_value("animation_speed_multiplier", value)
                    elif key == "menu_animations":
                        set_config_value("animations_enabled", value)
                    elif key == "menu_commentary":
                        set_config_value("menu.commentary_enabled", value)
                
                show_message(
                    f"Your settings have been saved successfully. Changes will take effect immediately.",
                    title="Setup Complete",
                    message_type="success"
                )
            except ImportError:
                show_message(
                    f"Could not save settings: configuration module not found.",
                    title="Setup Error",
                    message_type="error"
                )
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            show_message(
                f"Error saving settings: {str(e)}",
                title="Setup Error",
                message_type="error"
            )
    
    return result

@safe_execute()
def show_terminal_info():
    """Show terminal information."""
    try:
        term_width, term_height = shutil.get_terminal_size((80, 24))
        term_type = os.environ.get("TERM", "unknown")
        shell = os.environ.get("SHELL", "unknown")
        
        # Get more detailed system info
        python_version = sys.version.split()[0]
        platform_info = sys.platform
        
        # Check for WSL
        in_wsl = False
        if platform_info == "linux":
            try:
                with open("/proc/version", "r") as f:
                    if "microsoft" in f.read().lower():
                        in_wsl = True
            except:
                pass
        
        # Check for Rick Assistant env vars
        rick_dir = os.environ.get('RICK_ASSISTANT_SCRIPT_DIR', "Not set")
        rick_debug = "Enabled" if os.environ.get('RICK_ASSISTANT_DEBUG') else "Disabled"
        
        # Format the info for display
        info = f"""
Terminal Information:
--------------------
Terminal Type: {term_type}
Terminal Size: {term_width}x{term_height}
Shell: {shell}
Python Version: {python_version}
OS: {platform_info}{"(WSL)" if in_wsl else ""}

Rick Assistant:
--------------------
Script Directory: {rick_dir}
Debug Mode: {rick_debug}
Tab Completion: {"Available" if shutil.which("compdef") else "Not available"}
"""
        
        show_message(
            info, 
            title="Terminal Information", 
            message_type="info",
            with_animation=False
        )
    except Exception as e:
        logger.error(f"Error showing terminal info: {e}")
        show_message(
            f"Error retrieving terminal information: {str(e)}",
            title="Error",
            message_type="error"
        )

@safe_execute()
def show_menu_diagnostics():
    """Show menu system diagnostics information."""
    try:
        # Get terminal environment information
        term_width, term_height = shutil.get_terminal_size((80, 24))
        term_type = os.environ.get("TERM", "unknown")
        term_encoding = os.environ.get("LANG", "unknown")
        shell = os.environ.get("SHELL", "unknown")
        
        # Check Python configuration
        python_version = sys.version.split()[0]
        python_encoding = sys.getdefaultencoding()
        stdout_encoding = sys.stdout.encoding
        
        # Check locale settings
        try:
            current_locale = locale.getlocale()
        except:
            current_locale = ("unknown", "unknown")
        
        # Check for WSL
        in_wsl = False
        if sys.platform == "linux":
            try:
                with open("/proc/version", "r") as f:
                    in_wsl = "microsoft" in f.read().lower()
            except:
                pass
        
        # Get menu configuration - with proper error handling
        try:
            # Check if functions are available
            unicode_supported = supports_unicode()
            ansi_supported = supports_ansi_color()
            
            # Get configuration values with defaults if not set
            animations_enabled = get_config_value("menu.animations_enabled", False)
            use_static_portal = get_config_value("menu.use_static_portal", True)
            terminal_compatibility_mode = get_config_value("menu.terminal_compatibility_mode", False)
        except Exception as e:
            logger.error(f"Error getting configuration values: {e}")
            unicode_supported = "unknown"
            ansi_supported = "unknown"
            animations_enabled = False
            use_static_portal = True
            terminal_compatibility_mode = False
        
        # Build the diagnostic info
        info = f"""
Menu System Diagnostics:
=======================

Terminal Information:
  Type: {term_type}
  Size: {term_width}x{term_height}
  Shell: {shell}
  Environment Encoding: {term_encoding}
  WSL: {"Yes" if in_wsl else "No"}

Python Configuration:
  Version: {python_version}
  Default Encoding: {python_encoding}
  Stdout Encoding: {stdout_encoding}
  Locale: {current_locale[0]}.{current_locale[1]}

Menu Configuration:
  Unicode Support: {unicode_supported}
  ANSI Color Support: {ansi_supported}
  Animations Enabled: {animations_enabled}
  Static Portal: {use_static_portal}
  Terminal Compatibility Mode: {terminal_compatibility_mode}

Icon Test:
  Folder: {MENU_SYMBOLS.get("folder", "[?]")}
  Status: {MENU_SYMBOLS.get("status", "[?]")}
  Debug: {MENU_SYMBOLS.get("debug", "[?]")}
  Help: {MENU_SYMBOLS.get("help", "[?]")}
  
This information can help diagnose display issues in the menu system.
If you see squares or question marks instead of icons, your terminal
may have limited Unicode support.
"""
        
        # Display the diagnostics
        show_message(
            info,
            title="Menu Diagnostics",
            message_type="info",
            with_animation=False
        )
    except Exception as e:
        logger.error(f"Error showing menu diagnostics: {e}")
        show_message(
            f"Error retrieving menu diagnostics: {str(e)}",
            title="Diagnostics Error",
            message_type="error",
            with_animation=False
        )

@safe_execute()
def handle_toggle_setting(key: str, default: Any = None) -> Tuple[bool, str]:
    """
    Handle a toggle setting change from the menu.
    
    Args:
        key: The configuration key to toggle
        default: Default value if the setting doesn't exist
        
    Returns:
        Tuple[bool, str]: Success status and message
    """
    try:
        # Get current value
        current_value = get_config_value(key, default)
        
        # Toggle the value
        new_value = not current_value
        
        # Update the configuration
        set_config_value(key, new_value)
        
        # Log the change
        logger.debug(f"Toggle setting {key}: {current_value} -> {new_value}")
        
        # Return success with message
        return True, f"Setting '{key}' changed to {'ON' if new_value else 'OFF'}"
    except Exception as e:
        logger.error(f"Error toggling setting {key}: {e}")
        return False, f"Error toggling setting: {str(e)}"

@safe_execute()
def confirm_action(title="Confirm Action", message="Are you sure?", confirm_text="Yes", cancel_text="No", default=True):
    """
    Display a confirmation dialog and get user response.
    
    Args:
        title (str): The title of the confirmation dialog
        message (str): The message to display
        confirm_text (str): Text for the confirm button
        cancel_text (str): Text for the cancel button
        default (bool): Default selection (True for confirm, False for cancel)
    
    Returns:
        bool: True if confirmed, False if cancelled
    """
    # Create a simple menu with Yes/No options
    menu = Menu(title)
    
    # Add message
    menu.add_text(message)
    menu.add_separator()
    
    # Track result
    result = [default]  # Use list for mutable reference
    
    # Add options
    def confirm():
        result[0] = True
        return True
        
    def cancel():
        result[0] = False
        return True
    
    # Add items in the right order based on default
    if default:
        menu.add_item(confirm_text, confirm)
        menu.add_item(cancel_text, cancel)
    else:
        menu.add_item(cancel_text, cancel)
        menu.add_item(confirm_text, confirm)
    
    # Navigate menu
    menu.navigate()
    
    # Return result
    return result[0]

@safe_execute()
def main():
    """Main entry point for the menu launcher."""
    parser = argparse.ArgumentParser(description="Rick Assistant Menu Launcher")
    parser.add_argument("menu_type", nargs="?", default="main", 
                        help="Type of menu to launch (main, settings, tools)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--test-command", help="Test a specific command without menu")
    
    args = parser.parse_args()
    
    # Enable debug mode if requested
    if args.debug:
        logger.setLevel("DEBUG")
        os.environ['RICK_ASSISTANT_DEBUG'] = '1'
        logger.debug("Debug mode enabled")
    
    # Test a specific command if requested
    if args.test_command:
        logger.debug(f"Testing command: {args.test_command}")
        success, output = execute_rick_command(args.test_command)
        print(f"Command {'succeeded' if success else 'failed'}")
        print("Output:")
        print(output)
        return 0
    
    # Launch the appropriate menu based on type
    if args.menu_type == "main":
        return launch_main_menu()
    elif args.menu_type == "settings":
        return launch_settings_menu()
    elif args.menu_type == "help":
        return launch_help_menu()
    elif args.menu_type == "status":
        return launch_status_menu()
    elif args.menu_type == "test":
        return run_test_menu()
    else:
        show_message(f"Unknown menu type: {args.menu_type}", 
                     title="Error", message_type="error")
        return None

@safe_execute()
def launch_settings_menu():
    """Launch the settings menu directly."""
    # Create a settings menu
    settings_menu = Menu("Rick Assistant Settings")
    
    # Add menu implementation toggle
    settings_menu = add_menu_implementation_toggle(settings_menu)
    
    # Add other settings
    settings_menu.add_item("Display Settings", lambda: launch_display_settings())
    settings_menu.add_item("Prompt Settings", lambda: launch_prompt_settings())
    settings_menu.add_item("Menu Animations", lambda: launch_animation_settings())
    settings_menu.add_item("Back to Main Menu", lambda: launch_main_menu())
    
    # Navigate the menu
    return settings_menu.navigate()

# Add menu implementation toggle to settings
def add_menu_implementation_toggle(settings_menu):
    """
    Add menu implementation toggle to settings menu.
    
    Args:
        settings_menu: The settings menu to add the toggle to
    """
    # Get current setting
    use_python = get_config_value("menu.use_python_implementation", False)
    
    # Create toggle function
    def toggle_menu_implementation():
        current = get_config_value("menu.use_python_implementation", False)
        new_value = not current
        set_config_value("menu.use_python_implementation", new_value)
        
        # Show confirmation message
        if new_value:
            show_message(
                "Menu Implementation Changed",
                "Menu system will now use Python implementation.\n"
                "This change will take effect the next time you open the menu.",
                "info"
            )
        else:
            show_message(
                "Menu Implementation Changed",
                "Menu system will now use native ZSH implementation.\n"
                "This change will take effect the next time you open the menu.",
                "info"
            )
        
        # Update menu item text
        nonlocal settings_menu
        for item in settings_menu.items:
            if hasattr(item, 'toggle_menu_implementation'):
                item.text = f"Use Python Menu Implementation: {'Yes' if new_value else 'No'}"
                break
    
    # Add toggle to menu
    toggle_item = settings_menu.add_item(
        f"Use Python Menu Implementation: {'Yes' if use_python else 'No'}",
        toggle_menu_implementation
    )
    toggle_item.toggle_menu_implementation = True  # Add attribute for identification
    
    return settings_menu

@safe_execute()
def launch_display_settings():
    """Launch the display settings menu."""
    # Create a display settings menu
    menu = Menu("Display Settings")
    
    # Add display settings
    menu.add_toggle("Show Welcome Message", "general.show_welcome_message", True)
    menu.add_toggle("Use Color", "display.use_color", True)
    menu.add_toggle("Use Unicode", "display.use_unicode", True)
    
    # Add back option
    menu.add_item("Back to Settings", lambda: launch_settings_menu())
    
    # Navigate the menu
    return menu.navigate()

@safe_execute()
def launch_prompt_settings():
    """Launch the prompt settings menu."""
    # Create a prompt settings menu
    menu = Menu("Prompt Settings")
    
    # Add prompt settings
    menu.add_toggle("Enable Prompt Integration", "prompt.enabled", True)
    menu.add_toggle("Show Temperature", "prompt.show_temperature", True)
    menu.add_toggle("Show Status", "prompt.show_status", True)
    
    # Add back option
    menu.add_item("Back to Settings", lambda: launch_settings_menu())
    
    # Navigate the menu
    return menu.navigate()

@safe_execute()
def launch_animation_settings():
    """Launch the animation settings menu."""
    # Create an animation settings menu
    menu = Menu("Animation Settings")
    
    # Add animation settings
    menu.add_toggle("Enable Animations", "menu.animations_enabled", False)
    menu.add_toggle("Use Static Portal", "menu.use_static_portal", True)
    menu.add_toggle("Terminal Compatibility Mode", "menu.terminal_compatibility_mode", False)
    
    # Add back option
    menu.add_item("Back to Settings", lambda: launch_settings_menu())
    
    # Navigate the menu
    return menu.navigate()

@safe_execute()
def launch_help_menu():
    """Launch the help menu."""
    # Get help text
    success, help_text = execute_rick_command("help")
    if not success:
        help_text = "Error: Could not retrieve help information."
    
    # Show help text
    show_message(help_text, title="Rick Assistant Help", message_type="info")
    return 0

@safe_execute()
def launch_status_menu():
    """Launch the status menu."""
    # Get status text
    success, status_text = execute_rick_command("status")
    if not success:
        status_text = "Error: Could not retrieve status information."
    
    # Show status text
    show_message(status_text, title="Rick Assistant Status", message_type="info")
    return 0

if __name__ == "__main__":
    main() 