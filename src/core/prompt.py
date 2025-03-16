"""
Prompt formatting for Rick Assistant.

This module handles the generation and formatting of
the ZSH prompt with Rick's personality.
"""

import os
import pwd
import shutil
from typing import Dict, Any, List, Optional, Tuple
import random
from pathlib import Path
import time
import sys
import platform
import psutil
from datetime import datetime

# For compatibility with new integration system
from src.utils.config import get_config_value
from src.utils.logger import get_logger

# ANSI Color Codes
COLORS = {
    "reset": "\033[0m",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_green": "\033[92m",
    "bright_blue": "\033[94m",
    "portal_green": "\033[38;5;46m",  # Custom portal color
    "portal_blue": "\033[38;5;39m",    # Custom portal color
}

# Rick's catchphrases
CATCHPHRASES = [
    "Wubba lubba dub dub!",
    "That's the way the news goes!",
    "Rikki-tikki-tavi, biatch!",
    "And that's the waaaay the news goes!",
    "Hit the sack, Jack!",
    "Uh oh, somersault jump!",
    "AIDS!",
    "Grass tastes bad!",
    "Lick, lick, lick my balls!",
    "No jumping in the sewer!",
    "Burger time!",
    "Shum shum schlippity dop!",
    "I'm pickle Rick!",
    "I'm sorry, but your opinion means very little to me.",
    "I'm not a hero, I'm high functioning alcoholic."
]

# Warning thresholds for system metrics
WARNING_THRESHOLDS = {
    "cpu": 70,         # Warning at 70% CPU usage
    "cpu_critical": 90, # Critical at 90% CPU usage
    "ram": 70,         # Warning at 70% RAM usage
    "ram_critical": 90, # Critical at 90% RAM usage
    "disk": 80,        # Warning at 80% disk usage
    "disk_critical": 95, # Critical at 95% disk usage
    "temp": 70,        # Warning at 70°C
    "temp_critical": 80, # Critical at 80°C
    "battery": 30,     # Warning at 30% battery
    "battery_critical": 15, # Critical at 15% battery
}

# Cached system metrics
_cached_metrics = {}
_metrics_timestamp = 0
_metrics_cache_ttl = 5  # Cache TTL in seconds
_terminal_width_cache = 80
_terminal_width_timestamp = 0
_terminal_width_cache_ttl = 2  # Cache TTL in seconds

# Initialize logger
logger = get_logger(__name__)

# Rick's personality phrases
RICK_PHRASES = [
    "🧪 *burp* What now?",
    "🧪 I'm working here, Morty!",
    "🧪 This dimension's terminals are primitive",
    "🧪 *burp* Look at you, typing away like you know what you're doing",
    "🧪 Oh great, another command. *burp* I'm sooo excited",
    "🧪 *burp* Science!",
    "🧪 Wubba Lubba Dub Dub!",
    "🧪 I turned myself into a prompt, Morty!"
]

def format_rick_prompt() -> str:
    """
    Create the Rick prompt.
    
    Returns:
        A formatted Rick prompt string
    """
    try:
        return add_color("🧪 Rick> ", "portal_green")
    except Exception:
        return "🧪 Rick> "  # Fallback

def format_user_prompt(username: Optional[str] = None) -> str:
    """
    Create the user prompt with the provided username.
    
    Args:
        username: The username to display, or None to auto-detect
        
    Returns:
        A formatted user prompt string
    """
    try:
        if username is None:
            username = get_username()
        return add_color(f"👹 {username}> ", "yellow")
    except Exception:
        return "👹> "  # Fallback

def format_status_bar(path: Optional[str] = None, catchphrase: Optional[str] = None) -> str:
    """
    Format the status bar with path and system information.
    
    Args:
        path: Optional path to display (current directory if None)
        catchphrase: Optional catchphrase to display (random if None)
        
    Returns:
        Formatted status bar string
    """
    # Check if we should replace the path indicator based on configuration
    replace_path = get_config_value("prompt_integration.replace_path_indicator", False)
    
    if not replace_path and path is not None:
        # If configured not to replace path and a path is provided,
        # we respect Powerlevel10k's path indicator
        return ""
    
    # Original implementation for standalone mode or when configured to replace path
    width = get_terminal_width()
    
    # Get the current directory if not provided
    if path is None:
        path = os.getcwd()
    
    # Format the path
    path_display = format_current_directory(path)
    
    # Get a catchphrase if not provided
    if catchphrase is None:
        catchphrase = get_random_catchphrase()
    
    # Get system metrics
    metrics = get_system_metrics()
    metrics_display = format_system_metrics(metrics)
    
    # Format according to plan.md specifications
    components = []
    
    # Add path component with correct emoji
    components.append(f"📁 {path_display}")
    
    # Add metrics if available
    if metrics.get("cpu", {}).get("usage") is not None:
        cpu_usage = metrics["cpu"]["usage"]
        cpu_str = colorize_metrics("CPU", cpu_usage, WARNING_THRESHOLDS)
        components.append(f"🖥️ {cpu_str}")
    
    if metrics.get("ram", {}).get("percent") is not None:
        ram_usage = metrics["ram"]["percent"]
        ram_str = colorize_metrics("RAM", ram_usage, WARNING_THRESHOLDS)
        components.append(f"🔧 {ram_str}")
    
    # Add temperature if available
    if metrics.get("temperature", {}).get("available", False):
        try:
            from src.utils.temperature_alerts import get_temperature_status
            temp_status = get_temperature_status()
            if temp_status and "temperature" in temp_status:
                temp = temp_status["temperature"]
                temp_color = "green"
                if temp > 80:
                    temp_color = "red"
                elif temp > 60:
                    temp_color = "yellow"
                components.append(f"🌡️ TEMP:{temp:.1f}°C")
        except Exception:
            pass
    
    # Add universe indicator
    components.append("🌀 C-137")
    
    # Add catchphrase with correct emoji
    components.append(f"🧪 {catchphrase}")
    
    # Join all components with pipe separator
    status_bar = " | ".join(components)
    
    # Truncate if needed
    return truncate_status_bar(status_bar, width)

def get_prompt_structure() -> str:
    """
    Combine all elements into complete prompt structure.
    
    Returns:
        A complete prompt string with all components
    """
    try:
        rick_prompt = format_rick_prompt()
        status = format_status_bar()
        user_prompt = format_user_prompt()
        
        return f"{rick_prompt}\n{status}\n{user_prompt}"
    except Exception:
        # Simple fallback if anything goes wrong
        return "🧪 Rick> \n👹> "

def get_username() -> str:
    """
    Detect and return current username.
    
    Returns:
        The current username
    """
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return "user"  # Fallback

def format_current_directory(path: str) -> str:
    """
    Format directory for display.
    
    Args:
        path: The directory path to format
        
    Returns:
        Formatted directory string
    """
    try:
        home = os.path.expanduser("~")
        
        # Replace home directory with ~
        if path.startswith(home):
            path = "~" + path[len(home):]
            
        # Truncate if too long
        width = get_terminal_width()
        max_length = max(width // 6, 15)  # Reduced from 1/4 to 1/6 of width to accommodate metrics
        
        return truncate_path(path, max_length)
    except Exception:
        return path  # Fallback to original path

def truncate_path(path: str, max_length: int) -> str:
    """
    Shorten long paths intelligently.
    
    Args:
        path: The path to truncate
        max_length: Maximum length for the path
        
    Returns:
        Truncated path string
    """
    try:
        if len(path) <= max_length:
            return path
            
        parts = path.split(os.sep)
        
        # If just a single component that's too long, truncate it
        if len(parts) <= 2:
            return path[:max_length-3] + "..."
            
        # Start by keeping first and last components
        result = [parts[0], "...", parts[-1]]
        current_length = len(parts[0]) + 3 + len(parts[-1])
        
        # Fill in from the end as space permits
        for i in range(len(parts) - 2, 0, -1):
            part_len = len(parts[i]) + 1  # +1 for separator
            if current_length + part_len <= max_length:
                result.insert(2, parts[i])
                current_length += part_len
            else:
                break
                
        return os.sep.join(filter(None, result))
    except Exception:
        # Simple character truncation as fallback
        if len(path) > max_length:
            return path[:max_length-3] + "..."
        return path

def get_random_catchphrase() -> str:
    """
    Get a random Rick catchphrase.
    
    Returns:
        A random catchphrase string
    """
    try:
        return random.choice(CATCHPHRASES)
    except Exception:
        return "Wubba lubba dub dub!"  # Default catchphrase

def add_color(text: str, color: str) -> str:
    """
    Add ANSI color to text.
    
    Args:
        text: The text to colorize
        color: The color name to apply
        
    Returns:
        Colorized text string
    """
    try:
        if color in COLORS:
            return f"{COLORS[color]}{text}{COLORS['reset']}"
        return text
    except Exception:
        return text  # Fallback to plain text

def escape_special_chars(text: str) -> str:
    """
    Escape ZSH special characters.
    
    Args:
        text: The text to escape
        
    Returns:
        Escaped text string
    """
    try:
        # Characters that need escaping in ZSH prompt
        special_chars = ["%", "\\", "(", ")", "[", "]", "{", "}", "*", "$"]
        
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
            
        return text
    except Exception:
        return text  # Return original if something goes wrong

def get_terminal_width() -> int:
    """
    Get current terminal width with caching to reduce system calls.
    
    Returns:
        Terminal width in characters
    """
    global _terminal_width_cache, _terminal_width_timestamp, _terminal_width_cache_ttl
    
    try:
        # Use cached value if fresh
        current_time = time.time()  # Use actual time instead of random
        if (_terminal_width_timestamp > 0 and 
            (current_time - _terminal_width_timestamp) < _terminal_width_cache_ttl):
            return _terminal_width_cache
            
        # Get fresh width
        columns, _ = shutil.get_terminal_size()
        
        # Update cache
        _terminal_width_cache = columns
        _terminal_width_timestamp = current_time
        
        return columns
    except Exception:
        # If we can't get the width, use a reasonable default
        if _terminal_width_cache is None:
            _terminal_width_cache = 80  # Default width
        return _terminal_width_cache  # Use cached value as fallback

def truncate_status_bar(status_bar: str, width: int) -> str:
    """
    Intelligently truncate status bar for small terminals.
    Prioritizes different elements based on available width.
    
    Args:
        status_bar: The status bar to truncate
        width: Available width in characters
        
    Returns:
        Truncated status bar string
    """
    try:
        if len(status_bar) <= width:
            return status_bar
            
        # Split into components - expecting format: path | metrics | catchphrase
        components = status_bar.split(" | ")
        
        if len(components) < 2:
            # Not enough components, just truncate
            return status_bar[:width-3] + "..."
            
        # Handle based on terminal size categories
        if width < 30:  # Very narrow
            # Just show abbreviated path
            path_part = components[0]
            return path_part[:width-3] + "..."
            
        elif width < 60:  # Narrow
            # Show path and CPU only
            path_part = components[0]
            
            # Find CPU info in metrics if present
            cpu_text = ""
            for comp in components[1:-1]:  # Look in middle components (metrics)
                if "CPU:" in comp:
                    cpu_text = "CPU:" + comp.split("CPU:")[1].split()[0]
                    break
                    
            # Format based on available width
            if cpu_text:
                # Make sure we account for the separator and leave space for the ellipsis if needed
                path_width = width - len(cpu_text) - 5  # " | " = 3 + possible "..." = 3
                truncated_path = path_part[:path_width]
                if len(truncated_path) < len(path_part):
                    truncated_path = truncated_path[:path_width-3] + "..."
                
                # Double-check final length to ensure we don't exceed width
                result = f"{truncated_path} | {cpu_text}"
                if len(result) > width:
                    result = result[:width]
                return result
            else:
                # No CPU info, just show path
                return path_part[:width-3] + "..."
                
        elif width < 90:  # Medium
            # Show path, CPU & RAM, but no catchphrase
            path_part = components[0]
            
            # Collect essential metrics
            metrics_text = []
            for comp in components[1:-1]:  # Look in middle components (metrics)
                if "CPU:" in comp or "RAM:" in comp:
                    if "CPU:" in comp:
                        metrics_text.append("CPU:" + comp.split("CPU:")[1].split()[0])
                    if "RAM:" in comp:
                        metrics_text.append("RAM:" + comp.split("RAM:")[1].split()[0])
            
            if metrics_text:
                metrics_str = " | ".join(metrics_text)
                # Make sure we account for the separator
                path_width = width - len(metrics_str) - 5
                truncated_path = path_part[:path_width]
                if len(truncated_path) < len(path_part):
                    truncated_path = truncated_path[:path_width-3] + "..."
                
                # Double-check final length to ensure we don't exceed width
                result = f"{truncated_path} | {metrics_str}"
                if len(result) > width:
                    result = result[:width]
                return result
            else:
                # No metrics, show more path
                return path_part[:width-3] + "..."
                
        else:  # Wider but still needs truncation
            # Show path, all metrics, truncate catchphrase
            path_part = components[0]
            catchphrase_part = components[-1] if len(components) > 2 else ""
            
            # Join all metrics
            metrics_str = " | ".join(components[1:-1]) if len(components) > 2 else ""
            
            # Calculate available space for catchphrase
            available = width - len(path_part) - len(metrics_str) - 6  # " | " + " | " = 6
            
            if available > 10:  # If enough space for meaningful catchphrase
                truncated_catchphrase = catchphrase_part[:available]
                # Double-check final length to ensure we don't exceed width
                result = f"{path_part} | {metrics_str} | {truncated_catchphrase}"
                if len(result) > width:
                    result = result[:width]
                return result
            else:
                # Not enough for catchphrase, just show path and metrics
                result = f"{path_part} | {metrics_str}"
                if len(result) > width:
                    result = result[:width]
                return result
                
    except Exception:
        # Fallback to simple truncation
        if len(status_bar) > width:
            return status_bar[:width-3] + "..."
        return status_bar

def adapt_to_width(content: str, width: int) -> str:
    """
    Adjust content to fit terminal width with intelligent element prioritization.
    
    Args:
        content: The content to adjust
        width: Available width in characters
        
    Returns:
        Adjusted content string
    """
    # Use the more advanced truncation function
    return truncate_status_bar(content, width)

# System metrics integration
def cache_expensive_metrics() -> Dict[str, Any]:
    """
    Cache system metrics to improve performance.
    Coordinates with the system module's caching if available.
    
    Returns:
        Dict with cached metrics
    """
    global _cached_metrics, _metrics_timestamp, _metrics_cache_ttl
    
    try:
        # Check if cache is fresh
        current_time = time.time()  # Use actual time instead of random
        if _cached_metrics and (current_time - _metrics_timestamp) < _metrics_cache_ttl:
            return _cached_metrics
            
        # Try to use system module's caching
        try:
            from src.utils.system import format_all_metrics
            metrics = format_all_metrics()  # This uses system module's cache
        except ImportError:
            # Use direct psutil as fallback
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                
                metrics = {
                    "cpu": {"usage": cpu, "state": "normal" if cpu < 70 else "warning"},
                    "ram": {"percent": mem.percent, "state": "normal" if mem.percent < 80 else "warning"},
                    "temperature": {"available": False},
                    "timestamp": current_time
                }
            except ImportError:
                metrics = {}
        
        # Update cache
        _cached_metrics = metrics
        _metrics_timestamp = current_time
        
        return metrics
    except Exception:
        return _cached_metrics or {}  # Return existing cache or empty dict

def get_system_metrics() -> Dict[str, Any]:
    """
    Get formatted system metrics for prompt display.
    Uses caching to reduce overhead.
    
    Returns:
        Dict with system metrics or empty dict if unavailable
    """
    # Use the optimized caching function
    return cache_expensive_metrics()

def format_system_metrics(metrics: Dict[str, Any]) -> str:
    """
    Format system metrics for display in the status bar.
    Applies colorization based on thresholds.
    
    Args:
        metrics: Dictionary containing system metrics
        
    Returns:
        Formatted system metrics string
    """
    try:
        # Import here to avoid circular imports
        from src.utils.temperature_alerts import get_temperature_status, format_temperature_alert_for_statusbar
        
        result = []
        
        # CPU usage
        if metrics.get("cpu", {}).get("usage") is not None:
            cpu_usage = metrics["cpu"]["usage"]
            cpu_str = colorize_metrics("CPU", cpu_usage, WARNING_THRESHOLDS)
            result.append(f"🖥️ {cpu_str}")
        
        # RAM usage
        if metrics.get("ram", {}).get("percent") is not None:
            ram_usage = metrics["ram"]["percent"]
            ram_str = colorize_metrics("RAM", ram_usage, WARNING_THRESHOLDS)
            result.append(f"🔧 {ram_str}")
        
        # CPU Temperature with alerts
        if metrics.get("temperature", {}).get("available", False):
            try:
                # Get temperature status with alert info
                temp_status = get_temperature_status()
                
                # Format with alert highlighting
                temp_str = format_temperature_alert_for_statusbar(temp_status)
                if temp_str:
                    result.append(f"🌡️ {temp_str}")
            except (ImportError, Exception):
                # Fall back to basic temperature display if temperature_alerts not available
                if metrics.get("temperature", {}).get("temperature") is not None:
                    temp = metrics["temperature"]["temperature"]
                    temp_str = colorize_metrics("TEMP", temp, WARNING_THRESHOLDS, suffix="°C")
                    result.append(f"🌡️ {temp_str}")
        
        # Disk usage
        if metrics.get("disk", {}).get("percent") is not None:
            disk_usage = metrics["disk"]["percent"]
            disk_str = colorize_metrics("DISK", disk_usage, WARNING_THRESHOLDS)
            result.append(f"💾 {disk_str}")
        
        # Network info (if active)
        if metrics.get("network", {}).get("available", False):
            net = metrics["network"]
            if net.get("sent_speed", 0) > 0 or net.get("received_speed", 0) > 0:
                # Format speeds
                up_speed = format_bytes(net.get("sent_speed", 0)) + "/s"
                down_speed = format_bytes(net.get("received_speed", 0)) + "/s"
                result.append(f"🌐 ↑{up_speed} ↓{down_speed}")
            elif net.get("primary"):
                # Just show primary interface
                primary = net.get("primary", "")
                if primary and net.get("interfaces", {}).get(primary, {}).get("ipv4"):
                    ip = net["interfaces"][primary]["ipv4"]
                    result.append(f"🌐 {primary}:{ip}")
        
        # Add universe indicator
        result.append("🌀 C-137")
        
        # Join all components
        return " | ".join(result)
    except Exception as e:
        logger.error(f"Error formatting system metrics: {str(e)}")
        return ""

def colorize_metrics(metric: str, value: float, thresholds: Dict[str, float], suffix: str = "") -> str:
    """
    Apply color coding to metrics based on thresholds.
    
    Args:
        metric: Metric name (e.g., 'CPU', 'RAM')
        value: Metric value
        thresholds: Dictionary with threshold values
        suffix: Optional suffix to add after the value (e.g., '°C')
        
    Returns:
        Colorized metric string
    """
    # Determine threshold keys
    critical_key = f"{metric.lower()}_critical" if f"{metric.lower()}_critical" in thresholds else None
    warning_key = f"{metric.lower()}" if f"{metric.lower()}" in thresholds else None
    
    # Get threshold values
    critical = thresholds.get(critical_key, 90) if critical_key else 90
    warning = thresholds.get(warning_key, 70) if warning_key else 70
    
    # Determine color based on value
    if value >= critical:
        color = "red"
    elif value >= warning:
        color = "yellow"
    else:
        color = "green"
    
    # Format the metric value with the metric name
    formatted = f"{metric}:{value:.1f}{suffix}"
    
    # Add color
    return add_color(formatted, color)

# Powerlevel10k integration functions
def prompt_rick_assistant() -> Dict[str, Any]:
    """
    P10k segment function with enhanced system metrics support.
    
    Returns:
        A formatted segment for Powerlevel10k
    """
    try:
        # Get system metrics for P10k segment
        status = "active"  # Default status
        
        # Allow conditional display based on metrics
        segment = {
            "icon": format_p10k_icon(status),
            "content": format_p10k_content(status),
            "styles": get_p10k_styles(status)
        }
        
        # Extend with system metrics if terminal is wide enough
        if create_conditional_segment("metrics"):
            metrics = get_system_metrics()
            segment = extend_p10k_segment(segment, metrics)
            
        return segment
    except Exception:
        # Fallback to basic segment
        return {
            "icon": "🧪",
            "content": "",
            "styles": {"fg": "green"}
        }

def register_with_powerlevel10k() -> None:
    """
    Register Rick Assistant with Powerlevel10k.
    
    Note: This function is kept for backwards compatibility.
    The new implementation uses the prompt integration system.
    """
    # Check if we should use the legacy integration or the new one
    use_legacy = get_config_value("prompt_integration.use_legacy", False)
    
    if use_legacy:
        # Legacy implementation
        # This code is kept for backwards compatibility
        segment = get_p10k_segment()
        print(f"POWERLEVEL9K_CUSTOM_RICK=\"{segment['command']}\"")
        print(f"POWERLEVEL9K_CUSTOM_RICK_BACKGROUND={segment.get('background', 'clear')}")
        print(f"POWERLEVEL9K_CUSTOM_RICK_FOREGROUND={segment.get('foreground', 'green')}")
    else:
        # New implementation uses the prompt integration system
        # Don't output anything here as the new system handles everything
        pass

def format_p10k_segment(status: str) -> str:
    """
    Format content for Powerlevel10k segment.
    
    Args:
        status: Current status of the assistant
        
    Returns:
        Formatted string for the P10k segment
    """
    try:
        return format_p10k_icon(status)
    except Exception:
        return "🧪"  # Fallback

def format_p10k_icon(status: str) -> str:
    """
    Get the appropriate icon for P10k segment based on status.
    
    Args:
        status: Current status of the assistant
        
    Returns:
        Icon string for P10k segment
    """
    try:
        if status == "active":
            return "🧪"
        elif status == "disabled":
            return "⚗️"
        elif status == "error":
            return "💥"
        else:
            return "🧪"
    except Exception:
        return "🧪"  # Fallback

def format_p10k_content(status: str) -> str:
    """
    Get the text content for P10k segment based on status.
    
    Args:
        status: Current status of the assistant
        
    Returns:
        Content string for P10k segment
    """
    try:
        if status == "active":
            return ""  # Empty by default, will be extended with metrics if available
        elif status == "disabled":
            return "OFF"
        elif status == "error":
            return "ERR"
        else:
            return ""
    except Exception:
        return ""  # Fallback

def get_p10k_styles(status: str) -> Dict[str, str]:
    """
    Get styling options for P10k segment based on status.
    
    Args:
        status: Current status of the assistant
        
    Returns:
        Dict with style options for P10k
    """
    try:
        if status == "active":
            return {"fg": "green"}
        elif status == "disabled":
            return {"fg": "gray"}
        elif status == "error":
            return {"fg": "red"}
        else:
            return {"fg": "cyan"}
    except Exception:
        return {"fg": "green"}  # Fallback

def extend_p10k_segment(segment: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extend P10k segment with system metrics information.
    
    Args:
        segment: Base segment dict with icon and styles
        metrics: System metrics to add
        
    Returns:
        Extended segment dict
    """
    try:
        if not metrics:
            return segment
            
        # Start with the base segment
        result = segment.copy()
        content_parts = []
        
        # Add CPU if available
        if metrics and "cpu" in metrics and metrics["cpu"].get("usage") is not None:
            cpu = metrics["cpu"]
            cpu_value = cpu.get("usage", 0)
            cpu_state = cpu.get("state", "normal")
            content_parts.append(f"CPU:{cpu_value}%")
            
            # Update segment color based on worst state
            if cpu_state == "critical" and result["styles"]["fg"] != "red":
                result["styles"]["fg"] = "red"
            elif cpu_state == "warning" and result["styles"]["fg"] != "red":
                result["styles"]["fg"] = "yellow"
                
        # Add RAM if available and space permits
        if create_conditional_segment("extended_metrics") and metrics and "ram" in metrics and metrics["ram"].get("percent") is not None:
            ram = metrics["ram"]
            ram_value = ram.get("percent", 0)
            ram_state = ram.get("state", "normal")
            content_parts.append(f"RAM:{ram_value}%")
            
            # Update segment color based on worst state
            if ram_state == "critical" and result["styles"]["fg"] != "red":
                result["styles"]["fg"] = "red"
            elif ram_state == "warning" and result["styles"]["fg"] != "red":
                result["styles"]["fg"] = "yellow"
                
        # Join parts if any
        if content_parts:
            result["content"] = " ".join(content_parts)
            
        return result
    except Exception:
        return segment  # Return original segment on error

def create_conditional_segment(condition: str) -> bool:
    """
    Determine whether to show a segment feature based on condition.
    
    Args:
        condition: The condition to check
        
    Returns:
        bool: True if condition is met
    """
    try:
        # Get terminal width for space-based conditions
        width = get_terminal_width()
        
        if condition == "metrics":
            # Show metrics if terminal is at least medium width
            return width >= 80
            
        elif condition == "extended_metrics":
            # Show extended metrics if terminal is wide
            return width >= 100
            
        elif condition == "temperature":
            # Show temperature only in wide terminals
            return width >= 120
            
        # Default to enabling the condition
        return True
    except Exception:
        return False  # Disable on error

def get_p10k_segment() -> Dict[str, Any]:
    """
    Get the Powerlevel10k segment content.
    
    Returns:
        A dict with content for Powerlevel10k prompt
    """
    try:
        # Trigger optimization first
        optimize_prompt_rendering()
        
        # Return enhanced segment
        return prompt_rick_assistant()
    except Exception:
        # Fallback to basic segment
        return {
            "icon": "🧪",
            "content": "",
            "styles": {"fg": "green"}
        }

def optimize_prompt_rendering() -> None:
    """
    Optimize the prompt rendering process.
    Pre-fetches expensive data to reduce prompt generation time.
    """
    try:
        # Pre-cache terminal width
        get_terminal_width()
        
        # Pre-cache system metrics
        cache_expensive_metrics()
    except Exception:
        pass  # Silently fail - this is just an optimization

def format_bytes(bytes_value):
    """
    Format bytes value to human-readable format.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Human-readable string
    """
    if bytes_value < 1024:
        return f"{bytes_value}B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value/1024:.1f}K"
    elif bytes_value < 1024 * 1024 * 1024:
        return f"{bytes_value/(1024*1024):.1f}M"
    else:
        return f"{bytes_value/(1024*1024*1024):.1f}G"

# Functions for the new prompt integration system
def get_prompt_content() -> str:
    """
    Get the content to display in Rick's prompt segment.
    
    This function is used by the prompt integration system to get
    content for Rick's segment, based on configuration.
    
    Returns:
        str: The content to display
    """
    try:
        # Get configuration
        show_personality = get_config_value("prompt_integration.show_personality", True)
        status_indicators = get_config_value("prompt_integration.status_indicators", ["cpu", "memory", "temperature"])
        
        components = []
        
        # Get current path for directory component
        path_display = format_current_directory(os.getcwd())
        components.append(f"📁 {path_display}")
        
        # Add system metrics if configured
        if status_indicators:
            # Get metrics with error handling
            try:
                metrics = get_system_metrics()
                
                # CPU metrics
                if "cpu" in status_indicators and metrics and "cpu" in metrics:
                    if isinstance(metrics["cpu"], dict) and "usage" in metrics["cpu"]:
                        cpu = metrics["cpu"]["usage"]
                        cpu_color = "green"
                        if cpu > 70:
                            cpu_color = "red"
                        elif cpu > 40:
                            cpu_color = "yellow"
                        components.append(f"🖥️ CPU:{cpu:.1f}%")
                    elif isinstance(metrics["cpu"], (int, float)):
                        cpu = metrics["cpu"]
                        components.append(f"🖥️ CPU:{cpu:.1f}%")
                
                # Memory metrics
                if ("memory" in status_indicators or "ram" in status_indicators) and metrics:
                    if "ram" in metrics and isinstance(metrics["ram"], dict) and "percent" in metrics["ram"]:
                        mem = metrics["ram"]["percent"]
                        components.append(f"🔧 RAM:{mem:.1f}%")
                    elif "memory" in metrics and isinstance(metrics["memory"], dict) and "percent" in metrics["memory"]:
                        mem = metrics["memory"]["percent"]
                        components.append(f"🔧 RAM:{mem:.1f}%")
                
                # Temperature metrics
                if "temperature" in status_indicators and metrics and "temperature" in metrics:
                    if isinstance(metrics["temperature"], dict) and "temperature" in metrics["temperature"]:
                        temp = metrics["temperature"]["temperature"]
                        components.append(f"🌡️ TEMP:{temp:.1f}°C")
                    elif isinstance(metrics["temperature"], (int, float)):
                        temp = metrics["temperature"]
                        components.append(f"🌡️ TEMP:{temp:.1f}°C")
            except Exception as e:
                logger.error(f"Error accessing system metrics: {str(e)}")
        
        # Add universe indicator
        components.append("🌀 C-137")
        
        # Add Rick's catchphrase if configured
        if show_personality:
            phrase = get_rick_phrase(for_p10k=True)  # Don't include emoji in phrase
            if phrase:
                components.append(f"🧪 {phrase}")
        
        # Format the final output according to plan.md specifications
        return " | ".join(components)
    except Exception as e:
        logger.error(f"Error in get_prompt_content: {str(e)}")
        return "🧪 *burp* Error getting content"

def get_rick_phrase(for_p10k=False):
    """Get a random Rick catchphrase.
    
    This function returns a random Rick catchphrase from a predefined list.
    The catchphrases are designed to be fun and in character with Rick Sanchez.
    
    Args:
        for_p10k (bool): Whether this is being called from Powerlevel10k integration
                         If True, will return properly formatted p10k colors
                         If False, will use terminal color codes
    
    Returns:
        str: A random Rick catchphrase
    """
    try:
        from src.utils.logger import get_logger
        logger = get_logger(__name__)
        
        # Get the burp frequency from config
        burp_frequency = get_config_value("prompt.burp_frequency", 30)
        
        # Determine if we should add a burp (30% chance by default)
        should_burp = random.randint(1, 100) <= burp_frequency
        
        # Get a random catchphrase
        catchphrase = random.choice(CATCHPHRASES)
        
        # Format with the correct color syntax based on context
        if for_p10k:
            # Using p10k color syntax (%F{color}...%f)
            if should_burp:
                return f"%F{{green}}*burp*%f {catchphrase}"
            else:
                return f"%F{{green}}{catchphrase}%f"
        else:
            # Using terminal color codes for direct terminal output
            if should_burp:
                return f"🧪 \033[32m*burp*\033[0m {catchphrase}"
            else:
                return f"🧪 \033[32m{catchphrase}\033[0m"
                
    except Exception as e:
        # Provide a default catchphrase in case of an error
        if for_p10k:
            return "%F{yellow}*burp*%f Wubba lubba dub dub!"
        else:
            return "🧪 \033[33m*burp*\033[0m Wubba lubba dub dub!"

def _format_input_prompt(prompt_text):
    """Format the input prompt with Rick styling.
    
    Args:
        prompt_text (str): Base prompt text to format
        
    Returns:
        str: Formatted prompt with Rick styling
    """
    try:
        # Add Rick styling to the prompt
        return f"%F{{green}} %F{{cyan}}{prompt_text}%f > "
    except Exception as e:
        logger.error(f"Error formatting input prompt: {str(e)}")
        return f"{prompt_text} > "
