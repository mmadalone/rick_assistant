"""
Configuration Management Module for Rick Assistant ZSH Plugin

This module provides configuration loading, saving, and validation functionality
for the Rick Assistant plugin. It handles creating default configurations with 
Rick's personality and ensures safe atomic writes to prevent corruption.

"Listen up M-Morty! This *burp* configuration system is gonna keep your pathetic
settings from getting lost when your computer inevitably crashes. You're welcome!"
"""

import json
import os
import tempfile
import shutil
import logging
from typing import Any, Dict, Optional, Union, List, Tuple
from pathlib import Path

# Import utilities
from src.utils.errors import safe_execute, ConfigError
from src.utils.logger import get_logger
from src.utils.path_safety import (
    normalize_path,
    is_path_within_safe_directories,
    ensure_safe_directory,
    safe_atomic_write,
    validate_path_permissions
)

# Set up logger
logger = get_logger(__name__)

# Define config types
ConfigDict = Dict[str, Any]

# Constants - normalize and validate paths
_HOME_PATH = Path.home()
CONFIG_DIR_PATH = _HOME_PATH / ".rick_assistant"
DEFAULT_CONFIG_PATH = CONFIG_DIR_PATH / "config.json"
CONFIG_BACKUP_PATH = CONFIG_DIR_PATH / "config.json.bak"

# Legacy constants for backward compatibility
CONFIG_DIR = str(CONFIG_DIR_PATH)
DEFAULT_CONFIG_PATH_STR = str(DEFAULT_CONFIG_PATH)
CONFIG_BACKUP_PATH_STR = str(CONFIG_BACKUP_PATH)

@safe_execute(default_return={})
def get_default_config() -> ConfigDict:
    """
    Generate default configuration with Rick personality.
    
    Returns:
        Dictionary containing default configuration
    """
    # Basic configuration for Rick Assistant
    config = {
        "general": {
            "enabled": True,
            "log_level": "INFO",
            "show_welcome_message": True,
            "show_exit_message": True
        },
        "ui": {
            "theme": "portal",
            "animations": True,
            "prompt_style": "classic",
            "show_status_bar": True,
            "status_bar_elements": ["path", "metrics", "catchphrase"],
            "colors": {
                "primary": "green",
                "secondary": "blue",
                "accent": "yellow",
                "error": "red"
            }
        },
        "prompt_integration": {
            "mode": "auto",  # "powerlevel10k", "oh-my-zsh", "standalone", "auto"
            "display_style": "command_output",  # "segment", "right_prompt", "command_output", "custom_position"
            "segment_position": "right",  # "left", "right", "prefix", "suffix"
            "segment_priority": 10,
            "segment_content": ["personality", "system_status"],  # Components to show in segment
            "custom_position_index": 2,  # For custom positioning within segments
            "replace_path_indicator": False,
            "show_personality": True,
            "personality_frequency": 0.7,  # How often Rick's comments appear (0.0-1.0)
            "status_indicators": ["cpu", "memory", "temperature"]
        },
        "personality": {
            "character": "rick",
            "sass_level": 7,
            "burp_frequency": 0.3,
            "catchphrase_frequency": 0.2,
            "scientific_reference_level": 5,
            "custom_catchphrases": []
        },
        "system": {
            "metrics_refresh_rate": 5,
            "show_cpu_usage": True,
            "show_memory_usage": True,
            "show_disk_space": False,
            "show_temperature": False,
            "command_history_size": 1000
        },
        "safety": {
            "confirm_dangerous_commands": True,
            "warning_level": "medium",
            "command_whitelist": [],
            "path_whitelist": [],
            "secure_mode": True
        },
        "ai": {
            "enabled": False,
            "model": "local",
            "api_key": "",
            "max_tokens": 150,
            "temperature": 0.7,
            "show_thinking": False
        }
    }
    
    logger.debug("Default configuration generated")
    return config

@safe_execute(default_return={})
def load_config() -> ConfigDict:
    """
    Load configuration from file or use defaults if not found.
    
    Returns:
        Configuration dictionary
    """
    # Ensure config directory exists
    ensure_config_dir()
    
    # Normalize and validate the config path
    config_path = normalize_path(DEFAULT_CONFIG_PATH)
    if not config_path:
        logger.error(f"Invalid config path: {DEFAULT_CONFIG_PATH}")
        return get_default_config()
    
    # Check if path is within safe directories
    if not is_path_within_safe_directories(config_path):
        logger.error(f"Config path is outside safe directories: {config_path}")
        return get_default_config()
    
    # Check if config file exists
    if not config_path.exists():
        logger.info("Config file not found, using defaults")
        default_config = get_default_config()
        save_config(default_config)
        return default_config
    
    try:
        # Read config file safely
        try:
            # Verify file permissions before reading
            if not validate_path_permissions(config_path, os.R_OK):
                logger.error(f"No read permission for config file: {config_path}")
                return get_default_config()
                
            # Read the file
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
            
            # Validate and repair if needed
            config = validate_config(config)
            logger.debug("Configuration loaded successfully")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {str(e)}")
            logger.info("Using default configuration")
            
            # Attempt to repair corrupted config
            if repair_config():
                logger.info("Corrupted configuration repaired, trying again")
                return load_config()
                
            # If repair fails, use defaults
            default_config = get_default_config()
            save_config(default_config)
            return default_config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return get_default_config()

@safe_execute(default_return=False)
def save_config(config: ConfigDict) -> bool:
    """
    Save the configuration to file using safe atomic write.
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    # Validate config before saving
    config = validate_config(config)
    
    # Ensure the config directory exists
    config_dir = ensure_safe_directory(CONFIG_DIR_PATH)
    if not config_dir:
        logger.error(f"Failed to ensure config directory exists: {CONFIG_DIR_PATH}")
        return False
    
    # Create backup of existing config if it exists
    config_path = normalize_path(DEFAULT_CONFIG_PATH)
    backup_path = normalize_path(CONFIG_BACKUP_PATH)
    
    if not config_path or not backup_path:
        logger.error("Failed to normalize config paths")
        return False
    
    if config_path.exists():
        try:
            shutil.copy2(str(config_path), str(backup_path))
            logger.debug("Created backup of existing configuration")
        except Exception as e:
            logger.warning(f"Failed to create config backup: {str(e)}")
    
    # Use our safe atomic write function
    try:
        config_json = json.dumps(config, indent=2)
        result = safe_atomic_write(
            path=config_path,
            content=config_json,
            mode='w',
            encoding='utf-8'
        )
        
        if result:
            logger.debug("Configuration saved successfully")
            return True
        else:
            logger.error("Failed to save configuration")
            return False
    except Exception as e:
        logger.error(f"Error in save_config: {str(e)}")
        return False

@safe_execute()
def validate_config(config: ConfigDict) -> ConfigDict:
    """
    Validate and repair configuration if needed.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Validated (and possibly repaired) configuration
    """
    default_config = get_default_config()
    
    # If config is None or empty, return default
    if not config:
        return default_config
    
    # Ensure all required top-level sections exist
    for section in default_config.keys():
        if section not in config:
            logger.warning(f"Missing config section: {section}, using defaults")
            config[section] = default_config[section]
    
    # Filter out invalid sections
    config = _filter_invalid_keys(config, default_config)
    
    # Merge with default config to ensure no missing fields
    merged_config = _merge_configs(default_config, config)
    
    # Validation of specific fields or values could be added here
    
    return merged_config

@safe_execute(default_return=None)
def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a configuration value safely with fallback.
    
    Args:
        key: Configuration key (dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    if not key:
        return default
    
    config = load_config()
    keys = key.split('.')
    
    # Navigate through nested keys
    value = config
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        logger.debug(f"Config key not found: {key}, using default: {default}")
        return default

@safe_execute(default_return=False)
def set_config_value(key: str, value: Any) -> bool:
    """
    Set a configuration value and save.
    
    Args:
        key: Configuration key (dot notation for nested keys)
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    if not key:
        logger.error("Empty config key provided")
        return False
    
    config = load_config()
    keys = key.split('.')
    
    # Handle dotted key path
    if len(keys) > 1:
        # Navigate to the nested location
        target = config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            elif not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
    else:
        # Set at top level
        config[key] = value
    
    # Save updated config
    return save_config(config)

@safe_execute(default_return=False)
def ensure_config_dir() -> bool:
    """
    Ensure the configuration directory exists.
    
    Returns:
        True if directory exists or was created, False on error
    """
    dir_path = ensure_safe_directory(CONFIG_DIR_PATH, create=True)
    return dir_path is not None

@safe_execute(default_return=False)
def config_exists() -> bool:
    """
    Check if configuration file exists.
    
    Returns:
        True if config file exists, False otherwise
    """
    config_path = normalize_path(DEFAULT_CONFIG_PATH)
    if not config_path:
        return False
    
    return config_path.exists() and config_path.is_file()

@safe_execute(default_return=False)
def repair_config() -> bool:
    """
    Attempt to repair corrupted configuration.
    
    Returns:
        True if repaired successfully, False otherwise
    """
    # Normalize paths
    config_path = normalize_path(DEFAULT_CONFIG_PATH)
    backup_path = normalize_path(CONFIG_BACKUP_PATH)
    
    if not config_path or not backup_path:
        logger.error("Failed to normalize config paths")
        return False
    
    # Try to restore from backup
    if backup_path.exists() and backup_path.is_file():
        try:
            # Verify file permissions before reading
            if not validate_path_permissions(backup_path, os.R_OK):
                logger.error(f"No read permission for backup file: {backup_path}")
                return False
                
            # Try to read backup file
            with open(backup_path, "r") as config_file:
                backup_config = json.load(config_file)
            
            # If backup is valid, save it as the main config
            if backup_config:
                logger.info("Restoring config from backup")
                return safe_atomic_write(
                    path=config_path,
                    content=json.dumps(backup_config, indent=2),
                    mode='w',
                    encoding='utf-8'
                )
        except Exception as e:
            logger.error(f"Failed to restore config from backup: {str(e)}")
    
    # If no backup exists or restoration failed, create a new default config
    logger.info("Creating new default configuration")
    default_config = get_default_config()
    return safe_atomic_write(
        path=config_path,
        content=json.dumps(default_config, indent=2),
        mode='w',
        encoding='utf-8'
    )

@safe_execute(default_return=False)
def reset_to_defaults() -> bool:
    """
    Reset configuration to default values.
    
    Returns:
        True if reset successful, False otherwise
    """
    # Get default configuration
    default_config = get_default_config()
    
    # Normalize the config path
    config_path = normalize_path(DEFAULT_CONFIG_PATH)
    if not config_path:
        logger.error(f"Invalid config path: {DEFAULT_CONFIG_PATH}")
        return False
    
    # Backup existing config if it exists
    if config_path.exists() and config_path.is_file():
        backup_path = normalize_path(CONFIG_BACKUP_PATH)
        if backup_path:
            try:
                shutil.copy2(str(config_path), str(backup_path))
                logger.info("Backed up existing configuration before reset")
            except Exception as e:
                logger.warning(f"Failed to backup config before reset: {str(e)}")
    
    # Save default configuration
    logger.info("Resetting configuration to defaults")
    return save_config(default_config)

@safe_execute()
def get_config_path() -> str:
    """
    Get the path to the config file.
    
    Returns:
        Path to the config file as a string
    """
    return str(DEFAULT_CONFIG_PATH)

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def _merge_configs(default: ConfigDict, user: ConfigDict) -> ConfigDict:
    """
    Merge default and user configurations, preferring user values.
    
    Args:
        default: Default configuration
        user: User configuration
        
    Returns:
        Merged configuration
    """
    result = default.copy()
    
    for key, value in user.items():
        # Skip invalid keys
        if key not in result:
            continue
            
        # Recursively merge dictionaries
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            # Otherwise use user value
            result[key] = value
            
    return result

def _merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries, preferring values from dict2.
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge in (values preferred)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        # Skip invalid keys
        if key not in result:
            continue
            
        # Recursively merge nested dictionaries
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            # Otherwise use dict2 value
            result[key] = value
            
    return result

def _filter_invalid_keys(config: ConfigDict, reference: ConfigDict) -> ConfigDict:
    """
    Remove invalid keys from config that don't exist in reference.
    
    Args:
        config: Configuration to filter
        reference: Reference configuration with valid keys
        
    Returns:
        Filtered configuration
    """
    # Create a copy to avoid modifying the original
    filtered = {}
    
    for key, value in config.items():
        # Skip keys not in reference
        if key not in reference:
            logger.warning(f"Removing invalid config key: {key}")
            continue
            
        # Recursively filter nested dictionaries
        if isinstance(value, dict) and isinstance(reference[key], dict):
            filtered[key] = _filter_invalid_keys(value, reference[key])
        else:
            # Keep valid keys
            filtered[key] = value
            
    return filtered
