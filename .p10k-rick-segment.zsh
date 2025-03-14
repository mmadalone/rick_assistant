#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Segment Definition
# This file defines a segment function according to official Powerlevel10k guidelines

function prompt_my_rick() {
  # Default values
  local content=""
  local rick_icon="🧪"
  local cpu_info="CPU:?.?%"
  local ram_info="RAM:?.?%"
  local rick_phrase=$(shuf -n1 -e "*burp*" "Wubba lubba dub dub!" "And that's the way the news goes!" "Grass tastes bad!" "No jumpin' in the sewer!")
  
  # Try to get CPU info with Linux command (safer in WSL)
  if command -v grep &>/dev/null && [[ -f /proc/stat ]]; then
    # Get CPU usage using /proc/stat (very reliable in Linux/WSL)
    local cpu_line=$(grep '^cpu ' /proc/stat)
    local cpu_values=(${=cpu_line})
    local total=$((${cpu_values[2]} + ${cpu_values[3]} + ${cpu_values[4]} + ${cpu_values[5]}))
    local idle=${cpu_values[5]}
    
    # Need two measurements to calculate usage
    sleep 0.1
    
    local cpu_line_2=$(grep '^cpu ' /proc/stat)
    local cpu_values_2=(${=cpu_line_2})
    local total_2=$((${cpu_values_2[2]} + ${cpu_values_2[3]} + ${cpu_values_2[4]} + ${cpu_values_2[5]}))
    local idle_2=${cpu_values_2[5]}
    
    local diff_total=$((total_2 - total))
    local diff_idle=$((idle_2 - idle))
    local cpu_usage=$((100 * (diff_total - diff_idle) / diff_total))
    
    cpu_info="CPU:${cpu_usage}%"
  fi
  
  # Try to get RAM info with Linux command (safer in WSL)
  if command -v awk &>/dev/null && [[ -f /proc/meminfo ]]; then
    # Parse /proc/meminfo to get memory usage
    local mem_total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
    local mem_available=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
    local mem_used=$((mem_total - mem_available))
    local mem_percent=$((mem_used * 100 / mem_total))
    
    ram_info="RAM:${mem_percent}%"
  fi
  
  # Format the content with system metrics and Rick phrase
  content="${cpu_info} | ${ram_info} | ${rick_icon} | ${rick_phrase}"
  
  # Use p10k segment correctly
  p10k segment -f green -i "" -t "$content"
} 