#!/usr/bin/env zsh
# -*- mode: zsh; sh-indentation: 2; indent-tabs-mode: nil; sh-basic-offset: 2; -*-
# vim: ft=zsh sw=2 ts=2 et
#
# Zsh Native Temperature Monitoring for Rick Assistant
# This replaces the Python implementation with native Zsh for better performance

# Default temperature thresholds (°C)
RICK_TEMP_WARNING=70
RICK_TEMP_CRITICAL=80
RICK_TEMP_EMERGENCY=90

# Last alert times and status
typeset -A _rick_last_temp_alert_time
typeset -A _rick_temp_alert_active
typeset -g _rick_last_temp_check=$EPOCHSECONDS
typeset -g _rick_temp_check_interval=30  # Seconds between checks
typeset -g _rick_temp_alert_cooldown=300  # Seconds between alerts of the same level

# Temperature history
typeset -a _rick_temp_history
typeset -g _rick_temp_history_max=60  # Store last 60 readings

# Messages for different temperature states
typeset -A RICK_TEMP_MESSAGES

# Normal temperature messages
RICK_TEMP_MESSAGES[normal_1]="Temperature's fine. Unlike my *burp* burning hatred for bureaucracy."
RICK_TEMP_MESSAGES[normal_2]="System's running cooler than my relationship with the Galactic Federation."

# Warning temperature messages
RICK_TEMP_MESSAGES[warning_1]="System's heating up like my portal gun after a multiverse bender."
RICK_TEMP_MESSAGES[warning_2]="Temperature rising. What'd you do, install a Concentrated Dark Matter engine?"

# Critical temperature messages
RICK_TEMP_MESSAGES[critical_1]="System's hotter than a supernova! Shut it down before it melts into another dimension!"
RICK_TEMP_MESSAGES[critical_2]="CRITICAL TEMP! This thing's about to pull a Vindicators 3 and explode!"

# Emergency temperature messages
RICK_TEMP_MESSAGES[emergency_1]="Your CPU is about to melt! SHUT IT DOWN NOW, MORTY!"
RICK_TEMP_MESSAGES[emergency_2]="CPU EMERGENCY! It's hotter than the explosion that destroyed Cronenberg world!"

# Function to get temperature thresholds from config or use defaults
_rick_get_temp_thresholds() {
  # Try to get custom thresholds from config file if it exists
  local config_file="${RICK_ASSISTANT_DIR}/config.json"
  if [[ -f "$config_file" ]]; then
    if command -v jq >/dev/null 2>&1; then
      # Use jq to parse JSON if available
      local warning=$(jq -r '.system_monitoring.temperature.thresholds.warning // empty' "$config_file" 2>/dev/null)
      local critical=$(jq -r '.system_monitoring.temperature.thresholds.critical // empty' "$config_file" 2>/dev/null)
      local emergency=$(jq -r '.system_monitoring.temperature.thresholds.emergency // empty' "$config_file" 2>/dev/null)
      
      # Update thresholds if valid values found
      [[ -n "$warning" && "$warning" =~ ^[0-9]+(\.[0-9]+)?$ ]] && RICK_TEMP_WARNING=$warning
      [[ -n "$critical" && "$critical" =~ ^[0-9]+(\.[0-9]+)?$ ]] && RICK_TEMP_CRITICAL=$critical
      [[ -n "$emergency" && "$emergency" =~ ^[0-9]+(\.[0-9]+)?$ ]] && RICK_TEMP_EMERGENCY=$emergency
    elif command -v python3 >/dev/null 2>&1; then
      # Fallback to using Python to parse JSON
      local thresholds=$(python3 -c "
import json, sys
try:
  with open('$config_file', 'r') as f:
    config = json.load(f)
  temp_thresholds = config.get('system_monitoring', {}).get('temperature', {}).get('thresholds', {})
  warning = temp_thresholds.get('warning')
  critical = temp_thresholds.get('critical')
  emergency = temp_thresholds.get('emergency')
  if warning is not None:
    print(f'warning={warning}')
  if critical is not None:
    print(f'critical={critical}')
  if emergency is not None:
    print(f'emergency={emergency}')
except:
  pass
      " 2>/dev/null)
      
      # Parse Python output and set thresholds
      if [[ -n "$thresholds" ]]; then
        local line
        for line in ${(f)thresholds}; do
          if [[ "$line" =~ ^warning=([0-9]+(\.[0-9]+)?)$ ]]; then
            RICK_TEMP_WARNING=$match[1]
          elif [[ "$line" =~ ^critical=([0-9]+(\.[0-9]+)?)$ ]]; then
            RICK_TEMP_CRITICAL=$match[1]
          elif [[ "$line" =~ ^emergency=([0-9]+(\.[0-9]+)?)$ ]]; then
            RICK_TEMP_EMERGENCY=$match[1]
          fi
        done
      fi
    fi
  fi
  
  # Debug output
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && echo "Temperature thresholds: warning=$RICK_TEMP_WARNING, critical=$RICK_TEMP_CRITICAL, emergency=$RICK_TEMP_EMERGENCY" >&2
}

# Function to log a temperature alert
_rick_log_temp_alert() {
  local temp=$1
  local level=$2
  local timestamp=${3:-$EPOCHSECONDS}
  
  # Format timestamp
  local date_str=$(date -d @$timestamp "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r $timestamp "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date "+%Y-%m-%d %H:%M:%S")
  
  # Create alert message
  local message="[${date_str}] [${level}] CPU Temperature Alert: ${temp}°C"
  
  # Select a Rick-style message based on alert level
  # Choose randomly between the two messages for this level
  local random_suffix=$(( (RANDOM % 2) + 1 ))
  local message_key="${level}_${random_suffix}"
  local details="${RICK_TEMP_MESSAGES[$message_key]}"
  
  # Log the alert
  _rick_log "$level" "Temperature Alert: ${temp}°C - $details"
  
  # Also output to terminal if debug is enabled
  if [[ -n "$RICK_ASSISTANT_DEBUG" ]]; then
    # Use different colors based on severity
    case "$level" in
      warning) echo -e "\e[33m$message\e[0m" >&2 ;;
      critical) echo -e "\e[31m$message\e[0m" >&2 ;;
      emergency) echo -e "\e[1;31m$message\e[0m" >&2 ;;
      *) echo "$message" >&2 ;;
    esac
  fi
}

# Function to check if a temperature exceeds thresholds
_rick_check_temp_threshold() {
  local temp=$1
  
  # Check against thresholds (highest to lowest)
  if (( $(echo "$temp >= $RICK_TEMP_EMERGENCY" | bc -l) )); then
    echo "emergency"
  elif (( $(echo "$temp >= $RICK_TEMP_CRITICAL" | bc -l) )); then
    echo "critical"
  elif (( $(echo "$temp >= $RICK_TEMP_WARNING" | bc -l) )); then
    echo "warning"
  else
    echo "normal"
  fi
}

# Function to add a temperature reading to history
_rick_add_temp_reading() {
  local temp=$1
  local timestamp=${2:-$EPOCHSECONDS}
  
  # Add to history
  _rick_temp_history+=("$timestamp:$temp")
  
  # Trim history if needed
  if (( ${#_rick_temp_history[@]} > _rick_temp_history_max )); then
    _rick_temp_history=("${_rick_temp_history[@]:${#_rick_temp_history[@]}-$_rick_temp_history_max}")
  fi
}

# Function to get CPU temperature on Linux
_rick_get_linux_temperature() {
  # Try to get temperature from thermal zones
  for zone in {0..9}; do
    local temp_file="/sys/class/thermal/thermal_zone${zone}/temp"
    if [[ -f "$temp_file" ]]; then
      # Temperature is in millidegrees Celsius, convert to degrees
      local temp_raw=$(cat "$temp_file" 2>/dev/null)
      if [[ -n "$temp_raw" && "$temp_raw" =~ ^[0-9]+$ ]]; then
        echo "scale=1; $temp_raw / 1000" | bc -l
        return 0
      fi
    fi
  done
  
  # Try to get temperature from sensors command
  if command -v sensors >/dev/null 2>&1; then
    local sensors_output=$(sensors 2>/dev/null)
    if [[ -n "$sensors_output" ]]; then
      # Extract temperature from sensors output
      # This pattern matches lines like "Core 0: +45.0°C" and extracts "45.0"
      local temp_line=$(echo "$sensors_output" | grep -E "Core [0-9]+:" | head -n1)
      if [[ -n "$temp_line" && "$temp_line" =~ \+([0-9]+(\.[0-9]+)?)°C ]]; then
        echo "${match[1]}"
        return 0
      fi
    fi
  fi
  
  # No temperature available
  echo ""
  return 1
}

# Function to get CPU temperature on macOS
_rick_get_macos_temperature() {
  # Try using osx-cpu-temp if it's available
  if command -v osx-cpu-temp >/dev/null 2>&1; then
    local temp_output=$(osx-cpu-temp 2>/dev/null)
    if [[ -n "$temp_output" && "$temp_output" =~ CPU:\ ([0-9]+(\.[0-9]+)?)°C ]]; then
      echo "${match[1]}"
      return 0
    fi
  fi
  
  # Try using SMC utility if it's available
  if command -v smc >/dev/null 2>&1; then
    local temp_output=$(smc -k TC0D -r 2>/dev/null)
    if [[ -n "$temp_output" && "$temp_output" =~ TC0D:\ ([0-9]+(\.[0-9]+)?)\ C ]]; then
      echo "${match[1]}"
      return 0
    fi
  fi
  
  # No temperature available
  echo ""
  return 1
}

# Function to get CPU temperature on Windows (WSL)
_rick_get_windows_temperature() {
  # In WSL, we can try to use wmic through powershell
  if command -v powershell.exe >/dev/null 2>&1; then
    local temp_output=$(powershell.exe -Command "Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi | Select-Object -ExpandProperty CurrentTemperature" 2>/dev/null)
    if [[ -n "$temp_output" && "$temp_output" =~ ^[0-9]+$ ]]; then
      # Temperature is in tenths of Kelvin, convert to Celsius
      echo "scale=1; ($temp_output / 10) - 273.15" | bc -l
      return 0
    fi
  fi
  
  # No temperature available
  echo ""
  return 1
}

# Main function to check CPU temperature
rick_check_temperature() {
  local force_check=${1:-0}
  local current_time=$EPOCHSECONDS
  
  # Avoid checking too frequently unless forced
  if (( force_check == 0 && (current_time - _rick_last_temp_check) < _rick_temp_check_interval )); then
    return 0
  fi
  
  # Update last check time
  _rick_last_temp_check=$current_time
  
  # Get temperature thresholds
  _rick_get_temp_thresholds
  
  # Get temperature based on platform
  local temp=""
  local platform=$(uname -s)
  
  case "$platform" in
    Linux)
      if [[ -n "$(uname -r | grep -i microsoft)" ]]; then
        # Windows WSL
        temp=$(_rick_get_windows_temperature)
      else
        # Native Linux
        temp=$(_rick_get_linux_temperature)
      fi
      ;;
    Darwin)
      # macOS
      temp=$(_rick_get_macos_temperature)
      ;;
  esac
  
  # If no temperature available, exit
  if [[ -z "$temp" ]]; then
    [[ -n "$RICK_ASSISTANT_DEBUG" ]] && echo "Rick can't access temperature sensors" >&2
    return 0
  fi
  
  # Add temperature to history
  _rick_add_temp_reading "$temp" "$current_time"
  
  # Check threshold
  local alert_level=$(_rick_check_temp_threshold "$temp")
  
  # If normal temperature, clear any active alerts
  if [[ "$alert_level" == "normal" ]]; then
    for level in "${(@k)_rick_temp_alert_active}"; do
      if [[ "${_rick_temp_alert_active[$level]}" == "1" ]]; then
        _rick_log "INFO" "Temperature returned to normal from ${(U)level} state"
        _rick_temp_alert_active[$level]=0
      fi
    done
    return 0
  fi
  
  # Check if we've already alerted for this level recently
  local last_alert=${_rick_last_temp_alert_time[$alert_level]:-0}
  if (( (current_time - last_alert) < _rick_temp_alert_cooldown )) && \
     [[ "${_rick_temp_alert_active[$alert_level]:-0}" == "1" ]]; then
    # Skip alert if we've recently alerted for this level
    return 0
  fi
  
  # Create and log alert
  _rick_last_temp_alert_time[$alert_level]=$current_time
  _rick_temp_alert_active[$alert_level]=1
  _rick_log_temp_alert "$temp" "$alert_level" "$current_time"
  
  return 0
}

# Function to get current temperature status
rick_temperature_status() {
  # Get temperature thresholds
  _rick_get_temp_thresholds
  
  # Get temperature based on platform
  local temp=""
  local platform=$(uname -s)
  
  case "$platform" in
    Linux)
      if [[ -n "$(uname -r | grep -i microsoft)" ]]; then
        # Windows WSL
        temp=$(_rick_get_windows_temperature)
      else
        # Native Linux
        temp=$(_rick_get_linux_temperature)
      fi
      ;;
    Darwin)
      # macOS
      temp=$(_rick_get_macos_temperature)
      ;;
  esac
  
  # If no temperature available, return status
  if [[ -z "$temp" ]]; then
    echo "Temperature monitoring not available."
    return 0
  fi
  
  # Check threshold
  local alert_level=$(_rick_check_temp_threshold "$temp")
  
  # Format output
  echo "CPU Temperature: ${temp}°C (${(U)alert_level})"
  
  # If in debug mode, show more details
  if [[ -n "$RICK_ASSISTANT_DEBUG" ]]; then
    echo "Thresholds: WARNING=${RICK_TEMP_WARNING}°C, CRITICAL=${RICK_TEMP_CRITICAL}°C, EMERGENCY=${RICK_TEMP_EMERGENCY}°C"
    echo "Last check: $(date -d @$_rick_last_temp_check "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r $_rick_last_temp_check "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date "+%Y-%m-%d %H:%M:%S")"
    
    # Show last few temperature readings
    if (( ${#_rick_temp_history[@]} > 0 )); then
      echo "Temperature history (last ${#_rick_temp_history[@]} readings):"
      for i in {1..5}; do
        local idx=$((${#_rick_temp_history[@]} - $i))
        if (( idx >= 0 )); then
          local entry="${_rick_temp_history[$idx+1]}"
          local hist_time="${entry%%:*}"
          local hist_temp="${entry#*:}"
          local hist_date=$(date -d @$hist_time "+%H:%M:%S" 2>/dev/null || date -r $hist_time "+%H:%M:%S" 2>/dev/null || date "+%H:%M:%S")
          echo "  $hist_date: ${hist_temp}°C"
        fi
      done
    fi
  fi
  
  return 0
}

# Initialize temperature monitoring system
_rick_init_temperature_monitor() {
  # Set up initial variables
  _rick_last_temp_check=$EPOCHSECONDS
  _rick_temp_history=()
  
  # Run initial temperature check
  rick_check_temperature 1
  
  # Debug output
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && echo "Rick's temperature monitoring initialized" >&2
}

# Initialize temperature monitoring if not already done
_rick_init_temperature_monitor 