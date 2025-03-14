#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Integration Module
# 
# This file defines custom Powerlevel10k segments and functions for Rick Assistant
# to integrate with Powerlevel10k prompt system without conflicts.
#

# Enable debug logging for P10k integration
RICK_P10K_DEBUG=${RICK_P10K_DEBUG:-0}

# Debug function for integration
_rick_p10k_debug() {
  if [[ "${RICK_P10K_DEBUG}" -eq 1 ]]; then
    echo "[RICK_P10K_DEBUG] $1" >&2
  fi
}

_rick_p10k_debug "Loading Rick Assistant P10k integration module"

# Check if powerlevel10k is loaded
_rick_check_p10k() {
  [[ -n $POWERLEVEL9K_LEFT_PROMPT_ELEMENTS ]] || return 1
  _rick_p10k_debug "Powerlevel10k is detected"
  return 0
}

# Function to get Rick's content for the segment
_rick_get_prompt_content() {
  _rick_p10k_debug "Getting prompt content"
  local content=""
  
  # Use Rick Assistant's Python module to get content if available
  if command -v python3 >/dev/null 2>&1; then
    content=$(python3 -c 'from src.core.prompt import get_prompt_content; print(get_prompt_content())' 2>/dev/null)
    _rick_p10k_debug "Python module content: '$content'"
    if [[ -n "$content" ]]; then
      echo "$content"
      return 0
    fi
  fi
  
  # Fallback to a simple output if Python fails
  _rick_p10k_debug "Using fallback content"
  echo "🧪 *burp* Wubba Lubba Dub Dub!"
}

# Define the Rick Assistant segment for Powerlevel10k
function prompt_rick_assistant() {
  _rick_p10k_debug "prompt_rick_assistant function called"
  # Skip segment if Rick Assistant is disabled
  if [[ "${RICK_ASSISTANT_ENABLED:-1}" -eq 0 ]]; then
    _rick_p10k_debug "Rick Assistant is disabled, skipping segment"
    return
  fi
  
  # Get content for segment
  local rick_content=$(_rick_get_prompt_content)
  if [[ -z "$rick_content" ]]; then
    _rick_p10k_debug "Empty content received, skipping segment"
    return
  fi
  
  _rick_p10k_debug "Displaying segment with content: $rick_content"
  # Set segment properties based on configuration
  local rick_icon="🧪"
  local rick_color="green"
  
  # Display segment with appropriate styling
  p10k segment -f "$rick_color" -i "$rick_icon" -t "$rick_content"
}

# Function to add Rick segment to Powerlevel10k
_rick_add_p10k_segment() {
  _rick_p10k_debug "Attempting to add Rick segment to Powerlevel10k"
  if ! _rick_check_p10k; then
    _rick_p10k_debug "Powerlevel10k not detected, cannot add segment"
    return 1
  fi
  
  # Get segment position from configuration
  local position="right"
  if command -v python3 >/dev/null 2>&1; then
    position=$(python3 -c 'from src.utils.config import get_config_value; print(get_config_value("prompt_integration.segment_position", "right"))' 2>/dev/null)
  fi
  _rick_p10k_debug "Segment position: $position"
  
  # DIRECT MODIFICATION: Force-add segment with eval to ensure it takes effect
  if [[ "$position" == "left" ]]; then
    _rick_p10k_debug "FORCE-ADDING to left prompt elements"
    # Safer direct array manipulation instead of eval
    POWERLEVEL9K_LEFT_PROMPT_ELEMENTS+=(rick_assistant)
    _rick_p10k_debug "Left prompt elements: $POWERLEVEL9K_LEFT_PROMPT_ELEMENTS"
  else
    _rick_p10k_debug "FORCE-ADDING to right prompt elements"
    # Safer direct array manipulation instead of eval
    POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=(rick_assistant)
    _rick_p10k_debug "Right prompt elements: $POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS"
  fi
  
  # Configure segment properties - use direct assignment instead of eval
  _rick_p10k_debug "Configuring segment properties"
  # Direct typeset assignments instead of eval
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND=green
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_VISUAL_IDENTIFIER_EXPANSION=🧪
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_BACKGROUND=clear
  
  # Add a command to force prompt refresh
  _rick_p10k_debug "Attempting to force p10k refresh"
  if typeset -f p10k >/dev/null 2>&1; then
    p10k reload
  fi
  
  return 0
}

# Function to remove Rick segment from Powerlevel10k
_rick_remove_p10k_segment() {
  _rick_p10k_debug "Attempting to remove Rick segment from Powerlevel10k"
  if ! _rick_check_p10k; then
    _rick_p10k_debug "Powerlevel10k not detected, cannot remove segment"
    return 1
  fi
  
  # Remove from left prompt elements if present
  if [[ "$POWERLEVEL9K_LEFT_PROMPT_ELEMENTS" == *"rick_assistant"* ]]; then
    _rick_p10k_debug "Removing from left prompt elements"
    POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=("${(@)POWERLEVEL9K_LEFT_PROMPT_ELEMENTS:#rick_assistant}")
  fi
  
  # Remove from right prompt elements if present
  if [[ "$POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS" == *"rick_assistant"* ]]; then
    _rick_p10k_debug "Removing from right prompt elements"
    POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=("${(@)POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS:#rick_assistant}")
  fi
  
  return 0
}

# Expose the segment to p10k
# This is automatically picked up by powerlevel10k
# when the prompt is built
_rick_p10k_debug "Powerlevel10k integration module loaded" 