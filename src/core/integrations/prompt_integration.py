"""
Prompt Integration Module for Rick Assistant

This module provides the Python interface to the ZSH prompt integration system,
allowing different display modes for Rick's personality:
- segment: Adds Rick as a Powerlevel10k segment
- right_prompt: Places Rick in the right prompt
- command_output: Shows Rick's comments as command output (least intrusive)
- custom_position: Places Rick at a custom position in the prompt
"""

import os
import subprocess
import random
from typing import Optional, List, Dict, Any, Tuple, Union

from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.config import get_config_value, set_config_value

# Initialize logger
logger = get_logger(__name__)

# Define constants for prompt modes
MODE_SEGMENT = "segment"
MODE_RIGHT_PROMPT = "right_prompt"
MODE_COMMAND_OUTPUT = "command_output"
MODE_CUSTOM_POSITION = "custom_position"

# Valid modes
VALID_MODES = [
    MODE_SEGMENT,
    MODE_RIGHT_PROMPT,
    MODE_COMMAND_OUTPUT,
    MODE_CUSTOM_POSITION
]

# Rick Assistant script directory
SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
INTEGRATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

@safe_execute(default_return=False)
def is_powerlevel10k_available() -> bool:
    """
    Check if the terminal is using Powerlevel10k theme.
    
    Returns:
        bool: True if Powerlevel10k is available, False otherwise
    """
    try:
        # Run a zsh command to check for Powerlevel10k
        result = subprocess.run(
            ["zsh", "-c", "[[ -n $POWERLEVEL9K_LEFT_PROMPT_ELEMENTS ]] && echo 'yes' || echo 'no'"],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        
        return result.stdout.strip() == 'yes'
    except Exception as e:
        logger.warning(f"Error checking for Powerlevel10k: {e}")
        return False

@safe_execute(default_return="command_output")
def detect_prompt_system() -> str:
    """
    Detect the terminal's prompt system.
    
    Returns:
        str: "powerlevel10k", "oh-my-zsh", or "standalone"
    """
    try:
        # Use the ZSH detection script if available
        if os.path.exists(os.path.join(INTEGRATIONS_DIR, "prompt_modes.zsh")):
            result = subprocess.run(
                ["zsh", "-c", f"source {os.path.join(INTEGRATIONS_DIR, 'prompt_modes.zsh')} && rick_detect_prompt_system"],
                capture_output=True,
                text=True,
                timeout=1.0
            )
            
            system = result.stdout.strip()
            if system in ["powerlevel10k", "oh-my-zsh", "standalone"]:
                return system
        
        # Fallback detection
        if is_powerlevel10k_available():
            return "powerlevel10k"
        
        # Check for oh-my-zsh
        result = subprocess.run(
            ["zsh", "-c", "[[ -n $ZSH && -d $ZSH ]] && echo 'yes' || echo 'no'"],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        
        if result.stdout.strip() == 'yes':
            return "oh-my-zsh"
            
        return "standalone"
    except Exception as e:
        logger.warning(f"Error detecting prompt system: {e}")
        return "standalone"

@safe_execute(default_return=False)
def switch_prompt_mode(mode: str) -> bool:
    """
    Switch to a different prompt integration mode.
    
    Args:
        mode (str): One of "segment", "right_prompt", "command_output", "custom_position"
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate mode
    if mode not in VALID_MODES:
        logger.error(f"Invalid prompt mode: {mode}")
        return False
    
    # Update configuration
    set_config_value("prompt_integration.display_style", mode)
    
    # Apply mode using ZSH function if available
    try:
        if os.path.exists(os.path.join(INTEGRATIONS_DIR, "prompt_modes.zsh")):
            # Create a temporary script to source our file and call the function
            with open("/tmp/rick_switch_mode.zsh", "w") as f:
                f.write(f"""#!/usr/bin/env zsh
source {os.path.join(INTEGRATIONS_DIR, 'prompt_modes.zsh')}
rick_switch_prompt_mode "{mode}"
""")
            
            # Make it executable
            os.chmod("/tmp/rick_switch_mode.zsh", 0o755)
            
            # Run the script
            result = subprocess.run(
                ["zsh", "/tmp/rick_switch_mode.zsh"],
                timeout=2.0
            )
            
            # Clean up
            os.unlink("/tmp/rick_switch_mode.zsh")
            
            return result.returncode == 0
    except Exception as e:
        logger.error(f"Error switching prompt mode: {e}")
        return False
    
    return True

@safe_execute(default_return=False)
def auto_select_mode() -> bool:
    """
    Automatically select the best prompt mode based on the environment.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Detect the prompt system
    system = detect_prompt_system()
    
    # Set mode based on system
    if system == "powerlevel10k":
        return switch_prompt_mode(MODE_SEGMENT)
    elif system == "oh-my-zsh":
        return switch_prompt_mode(MODE_RIGHT_PROMPT)
    else:
        return switch_prompt_mode(MODE_COMMAND_OUTPUT)

@safe_execute(default_return="")
def get_prompt_content() -> str:
    """
    Get the content to display in Rick's prompt segment.
    
    This function generates the text to show in Rick's prompt segment,
    based on configuration and system status.
    
    Returns:
        str: The content to display
    """
    # Get configuration
    show_personality = get_config_value("prompt_integration.show_personality", True)
    personality_frequency = get_config_value("prompt_integration.personality_frequency", 0.7)
    segment_content = get_config_value("prompt_integration.segment_content", ["personality", "system_status"])
    
    components = []
    
    # Add personality component if configured
    if "personality" in segment_content and show_personality and random.random() < personality_frequency:
        from src.core.prompt import get_rick_phrase
        components.append(get_rick_phrase())
    
    # Add system status if configured
    if "system_status" in segment_content:
        status_indicators = get_config_value("prompt_integration.status_indicators", ["cpu", "memory", "temperature"])
        
        if "cpu" in status_indicators:
            try:
                # Simple CPU usage check (placeholder)
                with open("/proc/loadavg", "r") as f:
                    load = float(f.read().split()[0])
                    if load > 1.0:
                        components.append(f"CPU:{load:.1f}")
            except:
                pass
                
        if "temperature" in status_indicators:
            # This would be replaced with actual temperature monitoring
            components.append("Tmp:42°C")
    
    # Combine components
    if components:
        return " ".join(components)
    else:
        return "🧪"

def initialize() -> None:
    """
    Initialize the prompt integration system.
    
    This function is called during Rick Assistant startup to set up
    the prompt integration based on configuration.
    """
    logger.info("Initializing prompt integration")
    
    # Get configuration
    mode = get_config_value("prompt_integration.mode", "auto")
    display_style = get_config_value("prompt_integration.display_style", "command_output")
    
    # Auto-detect if configured
    if mode == "auto":
        auto_select_mode()
    else:
        # Apply configured mode
        switch_prompt_mode(display_style)
        
    logger.info(f"Prompt integration initialized with mode: {display_style}") 