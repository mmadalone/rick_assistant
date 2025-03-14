#!/usr/bin/env zsh
# rick-utils.zsh - Utility functions for Rick Assistant
#
# This module provides utility functions for the Rick Assistant menu system.

# Ensure the core module is loaded
(( ${+functions[rick_core_module_load]} )) || source "${0:A:h}/rick-core.zsh"

# Register this module
rick_core_module_load "utils" "${0:A}" || return 1

# Array of Rick quotes
typeset -ga RICK_QUOTES=(
  "Wubba lubba dub dub!"
  "I'm not a monster, I'm just ahead of the curve."
  "I'm pickle Riiiiick!"
  "Sometimes science is more art than science, Morty."
  "What, so everyone's supposed to sleep every single night now?"
  "I don't do adventures with boring people."
  "I'm sorry, but your opinion means very little to me."
  "Nobody exists on purpose, nobody belongs anywhere, everybody's gonna die."
  "I'm not arguing, I'm just explaining why I'm right."
  "That's planning for failure, Morty. Even dumber than regular planning."
  "To live is to risk it all."
  "I'm a scientist; because I invent, transform, create, and destroy for a living."
  "Weddings are basically funerals with cake."
  "Life is effort and I'll stop when I die!"
  "Boom! Big reveal! I turned myself into a pickle!"
  "Think for yourselves, don't be sheep."
  "Those who can, do. Those who can't, teach. Those who can't teach, teach gym."
  "I just want to go back to the quiet life of developing weapons for the government."
  "The universe is basically an animal. It grazes on the ordinary."
  "If there's a lesson here, and I'm not sure there is, it's that sometimes what you're looking for is right in front of you all along."
)

# Get CPU usage
get_cpu_usage() {
  local cpu_usage=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print int(usage) "%"}' 2>/dev/null || echo "N/A")
  echo $cpu_usage
}

# Get RAM usage
get_ram_usage() {
  local ram_usage=$(free -h | awk '/^Mem/ {print $3 "/" $2}' 2>/dev/null || echo "N/A")
  echo $ram_usage
}

# Get temperature
get_temperature() {
  local temp
  if [[ -f /sys/class/thermal/thermal_zone0/temp ]]; then
    temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{printf "%.1f°C", $1/1000}' 2>/dev/null || echo "N/A")
  else
    temp="N/A"
  fi
  echo $temp
}

# Get a random Rick quote
get_rick_quote() {
  # Get a random index
  local index=$(( RANDOM % ${#RICK_QUOTES[@]} ))
  echo "${RICK_QUOTES[$index]}"
}

# Get configuration value
get_config_value() {
  local key="$1"
  local default_value="$2"
  
  # Check if rick_core_get_config exists
  if (( ${+functions[rick_core_get_config]} )); then
    # Extract namespace and property from dot notation
    local namespace=$(echo "$key" | cut -d. -f1)
    local property=$(echo "$key" | cut -d. -f2-)
    
    # If there's no dot, use the whole key as property
    if [[ "$namespace" == "$property" ]]; then
      property=""
    fi
    
    # Use rick_core_get_config
    local value=$(rick_core_get_config "$namespace" "$property" "$default_value")
    echo "$value"
  else
    # Fallback to default value if function doesn't exist
    echo "$default_value"
  fi
}

# Set configuration value
set_config_value() {
  local key="$1"
  local value="$2"
  
  # Check if rick_core_set_config exists
  if (( ${+functions[rick_core_set_config]} )); then
    # Extract namespace and property from dot notation
    local namespace=$(echo "$key" | cut -d. -f1)
    local property=$(echo "$key" | cut -d. -f2-)
    
    # If there's no dot, use the whole key as property
    if [[ "$namespace" == "$property" ]]; then
      property=""
    fi
    
    # Use rick_core_set_config
    rick_core_set_config "$namespace" "$property" "$value"
    return $?
  else
    # Print an error message if function doesn't exist
    echo "Error: Configuration system not available" >&2
    return 1
  fi
}

# Register public functions
rick_core_register_function "get_cpu_usage" "public"
rick_core_register_function "get_ram_usage" "public"
rick_core_register_function "get_temperature" "public"
rick_core_register_function "get_rick_quote" "public"
rick_core_register_function "get_config_value" "public"
rick_core_register_function "set_config_value" "public"

# Initialize module
if (( RICK_DEBUG )); then
  print "Rick Assistant Utils Module loaded"
fi 