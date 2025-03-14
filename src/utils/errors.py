"""
Error Handling Module for Rick Assistant ZSH Plugin

This module provides a comprehensive error handling system for the Rick Assistant,
including custom exceptions, error formatting, and a decorator for safe function execution.

"Listen up! This *burp* error handling system is gonna save your pathetic code
from crashing and burning. You'll thank me later, if you're smart enough to use it."
"""
from typing import Type
import functools
import inspect
import logging
import random
import sys
import traceback
import io
import socket
import requests  # type: ignore # Moved to module level import
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast
from pathlib import Path
from functools import wraps

# Set up a basic logger in case the full logger isn't available
# This avoids circular imports but still allows logging
def _get_basic_logger(name: str) -> logging.Logger:
    """Get a basic logger to avoid circular imports."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Use basic logger initially
logger = _get_basic_logger(__name__)

# Type variables for decorator
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')

# ----------------------
# Custom Exception Classes
# ----------------------

class RickAssistantError(Exception):
    """Base exception class for all Rick Assistant errors."""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            original_exception: The original exception that caused this error, if any
        """
        self.message = message
        self.original_exception = original_exception
        super().__init__(message)

class ConfigError(RickAssistantError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error, if applicable
            original_exception: The original exception that caused this error, if any
        """
        self.config_key = config_key
        super().__init__(message, original_exception)

class ShellError(RickAssistantError):
    """Exception raised for shell integration errors."""
    
    def __init__(self, message: str, command: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            command: Shell command that caused the error, if applicable
            original_exception: The original exception that caused this error, if any
        """
        self.command = command
        super().__init__(message, original_exception)

class AIError(RickAssistantError):
    """Exception raised for AI-related errors."""
    
    def __init__(self, message: str, model: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            model: AI model that caused the error, if applicable
            original_exception: The original exception that caused this error, if any
        """
        self.model = model
        super().__init__(message, original_exception)

class ResourceError(RickAssistantError):
    """Exception raised for resource-related errors (filesystem, network, etc.)."""
    
    def __init__(self, message: str, resource: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            resource: Resource that caused the error, if applicable
            original_exception: The original exception that caused this error, if any
        """
        self.resource = resource
        super().__init__(message, original_exception)

class PathError(ResourceError):
    """Exception raised for path-related errors."""
    
    def __init__(self, message: str, path: Optional[Union[str, Path]] = None, 
                 error_type: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            path: Path that caused the error, if applicable
            error_type: Specific type of path error (traversal, permission, etc.)
            original_exception: The original exception that caused this error, if any
        """
        self.path = str(path) if path else None
        self.error_type = error_type
        super().__init__(message, self.path, original_exception)
        
    @classmethod
    def permission_error(cls, path: Union[str, Path], message: Optional[str] = None) -> 'PathError':
        """Create a permission error for a path."""
        msg = message or f"Permission denied for path: {path}"
        return cls(msg, path, "permission", None)
        
    @classmethod
    def traversal_error(cls, path: Union[str, Path], message: Optional[str] = None) -> 'PathError':
        """Create a path traversal error."""
        msg = message or f"Path traversal attempt detected: {path}"
        return cls(msg, path, "traversal", None)
        
    @classmethod
    def not_found_error(cls, path: Union[str, Path], message: Optional[str] = None) -> 'PathError':
        """Create a not found error for a path."""
        msg = message or f"Path not found: {path}"
        return cls(msg, path, "not_found", None)
        
    @classmethod
    def invalid_path_error(cls, path: Union[str, Path], message: Optional[str] = None) -> 'PathError':
        """Create an invalid path error."""
        msg = message or f"Invalid path format: {path}"
        return cls(msg, path, "invalid", None)

class ValidationError(RickAssistantError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None, 
                 original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            field: Field that failed validation, if applicable
            value: Value that failed validation, if applicable
            original_exception: The original exception that caused this error, if any
        """
        self.field = field
        self.value = value
        super().__init__(message, original_exception)

class SecurityError(RickAssistantError):
    """Exception raised for security-related issues."""
    
    def __init__(self, message: str, security_type: Optional[str] = None, 
                 resource: Optional[str] = None, original_exception: Optional[Exception] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            security_type: Type of security issue (e.g., 'path_traversal', 'injection')
            resource: Resource affected by the security issue
            original_exception: The original exception that caused this error, if any
        """
        self.security_type = security_type
        self.resource = resource
        super().__init__(message, original_exception)

# ----------------------
# Error Formatting
# ----------------------

def format_error(e: Exception) -> str:
    """
    Format an exception into a Rick-styled error message.
    
    Args:
        e: Exception to format
        
    Returns:
        Formatted error message with Rick's personality
    """
    # Get the error type name
    error_type = type(e).__name__
    
    # Get the error message
    if hasattr(e, 'message'):
        error_message = e.message
    else:
        error_message = str(e)
    
    # Rick-styled interjections
    interjections = [
        "Ugh, seriously?",
        "Well that's just perfect.",
        "Oh, great job there,",
        "Way to go,",
        "Listen up,",
        "Oh geez,",
        "Well *burp* congratulations,",
        "Brilliant move,",
        "Holy crap,",
        "For crying out loud,"
    ]
    
    # Rick-styled insults
    insults = [
        "genius",
        "Einstein",
        "Morty",
        "pal",
        "buddy",
        "champ",
        "sport",
        "professor",
        "mastermind",
        "whiz kid"
    ]
    
    # Rick-styled scientific references
    scientific_refs = [
        "You've collapsed the probability wave function of your code.",
        "Your code just crossed into a parallel dimension where it actually works.",
        "Somewhere in the multiverse, this code is running perfectly.",
        "You've achieved quantum superposition - your code both works and doesn't work.",
        "Even a Meeseeks couldn't fix this one.",
        "This is worse than interdimensional cable Season 3.",
        "Your code is more unstable than plutonic quartz.",
        "This is why we can't have nice things in dimension C-137."
    ]
    
    # Pick random elements
    interjection = random.choice(interjections)
    insult = random.choice(insults)
    scientific_ref = random.choice(scientific_refs)
    
    # Add burps randomly
    if random.random() < 0.3:  # 30% chance
        interjection = interjection.replace(" ", " *burp* ", 1)
    
    # Format the message
    if isinstance(e, RickAssistantError):
        # More detailed formatting for our custom exceptions
        message = f"{interjection} {insult}! {error_message}"
        
        # Add specific details based on exception type
        if isinstance(e, ConfigError) and e.config_key:
            message += f" Check your config key: '{e.config_key}'."
        elif isinstance(e, ShellError) and e.command:
            message += f" The command '{e.command}' blew up in your face."
        elif isinstance(e, PathError):
            if e.path:
                message += f" The path '{e.path}' is about as real as my respect for bureaucracy."
            if hasattr(e, 'error_type') and e.error_type:
                if e.error_type == "traversal":
                    message += " Nice try with that path traversal attack. Really clever. *slow clap*"
                elif e.error_type == "permission":
                    message += " What made you think you had permission to do that? Your optimism is adorable."
                elif e.error_type == "not_found":
                    message += " Did you think that path would magically appear if you wished hard enough?"
        elif isinstance(e, ValidationError):
            if e.field and e.value:
                message += f" Your '{e.field}' value '{e.value}' is garbage."
            elif e.field:
                message += f" Your '{e.field}' is invalid."
        elif isinstance(e, SecurityError):
            message += f" You triggered security protection! That's almost impressive."
            if hasattr(e, 'security_type') and e.security_type:
                message += f" ({e.security_type})"
    else:
        # Generic formatting for standard exceptions
        message = f"{interjection} {insult}! Got a {error_type}: {error_message}"
    
    # Add scientific reference occasionally
    if random.random() < 0.5:  # 50% chance
        message += f" {scientific_ref}"
    
    return message

def handle_exception(e: Exception, log_level: int = logging.ERROR, show_traceback: bool = True) -> None:
    """
    Handle an exception with appropriate logging and formatting.
    
    Args:
        e: Exception to handle
        log_level: Logging level to use
        show_traceback: Whether to include traceback in logs
    """
    # Get the exception message
    if hasattr(e, 'message'):
        error_message = e.message
    else:
        error_message = str(e)
    
    # Get calling function info for better context
    try:
        frame = inspect.currentframe().f_back
        if frame:
            func_name = frame.f_code.co_name
            file_name = frame.f_code.co_filename
            line_num = frame.f_lineno
            context = f"{file_name}:{line_num} in {func_name}()"
        else:
            context = "unknown context"
    except Exception:
        context = "unknown context"
    
    # Log the exception
    logger.log(log_level, f"Exception in {context}: {type(e).__name__}: {error_message}")
    
    # Log the original exception if available
    if hasattr(e, 'original_exception') and e.original_exception:
        logger.log(log_level, f"Original exception: {type(e.original_exception).__name__}: {e.original_exception}")
    
    # Log the traceback if requested
    if show_traceback:
        logger.log(log_level, f"Traceback: {traceback.format_exc()}")

def is_critical_error(e: Exception) -> bool:
    """
    Determine if an exception is a critical error that requires immediate attention.
    
    Args:
        e: Exception to check
        
    Returns:
        True if the exception is critical, False otherwise
    """
    # System-level exceptions are always critical
    critical_types = (
        SystemError,
        MemoryError,
        SystemExit,
        KeyboardInterrupt,
        ImportError
    )
    
    if isinstance(e, critical_types):
        return True
    
    # Check for specific error messages that indicate critical failures
    error_str = str(e).lower()
    critical_patterns = (
        "permission denied",
        "access is denied",
        "out of memory",
        "disk full",
        "connection refused",
        "database is locked",
        "disk quota exceeded"
    )
    
    for pattern in critical_patterns:
        if pattern in error_str:
            return True
    
    # ResourceErrors are critical if they involve system resources
    if isinstance(e, ResourceError):
        if hasattr(e, 'resource'):
            resource = getattr(e, 'resource', '')
            if resource and any(r in str(resource).lower() for r in (
                "/dev/", "/proc/", "/sys/", "/bin/", "/sbin/", "/etc/",
                "memory", "disk", "database", "network"
            )):
                return True
    
    # Path errors are critical if they involve path traversal
    if isinstance(e, PathError) and hasattr(e, 'error_type'):
        if e.error_type == "traversal":
            return True
    
    # Security errors are always critical
    if isinstance(e, SecurityError):
        return True
    
    # Config errors are critical if they prevent startup
    if isinstance(e, ConfigError) and hasattr(e, 'config_key'):
        config_key = getattr(e, 'config_key', '')
        critical_config_keys = (
            "general", "general.enabled", "paths", "security"
        )
        if config_key in critical_config_keys:
            return True
    
    return False

def get_error_fallback(func_name: str, error: Optional[Exception] = None) -> Any:
    """
    Get an appropriate fallback value for a function that failed with an error.
    
    Args:
        func_name: Name of the function that failed
        error: The exception that occurred, if available
        
    Returns:
        Appropriate fallback value based on function name
    """
    # Get the function name without module prefix
    short_name = func_name.split('.')[-1] if '.' in func_name else func_name
    
    # Path-related fallbacks
    if short_name.startswith('normalize_path'):
        return None
    elif short_name.startswith('resolve_path'):
        return None
    elif short_name.startswith('ensure_safe_directory'):
        return None
    elif short_name.startswith('is_path_within_safe_directories'):
        return False
    elif short_name.startswith('safe_atomic_write'):
        return False
        
    # Common fallback values based on function name patterns
    if any(short_name.startswith(prefix) for prefix in ('get_', 'load_', 'fetch_', 'retrieve_')):
        # Getter functions should return None or empty container
        if any(suffix in short_name for suffix in ('_dict', '_config', '_settings')):
            return {}
        elif any(suffix in short_name for suffix in ('_list', '_array', '_items')):
            return []
        elif any(suffix in short_name for suffix in ('_string', '_text', '_name')):
            return ""
        elif any(suffix in short_name for suffix in ('_bool', '_flag', '_enabled')):
            return False
        elif any(suffix in short_name for suffix in ('_int', '_count', '_number')):
            return 0
        else:
            return None
    
    elif any(short_name.startswith(prefix) for prefix in ('is_', 'has_', 'can_', 'should_', 'validate_')):
        # Boolean predicates should return False on error
        return False
    
    elif any(short_name.startswith(prefix) for prefix in ('create_', 'initialize_', 'setup_')):
        # Creation functions should return None or False
        return False
    
    # Default fallbacks by function name
    fallbacks = {
        'process_command': None,
        'execute_command': None,
        'parse_config': {},
        'get_plugin_status': {'status': 'error', 'enabled': False},
        'get_logger': logging.getLogger('fallback')
    }
    
    # Return specific fallback if available, otherwise None
    return fallbacks.get(short_name, None)

# ----------------------
# Error Handling Decorators
# ----------------------

def safe_execute(
    default_return: Any = None,
    log_level: int = logging.ERROR,
    show_user_message: bool = True,
    show_traceback: bool = True,
    handled_exceptions: Optional[List[Type[Exception]]] = None
) -> Callable[[F], F]:
    """
    Decorator for safely executing functions with error handling.
    
    Args:
        default_return: Value to return if function fails
        log_level: Logging level for errors
        show_user_message: Whether to show message to user
        show_traceback: Whether to include traceback in logs
        handled_exceptions: List of exception types to handle specifically
        
    Returns:
        Decorated function that catches exceptions
    """
    if handled_exceptions is None:
        handled_exceptions = []
        
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except tuple(handled_exceptions) as e:
                # Handle specific exceptions with custom logic
                logger.log(log_level, f"Handled {type(e).__name__} in {func.__name__}: {str(e)}")
                
                # Get function-specific fallback value
                fallback = default_return
                if fallback is None:
                    fallback = get_error_fallback(func.__name__, e)
                    
                # Show user message if requested
                if show_user_message:
                    print(format_error(e))
                    
                return fallback
            except Exception as e:
                # General exception handling
                handle_exception(e, log_level, show_traceback)
                
                # Get function-specific fallback value
                fallback = default_return
                if fallback is None:
                    fallback = get_error_fallback(func.__name__, e)
                    
                # Show user message if requested
                if show_user_message:
                    print(format_error(e))
                    
                return fallback
        return cast(F, wrapper)
    return decorator

def safe_execute_with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    default_return: Any = None,
    log_level: int = logging.ERROR,
    retry_exceptions: Optional[List[Type[Exception]]] = None
) -> Callable[[F], F]:
    """
    Decorator to safely execute a function with retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to increase delay between retries
        default_return: Default value to return on failure
        log_level: Logging level for errors
        retry_exceptions: List of exceptions to retry on
    
    Returns:
        Decorated function with retry logic
    """
    # Default exceptions to retry for are typically transient errors
    if retry_exceptions is None:
        # Common transient errors
        retry_exceptions = [
            TimeoutError,
            ConnectionError,
            socket.timeout,
            socket.error,
            io.IOError,
            OSError,
            requests.RequestException  # Direct reference to requests.RequestException
        ]
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time
            
            current_delay = delay
            last_exception = None
            
            # Try the function up to max_retries + 1 times (initial try + retries)
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(retry_exceptions) as e:
                    last_exception = e
                    
                    # If this was our last attempt, break out
                    if attempt >= max_retries:
                        break
                    
                    # Log the retry
                    logger.log(log_level, 
                              f"Attempt {attempt+1}/{max_retries+1} failed: {type(e).__name__}: {str(e)}")
                    logger.log(log_level, f"Retrying {func.__name__} in {current_delay:.2f} seconds...")
                    
                    # Wait before retrying
                    time.sleep(current_delay)
                    
                    # Increase delay for next attempt
                    current_delay *= backoff_factor
                except Exception as e:
                    # For exceptions that don't qualify for retry, just fail immediately
                    handle_exception(e, log_level)
                    
                    # Get function-specific fallback value
                    fallback = default_return
                    if fallback is None:
                        fallback = get_error_fallback(func.__name__, e)
                        
                    return fallback
            
            # If we get here, all retries failed
            if last_exception:
                handle_exception(last_exception, log_level)
                logger.error(f"All {max_retries+1} attempts failed for {func.__name__}")
                
                # Get function-specific fallback value
                fallback = default_return
                if fallback is None:
                    fallback = get_error_fallback(func.__name__, last_exception)
                    
                return fallback
            
            # This shouldn't happen, but just in case
            return default_return
            
        return cast(F, wrapper)
    return decorator

# Error handling policy documentation
ERROR_HANDLING_POLICY = """
Error Handling Policy for Rick Assistant

1. Use @safe_execute decorator for all functions that:
   - Interact with external systems (filesystem, network, etc.)
   - Could fail due to user input or configuration
   - Are called from ZSH hooks or command handlers

2. Use specific exception types:
   - ConfigError for configuration issues
   - ShellError for shell interaction issues
   - AIError for AI-related issues
   - ResourceError for resource access issues
   - PathError for path-related issues
   - ValidationError for validation issues
   - SecurityError for security violations
   - Use base RickAssistantError for general errors

3. Logging standards:
   - ERROR level for user-impacting issues
   - WARNING level for potential problems that are handled
   - INFO level for normal operations
   - DEBUG level for detailed diagnostics

4. Error recovery:
   - Functions should specify appropriate default returns
   - Critical functions should raise exceptions for immediate attention
   - User-facing functions should never crash
"""

# At module load, try to import the full logger
try:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Keep using the basic logger if the import fails
    pass
