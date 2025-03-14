"""
Rick Assistant Setup Module

This module handles the initial setup and directory creation for the Rick Assistant.
It ensures all necessary directories exist and are properly configured.

"Listen M-Morty, you can't just *burp* wing it with a setup. You gotta do it right
or everything falls apart. Trust me, I've seen universes collapse from sloppy setups!"
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import subprocess

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.errors import safe_execute, RickAssistantError
from src.utils.path_safety import (
    normalize_path,
    is_path_within_safe_directories,
    ensure_safe_directory,
    resolve_path,
    validate_path_permissions
)

# Setup logger
logger = get_logger("setup")

# Define color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Define required directories and their permissions
REQUIRED_DIRS = {
    "~/": {
        ".rick_assistant": {
            "description": "Main Rick Assistant directory",
            "permissions": 0o755,
            "subdirs": {
                "logs": {"description": "Log files", "permissions": 0o755},
                "cache": {"description": "Cache directory", "permissions": 0o755},
                "plugins": {"description": "Plugin directory", "permissions": 0o755},
                "data": {"description": "Data files", "permissions": 0o755}
            }
        }
    }
}

# ASCII Art for the portal
PORTAL_ASCII_ART = [
    # Frame 1
    """
    {green}        .--.        
    {green}    _.-'    `-._    
    {green}  .'   {blue}.-""-. {green}  `.  
    {green} /    {blue}/ _  _ \\{green}    \\ 
    {green}|    {blue}|{cyan}(_){blue} {cyan}(_){blue}|{green}    | 
    {green} \\    {blue}\\ {cyan}o  o {blue}/    {green}/ 
    {green}  `.   {blue}`.__.'  {green}.'  
    {green}    `-._      _.-'    
    {green}        `----'        
    {reset}""",
    
    # Frame 2
    """
    {green}        .--.        
    {green}    _.-'{cyan}~~~~{green}`-._    
    {green}  .'{cyan}~~~{blue}.-""-. {cyan}~~~{green}`.  
    {green} /{cyan}~~{blue}~~~/ _  _ \\~~~{cyan}~~{green}\\ 
    {green}|{cyan}~~{blue}~~~~|{cyan}(_){blue} {cyan}(_){blue}|~~~~{cyan}~~{green}| 
    {green} \\{cyan}~~{blue}~~~\\ {cyan}o  o {blue}/~~~{cyan}~~{green}/ 
    {green}  `.{cyan}~~~{blue}`.__.'  {cyan}~~~{green}.'  
    {green}    `-._      _.-'    
    {green}        `----'        
    {reset}""",
    
    # Frame 3
    """
    {green}        .--.        
    {green}    _.-'{cyan}@@@@{green}`-._    
    {green}  .'{cyan}@@@{blue}.-""-. {cyan}@@@{green}`.  
    {green} /{cyan}@@{blue}@@@/ _  _ \\@@@{cyan}@@{green}\\ 
    {green}|{cyan}@@{blue}@@@@|{cyan}(_){blue} {cyan}(_){blue}|@@@@{cyan}@@{green}| 
    {green} \\{cyan}@@{blue}@@@\\ {cyan}o  o {blue}/@@@{cyan}@@{green}/ 
    {green}  `.{cyan}@@@{blue}`.__.'  {cyan}@@@{green}.'  
    {green}    `-._      _.-'    
    {green}        `----'        
    {reset}"""
]

@safe_execute()
def print_rick_dialog(text: str, burp_frequency: float = 0.3) -> None:
    """
    Print text styled as Rick's dialog with random burps.
    
    Args:
        text (str): The text to display as Rick's dialog
        burp_frequency (float): Probability of adding a burp (0.0-1.0)
    """
    # Add random burps to the dialog
    words = text.split()
    for i in range(len(words) - 1):
        if random.random() < burp_frequency:
            words[i] = words[i] + " *burp*"
    
    # Reassemble the text with burps
    burped_text = " ".join(words)
    
    # Print styled dialog
    print(f"\n{CYAN}{BOLD}Rick: {YELLOW}{burped_text}{RESET}\n")
    
    # Small delay for readability
    time.sleep(0.5)

@safe_execute()
def print_portal_animation(frames: int = 3, frame_duration: float = 0.3) -> None:
    """
    Display an animated portal ASCII art.
    
    Args:
        frames (int): Number of frames to show
        frame_duration (float): Duration to show each frame
    """
    logger.debug("Displaying portal animation")
    
    portal_frames = PORTAL_ASCII_ART
    num_frames = len(portal_frames)
    
    # Clear terminal before animation
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Display animation frames
    for _ in range(frames):
        for frame in portal_frames:
            # Format frame with colors
            colored_frame = frame.format(
                green=GREEN,
                blue=BLUE,
                cyan=CYAN,
                reset=RESET
            )
            
            # Clear terminal and show frame
            os.system('cls' if os.name == 'nt' else 'clear')
            print(colored_frame)
            
            # Wait for next frame
            time.sleep(frame_duration)
    
    # Wait a moment after animation completes
    time.sleep(0.5)

@safe_execute()
def show_welcome_screen() -> None:
    """
    Display a welcome screen with portal animation and Rick's welcome message.
    """
    # Show portal animation
    print_portal_animation(frames=5)
    
    # Display welcome title
    welcome_title = f"""
    {GREEN}{BOLD}========================================{RESET}
    {CYAN}{BOLD}   WELCOME TO THE RICK ASSISTANT SETUP   {RESET}
    {GREEN}{BOLD}========================================{RESET}
    """
    print(welcome_title)
    
    # Rick's welcome message
    welcome_message = """
    Welcome to Rick Assistant, morty! I'm gonna be your sidekick 
    in this terminal. Try not to screw things up too badly, alright?
    
    Let's get this setup going so I can start judging your terrible 
    command line choices.
    """
    print_rick_dialog(welcome_message)
    
    # Pause to let user read
    print(f"{YELLOW}Press Enter to continue...{RESET}")
    input()

@safe_execute(default_return=False)
def is_first_run() -> bool:
    """
    Check if this is the first time running the plugin.
    
    This function checks for the existence of the config directory and config file
    to determine if this is the first run of the plugin.
    
    Returns:
        bool: True if this is the first run, False otherwise
    """
    logger.debug("Checking if this is the first run of Rick Assistant")
    
    # Check if the ~/.rick_assistant directory exists
    config_dir = Path.home() / ".rick_assistant"
    
    # Check if the config file exists
    config_file = config_dir / "config.json"
    
    is_first = not (config_dir.exists() and config_file.exists())
    
    if is_first:
        logger.info("This is the first run of Rick Assistant")
    else:
        logger.debug("Not the first run of Rick Assistant")
        
    return is_first

@safe_execute(default_return=False)
def setup_directories() -> bool:
    """
    Create required directories for Rick Assistant.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    logger.info("Setting up Rick Assistant directories")
    
    success = True
    for base_dir, subdirs in REQUIRED_DIRS.items():
        # Handle home directory expansion
        if base_dir == "~/":
            base_path = Path.home()
        else:
            # Normalize the path to ensure safety
            base_path = normalize_path(base_dir)
            
            # Validate the base path
            if not base_path or not is_path_within_safe_directories(base_path):
                logger.error(f"Invalid or unsafe base directory: {base_dir}")
                success = False
                continue
                
        # Create subdirectories
        result = _create_subdirectories(base_path, subdirs)
        if not result:
            success = False
            
    if success:
        logger.info("All directories created successfully")
    else:
        logger.warning("Some directories could not be created")
        
    return success

@safe_execute(default_return=False)
def _create_subdirectories(
    base_path: Path, 
    subdirs: Dict[str, Dict[str, Any]]
) -> bool:
    """
    Recursively create subdirectories with proper permissions.
    
    Args:
        base_path: Base path to create directories under
        subdirs: Dictionary of subdirectories to create
        
    Returns:
        bool: True if all directories were created successfully
    """
    success = True
    
    for dir_name, properties in subdirs.items():
        # Calculate the full path
        dir_path = base_path / dir_name
        
        # Ensure the path is safe
        safe_path = ensure_safe_directory(dir_path, create=True, mode=properties.get("permissions", 0o755))
        
        if not safe_path:
            logger.error(f"Failed to create directory: {dir_path}")
            success = False
            continue
            
        logger.debug(f"Created directory: {dir_path} ({properties.get('description', 'No description')})")
        
        # Create any nested subdirectories
        if "subdirs" in properties and properties["subdirs"]:
            subdir_result = _create_subdirectories(dir_path, properties["subdirs"])
            if not subdir_result:
                success = False
                
    return success

@safe_execute(default_return=None)
def verify_directory_structure() -> Optional[Dict[str, Any]]:
    """
    Verify that the directory structure is complete and correct.
    
    Returns:
        Dict with verification results or None on error
    """
    logger.info("Verifying Rick Assistant directory structure")
    
    results = {
        "success": True,
        "missing_dirs": [],
        "permission_issues": [],
        "details": {}
    }
    
    # Check all required directories
    for base_dir, subdirs in REQUIRED_DIRS.items():
        # Handle home directory expansion
        if base_dir == "~/":
            base_path = Path.home()
        else:
            base_path = normalize_path(base_dir)
            if not base_path:
                logger.error(f"Invalid base directory: {base_dir}")
                results["success"] = False
                results["details"][base_dir] = {"status": "error", "reason": "Invalid path"}
                continue
                
        # Verify subdirectories
        verify_result = _verify_subdirectories(base_path, subdirs, base_dir)
        
        # Update results
        results["success"] = results["success"] and verify_result["success"]
        results["missing_dirs"].extend(verify_result["missing_dirs"])
        results["permission_issues"].extend(verify_result["permission_issues"])
        results["details"].update(verify_result["details"])
        
    if results["success"]:
        logger.info("Directory structure verification passed")
    else:
        logger.warning("Directory structure verification failed")
        if results["missing_dirs"]:
            logger.warning(f"Missing directories: {', '.join(results['missing_dirs'])}")
        if results["permission_issues"]:
            logger.warning(f"Permission issues: {', '.join(results['permission_issues'])}")
            
    return results

@safe_execute(default_return=None)
def _verify_subdirectories(
    base_path: Path, 
    subdirs: Dict[str, Dict[str, Any]],
    path_prefix: str
) -> Dict[str, Any]:
    """
    Recursively verify subdirectories existence and permissions.
    
    Args:
        base_path: Base path to verify under
        subdirs: Dictionary of subdirectories to verify
        path_prefix: String prefix for the path (for reporting)
        
    Returns:
        Dict with verification results
    """
    results = {
        "success": True,
        "missing_dirs": [],
        "permission_issues": [],
        "details": {}
    }
    
    for dir_name, properties in subdirs.items():
        # Calculate the full path
        dir_path = base_path / dir_name
        full_path_str = f"{path_prefix}/{dir_name}"
        
        # Check if directory exists
        if not dir_path.exists():
            results["success"] = False
            results["missing_dirs"].append(full_path_str)
            results["details"][full_path_str] = {"status": "missing", "path": str(dir_path)}
            continue
            
        # Check permissions
        expected_perms = properties.get("permissions", 0o755)
        perms_ok = validate_path_permissions(dir_path, expected_perms)
        
        if not perms_ok:
            results["success"] = False
            results["permission_issues"].append(full_path_str)
            results["details"][full_path_str] = {
                "status": "permission_error",
                "path": str(dir_path),
                "expected_permissions": oct(expected_perms)
            }
        else:
            results["details"][full_path_str] = {
                "status": "ok",
                "path": str(dir_path),
                "description": properties.get("description", "No description")
            }
            
        # Check subdirectories recursively
        if "subdirs" in properties and properties["subdirs"]:
            subdir_results = _verify_subdirectories(dir_path, properties["subdirs"], full_path_str)
            
            # Update results
            results["success"] = results["success"] and subdir_results["success"]
            results["missing_dirs"].extend(subdir_results["missing_dirs"])
            results["permission_issues"].extend(subdir_results["permission_issues"])
            results["details"].update(subdir_results["details"])
            
    return results

@safe_execute(default_return=False)
def repair_directories() -> bool:
    """
    Repair missing or incorrect directories in the Rick Assistant structure.
    
    Returns:
        bool: True if repair was successful, False otherwise
    """
    logger.info("Repairing Rick Assistant directory structure")
    
    # First verify the existing structure
    verification = verify_directory_structure()
    if not verification:
        logger.error("Failed to verify directory structure")
        return False
        
    # If everything is fine, no repair needed
    if verification["success"]:
        logger.info("No repairs needed, directory structure is correct")
        return True
        
    # Setup directories to fix issues
    return setup_directories()

@safe_execute()
def get_directory(dir_type: str) -> Optional[Path]:
    """
    Get the path to a specific Rick Assistant directory.
    
    Args:
        dir_type: Type of directory to retrieve (logs, cache, plugins, data)
        
    Returns:
        Path object or None if directory doesn't exist or is invalid
    """
    home_path = Path.home()
    
    # Define directory mapping
    dir_map = {
        "root": home_path / ".rick_assistant",
        "logs": home_path / ".rick_assistant" / "logs",
        "cache": home_path / ".rick_assistant" / "cache",
        "plugins": home_path / ".rick_assistant" / "plugins",
        "data": home_path / ".rick_assistant" / "data",
    }
    
    # Check if the requested directory type exists in our mapping
    if dir_type not in dir_map:
        logger.error(f"Unknown directory type: {dir_type}")
        return None
        
    # Get the directory path
    dir_path = dir_map[dir_type]
    
    # Ensure path is safe and exists
    if not ensure_safe_directory(dir_path, create=True):
        logger.error(f"Failed to ensure directory exists: {dir_path}")
        return None
        
    return dir_path

@safe_execute(default_return=False)
def confirm_setup_choices(preferences: Dict[str, Any]) -> bool:
    """
    Show a summary of user choices and ask for confirmation.
    
    Args:
        preferences (Dict[str, Any]): User preferences dictionary
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n" + f"{CYAN}{BOLD}Summary of Your Choices:{RESET}")
    print(f"  Username: {GREEN}{preferences['general'].get('username', 'Unknown')}{RESET}")
    print(f"  Theme: {GREEN}{preferences['ui'].get('theme', 'portal')}{RESET}")
    print(f"  Animations: {GREEN}{'Enabled' if preferences['ui'].get('animations', True) else 'Disabled'}{RESET}")
    print(f"  Sass Level: {GREEN}{preferences['personality'].get('sass_level', 7)}{RESET}")
    print(f"  Burp Frequency: {GREEN}{preferences['personality'].get('burp_frequency', 0.3)}{RESET}")
    
    print_rick_dialog("Look at these choices. Are you sure about this? I mean, I've seen worse. Not many, but I have.")
    
    confirm_validator = lambda x: x.lower() in ['y', 'yes', 'n', 'no']
    confirmation = get_validated_input(
        "Confirm these settings? (y/n)",
        validator=confirm_validator,
        default="y",
        error_msg="It's a yes or no question. Just type 'y' or 'n'."
    )
    
    return confirmation.lower() in ['y', 'yes']

@safe_execute(default_return=False)
def save_user_preferences(preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to config file.
    
    Args:
        preferences (Dict[str, Any]): User preferences dictionary
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    import json
    
    logger.debug(f"Attempting to save user preferences: {preferences}")
    
    # Get the config directory path
    config_dir = Path.home() / ".rick_assistant"
    logger.debug(f"Config directory path: {config_dir}")
    
    # Ensure config directory exists
    if not config_dir.exists():
        logger.debug("Config directory does not exist, creating it now")
        try:
            config_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
            logger.debug(f"Successfully created config directory: {config_dir}")
        except Exception as e:
            logger.error(f"Failed to create config directory: {str(e)}")
            print(f"Error creating directory: {str(e)}")
            return False
    
    # Define the config file path
    config_file = config_dir / "config.json"
    logger.debug(f"Config file path: {config_file}")
    
    try:
        # Add metadata to the preferences
        preferences["_metadata"] = {
            "version": "0.1.0",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create parent directories if they don't exist
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write preferences to file atomically
        # First write to a temporary file, then rename
        temp_file = config_file.with_suffix(".tmp")
        logger.debug(f"Writing to temporary file: {temp_file}")
        
        # Make sure the parent directory exists
        if not temp_file.parent.exists():
            logger.debug(f"Parent directory for temp file doesn't exist, creating: {temp_file.parent}")
            temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
                
                # Make sure the write is completed
                f.flush()
                os.fsync(f.fileno())
                
            logger.debug(f"Successfully wrote to temporary file: {temp_file}")
        except Exception as e:
            logger.error(f"Failed to write to temporary file: {str(e)}")
            print(f"Error writing to temporary file: {str(e)}")
            return False
        
        # Rename the temp file to the actual config file
        try:
            temp_file.replace(config_file)
            logger.debug(f"Successfully renamed temp file to config file: {config_file}")
        except Exception as e:
            logger.error(f"Failed to rename temp file to config file: {str(e)}")
            print(f"Error renaming temp file: {str(e)}")
            return False
        
        # Set appropriate permissions
        try:
            os.chmod(config_file, 0o644)
            logger.debug(f"Successfully set permissions on config file: {config_file}")
        except Exception as e:
            logger.error(f"Failed to set permissions on config file: {str(e)}")
            print(f"Error setting permissions: {str(e)}")
            # Continue anyway as this is not critical
        
        logger.info(f"Successfully saved user preferences to {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save preferences: {str(e)}")
        print(f"Error saving preferences: {str(e)}")
        return False

@safe_execute()
def show_completion_message() -> None:
    """
    Display a setup completion message with Rick's commentary.
    """
    success_title = f"""
    {GREEN}{BOLD}========================================{RESET}
    {CYAN}{BOLD}     RICK ASSISTANT SETUP COMPLETE      {RESET}
    {GREEN}{BOLD}========================================{RESET}
    """
    print(success_title)
    
    # Rick's completion message
    completion_message = """
    Well, look at that! You actually managed to complete the setup without 
    screwing everything up. I gotta say, I'm mildly impressed.
    
    Now I'll be hanging around your terminal, judging your command choices 
    and occasionally helping when I feel like it. 
    
    Type 'help' after any command for Rick-style assistance, or '!rick' if 
    you just want to hear one of my brilliant insights.
    """
    print_rick_dialog(completion_message)
    
    # Show portal animation to end
    print(f"{YELLOW}Rick Assistant is now active! Press Enter to continue...{RESET}")
    input()
    print_portal_animation(frames=3)

@safe_execute(default_return=False)
def create_messages_file() -> bool:
    """
    Create the default messages file for Rick Assistant.
    
    Returns:
        bool: True if creation was successful, False otherwise
    """
    import json
    
    # Get the data directory path
    data_dir = Path.home() / ".rick_assistant" / "data"
    
    # Ensure data directory exists
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create data directory: {str(e)}")
            return False
    
    # Define the messages file path
    messages_file = data_dir / "messages.json"
    
    # Skip if file already exists
    if messages_file.exists():
        logger.debug(f"Messages file already exists at {messages_file}")
        return True
    
    try:
        # Default message categories
        default_messages = {
            "GREETING": [
                "What up {username}! Ready to mess with some terminal stuff?",
                "Oh great, {username}'s back. What dimension-bending command are we typing today?",
                "Look who it is! {username}, the command line... enthusiast. That's being generous.",
                "Welcome back {username}! Let's see what terrible decisions we make today."
            ],
            "RESPONSE": [
                "Fine, I'll run your {command}...",
                "Executing that garbage? Whatever...",
                "That command is about as efficient as Jerry's job search, but I'll run it.",
                "Sure, let's try {command}. What's the worst that could happen? Oh wait, I know - EVERYTHING."
            ],
            "ERROR": [
                "You really screwed that up, didn't you?",
                "That's about as functional as Jerry's career.",
                "Wow, nice error. Did you learn programming at the Citadel's reject academy?",
                "That command failed harder than Morty's attempts to talk to girls."
            ],
            "WARNING": [
                "This command looks dangerous, even for me.",
                "Whoa, you're about to wreck your system, genius.",
                "Are you sure about that command? It looks more dangerous than a Meeseeks after 48 hours.",
                "I've seen some dumb ideas, but this command might take the cake."
            ],
            "CATCHPHRASE": [
                "Wubba lubba dub dub!",
                "And that's the waaaaay the news goes!",
                "Rikki-tikki-tavi, biatch!",
                "Grass... tastes bad!",
                "Lick, lick, lick my balls!",
                "I'm Pickle Riiiiick!",
                "AIDS!",
                "Hit the sack, Jack!",
                "Uh-oh, somersault jump!",
                "Shum shum schlippity dop!"
            ]
        }
        
        # Write messages to file atomically
        temp_file = messages_file.with_suffix(".tmp")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(default_messages, f, indent=2)
            
        # Make sure the write is completed
        f.flush()
        os.fsync(f.fileno())
        
        # Rename the temp file to the actual messages file
        temp_file.replace(messages_file)
        
        # Set appropriate permissions
        os.chmod(messages_file, 0o644)
        
        logger.info(f"Successfully created default messages file at {messages_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create messages file: {str(e)}")
        return False

@safe_execute(default_return="command_output")
def detect_prompt_system() -> str:
    """
    Detect the terminal's prompt system.
    
    Returns:
        str: "powerlevel10k", "oh-my-zsh", or "standalone"
    """
    # Check for Powerlevel10k
    try:
        result = subprocess.run(
            ["zsh", "-c", "[[ -n $POWERLEVEL9K_LEFT_PROMPT_ELEMENTS ]] && echo 'yes' || echo 'no'"],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        
        if result.stdout.strip() == 'yes':
            return "powerlevel10k"
    except Exception:
        pass
        
    # Check for oh-my-zsh
    try:
        result = subprocess.run(
            ["zsh", "-c", "[[ -n $ZSH && -d $ZSH ]] && echo 'yes' || echo 'no'"],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        
        if result.stdout.strip() == 'yes':
            return "oh-my-zsh"
    except Exception:
        pass
        
    return "standalone"

@safe_execute(default_return={})
def setup_prompt_integration() -> Dict[str, Any]:
    """
    Set up the prompt integration based on detected environment.
    
    This function detects the user's prompt system and sets up
    the appropriate integration mode.
    
    Returns:
        Dict[str, Any]: Configuration for prompt integration
    """
    from src.utils.config import get_config_value, set_config_value
    
    logger.info("Setting up prompt integration")
    
    # Check if prompt integration is already configured
    current_mode = get_config_value("prompt_integration.mode", "auto")
    if current_mode != "auto":
        logger.info(f"Prompt integration already configured with mode: {current_mode}")
        return {
            "mode": current_mode,
            "display_style": get_config_value("prompt_integration.display_style", "command_output")
        }
    
    # Detect the prompt system
    system = detect_prompt_system()
    logger.info(f"Detected prompt system: {system}")
    
    # Set default display style based on the detected system
    display_style = "command_output"  # Least intrusive default
    
    if system == "powerlevel10k":
        # For Powerlevel10k, we recommend segment mode
        display_style = "segment"
        replace_path = False  # Don't replace Powerlevel10k's path by default
    elif system == "oh-my-zsh":
        # For Oh My Zsh without Powerlevel10k, recommend right prompt
        display_style = "right_prompt"
        replace_path = True
    else:
        # For standalone terminals, use command output as least intrusive
        display_style = "command_output"
        replace_path = True
    
    # Save the configuration
    set_config_value("prompt_integration.mode", system)
    set_config_value("prompt_integration.display_style", display_style)
    set_config_value("prompt_integration.replace_path_indicator", replace_path)
    
    logger.info(f"Prompt integration configured with mode: {system}, display_style: {display_style}")
    
    return {
        "mode": system,
        "display_style": display_style,
        "replace_path_indicator": replace_path
    }

@safe_execute(default_return=True)
def initialize() -> bool:
    """
    Initialize the Rick Assistant.
    
    This function initializes the Rick Assistant, running the setup wizard
    if this is the first run.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info("Initializing Rick Assistant")
    
    # Run setup wizard if needed
    if not setup_if_needed():
        logger.error("Setup wizard failed")
        return False
    
    # Verify directory structure even if setup was not needed
    verification = verify_directory_structure()
    if not verification or not verification["success"]:
        logger.error("Directory structure verification failed")
        if not repair_directories():
            logger.error("Failed to repair directory structure")
            return False
    
    # Set up prompt integration
    setup_prompt_integration()
    
    logger.info("Rick Assistant initialized successfully")
    return True

@safe_execute(default_return=False)
def run_setup_wizard() -> bool:
    """
    Run the Rick Assistant setup wizard.
    
    This interactive wizard guides the user through setting up their preferences.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    show_welcome_screen()
    
    try:
        # Create and verify directories
        if not setup_directories():
            logger.error("Failed to create directories")
            return False
            
        # Get user preferences
        preferences = get_user_preferences()
        
        # Confirm choices
        if not confirm_setup_choices(preferences):
            print(f"\n{YELLOW}Setup canceled by user.{RESET}")
            return False
            
        # Save user preferences
        if not save_user_preferences(preferences):
            logger.error("Failed to save user preferences")
            return False
            
        # Create messages file
        if not create_messages_file():
            logger.warning("Failed to create messages file")
        
        # Set up prompt integration (new section)
        print(f"\n{CYAN}{BOLD}Setting up prompt integration...{RESET}")
        prompt_config = setup_prompt_integration()
        
        # Print integration details
        system_map = {
            "powerlevel10k": "Powerlevel10k theme",
            "oh-my-zsh": "Oh My Zsh",
            "standalone": "Standard terminal"
        }
        
        display_style_map = {
            "segment": "Custom Powerlevel10k segment",
            "right_prompt": "Right side prompt",
            "command_output": "Command output messages",
            "custom_position": "Custom prompt position"
        }
        
        detected_system = system_map.get(prompt_config.get("mode", "standalone"), "Unknown terminal")
        display_style = display_style_map.get(prompt_config.get("display_style", "command_output"), "Command output")
        
        print(f"\n{CYAN}Detected terminal environment: {YELLOW}{detected_system}{RESET}")
        print(f"{CYAN}Selected display style: {YELLOW}{display_style}{RESET}")
        print(f"\n{CYAN}You can change this anytime with: {GREEN}rick prompt{CYAN} command{RESET}")
        
        show_completion_message()
        
        return True
    except Exception as e:
        logger.error(f"Error in setup wizard: {str(e)}")
        print(f"\n{YELLOW}An error occurred during setup: {str(e)}{RESET}")
        print(f"\n{YELLOW}Please try running the setup again.{RESET}")
        return False

@safe_execute(default_return=False)
def setup_if_needed() -> bool:
    """
    Run the setup wizard if this is the first run.
    
    Returns:
        bool: True if setup was successful or not needed, False otherwise
    """
    if is_first_run():
        logger.info("First run detected, launching setup wizard")
        return run_setup_wizard()
    else:
        logger.debug("Not first run, skipping setup wizard")
        return True

@safe_execute(default_return=None)
def get_validated_input(prompt: str, validator=None, default=None, error_msg=None) -> Optional[str]:
    """
    Get user input with validation.
    
    Args:
        prompt (str): The prompt to display to the user
        validator (callable, optional): Function to validate input
        default (str, optional): Default value if input is empty
        error_msg (str, optional): Message to show on validation failure
    
    Returns:
        Optional[str]: The validated input or None if validation fails repeatedly
    """
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        # Show prompt with default if provided
        if default:
            user_input = input(f"{YELLOW}{prompt} [{default}]: {RESET}")
        else:
            user_input = input(f"{YELLOW}{prompt}: {RESET}")
        
        # Use default if input is empty
        if not user_input and default:
            return default
        
        # Validate input if validator provided
        if validator and user_input:
            try:
                if validator(user_input):
                    return user_input
                else:
                    if error_msg:
                        print(f"{BLUE}{error_msg}{RESET}")
                    else:
                        print(f"{BLUE}Invalid input. Please try again.{RESET}")
            except Exception as e:
                logger.error(f"Input validation error: {str(e)}")
                print(f"{BLUE}Invalid input. Please try again.{RESET}")
        elif user_input:  # No validator, just return input
            return user_input
        else:
            print(f"{BLUE}Input cannot be empty. Please try again.{RESET}")
        
        attempts += 1
    
    # If we get here, validation failed too many times
    print_rick_dialog(f"Ugh, you can't even enter valid input after {max_attempts} tries. I'll just go with the default.")
    return default

@safe_execute(default_return={})
def get_user_preferences() -> Dict[str, Any]:
    """
    Collect user preferences for the Rick Assistant.
    
    Returns:
        Dict[str, Any]: Dictionary of user preferences
    """
    print_rick_dialog("Alright, let's set up your preferences. Try not to make choices as bad as Morty's life decisions.")
    
    preferences = {
        "general": {},
        "ui": {},
        "personality": {}
    }
    
    # Get username (with system username as default)
    import getpass
    system_username = getpass.getuser()
    username = get_validated_input(
        f"What should I call you? (You look like a '{system_username}' to me)",
        default=system_username
    )
    preferences["general"]["username"] = username
    
    print_rick_dialog(f"Fine, {username} it is. Not like I had better options.")
    
    # Get preferred theme
    print("\n" + f"{CYAN}{BOLD}Choose your preferred theme:{RESET}")
    print(f"  {GREEN}1. Portal{RESET} - Green and blue portal theme")
    print(f"  {BLUE}2. Science{RESET} - Blue science lab theme")
    print(f"  {YELLOW}3. Citadel{RESET} - Yellow Citadel of Ricks theme")
    
    theme_validator = lambda x: x in ['1', '2', '3']
    theme_choice = get_validated_input(
        "Enter theme number",
        validator=theme_validator,
        default="1",
        error_msg="That's not even a valid choice. Choose 1, 2, or 3."
    )
    
    theme_map = {"1": "portal", "2": "science", "3": "citadel"}
    theme_name = theme_map.get(theme_choice, "portal")
    preferences["ui"]["theme"] = theme_name
    
    # Get animation preference
    anim_validator = lambda x: x.lower() in ['y', 'yes', 'n', 'no']
    anim_choice = get_validated_input(
        "Do you want to enable animations? (y/n)",
        validator=anim_validator,
        default="y",
        error_msg="It's a simple yes or no question. Even Jerry could answer this."
    )
    
    preferences["ui"]["animations"] = anim_choice.lower() in ['y', 'yes']
    
    # Select personality level
    sass_level = select_personality_level()
    preferences["personality"]["sass_level"] = sass_level
    
    # Get burp frequency
    try:
        burp_frequency = float(get_validated_input(
            "How often should I burp? (0.0-1.0)",
            validator=lambda x: 0.0 <= float(x) <= 1.0,
            default="0.3",
            error_msg="Enter a number between 0.0 and 1.0, genius."
        ))
    except (ValueError, TypeError):
        burp_frequency = 0.3
        
    preferences["personality"]["burp_frequency"] = burp_frequency
    
    return preferences

@safe_execute(default_return=5)
def select_personality_level() -> int:
    """
    Let the user select Rick's sass level.
    
    Returns:
        int: Selected sass level (1-10)
    """
    print("\n" + f"{CYAN}{BOLD}Choose Rick's Sass Level:{RESET}")
    print(f"  {GREEN}1-3: Mild{RESET} - Only slightly judgmental")
    print(f"  {YELLOW}4-7: Medium{RESET} - Regular Rick sarcasm")
    print(f"  {BLUE}8-10: Extreme{RESET} - Full Rick insanity")
    
    try:
        sass_level = int(get_validated_input(
            "Select sass level (1-10)",
            validator=lambda x: 1 <= int(x) <= 10,
            default="7",
            error_msg="It's 1 to 10. How hard is that to understand?"
        ))
    except (ValueError, TypeError):
        sass_level = 7
        
    # Rick's commentary on choice
    if sass_level <= 3:
        print_rick_dialog(f"Only a {sass_level}? What are you, a Jerry? Fine, I'll keep it mild.")
    elif sass_level <= 7:
        print_rick_dialog(f"A {sass_level}, huh? At least you're not completely boring.")
    else:
        print_rick_dialog(f"Cranking it up to {sass_level}? You might regret that decision. I like your style.")
        
    return sass_level
