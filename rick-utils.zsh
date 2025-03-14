#!/usr/bin/env zsh
# Rick Assistant - Utility functions for the menu system

# Check terminal capabilities
_rick_menu_check_terminal() {
  # Check if terminal supports colors
  if ! tput colors &>/dev/null; then
    print -P "%F{red}Error: Your terminal does not support colors.%f"
    return 1
  fi
  
  # Check if terminal supports cursor movement
  if ! tput cup 0 0 &>/dev/null; then
    print -P "%F{red}Error: Your terminal does not support cursor movement.%f"
    return 1
  fi
  
  return 0
}

# Clear screen with fallback
_rick_menu_clear() {
  clear 2>/dev/null || printf "\033c" || echo -en "\ec" || echo -en "\033[2J"
}

# Center text in terminal
_rick_menu_centered() {
  local text="$1"
  local width="${2:-$(tput cols)}"
  local padding=$(( (width - ${#text}) / 2 ))
  padding=$(( padding < 0 ? 0 : padding ))
  
  printf "%${padding}s%s\n" "" "$text"
}

# Get CPU usage
_rick_get_cpu_usage() {
  # Try different methods to get CPU usage
  if command -v top >/dev/null 2>&1; then
    # Use top command
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
  elif [[ -f /proc/stat ]]; then
    # Use /proc/stat
    local cpu_usage
    cpu_usage=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print int(usage)}')
    echo "$cpu_usage"
  else
    # No method available
    return 1
  fi
}

# Get RAM usage
_rick_get_ram_usage() {
  # Try different methods to get RAM usage
  if command -v free >/dev/null 2>&1; then
    # Use free command
    free | awk '/^Mem/ {print int($3/$2 * 100)}'
  elif [[ -f /proc/meminfo ]]; then
    # Use /proc/meminfo
    local mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_avail=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    local mem_used=$((mem_total - mem_avail))
    echo $((mem_used * 100 / mem_total))
  else
    # No method available
    return 1
  fi
}

# Get disk usage
_rick_get_disk_usage() {
  # Try different methods to get disk usage
  if command -v df >/dev/null 2>&1; then
    # Use df command
    df -h / | awk 'NR==2 {print $5}' | tr -d '%'
  else
    # No method available
    return 1
  fi
}

# Get temperature
_rick_get_temperature() {
  # Try different methods to get temperature
  if [[ -f /sys/class/thermal/thermal_zone0/temp ]]; then
    # Use thermal_zone0
    cat /sys/class/thermal/thermal_zone0/temp | awk '{printf "%.0f", $1/1000}'
  elif command -v vcgencmd >/dev/null 2>&1; then
    # Use vcgencmd for Raspberry Pi
    vcgencmd measure_temp | sed 's/temp=\([0-9.]*\).*/\1/'
  else
    # No method available
    return 1
  fi
}

# Get uptime
_rick_get_uptime() {
  # Try different methods to get uptime
  if command -v uptime >/dev/null 2>&1; then
    # Use uptime command
    uptime -p | sed 's/^up //'
  elif [[ -f /proc/uptime ]]; then
    # Use /proc/uptime
    local uptime=$(cat /proc/uptime | awk '{print $1}')
    local days=$((uptime/86400))
    local hours=$(((uptime%86400)/3600))
    local minutes=$(((uptime%3600)/60))
    
    if [[ $days -gt 0 ]]; then
      echo "${days}d ${hours}h ${minutes}m"
    elif [[ $hours -gt 0 ]]; then
      echo "${hours}h ${minutes}m"
    else
      echo "${minutes}m"
    fi
  else
    # No method available
    return 1
  fi
}

# Get config value with fallback
_rick_get_config_value() {
  local key="$1"
  local default="${2:-}"
  
  # Call the Python config getter if available
  if type get_config_value >/dev/null 2>&1; then
    get_config_value "$key" "$default"
    return $?
  fi
  
  # Otherwise use a simplified version
  # First check if config file exists
  local config_file="${HOME}/.rick_assistant/config.json"
  if [[ ! -f "$config_file" ]]; then
    echo "$default"
    return 0
  fi
  
  # Try to use jq if available
  if command -v jq >/dev/null 2>&1; then
    local value=$(jq -r ".$key // \"$default\"" "$config_file" 2>/dev/null)
    if [[ -n "$value" && "$value" != "null" ]]; then
      echo "$value"
      return 0
    fi
  fi
  
  # Fallback to grep/sed for simple keys
  local simple_key=$(echo "$key" | cut -d. -f1)
  local value=$(grep "\"$simple_key\":" "$config_file" | head -1 | sed 's/.*: *"\(.*\)".*/\1/' 2>/dev/null)
  if [[ -n "$value" ]]; then
    echo "$value"
    return 0
  fi
  
  # Return default if nothing found
  echo "$default"
  return 0
}

# Set config value
_rick_set_config_value() {
  local key="$1"
  local value="$2"
  
  # Call the Python config setter if available
  if type set_config_value >/dev/null 2>&1; then
    set_config_value "$key" "$value"
    return $?
  fi
  
  # Otherwise use a simplified version
  # First check if config dir exists
  local config_dir="${HOME}/.rick_assistant"
  local config_file="${config_dir}/config.json"
  
  # Create config dir if it doesn't exist
  if [[ ! -d "$config_dir" ]]; then
    mkdir -p "$config_dir"
  fi
  
  # Create empty config file if it doesn't exist
  if [[ ! -f "$config_file" ]]; then
    echo "{}" > "$config_file"
  fi
  
  # Try to use jq if available
  if command -v jq >/dev/null 2>&1; then
    local temp_file="${config_file}.tmp"
    jq ".[\"$key\"] = \"$value\"" "$config_file" > "$temp_file" 2>/dev/null
    if [[ $? -eq 0 ]]; then
      mv "$temp_file" "$config_file"
      return 0
    fi
  fi
  
  # Python fallback if jq isn't available but Python is
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, os
try:
    config_file = '$config_file'
    with open(config_file, 'r') as f:
        data = json.load(f)
    data['$key'] = '$value'
    with open(config_file, 'w') as f:
        json.dump(data, f)
except Exception as e:
    print(f'Error updating config: {e}')
    exit(1)
" 2>/dev/null
    if [[ $? -eq 0 ]]; then
      return 0
    fi
  fi
  
  # Simple fallback for basic config files
  # This is a very basic implementation that doesn't properly handle nested keys
  # It preserves the key as is, including dots
  if grep -q "\"$key\":" "$config_file"; then
    # Update existing key (very simple implementation)
    sed -i "s/\"$key\": *\"[^\"]*\"/\"$key\": \"$value\"/" "$config_file"
  else
    # Add new key (very simple implementation)
    sed -i "s/{/{\"$key\": \"$value\", /" "$config_file"
  fi
  
  return 0
}

# Load the functions into the current shell
autoload -U _rick_menu_read_key
autoload -U _rick_menu_handle_key
autoload -U _rick_menu_navigate
autoload -U _rick_menu_main
autoload -U _rick_menu_simple
autoload -U _rick_menu_simple_arrows
autoload -U _rick_menu_brain
autoload -U _rick_menu_shell
autoload -U _rick_menu_settings
autoload -U _rick_menu_general_settings
autoload -U _rick_menu_monitoring 