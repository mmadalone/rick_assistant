#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Integration Script
# This script properly integrates the Rick segment with Powerlevel10k

# Debug function
_rick_p10k_debug() {
  if [[ "${RICK_P10K_DEBUG}" == "true" ]]; then
    echo "[RICK_P10K_DEBUG] $1" >&2
  fi
}

# First, make sure Powerlevel10k is available
if ! typeset -f p10k &>/dev/null; then
  _rick_p10k_debug "Powerlevel10k not available, cannot integrate Rick Assistant"
  return 1
fi

_rick_p10k_debug "Starting Rick Assistant integration with Powerlevel10k"

# Source the segment definition file
if [[ -f "${HOME}/.p10k.rick-segment.zsh" ]]; then
  _rick_p10k_debug "Sourcing segment definition file"
  source "${HOME}/.p10k.rick-segment.zsh"
else
  _rick_p10k_debug "Error: Segment definition file not found"
  echo "Error: Rick Assistant segment definition file not found" >&2
  return 1
fi

# Check if segment function is now available
if ! typeset -f prompt_my_rick_assistant &>/dev/null; then
  _rick_p10k_debug "Error: Segment function not defined correctly"
  echo "Error: Rick Assistant segment function not defined correctly" >&2
  return 1
fi

_rick_p10k_debug "Segment function found, proceeding with integration"

# Add the segment to prompt elements if not already there
if (( ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)my_rick_assistant]} == 0 )); then
  _rick_p10k_debug "Adding Rick Assistant segment to right prompt elements"
  
  # Add to the beginning of the right prompt
  POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    my_rick_assistant
    "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]}"
  )
  
  # Define segment styling if not already defined
  # These will be respected by Powerlevel10k
  typeset -g POWERLEVEL9K_MY_RICK_ASSISTANT_FOREGROUND="green"
  typeset -g POWERLEVEL9K_MY_RICK_ASSISTANT_BACKGROUND="clear"
  typeset -g POWERLEVEL9K_MY_RICK_ASSISTANT_VISUAL_IDENTIFIER_EXPANSION='🧪'
  
  _rick_p10k_debug "Right prompt elements: ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[*]}"
  _rick_p10k_debug "Segment styling configured"
else
  _rick_p10k_debug "Rick Assistant segment already in prompt elements"
fi

# Attempt to reload p10k to apply changes
if typeset -f p10k &>/dev/null; then
  _rick_p10k_debug "Reloading p10k to apply changes"
  p10k reload
fi

_rick_p10k_debug "Rick Assistant integration completed" 