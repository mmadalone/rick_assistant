#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Temperature Alert System for Rick Assistant.

This module provides temperature monitoring, threshold detection, and alerting capabilities.
It tracks CPU temperature over time and provides notifications when temperatures exceed thresholds.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import threading

# Import internal modules
from src.utils.logger import get_logger
from src.utils.errors import safe_execute, RickAssistantError
from src.utils.config import get_config_value
from src.utils.system import get_cpu_temperature

# Set up logger
logger = get_logger(__name__)

# Default temperature thresholds (°C)
DEFAULT_THRESHOLDS = {
    "warning": 70,    # °C - Warning threshold
    "critical": 80,   # °C - Critical threshold  
    "emergency": 90,  # °C - Emergency threshold
}

# Global variables for temperature tracking
_temperature_history = []
_last_alert_time = {}
_alert_active = {}
_last_check_time = 0
_check_interval = 30  # Seconds between temperature checks
_history_max_size = 60  # Maximum number of temperature readings to keep (1 hour at 1 reading per minute)
_alert_cooldown = 300  # Seconds between repeated alerts of the same level
_monitor_thread = None
_stop_monitor = False

class TemperatureAlert:
    """Temperature alert object with severity and details."""
    
    def __init__(self, temp: float, level: str, timestamp: float = None):
        self.temperature = temp
        self.level = level
        self.timestamp = timestamp or time.time()
        self.acknowledged = False
        
    def __str__(self) -> str:
        time_str = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{time_str}] {self.level.upper()} ALERT: CPU temperature {self.temperature:.1f}°C"

@safe_execute(default_return=None)
def check_temperature_threshold(temp: float) -> Optional[str]:
    """
    Check if a temperature exceeds any thresholds.
    
    Args:
        temp: Current temperature in Celsius
        
    Returns:
        Alert level ('warning', 'critical', 'emergency') or None if no threshold exceeded
    """
    # Get thresholds from config or use defaults
    thresholds = get_temperature_thresholds()
    
    # Check against thresholds (highest to lowest)
    if temp >= thresholds["emergency"]:
        return "emergency"
    elif temp >= thresholds["critical"]:
        return "critical"
    elif temp >= thresholds["warning"]:
        return "warning"
    
    return None

@safe_execute(default_return=DEFAULT_THRESHOLDS)
def get_temperature_thresholds() -> Dict[str, float]:
    """
    Get temperature thresholds from config or use defaults.
    
    Returns:
        Dict with threshold values for different alert levels
    """
    # Try to get thresholds from config
    config_thresholds = get_config_value("system_monitoring.temperature.thresholds", {})
    
    # Start with defaults
    thresholds = DEFAULT_THRESHOLDS.copy()
    
    # Update with config values if they exist
    for level, default in thresholds.items():
        config_value = config_thresholds.get(level)
        if config_value is not None and isinstance(config_value, (int, float)):
            thresholds[level] = float(config_value)
    
    return thresholds

@safe_execute(default_return=[])
def get_temperature_history() -> List[Tuple[float, float]]:
    """
    Get temperature history as list of (timestamp, temperature) tuples.
    
    Returns:
        List of (timestamp, temperature) tuples
    """
    return _temperature_history.copy()

@safe_execute()
def add_temperature_reading(temp: Optional[float] = None, timestamp: Optional[float] = None) -> None:
    """
    Add a temperature reading to the history.
    
    Args:
        temp: Temperature in Celsius, or None to measure now
        timestamp: Optional timestamp, defaults to current time
    """
    global _temperature_history
    
    # Use current time if not specified
    if timestamp is None:
        timestamp = time.time()
    
    # Measure temperature if not provided
    if temp is None:
        temp_info = get_cpu_temperature()
        if not temp_info.get("available", False):
            return
        temp = temp_info.get("temperature")
        if temp is None:
            return
    
    # Add to history
    _temperature_history.append((timestamp, temp))
    
    # Trim history if needed
    if len(_temperature_history) > _history_max_size:
        _temperature_history = _temperature_history[-_history_max_size:]

@safe_execute()
def check_temperature_alert() -> Optional[TemperatureAlert]:
    """
    Check current CPU temperature and create an alert if thresholds are exceeded.
    
    Returns:
        TemperatureAlert if threshold exceeded, None otherwise
    """
    global _last_check_time, _last_alert_time, _alert_active
    
    # Avoid checking too frequently
    current_time = time.time()
    if current_time - _last_check_time < _check_interval:
        return None
    
    _last_check_time = current_time
    
    # Get current temperature
    temp_info = get_cpu_temperature()
    if not temp_info.get("available", False):
        logger.debug("Temperature monitoring not available, skipping check")
        return None
    
    temp = temp_info.get("temperature")
    if temp is None:
        logger.debug("No temperature reading available, skipping check")
        return None
    
    # Add to history
    add_temperature_reading(temp, current_time)
    
    # Check threshold
    alert_level = check_temperature_threshold(temp)
    if not alert_level:
        # No alert needed, clear active alerts
        for level in list(_alert_active.keys()):
            if _alert_active.get(level, False):
                logger.info(f"Temperature returned to normal from {level.upper()} state")
                _alert_active[level] = False
        return None
    
    # Check if we've already alerted for this level recently
    last_alert = _last_alert_time.get(alert_level, 0)
    if (current_time - last_alert < _alert_cooldown and 
        _alert_active.get(alert_level, False)):
        # Skip alert if we've recently alerted for this level
        return None
    
    # Create and return alert
    _last_alert_time[alert_level] = current_time
    _alert_active[alert_level] = True
    
    alert = TemperatureAlert(temp, alert_level, current_time)
    log_temperature_alert(alert)
    
    return alert

@safe_execute()
def log_temperature_alert(alert: TemperatureAlert) -> None:
    """
    Log a temperature alert to the system log.
    
    Args:
        alert: The TemperatureAlert to log
    """
    # Log to appropriate level
    message = f"CPU Temperature Alert: {alert.temperature:.1f}°C ({alert.level.upper()})"
    
    if alert.level == "emergency":
        logger.critical(message)
    elif alert.level == "critical":
        logger.error(message)
    else:  # warning
        logger.warning(message)
    
    # Add more detailed Rick-style message
    if alert.level == "emergency":
        details = "Your CPU is about to melt! SHUT IT DOWN NOW, MORTY!"
    elif alert.level == "critical":
        details = "Your CPU is getting *burp* dangerously hot. Better fix it before it's too late."
    else:  # warning
        details = "Your CPU is heating up. Might want to close some of those useless programs."
    
    logger.info(f"Temperature details: {details}")

@safe_execute()
def get_temperature_status() -> Dict[str, Any]:
    """
    Get the current temperature status including alert state.
    
    Returns:
        Dict with current temperature info and alert status
    """
    # Get current temperature
    temp_info = get_cpu_temperature()
    
    # Default result structure
    result = {
        "available": False,
        "temperature": None,
        "alert_level": None,
        "alert_active": False,
        "alert_time": None,
        "message": "Temperature monitoring not available."
    }
    
    # Update with current temperature info
    if temp_info.get("available", False):
        result["available"] = True
        result["temperature"] = temp_info.get("temperature")
        
        # Check if any alert is active
        for level in ["emergency", "critical", "warning"]:
            if _alert_active.get(level, False):
                result["alert_level"] = level
                result["alert_active"] = True
                result["alert_time"] = _last_alert_time.get(level)
                break
                
        # Add message based on alert state
        if result["alert_active"]:
            if result["alert_level"] == "emergency":
                result["message"] = f"EMERGENCY: CPU temperature critical at {result['temperature']:.1f}°C! Shutdown recommended!"
            elif result["alert_level"] == "critical":
                result["message"] = f"CRITICAL: CPU temperature at {result['temperature']:.1f}°C! Take action immediately!"
            else:  # warning
                result["message"] = f"WARNING: CPU temperature high at {result['temperature']:.1f}°C. Monitor the situation."
        else:
            # Use the message from the temperature info
            result["message"] = temp_info.get("message", "Temperature is within normal range.")
    
    return result

@safe_execute()
def get_temperature_trend() -> str:
    """
    Calculate the temperature trend (rising, falling, stable).
    
    Returns:
        String describing the trend: 'rising', 'falling', 'stable', or 'unknown'
    """
    if len(_temperature_history) < 3:
        return "unknown"
    
    # Get recent readings (last 10 minutes)
    cutoff_time = time.time() - 600  # 10 minutes ago
    recent = [(t, temp) for t, temp in _temperature_history if t >= cutoff_time]
    
    if not recent:
        return "unknown"
    
    # Compare first and last reading
    first_temp = recent[0][1]
    last_temp = recent[-1][1]
    
    # Calculate difference and determine trend
    diff = last_temp - first_temp
    
    if abs(diff) < 2:  # Less than 2°C change is considered stable
        return "stable"
    elif diff > 0:
        return "rising"
    else:
        return "falling"

@safe_execute()
def format_temperature_alert_for_statusbar(temp_info: Dict[str, Any]) -> str:
    """
    Format temperature information for status bar, with alert highlighting.
    
    Args:
        temp_info: Temperature information from get_temperature_status()
        
    Returns:
        Formatted temperature string with alert status
    """
    if not temp_info.get("available", False) or temp_info.get("temperature") is None:
        return ""
    
    # Get temperature and alert info
    temp = temp_info.get("temperature")
    alert_level = temp_info.get("alert_level")
    
    # Get trend if available
    trend = get_temperature_trend()
    trend_indicator = ""
    
    if trend == "rising":
        trend_indicator = "↑"
    elif trend == "falling":
        trend_indicator = "↓"
    elif trend == "stable":
        trend_indicator = "→"
    
    # Format based on alert level
    if alert_level == "emergency":
        return f"🔥 TEMP:{temp:.1f}°C{trend_indicator}!"
    elif alert_level == "critical":
        return f"🌡️ TEMP:{temp:.1f}°C{trend_indicator}!"
    elif alert_level == "warning":
        return f"🌡️ TEMP:{temp:.1f}°C{trend_indicator}"
    else:
        return f"🌡️ TEMP:{temp:.1f}°C{trend_indicator}"

# Temperature monitoring thread function
def _temperature_monitor_thread():
    """Background thread function for temperature monitoring."""
    global _stop_monitor
    
    logger.debug("Temperature monitoring thread started")
    
    while not _stop_monitor:
        try:
            # Check temperature
            check_temperature_alert()
            
            # Sleep for the check interval
            for _ in range(min(60, _check_interval)):
                if _stop_monitor:
                    break
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in temperature monitor thread: {str(e)}")
            time.sleep(60)  # Sleep longer on error
    
    logger.debug("Temperature monitoring thread stopped")

@safe_execute(default_return=False)
def start_temperature_monitor() -> bool:
    """
    Start the background temperature monitoring thread.
    
    Returns:
        True if successfully started, False otherwise
    """
    global _monitor_thread, _stop_monitor
    
    # Check if already running
    if _monitor_thread and _monitor_thread.is_alive():
        logger.debug("Temperature monitor thread is already running")
        return True
    
    # Reset stop flag
    _stop_monitor = False
    
    # Start thread
    _monitor_thread = threading.Thread(
        target=_temperature_monitor_thread,
        name="temp_monitor",
        daemon=True
    )
    _monitor_thread.start()
    
    logger.info("Temperature monitoring started")
    return True

@safe_execute(default_return=False)
def stop_temperature_monitor() -> bool:
    """
    Stop the background temperature monitoring thread.
    
    Returns:
        True if successfully stopped, False otherwise
    """
    global _monitor_thread, _stop_monitor
    
    # Set stop flag
    _stop_monitor = True
    
    # Wait for thread to finish
    if _monitor_thread and _monitor_thread.is_alive():
        _monitor_thread.join(timeout=5)
        
    # Check if stopped
    if _monitor_thread and _monitor_thread.is_alive():
        logger.warning("Temperature monitor thread did not stop cleanly")
        return False
    
    logger.info("Temperature monitoring stopped")
    return True

@safe_execute(default_return=False)
def set_check_interval(seconds: int) -> bool:
    """
    Set the interval between temperature checks.
    
    Args:
        seconds: Interval in seconds (minimum 5)
        
    Returns:
        True if successfully set, False otherwise
    """
    global _check_interval
    
    # Validate
    if seconds < 5:
        logger.warning(f"Temperature check interval too low: {seconds}, using 5 seconds")
        seconds = 5
    
    # Set interval
    _check_interval = seconds
    logger.debug(f"Temperature check interval set to {seconds} seconds")
    
    return True

@safe_execute(default_return=False)
def set_history_size(count: int) -> bool:
    """
    Set the maximum number of temperature readings to keep in history.
    
    Args:
        count: Maximum number of readings to keep
        
    Returns:
        True if successfully set, False otherwise
    """
    global _history_max_size
    
    # Validate
    if count < 10:
        logger.warning(f"Temperature history size too low: {count}, using 10")
        count = 10
    
    # Set size
    _history_max_size = count
    logger.debug(f"Temperature history size set to {count} readings")
    
    return True

@safe_execute()
def initialize_temperature_monitor() -> None:
    """Initialize the temperature monitoring system."""
    # Load settings
    interval = get_config_value("system_monitoring.temperature.check_interval", _check_interval)
    set_check_interval(interval)
    
    history = get_config_value("system_monitoring.temperature.history_size", _history_max_size)
    set_history_size(history)
    
    # Start monitoring
    if get_config_value("system_monitoring.temperature.alerts.enabled", True):
        start_temperature_monitor()
    
    logger.info("Temperature monitoring system initialized")

# Initialize temperature monitor automatically when module is imported
initialize_temperature_monitor()

logger.info("Temperature alert system initialized") 