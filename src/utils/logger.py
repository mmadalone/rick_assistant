#!/usr/bin/env python3
"""
Logging Module for Rick Assistant

This module provides logging functionality for the Rick Assistant
with built-in path safety, configurable levels, and multiple output options.

"Listen Morty, you need logs for wh-when things go wrong. Trust me on this one!"
"""

import logging
import os
import sys
import time
import random
import shutil
import tempfile
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Union, Dict, Any, List

# Define constants for log directories - using Path objects
HOME_PATH = Path.home()
DEFAULT_LOG_DIR = HOME_PATH / ".rick_assistant" / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "rick_assistant.log"
ERROR_LOG_FILE = DEFAULT_LOG_DIR / "error.log"

# For backward compatibility
DEFAULT_LOG_DIR_STR = str(DEFAULT_LOG_DIR)
DEFAULT_LOG_FILE_STR = str(DEFAULT_LOG_FILE)
ERROR_LOG_FILE_STR = str(ERROR_LOG_FILE)

# Global logger cache to avoid creating multiple instances
_loggers = {}

# Default format strings
DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Max log file size (5MB)
MAX_LOG_SIZE = 5 * 1024 * 1024

# Rick-themed error messages for random selection
RICK_ERROR_MESSAGES = [
    "Oh geez! Something went wrong with {}",
    "W-w-way to go {}! You broke it!",
    "Error in {}: It's completely *burp* wrecked!",
    "Great job {}! You somehow managed to break a perfectly functioning system!",
    "Error detected in {}: What kind of interdimensional idiot wrote this?",
    "You know what your problem is, {}? You're always breaking things!",
    "Oh fantastic! {} is throwing errors again! Just what we needed!",
    "Your code in {} is about as functional as a Jerry!",
    "{} broke. Fix it or don't. The multiverse is infinite, so...",
    "This isn't rocket science {}, it's way more complicated! And you still broke it!"
]

# Safe directory patterns - directories that are considered safe for operations
SAFE_DIRS = [
    # Home directory and subdirectories
    str(HOME_PATH),
    # Temp directories
    tempfile.gettempdir(),
    # Current working directory and subdirectories
    os.getcwd()
]

def _is_path_safe(path: Union[str, Path]) -> bool:
    """Simple internal function to check if a path is safe."""
    if not path:
        return False
        
    # Convert to Path object
    path_obj = Path(path).resolve() if isinstance(path, str) else path.resolve()
    
    # Check if path is within safe directories
    path_str = str(path_obj)
    return any(path_str.startswith(safe_dir) for safe_dir in SAFE_DIRS)

def _ensure_dir_exists(path: Union[str, Path]) -> bool:
    """Simple internal function to ensure a directory exists."""
    if not path:
        return False
        
    # Convert to Path object
    path_obj = Path(path).resolve() if isinstance(path, str) else path.resolve()
    
    # Check if path is safe
    if not _is_path_safe(path_obj):
        return False
        
    # Create directory if it doesn't exist
    try:
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj.is_dir()
    except:
        return False

def get_logger(name: str, level: Optional[Union[str, int]] = None) -> logging.Logger:
    """
    Get a configured logger by name with path-safe file handling.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        level: Optional logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured Logger instance
    """
    # If logger already exists in cache, return it
    if name in _loggers:
        logger = _loggers[name]
        if level:
            logger.setLevel(_parse_level(level))
        return logger
    
    # Create new logger
    logger = logging.getLogger(name)
    
    # Set level (default to INFO if not specified)
    logger.setLevel(_parse_level(level) if level else logging.INFO)
    
    # Don't propagate to root logger to avoid duplicate logs
    logger.propagate = False
    
    # Configure handlers if they don't exist
    if not logger.handlers:
        # Create file handler with safe path handling
        try:
            # Ensure log directory exists safely
            if not _ensure_dir_exists(DEFAULT_LOG_DIR):
                # If we can't create the directory, log an error to console
                console = logging.StreamHandler(sys.stderr)
                console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
                logger.addHandler(console)
                logger.error(f"Failed to create log directory: {DEFAULT_LOG_DIR}")
            else:
                # Use rotating file handler with 5MB max size, keep 3 backups
                if _is_path_safe(DEFAULT_LOG_FILE):
                    file_handler = RotatingFileHandler(
                        str(DEFAULT_LOG_FILE),
                        maxBytes=MAX_LOG_SIZE,
                        backupCount=3,
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
                    logger.addHandler(file_handler)
                    
                    # Also add an error file handler for ERROR and CRITICAL messages
                    if _is_path_safe(ERROR_LOG_FILE):
                        error_handler = RotatingFileHandler(
                            str(ERROR_LOG_FILE),
                            maxBytes=MAX_LOG_SIZE,
                            backupCount=3,
                            encoding='utf-8'
                        )
                        error_handler.setLevel(logging.ERROR)
                        error_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
                        logger.addHandler(error_handler)
                else:
                    # Log path is invalid or unsafe
                    console = logging.StreamHandler(sys.stderr)
                    console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
                    logger.addHandler(console)
                    logger.error(f"Invalid or unsafe log path: {DEFAULT_LOG_FILE}")
        except Exception as e:
            # Fallback to console logging if file logging fails
            console = logging.StreamHandler(sys.stderr)
            console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
            logger.addHandler(console)
            logger.error(f"Failed to setup file logging: {str(e)}")
    
    # Add Rick-themed error handler method
    def rick_error(msg, *args, **kwargs):
        rick_msg = random.choice(RICK_ERROR_MESSAGES).format(name)
        logger.error(f"{rick_msg}: {msg}", *args, **kwargs)
    
    # Attach as a method to the logger
    logger.rick_error = rick_error
    
    # Store in cache
    _loggers[name] = logger
    return logger

def set_log_level(level: Union[str, int], logger_name: Optional[str] = None) -> None:
    """
    Set the logging level for a specific logger or all loggers.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional logger name, if None affects all loggers
    """
    parsed_level = _parse_level(level)
    
    if logger_name:
        # Set level for specific logger
        if logger_name in _loggers:
            _loggers[logger_name].setLevel(parsed_level)
    else:
        # Set level for all loggers
        for logger in _loggers.values():
            logger.setLevel(parsed_level)

def add_console_handler(logger_name: str, level: Optional[Union[str, int]] = None) -> None:
    """
    Add a console handler to a logger.
    
    Args:
        logger_name: Name of the logger to add console handler to
        level: Optional logging level for this handler
    """
    if logger_name not in _loggers:
        return
    
    logger = _loggers[logger_name]
    
    # Check if console handler already exists
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream in (sys.stdout, sys.stderr):
            return
    
    # Add console handler
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
    
    if level:
        console.setLevel(_parse_level(level))
    
    logger.addHandler(console)

def log_to_file(message: str, level: str = "INFO", file_path: Optional[str] = None) -> bool:
    """
    Log a message directly to a file with proper safety checks.
    
    Args:
        message: Message to log
        level: Log level string
        file_path: Optional custom log file path
        
    Returns:
        True if logging succeeded, False otherwise
    """
    try:
        # Format the log message
        timestamp = time.strftime(DEFAULT_DATE_FORMAT, time.localtime())
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Determine the log file path
        if file_path:
            # Convert to Path and validate
            log_path = Path(file_path).resolve()
            if not _is_path_safe(log_path):
                return False
        else:
            # Use default log file
            log_path = DEFAULT_LOG_FILE
            if not _is_path_safe(log_path):
                return False
        
        # Ensure parent directory exists
        parent_dir = log_path.parent
        if not _ensure_dir_exists(parent_dir):
            return False
            
        # Append to the log file using safe atomic write-like pattern
        try:
            # Create a temporary file in the same directory
            temp_fd, temp_file = tempfile.mkstemp(dir=str(parent_dir))
            
            try:
                # Read existing content if the file exists
                existing_content = ""
                if log_path.exists():
                    with open(log_path, "r", encoding="utf-8") as f:
                        existing_content = f.read()
                
                # Write to temp file
                with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                    f.write(existing_content + log_entry)
                
                # Atomic replace
                os.replace(temp_file, log_path)
                return True
            except Exception:
                # Clean up if failed
                os.close(temp_fd)
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                return False
        except:
            # Direct append as fallback
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
            return True
        
    except Exception:
        # Silently fail - we can't log a logging failure!
        return False

def log_exception(exception: Exception, logger_name: Optional[str] = None) -> None:
    """
    Log an exception with traceback.
    
    Args:
        exception: Exception to log
        logger_name: Optional logger name to use
    """
    import traceback
    
    if logger_name and logger_name in _loggers:
        logger = _loggers[logger_name]
    else:
        logger = get_logger("exception_handler")
    
    error_message = f"{type(exception).__name__}: {str(exception)}"
    logger.error(error_message)
    
    # Get and log the traceback
    tb = traceback.format_exc()
    logger.debug(f"Traceback:\n{tb}")
    
    # Also log to error log file
    try:
        if _is_path_safe(ERROR_LOG_FILE):
            # Ensure error log directory exists
            if _ensure_dir_exists(ERROR_LOG_FILE.parent):
                # Write the error and traceback
                timestamp = time.strftime(DEFAULT_DATE_FORMAT, time.localtime())
                error_entry = f"[{timestamp}] {error_message}\n{tb}\n"
                
                # Append to the error log file
                with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(error_entry)
    except Exception:
        # Can't handle logging errors in the exception logger
        pass

def get_all_loggers() -> Dict[str, logging.Logger]:
    """
    Get all registered loggers.
    
    Returns:
        Dictionary of logger names to logger objects
    """
    return _loggers.copy()

def shutdown_logging() -> None:
    """
    Properly shutdown logging system, flushing and closing all handlers.
    """
    for logger in _loggers.values():
        for handler in logger.handlers:
            handler.flush()
            handler.close()
            logger.removeHandler(handler)
    
    _loggers.clear()

def configure_root_logger(level: Union[str, int] = "WARNING") -> None:
    """
    Configure the root logger with safe file handling.
    
    Args:
        level: Logging level for the root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(_parse_level(level))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler for the root logger
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
    root_logger.addHandler(console)
    
    # Add file handler if possible
    try:
        # Ensure log directory exists safely
        if _ensure_dir_exists(DEFAULT_LOG_DIR):
            # Validate the log file path
            if _is_path_safe(DEFAULT_LOG_FILE):
                # Use rotating file handler
                file_handler = RotatingFileHandler(
                    str(DEFAULT_LOG_FILE),
                    maxBytes=MAX_LOG_SIZE,
                    backupCount=3,
                    encoding='utf-8'
                )
                file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
                root_logger.addHandler(file_handler)
    except Exception as e:
        # Just log to console if file logging setup fails
        console.setFormatter(logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT))
        root_logger.error(f"Failed to setup file logging for root logger: {str(e)}")

def _parse_level(level: Union[str, int]) -> int:
    """
    Parse a logging level from string or int.
    
    Args:
        level: Level as string or int
        
    Returns:
        Logging level constant
    """
    if isinstance(level, int):
        return level
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    return level_map.get(level.upper(), logging.INFO)

# Initialize logging on module import
configure_root_logger()
