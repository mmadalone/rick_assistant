#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Segment Definition
# This file defines a segment function according to official Powerlevel10k guidelines

# Add line counter for debugging
debug_line_counter=0
# Function is disabled - completely commented out
#_debug_line() {
#  ((debug_line_counter++))
#  echo "SEGMENT_FILE LINE $debug_line_counter: $1"
#}

# Instead of calling the debug function directly, we'll use:
# Comment out all debug line calls for clean output
#_debug_line "Starting segment file processing"

# Function to get a random Rick phrase
_get_rick_phrase() {
  #_debug_line "Starting _get_rick_phrase function"
  
  # Use simple quotes without apostrophes for now to avoid any quoting issues
  local phrases=(
    "*burp*"
    "Wubba lubba dub dub!"
    "And that's the way the news goes!"
    "Grass tastes bad!"
    "Lick lick lick my balls!"
    "No jumping in the sewer!"
    "Rikki-tikki-tavi, biatch!"
    "I'm Pickle Rick!"
    "*buuurrrrp*"
    "AIDS!"
    "Hit the sack, Jack!"
  )

  echo "${phrases[$(($RANDOM % ${#phrases[@]}+ 1))]}"
  #_debug_line "Completed _get_rick_phrase function"
}

# Function to get the universe designation
_get_universe() {
  #_debug_line "Starting _get_universe function"
  
  local universe=(
    "C-137"
    "C-500A"
    "C-131"
    "D-99"
    "J-22"
    "K-22"
    "C-35"
    "C-595"
    "F-192"
    "C-1239"
  )

  echo "${universe[$(($RANDOM % ${#universe[@]}+ 1))]}"
  #_debug_line "Completed _get_universe function"
}

# Define the segment function using the standard naming convention
prompt_my_rick_metrics() {
  #_debug_line "Starting prompt_my_rick_metrics function"
  
  # Default values
  local content=""
  local cpu_info="CPU: ?.???"
  local ram_info="RAM: ?.???"
  local temp_info="| 🌡️  ?.???"
  local rick_phrase=$(_get_rick_phrase)
  local universe=$(_get_universe)
  
  # Get current directory path
  local current_path=$(pwd)
  
  # Get CPU usage - multiplatform method
  if [[ -f /proc/stat ]]; then
    # Linux /proc/stat method (works on most distros)
    local cpu_line=$(grep '^cpu ' /proc/stat)
    local cpu_values=(${=cpu_line})
    local total=$((${cpu_values[2]}+ ${cpu_values[3]} + ${cpu_values[4]} + ${cpu_values[5]}))
    local idle=${cpu_values[5]}
    
    # Need two measurements to calculate usage
    sleep 0.1
    
    local cpu_line_2=$(grep '^cpu ' /proc/stat)
    local cpu_values_2=(${=cpu_line_2})
    local total_2=$((${cpu_values_2[2]}+ ${cpu_values_2[3]} + ${cpu_values_2[4]} + ${cpu_values_2[5]}))
    local idle_2=${cpu_values_2[5]}
    
    local diff_total=$((total_2 - total))
    local diff_idle=$((idle_2 - idle))
    
    if [[ $diff_total -gt 0 ]]; then
      # Format with two decimal places for better precision
      local cpu_raw=$((100.0 * (diff_total - diff_idle) / diff_total))
      local cpu_usage=$(printf "%.2f" $cpu_raw)
      cpu_info="CPU: ${cpu_usage} %"
    fi
  elif command -v top >/dev/null 2>&1; then
    # Fallback to top command (more universal)
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if [[ -n "$cpu_usage" ]]; then
      # Format with two decimal places
      cpu_info="CPU: $(printf "%.2f" $cpu_usage) %"
    fi
  fi
  
  # Get RAM info - multiplatform method
  if [[ -f /proc/meminfo ]]; then
    # Parse /proc/meminfo to get memory usage (Linux)
    local mem_total=$(grep 'MemTotal' /proc/meminfo | awk '{print $2}')
    local mem_available=$(grep 'MemAvailable\|MemFree' /proc/meminfo | head -n1 | awk '{print $2}')
    
    if [[ -n "$mem_total" && -n "$mem_available" && "$mem_total" -gt 0 ]]; then
      local mem_used=$((mem_total - mem_available))
      # Calculate with better precision and format with two decimal places
      local mem_raw=$((mem_used * 100.0 / mem_total))
      local mem_percent=$(printf "%.2f" $mem_raw)
      ram_info="RAM: ${mem_percent}%"
    fi
  elif command -v vm_stat >/dev/null 2>&1; then
    # macOS memory info
    local mem_info=$(vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\.//')
    if [[ -n "$mem_info" ]]; then
      # Format with two decimal places
      local mem_percent=$(printf "%.2f" $mem_info)
      ram_info="RAM: ${mem_percent}%"
    fi
  fi
  
  # Get temperature - if available (suppress all errors)
  if [[ -f /sys/class/thermal/thermal_zone0/temp ]]; then
    # Linux temperature method
    local temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)
    if [[ -n "$temp" && "$temp" -gt 0 ]]; then
      # Convert milli-celsius to celsius with 2 decimal precision
      local temp_raw=$(echo "scale=2; $temp / 1000" | bc 2>/dev/null)
      local temp_formatted=$(printf "%.2f" ${temp_raw:-$(($temp / 1000))})
      temp_info="| 🌡️  ${temp_formatted}"
    fi
  elif command -v sensors >/dev/null 2>&1; then
    # Try using lm-sensors if available, but redirect all output to /dev/null
    local temp=$(sensors 2>/dev/null | grep -oP 'Package id 0:\s+\+\K[0-9.]+' 2>/dev/null | head -n1)
    if [[ -n "$temp" ]]; then
      # Format with two decimal places
      local temp_formatted=$(printf "%.2f" $temp)
      temp_info="| 🌡️   ${temp_formatted}°C"
    fi
  fi
  
  # Format the content with full path, system metrics and Rick phrase
  # Use exact format requested by user - use a simple concatenation approach
  # to avoid complex quoting issues
  content="📁 ${current_path} | 🖥️  ${cpu_info} | 🔧 ${ram_info} | ${temp_info} | 🌀 ${universe} | 🧪 ${rick_phrase}"
  
  # Use p10k segment with transparent background and no icon
  p10k segment -b clear -f green -i "" -t "${content}"
  
  #_debug_line "Completed prompt_my_rick_metrics function"
}