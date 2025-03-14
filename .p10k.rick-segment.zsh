#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Segment Definition
# This file defines the segment function according to official Powerlevel10k guidelines

# Define the segment function using the standard naming convention
function prompt_my_rick_assistant() {
  # This function will be called during prompt rendering by Powerlevel10k
  
  # Default values
  local content=""
  local rick_icon="🧪"
  local rick_color="green"
  
  # Only collect system metrics if plain mode is not enabled
  if [[ "${RICK_P10K_PLAIN_MODE}" != "true" ]]; then
    # Get system metrics using Python script if available
    if command -v python3 >/dev/null 2>&1; then
      # Use a simple inline script for metrics to avoid external dependencies
      content=$(python3 -c '
import sys
try:
    import psutil
    # Get CPU/RAM metrics safely
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    print(f"CPU:{cpu:.1f}% RAM:{ram:.1f}%")
except ImportError:
    print("🧪 *burp*")
except Exception as e:
    print(f"🧪 Wubba Lubba Dub Dub!")
' 2>/dev/null)
    fi
  else
    # Plain text mode - just show a simple message
    content="Rick's here!"
  fi
  
  # Fallback if something went wrong
  if [[ -z "$content" ]]; then
    content="🧪 Rick's here!"
  fi
  
  # Debug output if enabled
  if [[ "${RICK_P10K_DEBUG}" == "true" ]]; then
    echo "[RICK_P10K_DEBUG] Segment content: $content" >&2
  fi
  
  # Use p10k segment correctly during prompt rendering
  p10k segment -f "$rick_color" -i "$rick_icon" -t "$content"
}

# Export any needed variables
export RICK_P10K_PLAIN_MODE=${RICK_P10K_PLAIN_MODE:-false}
export RICK_P10K_DEBUG=${RICK_P10K_DEBUG:-false}

# Note: We don't add the segment to the prompt elements here
# That will be done in the integration file 