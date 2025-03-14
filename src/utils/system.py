#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Information Monitor Module for Rick Assistant.

This module provides system monitoring capabilities including CPU, RAM, disk usage,
temperature, and uptime information with Rick-themed formatting and commentary.
Cross-platform support is implemented with appropriate fallbacks for unavailable metrics.
"""

import os
import time
import platform
import threading
import json
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime
import socket

# Clean imports - no try/except to prevent fallback implementation conflicts
import time
import threading
import platform
import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple

# Try to import psutil with proper error handling
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Import internal modules directly without fallbacks
from src.utils.logger import get_logger
from src.utils.errors import safe_execute, RickAssistantError, ResourceError
from src.utils.config import get_config_value
from src.ui.text import get_terminal_width

# Set up logger
logger = get_logger(__name__)

# Display warning for missing psutil
if not HAS_PSUTIL:
    logger.warning("psutil package not installed - system monitoring capabilities will be limited")

# Constants for the module
DEFAULT_CACHE_TTL = 60  # Default cache TTL in seconds
WARNING_THRESHOLDS = {
    "cpu": 70,  # CPU usage percentage warning
    "cpu_critical": 90,  # CPU usage percentage critical
    "ram": 80,  # RAM usage percentage warning
    "ram_critical": 95,  # RAM usage percentage critical
    "disk": 85,  # Disk usage percentage warning
    "disk_critical": 95,  # Disk usage percentage critical
    "temp": 70,  # Temperature warning in °C
    "temp_critical": 85,  # Temperature critical in °C
}

# Define cache for system metrics
_metrics_cache = {}
_cache_timestamps = {}
_cache_ttl = {}
_cache_lock = threading.RLock()
_update_thread = None
_stop_event = threading.Event()
_update_interval = 60  # Default update interval in seconds

# Platform constants
PLATFORM_LINUX = 'linux'
PLATFORM_MACOS = 'darwin'
PLATFORM_WINDOWS = 'windows'
PLATFORM_UNKNOWN = 'unknown'

# Current platform (set by _detect_platform)
_current_platform = None

# Rick-themed commentary for different system states
SYSTEM_COMMENTARY = {
    "cpu_normal": [
        "CPU's hardly breaking a *burp* sweat. Boring.",
        "CPU usage is lower than Jerry's IQ, which isn't saying much."
    ],
    "cpu_warning": [
        "CPU's starting to work harder than I do, which isn't saying much.",
        "Your CPU is like a Meeseeks that's been alive too long - getting stressed."
    ],
    "cpu_critical": [
        "Holy crap! Your CPU is about to *burp* meltdown faster than a Kronenberg experiment!",
        "Your CPU is more overworked than a Meeseeks at Jerry's golf lesson!"
    ],
    "ram_normal": [
        "RAM usage is fine. Not that I *burp* care.",
        "Memory's functioning better than your own. Low standards, I know."
    ],
    "ram_warning": [
        "Memory's filling up like Rick's flask at a family dinner.",
        "RAM is getting full. Might want to close some of those \"research\" tabs, Morty."
    ],
    "ram_critical": [
        "Your RAM is more stuffed than a Plumbus factory! Everything's gonna crash!",
        "Memory critically low! Even a collective hivemind wouldn't be this inefficient!"
    ],
    "disk_normal": [
        "Disk space is fine. Wubba lubba dub *burp* dub.",
        "Your drive has more free space than my capacity to care."
    ],
    "disk_warning": [
        "Disk getting full. What are you storing, alternate universe backups?",
        "Disk space is like my patience - running out quickly."
    ],
    "disk_critical": [
        "Disk critically full! Even infinite universes don't have enough space for your junk!",
        "Your disk is fuller than a Dimension C-137 Jerry convention! Delete something!"
    ],
    "temp_normal": [
        "Temperature's fine. Unlike my *burp* burning hatred for bureaucracy.",
        "System's running cooler than my relationship with the Galactic Federation."
    ],
    "temp_warning": [
        "System's heating up like my portal gun after a multiverse bender.",
        "Temperature rising. What'd you do, install a Concentrated Dark Matter engine?"
    ],
    "temp_critical": [
        "System's hotter than a supernova! Shut it down before it melts into another dimension!",
        "CRITICAL TEMP! This thing's about to pull a Vindicators 3 and explode!"
    ],
}

def _detect_platform() -> str:
    """
    Detect the current platform/operating system.
    
    Returns:
        str: One of 'linux', 'darwin', 'windows', or 'unknown'
    """
    global _current_platform
    
    try:
        system = platform.system().lower()
        
        if system == 'linux':
            _current_platform = 'linux'
            logger.debug("Detected Linux platform")
        elif system == 'darwin':
            _current_platform = 'darwin'
            logger.debug("Detected macOS (Darwin) platform")
        elif system == 'windows':
            _current_platform = 'windows'
            logger.debug("Detected Windows platform")
        else:
            _current_platform = 'unknown'
            logger.warning(f"Unknown platform detected: {system}")
            
        # Add more detailed platform info for debugging
        logger.debug(f"Platform details: {platform.platform()}")
        return _current_platform
    except Exception as e:
        logger.error(f"Error detecting platform: {str(e)}")
        _current_platform = 'unknown'
        return _current_platform


def get_platform() -> str:
    """
    Get the current platform/operating system.
    If platform hasn't been detected yet, detect it.
    
    Returns:
        str: One of 'linux', 'darwin', 'windows', or 'unknown'
    """
    global _current_platform
    
    if _current_platform is None:
        return _detect_platform()
    return _current_platform


# System monitoring functions
@safe_execute(default_return={
    "usage": None, 
    "state": "unknown",
    "message": "Error retrieving CPU information. Something went wrong."
})
def get_cpu_usage() -> Dict[str, Any]:
    """
    Get current CPU usage percentage with Rick-styled commentary.
    
    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - usage (float): CPU usage percentage (0-100) or None if unavailable
            - state (str): One of 'normal', 'warning', 'critical', or 'unknown'
            - message (str): Rick-styled commentary on the CPU state
    """
    if not HAS_PSUTIL:
        logger.debug("psutil not available for CPU monitoring")
        return {
            "usage": None, 
            "state": "unknown",
            "message": "CPU monitoring unavailable. Even a *burp* genius like me needs tools."
        }

    try:
        # Platform-specific monitoring (all using psutil but with different fallbacks)
        platform_type = get_platform()
        
        if platform_type == 'linux':
            usage = _get_linux_cpu_usage()
        elif platform_type == 'darwin':
            usage = _get_macos_cpu_usage()
        elif platform_type == 'windows':
            usage = _get_windows_cpu_usage()
        else:
            # Generic fallback using psutil
            usage = psutil.cpu_percent(interval=0.1)
            
        # Determine state based on thresholds
        if usage is None:
            state = "unknown"
            message = "CPU status unknown. Multiverse interference probably."
        elif usage >= WARNING_THRESHOLDS["cpu_critical"]:
            state = "critical"
            import random
            message = random.choice(SYSTEM_COMMENTARY["cpu_critical"])
        elif usage >= WARNING_THRESHOLDS["cpu"]:
            state = "warning"
            import random
            message = random.choice(SYSTEM_COMMENTARY["cpu_warning"])
        else:
            state = "normal"
            import random
            message = random.choice(SYSTEM_COMMENTARY["cpu_normal"])
            
        return {
            "usage": usage,
            "state": state,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error getting CPU usage: {str(e)}")
        return {
            "usage": None,
            "state": "error",
            "message": f"Error getting CPU usage. What did you *burp* break now?"
        }


@safe_execute(default_return=None)
def _get_linux_cpu_usage() -> Optional[float]:
    """
    Get CPU usage on Linux systems.
    
    Returns:
        Optional[float]: CPU usage percentage (0-100) or None if unavailable
    """
    return psutil.cpu_percent(interval=0.1)


@safe_execute(default_return=None)
def _get_macos_cpu_usage() -> Optional[float]:
    """
    Get CPU usage on macOS systems.
    
    Returns:
        Optional[float]: CPU usage percentage (0-100) or None if unavailable
    """
    return psutil.cpu_percent(interval=0.1)


@safe_execute(default_return=None)
def _get_windows_cpu_usage() -> Optional[float]:
    """
    Get CPU usage on Windows systems.
    
    Returns:
        Optional[float]: CPU usage percentage (0-100) or None if unavailable
    """
    return psutil.cpu_percent(interval=0.1)


@safe_execute(default_return={
    "percent": None,
    "total": None,
    "used": None,
    "free": None,
    "state": "unknown",
    "message": "Error retrieving memory information."
})
def get_ram_info() -> Dict[str, Any]:
    """
    Get RAM usage information with Rick-styled commentary.
    
    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - total (int): Total RAM in MB or None if unavailable
            - used (int): Used RAM in MB or None if unavailable
            - percent (float): Percentage of RAM used (0-100) or None if unavailable
            - state (str): One of 'normal', 'warning', 'critical', or 'unknown'
            - message (str): Rick-styled commentary on the RAM state
    """
    if not HAS_PSUTIL:
        logger.debug("psutil not available for RAM monitoring")
        return {
            "total": None,
            "used": None,
            "percent": None,
            "state": "unknown",
            "message": "RAM monitoring unavailable. What, you expect me to count bytes manually?"
        }
    
    try:
        # Get memory info - psutil handles this similarly across platforms
        memory = psutil.virtual_memory()
        
        # Convert to MB for easier reading
        total_mb = memory.total // (1024 * 1024)
        used_mb = memory.used // (1024 * 1024)
        percent = memory.percent
        
        # Determine state based on thresholds
        if percent >= WARNING_THRESHOLDS["ram_critical"]:
            state = "critical"
            import random
            message = random.choice(SYSTEM_COMMENTARY["ram_critical"])
        elif percent >= WARNING_THRESHOLDS["ram"]:
            state = "warning"
            import random
            message = random.choice(SYSTEM_COMMENTARY["ram_warning"])
        else:
            state = "normal"
            import random
            message = random.choice(SYSTEM_COMMENTARY["ram_normal"])
        
        return {
            "total": total_mb,
            "used": used_mb,
            "percent": percent,
            "state": state,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error getting RAM info: {str(e)}")
        return {
            "total": None,
            "used": None,
            "percent": None,
            "state": "error",
            "message": f"Error getting RAM info. Your *burp* memory's as reliable as Jerry."
        }


@safe_execute(default_return={
    "available": False,
    "temperature": None,
    "state": "unknown",
    "message": "Error retrieving temperature information."
})
def get_cpu_temperature() -> Dict[str, Any]:
    """
    Get CPU temperature with Rick-styled commentary.
    Not all systems support temperature monitoring.
    
    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - available (bool): Whether temperature monitoring is available
            - temperature (float): CPU temperature in Celsius or None if unavailable
            - state (str): One of 'normal', 'warning', 'critical', or 'unknown'
            - message (str): Rick-styled commentary on the temperature
    """
    platform_type = get_platform()
    temperature = None
    available = False
    
    try:
        # Use platform-specific methods to get temperature
        if platform_type == 'linux':
            temperature = _get_linux_temperature()
            available = temperature is not None
        elif platform_type == 'darwin':
            temperature = _get_macos_temperature()
            available = temperature is not None
        elif platform_type == 'windows':
            temperature = _get_windows_temperature()
            available = temperature is not None
        
        # Handle unavailable temperature data
        if not available or temperature is None:
            return {
                "available": False,
                "temperature": None,
                "state": "unknown",
                "message": "Temperature sensing unavailable. What, you think I have thermal vision?"
            }
        
        # Determine state based on thresholds
        if temperature >= WARNING_THRESHOLDS["temp_critical"]:
            state = "critical"
            import random
            message = random.choice(SYSTEM_COMMENTARY["temp_critical"])
        elif temperature >= WARNING_THRESHOLDS["temp"]:
            state = "warning"
            import random
            message = random.choice(SYSTEM_COMMENTARY["temp_warning"])
        else:
            state = "normal"
            import random
            message = random.choice(SYSTEM_COMMENTARY["temp_normal"])
        
        return {
            "available": available,
            "temperature": temperature,
            "state": state,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error getting CPU temperature: {str(e)}")
        return {
            "available": False,
            "temperature": None,
            "state": "error",
            "message": "Error reading temperature. What did you do, stick a *burp* thermometer in the CPU?"
        }


@safe_execute(default_return=None)
def _get_linux_temperature() -> Optional[float]:
    """
    Get CPU temperature on Linux systems.
    
    Returns:
        Optional[float]: CPU temperature in Celsius or None if unavailable
    """
    if not HAS_PSUTIL:
        return None
    
    try:
        # Try psutil first
        temperatures = psutil.sensors_temperatures()
        if not temperatures:
            # Fallback to reading from sysfs
            for thermal_zone in range(10):  # Check first 10 thermal zones
                path = f"/sys/class/thermal/thermal_zone{thermal_zone}/temp"
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        # Value is in millidegrees Celsius
                        return int(f.read().strip()) / 1000
            return None
        
        # Process psutil temperatures
        for name, entries in temperatures.items():
            # Common CPU temperature sources
            if name.lower() in ['coretemp', 'k10temp', 'cpu_thermal']:
                if entries:
                    # Average across cores if multiple readings
                    temps = [entry.current for entry in entries if hasattr(entry, 'current')]
                    if temps:
                        return sum(temps) / len(temps)
        
        # If we couldn't find a specific CPU temp source but have other sensors
        for name, entries in temperatures.items():
            if entries:
                # Just take the first available temperature
                return entries[0].current if hasattr(entries[0], 'current') else None
                
        return None
    except Exception as e:
        logger.error(f"Error getting Linux temperature: {str(e)}")
        return None


@safe_execute(default_return=None)
def _get_macos_temperature() -> Optional[float]:
    """
    Get CPU temperature on macOS systems.
    
    Returns:
        Optional[float]: CPU temperature in Celsius or None if unavailable
    """
    if not HAS_PSUTIL:
        return None
    
    try:
        # Unfortunately, psutil doesn't support temperature on macOS
        # Try using the osx-cpu-temp utility if it's installed
        import subprocess
        try:
            # Check if osx-cpu-temp is available
            result = subprocess.run(['which', 'osx-cpu-temp'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    timeout=1,
                                    check=False)
            
            if result.returncode == 0:
                # Run osx-cpu-temp to get temperature
                temp_result = subprocess.run(['osx-cpu-temp'], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            timeout=1,
                                            check=False)
                
                if temp_result.returncode == 0:
                    # Extract temperature value
                    output = temp_result.stdout.decode('utf-8').strip()
                    # Output format is typically "CPU: 54.2°C"
                    if '°C' in output:
                        temp_str = output.split('°C')[0].split(':')[-1].strip()
                        return float(temp_str)
        except (subprocess.SubprocessError, ValueError, IndexError) as e:
            logger.debug(f"Failed to get macOS temperature using osx-cpu-temp: {str(e)}")
        
        # If osx-cpu-temp fails, try using SMC utility if it's available
        try:
            result = subprocess.run(['which', 'smc'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    timeout=1,
                                    check=False)
            
            if result.returncode == 0:
                # Run SMC to get CPU die temperature (TC0D or similar)
                temp_result = subprocess.run(['smc', '-k', 'TC0D', '-r'], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            timeout=1,
                                            check=False)
                
                if temp_result.returncode == 0:
                    # Extract temperature value
                    output = temp_result.stdout.decode('utf-8').strip()
                    # Parse the output format which varies by SMC version
                    if '(' in output and ')' in output:
                        # Newer format: "TC0D: 45.8 C (ok)"
                        temp_str = output.split('(')[0].split(':')[1].strip().split()[0]
                        return float(temp_str)
        except (subprocess.SubprocessError, ValueError, IndexError) as e:
            logger.debug(f"Failed to get macOS temperature using SMC: {str(e)}")
            
        logger.debug("No temperature utilities available on macOS")
        return None
    except Exception as e:
        logger.error(f"Error getting macOS temperature: {str(e)}")
        return None


@safe_execute(default_return=None)
def _get_windows_temperature() -> Optional[float]:
    """
    Get CPU temperature on Windows systems using WMI.
    
    Returns:
        Optional[float]: CPU temperature in Celsius or None if unavailable
    """
    if not HAS_PSUTIL:
        return None
    
    try:
        # Use psutil if it supports temperatures on Windows
        if hasattr(psutil, 'sensors_temperatures'):
            temperatures = psutil.sensors_temperatures()
            if temperatures:
                for name, entries in temperatures.items():
                    if entries:
                        # Average across cores if multiple readings
                        temps = [entry.current for entry in entries if hasattr(entry, 'current')]
                        if temps:
                            return sum(temps) / len(temps)
        
        # Try using WMI as a fallback for Windows
        try:
            import wmi # type: ignore
            w = wmi.WMI(namespace=r"root\wmi")  # Use raw string for namespace path
            temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
            # Convert from tenths of Kelvin to Celsius
            temp_kelvin = getattr(temperature_info, 'CurrentTemperature', 0) / 10
            return temp_kelvin - 273.15  # Kelvin to Celsius
        except ImportError:
            logger.debug("WMI module not available for Windows temperature monitoring")
        except Exception as e:
            logger.debug(f"Failed to get Windows temperature using WMI: {str(e)}")
        
        # If all else fails, return None
        logger.debug("No temperature monitoring available on Windows")
        return None
    except Exception as e:
        logger.error(f"Error getting Windows temperature: {str(e)}")
        return None


@safe_execute(default_return={
    "percent": None,
    "total": None,
    "used": None,
    "free": None,
    "path": None,
    "state": "unknown",
    "message": "Error retrieving disk information."
})
def get_disk_usage(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get disk usage information for the specified path with Rick-styled commentary.
    
    Args:
        path: Path to check disk usage (default: current directory)
        
    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - percent (float): Disk usage percentage (0-100) or None if unavailable
            - total (float): Total disk space in GB or None if unavailable
            - used (float): Used disk space in GB or None if unavailable
            - free (float): Free disk space in GB or None if unavailable
            - path (str): Path that was checked
            - state (str): One of 'normal', 'warning', 'critical', or 'unknown'
            - message (str): Rick-styled commentary on the disk state
    """
    # Use current directory if no path specified
    if path is None:
        path = os.getcwd()
    
    if not HAS_PSUTIL:
        logger.debug(f"psutil not available for disk monitoring: {path}")
        return {
            "total": None,
            "used": None,
            "free": None,
            "percent": None,
            "path": path,
            "state": "unknown",
            "message": "Disk monitoring unavailable. What am I, your personal *burp* storage manager?"
        }
    
    try:
        # Get disk usage statistics
        disk = psutil.disk_usage(path)
        
        # Convert to GB for easier reading
        total_gb = disk.total / (1024 * 1024 * 1024)
        used_gb = disk.used / (1024 * 1024 * 1024)
        free_gb = disk.free / (1024 * 1024 * 1024)
        percent = disk.percent
        
        # Format path for display
        display_path = path
        # If path is home directory, show ~ instead
        home = os.path.expanduser("~")
        if path.startswith(home):
            display_path = "~" + path[len(home):]
        
        # Determine state based on thresholds
        if percent >= WARNING_THRESHOLDS["disk_critical"]:
            state = "critical"
            import random
            message = random.choice(SYSTEM_COMMENTARY["disk_critical"])
        elif percent >= WARNING_THRESHOLDS["disk"]:
            state = "warning"
            import random
            message = random.choice(SYSTEM_COMMENTARY["disk_warning"])
        else:
            state = "normal"
            import random
            message = random.choice(SYSTEM_COMMENTARY["disk_normal"])
        
        return {
            "total": round(total_gb, 2),
            "used": round(used_gb, 2),
            "free": round(free_gb, 2),
            "percent": percent,
            "path": display_path,
            "state": state,
            "message": message
        }
    except PermissionError:
        logger.error(f"Permission denied accessing disk information for: {path}")
        return {
            "total": None,
            "used": None,
            "free": None,
            "percent": None,
            "path": path,
            "state": "error",
            "message": f"Permission denied checking {path}. What, you think you're *burp* special?"
        }
    except FileNotFoundError:
        logger.error(f"Path not found for disk check: {path}")
        return {
            "total": None,
            "used": None,
            "free": None,
            "percent": None,
            "path": path,
            "state": "error",
            "message": f"Path {path} doesn't exist, genius. Try looking somewhere in this *burp* dimension."
        }
    except Exception as e:
        logger.error(f"Error getting disk usage for {path}: {str(e)}")
        return {
            "total": None,
            "used": None,
            "free": None,
            "percent": None,
            "path": path,
            "state": "error",
            "message": f"Error checking disk for {path}. Your filesystem is more messed up than the Cronenberg dimension."
        }


@safe_execute(default_return={
    "uptime_seconds": None,
    "formatted": "Unknown",
    "message": "Error retrieving system uptime."
})
def get_system_uptime() -> Dict[str, Any]:
    """
    Get system uptime information with Rick-styled commentary.
    
    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - uptime_seconds (float): System uptime in seconds or None if unavailable
            - formatted (str): Human-readable uptime string
            - message (str): Rick-styled commentary on the uptime
    """
    if not HAS_PSUTIL:
        logger.debug("psutil not available for uptime monitoring")
        return {
            "uptime_seconds": None,
            "formatted": "Unknown",
            "message": "Uptime monitoring unavailable. What, you can't just look at a *burp* clock?",
            "boot_time": None
        }
    
    try:
        # Get boot time and calculate uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        # Format boot time
        boot_datetime = datetime.fromtimestamp(boot_time)
        formatted_boot_time = boot_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format uptime in a human-readable way
        formatted_uptime = _format_uptime(uptime_seconds)
        
        # Generate Rick-styled commentary based on uptime
        message = _get_uptime_commentary(uptime_seconds)
        
        return {
            "uptime_seconds": int(uptime_seconds),
            "formatted": formatted_uptime,
            "message": message,
            "boot_time": formatted_boot_time
        }
    except Exception as e:
        logger.error(f"Error getting system uptime: {str(e)}")
        return {
            "uptime_seconds": None,
            "formatted": None,
            "message": "Error getting uptime. Time is just a *burp* construct anyway.",
            "boot_time": None
        }


def _format_uptime(seconds: float) -> str:
    """Format uptime seconds into a human-readable string."""
    try:
        # Calculate days, hours, minutes, seconds
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Build the formatted string
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0 or days > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        # Join with commas and 'and' for the last part
        if len(parts) > 1:
            formatted = ", ".join(parts[:-1]) + " and " + parts[-1]
        else:
            formatted = parts[0]
            
        return formatted
    except Exception as e:
        logger.error(f"Error formatting uptime: {str(e)}")
        return f"{int(seconds)} seconds"


def _get_uptime_commentary(seconds: float) -> str:
    """Generate Rick-styled commentary based on system uptime."""
    try:
        days = seconds / 86400  # Convert to days
        
        if days < 0.01:  # Less than ~15 minutes
            return "Just booted? What, did you *burp* break something again?"
        elif days < 0.1:  # Less than ~2.4 hours
            return "System barely started. At least give it time to *burp* disappoint you properly."
        elif days < 1:
            return "Less than a day uptime? What are you, some kind of reboot enthusiast?"
        elif days < 7:
            return "About as stable as my portal gun after a *burp* bender. Not bad."
        elif days < 30:
            return "Weeks without crashing? Your system's more stable than my sobriety. Low bar."
        elif days < 90:
            return "Months of uptime? *burp* Either your system is great or you never install updates."
        elif days < 365:
            return "This thing's been running longer than most of my *burp* marriages last."
        else:
            return "Over a year uptime? You've got a better uptime than my will to *burp* live. Impressive."
    except Exception as e:
        logger.error(f"Error generating uptime commentary: {str(e)}")
        return "Time is relative. Einstein said that. Or was it me? *burp* Whatever."


# Caching system implementation
def initialize_cache() -> None:
    """
    Initialize the metrics cache system.
    """
    global _metrics_cache
    
    logger.debug("Initializing system metrics cache")
    with _cache_lock:
        _metrics_cache = {}


@safe_execute(default_return=False)
def cache_metric(name: str, value: Any, ttl: int = None) -> None:
    """
    Cache a system metric with optional TTL (time to live).
    
    Args:
        name: Name/key of the metric to cache
        value: Value to cache
        ttl: Time-to-live in seconds (default: use system default)
    
    Returns:
        bool: True if successful, False on error
    """
    global _metrics_cache
    
    if ttl is None:
        ttl = get_config_value("system.cache_ttl", DEFAULT_CACHE_TTL)
    
    with _cache_lock:
        _metrics_cache[name] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
        
    logger.debug(f"Cached metric '{name}' with TTL {ttl}s")


@safe_execute(default_return=None)
def get_cached_metric(name: str, default: Any = None) -> Any:
    """
    Get a cached metric value or default if not found/expired.
    
    Args:
        name: Name/key of the metric to retrieve
        default: Default value if metric not found
        
    Returns:
        Any: The cached value or the default
    """
    global _metrics_cache
    
    with _cache_lock:
        # Check if metric exists in cache
        if name not in _metrics_cache:
            return default
        
        # Get cached entry
        entry = _metrics_cache[name]
        
        # Check if cache is stale
        if is_cache_stale(name):
            logger.debug(f"Cached metric '{name}' is stale")
            return default
        
        return entry["value"]


@safe_execute(default_return=True)
def is_cache_stale(metric_name: str) -> bool:
    """
    Check if a cached metric is stale (expired or not found).
    
    Args:
        metric_name: Name of the metric to check
        
    Returns:
        bool: True if stale or not found, False if fresh
    """
    global _metrics_cache
    
    with _cache_lock:
        # Check if metric exists
        if metric_name not in _metrics_cache:
            return True
        
        entry = _metrics_cache[metric_name]
        current_time = time.time()
        age = current_time - entry["timestamp"]
        
        # Check if older than TTL
        return age > entry["ttl"]


@safe_execute(default_return=False)
def refresh_background_metrics() -> None:
    """
    Refresh all background metrics.
    This is called by the background updater thread.
    
    Returns:
        bool: True if successful, False on error
    """
    logger.debug("Refreshing all background metrics")
    
    try:
        # Update CPU usage
        cpu_info = get_cpu_usage()
        cache_metric("cpu_usage", cpu_info)
        
        # Update RAM info
        ram_info = get_ram_info()
        cache_metric("ram_info", ram_info)
        
        # Update temperature (if available)
        temp_info = get_cpu_temperature()
        cache_metric("cpu_temperature", temp_info)
        
        # Update disk usage for current directory
        disk_info = get_disk_usage()
        cache_metric("disk_usage", disk_info)
        
        # Update uptime
        uptime_info = get_system_uptime()
        cache_metric("system_uptime", uptime_info)
        
        # Update network info
        network_info = get_network_info()
        cache_metric("network_info", network_info)
        
        # Update CPU governor
        governor_info = get_cpu_governor()
        cache_metric("cpu_governor", governor_info)
        
        # Update battery info
        battery_info = get_battery_info()
        cache_metric("battery_info", battery_info)
        
        # Update process info
        process_info = get_process_info()
        cache_metric("process_info", process_info)
        
        logger.debug("Background metrics refresh complete")
        return True
    except Exception as e:
        logger.error(f"Error refreshing background metrics: {str(e)}")
        return False


def _background_updater() -> None:
    """
    Background thread function to update metrics periodically.
    """
    global _stop_event, _update_interval
    
    logger.info("Background metrics updater started")
    
    while not _stop_event.is_set():
        try:
            # Refresh all metrics
            refresh_background_metrics()
            
            # Wait for the next update interval or until stopped
            _stop_event.wait(timeout=_update_interval)
        except Exception as e:
            logger.error(f"Error in background updater: {str(e)}")
            # Still wait before retry to avoid thrashing
            _stop_event.wait(timeout=5)


@safe_execute(default_return=False)
def start_background_updater() -> bool:
    """
    Start the background metrics updater thread.
    
    Returns:
        bool: True if successfully started, False otherwise
    """
    global _update_thread, _stop_event
    
    # Don't start if already running
    if _update_thread is not None and _update_thread.is_alive():
        logger.debug("Background updater already running")
        return True
    
    try:
        # Clear stop flag
        _stop_event.clear()
        
        # Create and start thread
        _update_thread = threading.Thread(
            target=_background_updater,
            name="MetricsUpdater",
            daemon=True  # Make daemon so it doesn't block program exit
        )
        _update_thread.start()
        
        logger.info("Started background metrics updater")
        return True
    except Exception as e:
        logger.error(f"Failed to start background updater: {str(e)}")
        return False


@safe_execute(default_return=False)
def stop_background_updater() -> bool:
    """
    Stop the background metrics updater thread.
    
    Returns:
        bool: True if successfully stopped, False otherwise
    """
    global _update_thread, _stop_event
    
    # Nothing to stop if not running
    if _update_thread is None or not _update_thread.is_alive():
        logger.debug("No background updater running")
        return True
    
    try:
        # Signal thread to stop
        _stop_event.set()
        
        # Wait for thread to terminate (with timeout)
        _update_thread.join(timeout=2.0)
        
        # Check if thread is still alive after timeout
        if _update_thread.is_alive():
            logger.warning("Background updater thread did not stop gracefully")
            return False
        
        logger.info("Stopped background metrics updater")
        return True
    except Exception as e:
        logger.error(f"Error stopping background updater: {str(e)}")
        return False


@safe_execute(default_return=False)
def set_update_interval(seconds: int) -> None:
    """
    Set the update interval for background metrics.
    
    Args:
        seconds: Update interval in seconds
        
    Returns:
        bool: True if successful, False on error
    """
    global _update_interval
    
    # Validate input
    if seconds < 1:
        seconds = 1
        logger.warning(f"Update interval too low, setting to minimum (1s)")
    elif seconds > 3600:
        seconds = 3600
        logger.warning(f"Update interval too high, setting to maximum (3600s)")
    
    _update_interval = seconds
    logger.info(f"Set metrics update interval to {seconds}s")


@safe_execute(default_return={
    "value": None,
    "unit": "",
    "state": "unknown",
    "message": "Error formatting metric."
})
def format_metric(value: Any, unit: str, warning_threshold: float, critical_threshold: float = None) -> Dict[str, Any]:
    """
    Format a metric value with thresholds and status.
    
    Args:
        value: The value to format
        unit: Unit string (e.g., "%", "°C")
        warning_threshold: Threshold for warning state
        critical_threshold: Threshold for critical state
        
    Returns:
        Dict[str, Any]: A dictionary with formatting information
    """
    if value is None:
        return {
            "value": "N/A",
            "state": "unknown",
            "formatted": "N/A"
        }
    
    # Set default critical threshold if not provided
    if critical_threshold is None:
        critical_threshold = warning_threshold * 1.5
    
    # Determine state based on thresholds
    if value >= critical_threshold:
        state = "critical"
    elif value >= warning_threshold:
        state = "warning"
    else:
        state = "normal"
    
    # Format the value with unit
    formatted = f"{value}{unit}"
    
    return {
        "value": value,
        "state": state,
        "formatted": formatted
    }


@safe_execute(default_return={
    "cpu": {"state": "unknown", "message": "Error retrieving CPU metrics"},
    "ram": {"state": "unknown", "message": "Error retrieving memory metrics"},
    "temperature": {"state": "unknown", "message": "Error retrieving temperature metrics"},
    "disk": {"state": "unknown", "message": "Error retrieving disk metrics"},
    "uptime": {"state": "unknown", "message": "Error retrieving uptime metrics"},
    "network": {"state": "unknown", "message": "Error retrieving network metrics"},
    "governor": {"state": "unknown", "message": "Error retrieving CPU governor"},
    "battery": {"state": "unknown", "message": "Error retrieving battery metrics"},
    "processes": {"state": "unknown", "message": "Error retrieving process metrics"},
    "timestamp": time.time()
})
def format_all_metrics() -> Dict[str, Any]:
    """
    Format all system metrics for display.
    
    Returns:
        Dict[str, Any]: A dictionary with all system metrics
    """
    # Get metrics, preferring cached values
    try:
        cpu_info = get_cached_metric("cpu_usage", get_cpu_usage())
        ram_info = get_cached_metric("ram_info", get_ram_info())
        temp_info = get_cached_metric("cpu_temperature", get_cpu_temperature())
        disk_info = get_cached_metric("disk_usage", get_disk_usage())
        uptime_info = get_cached_metric("system_uptime", get_system_uptime())
        network_info = get_cached_metric("network_info", get_network_info())
        governor_info = get_cached_metric("cpu_governor", get_cpu_governor())
        battery_info = get_cached_metric("battery_info", get_battery_info())
        process_info = get_cached_metric("process_info", get_process_info())
        
        return {
            "cpu": cpu_info,
            "ram": ram_info,
            "temperature": temp_info,
            "disk": disk_info,
            "uptime": uptime_info,
            "network": network_info,
            "governor": governor_info,
            "battery": battery_info,
            "processes": process_info,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error formatting metrics: {str(e)}")
        return {
            "cpu": {"state": "error", "message": "Error retrieving CPU information"},
            "ram": {"state": "error", "message": "Error retrieving RAM information"},
            "temperature": {"state": "error", "message": "Error retrieving temperature information"},
            "disk": {"state": "error", "message": "Error retrieving disk information"},
            "uptime": {"state": "error", "message": "Error retrieving uptime information"},
            "network": {"state": "error", "message": "Error retrieving network information"},
            "governor": {"state": "error", "message": "Error retrieving CPU governor"},
            "battery": {"state": "error", "message": "Error retrieving battery information"},
            "processes": {"state": "error", "message": "Error retrieving process information"},
            "timestamp": time.time()
        }


@safe_execute(default_return={})
def get_cpu_governor() -> Dict[str, Any]:
    """
    Get the current CPU governor/power management mode.
    
    On Linux, detects the scaling governor from /sys/devices/system/cpu/
    On macOS and Windows, provides basic power management detection.
    
    Returns:
        Dict containing:
            - 'governor': Governor name (e.g., 'performance', 'powersave')
            - 'governors': List of all available governors (Linux only)
            - 'available': Whether governor detection is supported
            - 'per_cpu': Dict of per-CPU governors if they differ (Linux only)
            - 'message': Rick-styled comment about the governor
    """
    # Get the platform
    platform = get_platform()
    
    # Default return structure
    result = {
        'governor': 'unknown',
        'governors': [],
        'available': False,
        'per_cpu': {},
        'message': "I can't see the CPU governor. What, you expect me to be psychic now?"
    }
    
    if platform == 'linux':
        return _get_linux_cpu_governor()
    elif platform == 'darwin':
        return _get_macos_cpu_governor()
    elif platform == 'windows':
        return _get_windows_cpu_governor()
    else:
        result['message'] = "Unknown platform. Can't determine CPU governor. It's probably terrible though."
        return result

def _get_linux_cpu_governor() -> Dict[str, Any]:
    """
    Get the CPU governor information on Linux systems.
    
    Returns:
        Dict containing governor information
    """
    result = {
        'governor': 'unknown',
        'governors': [],
        'available': False,
        'per_cpu': {},
        'message': "Couldn't read CPU governor. You're probably better off not knowing."
    }
    
    try:
        # First check if the cpufreq system exists
        cpufreq_path = "/sys/devices/system/cpu/cpu0/cpufreq"
        if not os.path.exists(cpufreq_path):
            result['message'] = "This Linux system doesn't support CPU frequency scaling. *burp* What a primitive setup."
            return result
            
        # Check for available governors
        available_path = os.path.join(cpufreq_path, "scaling_available_governors")
        if os.path.exists(available_path):
            with open(available_path, 'r') as f:
                governors = f.read().strip().split()
                result['governors'] = governors
                result['available'] = True
        
        # Check each CPU's governor
        cpu_count = os.cpu_count() or 1
        governors = []
        
        for cpu in range(cpu_count):
            governor_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"
            
            if os.path.exists(governor_path):
                with open(governor_path, 'r') as f:
                    governor = f.read().strip()
                    result['per_cpu'][f'cpu{cpu}'] = governor
                    governors.append(governor)
        
        # Determine the primary governor (most common)
        if governors:
            # Use the most common governor as the main one
            from collections import Counter
            counter = Counter(governors)
            result['governor'] = counter.most_common(1)[0][0]
            
            # Create a message based on the governor
            if result['governor'] == 'performance':
                result['message'] = "Running in performance mode. *burp* At least you're not skimping on power."
            elif result['governor'] == 'powersave':
                result['message'] = "Powersave mode? What, is your electricity bill more important than performance?"
            elif result['governor'] == 'ondemand':
                result['message'] = "Ondemand governor. Not committed to performance or efficiency. Typical fence-sitter."
            elif result['governor'] == 'conservative':
                result['message'] = "Conservative governor. Slow to react, just like your brain."
            elif result['governor'] == 'schedutil':
                result['message'] = "Using schedutil governor. At least the scheduler knows what it's doing, unlike you."
            else:
                result['message'] = f"Using {result['governor']} governor. Never heard of it. Must be something you broke."
    
    except Exception as e:
        logger.error(f"Error getting Linux CPU governor: {str(e)}")
        result['message'] = "Failed to get CPU governor. Probably another Linux quirk. *burp*"
    
    return result

def _get_macos_cpu_governor() -> Dict[str, Any]:
    """
    Get the CPU governor information on macOS systems.
    
    Note: macOS doesn't expose governors in the same way as Linux,
    but we can determine power management status.
    
    Returns:
        Dict containing governor information
    """
    result = {
        'governor': 'unknown',
        'governors': ['automatic'],
        'available': False,
        'per_cpu': {},
        'message': "macOS doesn't let you control CPU governors. Apple knows better than you, apparently."
    }
    
    try:
        if not HAS_PSUTIL:
            result['message'] = "Install psutil to get better CPU information on macOS. Even Apple can't help you here."
            return result
            
        # Get the CPU frequency info
        freq = psutil.cpu_freq()
        
        if freq is None:
            result['message'] = "Can't determine CPU frequency on this Mac. Apple's walled garden strikes again."
            return result
            
        # Check if current frequency is close to max (performance) or min (powersave)
        if freq.current and freq.max:
            ratio = freq.current / freq.max
            
            if ratio > 0.8:
                result['governor'] = 'performance'
                result['available'] = True
                result['message'] = "Your Mac is running at high frequency. Burning battery like there's no tomorrow, huh?"
            elif ratio < 0.5:
                result['governor'] = 'powersave'
                result['available'] = True
                result['message'] = "Your Mac is conserving power. What's wrong, can't find your charger?"
            else:
                result['governor'] = 'balanced'
                result['available'] = True
                result['message'] = "Your Mac is balancing performance and power. The bare minimum of competence."
                
            # Fill per_cpu with the same value since we don't have per-core info
            for i in range(psutil.cpu_count(logical=False) or 1):
                result['per_cpu'][f'cpu{i}'] = result['governor']
    
    except Exception as e:
        logger.error(f"Error getting macOS CPU governor: {str(e)}")
        result['message'] = "Failed to determine CPU power state. Blame Apple's secretive nature."
    
    return result

def _get_windows_cpu_governor() -> Dict[str, Any]:
    """
    Get the CPU governor information on Windows systems.
    
    Note: Windows uses power plans rather than governors,
    but we can map these to equivalent Linux governor concepts.
    
    Returns:
        Dict containing governor information
    """
    result = {
        'governor': 'unknown',
        'governors': ['balanced', 'performance', 'powersave'],
        'available': False,
        'per_cpu': {},
        'message': "Windows doesn't have proper CPU governors. Another reason Windows is inferior."
    }
    
    try:
        if not HAS_PSUTIL:
            result['message'] = "Install psutil to get CPU power information on Windows. *burp* Even Bill Gates can't save you now."
            return result
            
        # Try to determine current power plan
        import subprocess
        
        # Get active power scheme using powercfg
        try:
            output = subprocess.check_output(['powercfg', '/getactivescheme'], 
                                          stderr=subprocess.DEVNULL,
                                          universal_newlines=True)
            
            if "Power Scheme GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" in output:
                result['governor'] = 'balanced'
                result['available'] = True
                result['message'] = "Using Balanced power plan. Not terrible, not great. Story of your life."
            elif "Power Scheme GUID: 381b4222-f694-41f0-9685-ff5bb260df2e" in output:
                result['governor'] = 'performance'
                result['available'] = True
                result['message'] = "Using High Performance power plan. *burp* Wasting electricity to compensate for Windows' inefficiency."
            elif "Power Scheme GUID: a1841308-3541-4fab-bc81-f71556f20b4a" in output:
                result['governor'] = 'powersave'
                result['available'] = True
                result['message'] = "Using Power Saver plan. Making your slow computer even slower. Smart move."
            else:
                result['governor'] = 'custom'
                result['available'] = True
                result['message'] = "Using a custom power plan. Thinking you know better than Microsoft? You probably do."
        except:
            # If powercfg doesn't work, fall back to CPU frequency heuristic
            freq = psutil.cpu_freq()
            
            if freq and freq.current and freq.max:
                ratio = freq.current / freq.max
                
                if ratio > 0.8:
                    result['governor'] = 'performance'
                    result['available'] = True
                    result['message'] = "CPU running at high frequency. Windows is hogging your power, as usual."
                elif ratio < 0.5:
                    result['governor'] = 'powersave'
                    result['available'] = True
                    result['message'] = "CPU running at low frequency. Windows is being merciful to your battery for once."
                else:
                    result['governor'] = 'balanced'
                    result['available'] = True
                    result['message'] = "CPU running at moderate frequency. Windows is trying its best, which isn't saying much."
            
        # Fill per_cpu with the same value
        for i in range(psutil.cpu_count(logical=False) or 1):
            result['per_cpu'][f'cpu{i}'] = result['governor']
            
    except Exception as e:
        logger.error(f"Error getting Windows CPU governor: {str(e)}")
        result['message'] = "Failed to determine power plan. Windows being Windows, am I right?"
    
    return result


# Safe module initialization
def initialize_module():
    """Initialize the system module safely."""
    # Initialize the platform detection
    get_platform()
    
    # Initialize the cache
    initialize_cache()
    
    # We don't auto-start the background updater to prevent import issues
    # It should be explicitly called by the application

# Call initialization
initialize_module()

@safe_execute(default_return={
    "available": False,
    "interfaces": {},
    "primary": None,
    "total_sent": None,
    "total_received": None,
    "sent_speed": None,
    "received_speed": None,
    "state": "unknown",
    "message": "Network information unavailable. What, you expect me to be psychic?"
})
def get_network_info() -> Dict[str, Any]:
    """
    Get network usage information including traffic statistics.
    
    Returns:
        Dict containing:
            - 'available': Whether network statistics are available
            - 'interfaces': Dict with per-interface statistics
            - 'primary': Name of the primary interface
            - 'total_sent': Total bytes sent
            - 'total_received': Total bytes received
            - 'sent_speed': Current upload speed in bytes/sec
            - 'received_speed': Current download speed in bytes/sec
            - 'state': Network state ('normal', 'high', 'low', 'unknown')
            - 'message': Rick-styled commentary on network usage
    """
    # Default result structure
    result = {
        "available": False,
        "interfaces": {},
        "primary": None,
        "total_sent": None,
        "total_received": None,
        "sent_speed": None,
        "received_speed": None,
        "state": "unknown",
        "message": "Network information unavailable. What, you expect me to be psychic?"
    }
    
    # Check for psutil availability
    if not HAS_PSUTIL:
        result["message"] = "Install psutil to get network information. Otherwise you're flying blind, *burp* dummy."
        return result
    
    try:
        # Get current counters for all interfaces
        counters = psutil.net_io_counters(pernic=True)
        if not counters:
            result["message"] = "No network interfaces detected. What, are you using two cans and a string?"
            return result
        
        # Get cached previous readings for speed calculation
        prev_counters = get_cached_metric("network_counters", {})
        prev_time = get_cached_metric("network_time", time.time() - 1)  # Default to 1 second ago
        current_time = time.time()
        time_diff = current_time - prev_time
        
        # Avoid division by zero
        if time_diff <= 0:
            time_diff = 1
        
        # Get addresses to find primary interface
        addrs = psutil.net_if_addrs()
        
        # Calculate statistics for each interface
        total_sent = 0
        total_received = 0
        total_sent_speed = 0
        total_received_speed = 0
        active_interfaces = []
        
        for iface, data in counters.items():
            # Skip loopback interface
            if iface.startswith('lo'):
                continue
                
            # Get current values
            sent = data.bytes_sent
            received = data.bytes_recv
            
            # Calculate speeds using cached values
            sent_speed = 0
            received_speed = 0
            
            if iface in prev_counters:
                prev_sent = prev_counters[iface].bytes_sent
                prev_recv = prev_counters[iface].bytes_recv
                
                # Calculate speed (bytes/sec)
                sent_speed = (sent - prev_sent) / time_diff
                received_speed = (received - prev_recv) / time_diff
            
            # Store interface data
            result["interfaces"][iface] = {
                "sent": sent,
                "received": received,
                "sent_speed": sent_speed,
                "received_speed": received_speed,
                "has_ipv4": False,
                "has_ipv6": False
            }
            
            # Check if interface has IPv4/IPv6 addresses
            if iface in addrs:
                for addr in addrs[iface]:
                    if addr.family == socket.AF_INET:  # IPv4
                        result["interfaces"][iface]["has_ipv4"] = True
                        result["interfaces"][iface]["ipv4"] = addr.address
                    elif addr.family == socket.AF_INET6:  # IPv6
                        result["interfaces"][iface]["has_ipv6"] = True
                        result["interfaces"][iface]["ipv6"] = addr.address
            
            # Accumulate totals
            total_sent += sent
            total_received += received
            total_sent_speed += sent_speed
            total_received_speed += received_speed
            
            # Track active interfaces (those with traffic)
            if sent_speed > 0 or received_speed > 0:
                active_interfaces.append(iface)
        
        # Determine primary interface (one with most traffic or first with IP)
        if active_interfaces:
            # Use interface with highest combined speed
            result["primary"] = max(active_interfaces, 
                                   key=lambda i: (result["interfaces"][i]["sent_speed"] + 
                                                 result["interfaces"][i]["received_speed"]))
        else:
            # If no active interfaces, use first one with an IP
            for iface in result["interfaces"]:
                if result["interfaces"][iface].get("has_ipv4", False):
                    result["primary"] = iface
                    break
        
        # Save totals to result
        result["total_sent"] = total_sent
        result["total_received"] = total_received
        result["sent_speed"] = total_sent_speed
        result["received_speed"] = total_received_speed
        result["available"] = True
        
        # Determine state based on speeds
        if total_received_speed > 1048576:  # More than 1 MB/s download
            result["state"] = "high"
            result["message"] = f"Heavy download traffic. Downloading your usual *burp* questionable content?"
        elif total_sent_speed > 1048576:  # More than 1 MB/s upload
            result["state"] = "high"
            result["message"] = f"Heavy upload traffic. Sharing your genius with the world? How noble."
        elif total_received_speed > 0 or total_sent_speed > 0:
            result["state"] = "normal"
            result["message"] = f"Normal network traffic. Nothing exciting, just like your life."
        else:
            result["state"] = "low"
            result["message"] = f"No network activity. What, are you actually working for once?"
        
        # Update cache for next speed calculation
        cache_metric("network_counters", counters)
        cache_metric("network_time", current_time)
        
    except Exception as e:
        logger.error(f"Error getting network information: {str(e)}")
        result["message"] = f"Failed to get network info. Your network is as reliable as Jerry's career."
    
    return result


def format_network_speed(bytes_per_sec: float) -> str:
    """
    Format network speed in appropriate units (B/s, KB/s, MB/s, GB/s).
    
    Args:
        bytes_per_sec: Speed in bytes per second
        
    Returns:
        Formatted string with appropriate units
    """
    if bytes_per_sec < 0:
        return "0 B/s"
    
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec/1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec/(1024*1024):.1f} MB/s"
    else:
        return f"{bytes_per_sec/(1024*1024*1024):.1f} GB/s"


def format_data_size(bytes_val: float) -> str:
    """
    Format data size in appropriate units (B, KB, MB, GB, TB).
    
    Args:
        bytes_val: Size in bytes
        
    Returns:
        Formatted string with appropriate units
    """
    if bytes_val < 0:
        return "0 B"
    
    if bytes_val < 1024:
        return f"{bytes_val:.0f} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val/1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val/(1024*1024):.1f} MB"
    elif bytes_val < 1024 * 1024 * 1024 * 1024:
        return f"{bytes_val/(1024*1024*1024):.1f} GB"
    else:
        return f"{bytes_val/(1024*1024*1024*1024):.1f} TB"


@safe_execute(default_return={
    "available": False,
    "power_plugged": None,
    "percent": None,
    "time_left": None,
    "state": "unknown",
    "message": "Battery information unavailable. Is this a potato you're running?"
})
def get_battery_info() -> Dict[str, Any]:
    """
    Get battery status information including charge and power state.
    
    Returns:
        Dict containing:
            - 'available': Whether battery information is available
            - 'power_plugged': Whether the device is plugged in
            - 'percent': Percentage of battery remaining
            - 'time_left': Estimated time remaining in seconds
            - 'state': Battery state ('full', 'high', 'normal', 'low', 'critical', 'charging', 'unknown')
            - 'message': Rick-styled commentary on battery status
    """
    # Default result structure
    result = {
        "available": False,
        "power_plugged": None,
        "percent": None,
        "time_left": None,
        "state": "unknown",
        "message": "Battery information unavailable. Is this a potato you're running?"
    }
    
    # Check for psutil availability
    if not HAS_PSUTIL:
        result["message"] = "Install psutil to get battery information. What, you expect to power your device with good intentions?"
        return result
    
    try:
        # Get battery information
        battery = psutil.sensors_battery()
        
        # No battery found
        if battery is None:
            result["message"] = "No battery detected. Probably a desktop. How *burp* antiquated."
            return result
        
        # Extract battery information
        result["available"] = True
        result["power_plugged"] = battery.power_plugged
        result["percent"] = battery.percent
        result["time_left"] = battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
        
        # Determine state and message based on charge level and power state
        if battery.power_plugged:
            if battery.percent >= 99:
                result["state"] = "full"
                result["message"] = "Battery fully charged. You can stop hogging that outlet now."
            else:
                result["state"] = "charging"
                result["message"] = f"Battery charging at {battery.percent:.1f}%. The electronic equivalent of stuffing your face."
        else:
            # Not plugged in, determine status based on percentage
            if battery.percent >= 80:
                result["state"] = "high"
                result["message"] = f"Battery at {battery.percent:.1f}%. Still plenty of juice left, unlike your motivation."
            elif battery.percent >= 40:
                result["state"] = "normal"
                result["message"] = f"Battery at {battery.percent:.1f}%. Average, like most of your achievements."
            elif battery.percent >= 15:
                result["state"] = "low"
                result["message"] = f"Battery at {battery.percent:.1f}%. Starting to get nervous yet?"
            else:
                result["state"] = "critical"
                result["message"] = f"Battery critically low at {battery.percent:.1f}%! Plug in or shut up, your choice."
    
    except Exception as e:
        logger.error(f"Error getting battery information: {str(e)}")
        result["message"] = f"Failed to get battery info. Even your battery is trying to hide from you."
    
    return result


def format_battery_time(seconds: int) -> str:
    """
    Format battery time remaining in a human-readable format.
    
    Args:
        seconds: Time remaining in seconds
        
    Returns:
        Formatted time string
    """
    if seconds == psutil.POWER_TIME_UNLIMITED:
        return "unlimited"
    
    if seconds < 0:
        return "calculating..."
    
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"


@safe_execute(default_return={
    "available": False,
    "total": 0,
    "running": 0,
    "sleeping": 0,
    "top_cpu": [],
    "top_memory": [],
    "state": "unknown",
    "message": "Process information unavailable. What, you expect me to spy on your processes?"
})
def get_process_info(num_processes: int = 5) -> Dict[str, Any]:
    """
    Get information about running processes including top CPU and memory users.
    
    Args:
        num_processes: Number of top processes to return
        
    Returns:
        Dict containing:
            - 'available': Whether process information is available
            - 'total': Total number of processes
            - 'running': Number of running processes
            - 'sleeping': Number of sleeping processes
            - 'top_cpu': List of top CPU-consuming processes
            - 'top_memory': List of top memory-consuming processes
            - 'state': Process state ('normal', 'high', 'critical', 'unknown')
            - 'message': Rick-styled commentary on processes
    """
    # Default result structure
    result = {
        "available": False,
        "total": 0,
        "running": 0,
        "sleeping": 0,
        "top_cpu": [],
        "top_memory": [],
        "state": "unknown",
        "message": "Process information unavailable. What, you expect me to spy on your processes?"
    }
    
    # Check for psutil availability
    if not HAS_PSUTIL:
        result["message"] = "Install psutil to get process information. Can't see what's running without eyes, *burp* genius."
        return result
    
    try:
        # Get all process information
        process_list = []
        total_processes = 0
        running_count = 0
        sleeping_count = 0
        
        # Collect information about each process
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent', 'memory_info', 'create_time']):
            try:
                # Get basic process info
                process_info = proc.info
                total_processes += 1
                
                # Count process states
                if process_info['status'] == psutil.STATUS_RUNNING:
                    running_count += 1
                elif process_info['status'] == psutil.STATUS_SLEEPING:
                    sleeping_count += 1
                
                # Skip processes with 0 CPU and very low memory usage to avoid cluttering the list
                if process_info['cpu_percent'] < 0.1 and (process_info['memory_percent'] or 0) < 0.1:
                    continue
                    
                # Add more info for interesting processes
                mem_info = process_info.get('memory_info')
                if mem_info:
                    memory_mb = mem_info.rss / (1024 * 1024)  # Convert to MB
                else:
                    memory_mb = 0
                
                # Get command line if accessible
                try:
                    cmdline = proc.cmdline()
                    command = ' '.join(cmdline) if cmdline else process_info['name']
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    command = process_info['name']
                
                # Get a clean process name (remove path and extensions)
                name = process_info['name']
                if os.path.sep in name:
                    name = os.path.basename(name)
                    
                # Remove common extensions
                for ext in ['.exe', '.app', '.bin', '.sh']:
                    if name.lower().endswith(ext):
                        name = name[:-len(ext)]
                
                # Get process age
                try:
                    if 'create_time' in process_info and process_info['create_time']:
                        age_seconds = time.time() - process_info['create_time']
                        # Format age
                        if age_seconds < 60:
                            age = f"{int(age_seconds)}s"
                        elif age_seconds < 3600:
                            age = f"{int(age_seconds/60)}m"
                        else:
                            age = f"{int(age_seconds/3600)}h"
                    else:
                        age = "?"
                except:
                    age = "?"
                    
                # Add process to list
                process_list.append({
                    'pid': process_info['pid'],
                    'name': name,
                    'full_name': process_info['name'],
                    'command': command,
                    'user': process_info.get('username', ''),
                    'status': process_info.get('status', ''),
                    'cpu': process_info.get('cpu_percent', 0),
                    'memory_percent': process_info.get('memory_percent', 0),
                    'memory_mb': memory_mb,
                    'age': age
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                pass
        
        # Sort processes by CPU and memory usage
        top_cpu = sorted(process_list, key=lambda x: x['cpu'], reverse=True)[:num_processes]
        top_memory = sorted(process_list, key=lambda x: x['memory_mb'], reverse=True)[:num_processes]
        
        # Fill the result
        result['available'] = True
        result['total'] = total_processes
        result['running'] = running_count
        result['sleeping'] = sleeping_count
        result['top_cpu'] = top_cpu
        result['top_memory'] = top_memory
        
        # Determine state and message
        if any(p['cpu'] > 90 for p in top_cpu):
            result['state'] = 'critical'
            high_proc = next(p for p in top_cpu if p['cpu'] > 90)
            result['message'] = f"Process {high_proc['name']} is using {high_proc['cpu']:.1f}% CPU! It's about to melt your pathetic hardware."
        elif any(p['cpu'] > 70 for p in top_cpu):
            result['state'] = 'high'
            high_proc = next(p for p in top_cpu if p['cpu'] > 70)
            result['message'] = f"Process {high_proc['name']} is hogging {high_proc['cpu']:.1f}% CPU. What's it doing, calculating pi?"
        elif any(p['cpu'] > 30 for p in top_cpu):
            result['state'] = 'moderate'
            high_proc = next(p for p in top_cpu if p['cpu'] > 30)
            result['message'] = f"Process {high_proc['name']} is using {high_proc['cpu']:.1f}% CPU. At least something's working hard around here."
        else:
            result['state'] = 'normal'
            if top_cpu:
                result['message'] = f"Running {result['total']} processes. Nothing interesting, just like your personal projects."
            else:
                result['message'] = f"Running {result['total']} processes. Your computer's practically in a *burp* coma."
    
    except Exception as e:
        logger.error(f"Error getting process information: {str(e)}")
        result["message"] = f"Failed to get process info. Even your computer doesn't want to tell you what it's doing."
    
    return result


def format_process_info_for_statusbar(process_info: Dict[str, Any], mode: str = "adaptive", width: Optional[int] = None) -> str:
    """
    Format process information for display in the status bar with adaptive width.
    
    Args:
        process_info: Process information dict from get_process_info()
        mode: Display mode ('adaptive', 'basic', 'detailed', 'top_only', 'off')
        width: Available width (used for adaptive mode)
        
    Returns:
        Formatted process information string
    """
    if not process_info.get("available", False) or mode == "off":
        return ""
    
    # Basic mode just shows the process count
    if mode == "basic":
        return f"📊 PROC:{process_info['total']}"
    
    # Get top CPU process if available
    top_process = process_info.get("top_cpu", [])
    if not top_process:
        return f"📊 PROC:{process_info['total']}"
    
    top = top_process[0]
    
    # Top-only mode shows only the highest CPU process
    if mode == "top_only":
        return f"📊 {top['name']}({top['cpu']:.1f}%)"
    
    # Detailed mode shows multiple processes
    if mode == "detailed":
        # Format multiple processes
        proc_strs = []
        for proc in process_info.get("top_cpu", [])[:3]:  # Show up to 3 processes
            proc_strs.append(f"{proc['name']}({proc['cpu']:.1f}%)")
        
        if proc_strs:
            return f"📊 {','.join(proc_strs)}"
        else:
            return f"📊 PROC:{process_info['total']}"
    
    # Adaptive mode (default)
    if width is None:
        width = get_terminal_width()
    
    # Very narrow terminal
    if width < 50:
        return f"📊 {process_info['total']}"
    
    # Narrow terminal
    if width < 80:
        return f"📊 {top['name']}({top['cpu']:.1f}%)"
    
    # Medium terminal
    if width < 120:
        # Show top 2 processes
        proc_strs = []
        for proc in process_info.get("top_cpu", [])[:2]:
            proc_strs.append(f"{proc['name']}({proc['cpu']:.1f}%)")
        
        if proc_strs:
            return f"📊 {','.join(proc_strs)}"
        else:
            return f"📊 PROC:{process_info['total']}"
    
    # Wide terminal - show both CPU and memory
    top_cpu = process_info.get("top_cpu", [])
    top_mem = process_info.get("top_memory", [])
    
    cpu_str = ""
    mem_str = ""
    
    if top_cpu:
        cpu_procs = []
        for proc in top_cpu[:2]:
            cpu_procs.append(f"{proc['name']}({proc['cpu']:.1f}%)")
        cpu_str = f"CPU:{','.join(cpu_procs)}"
    
    if top_mem:
        top = top_mem[0]
        mem_str = f"MEM:{top['name']}({top['memory_mb']:.0f}MB)"
    
    if cpu_str and mem_str:
        return f"📊 {cpu_str} {mem_str}"
    elif cpu_str:
        return f"📊 {cpu_str}"
    elif mem_str:
        return f"📊 {mem_str}"
    else:
        return f"📊 PROC:{process_info['total']}" 