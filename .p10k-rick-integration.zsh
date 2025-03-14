#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Integration Script
# This script properly integrates the Rick segment with Powerlevel10k

# Define the segment function
if [[ -f ~/.p10k-rick-segment.zsh ]]; then
  source ~/.p10k-rick-segment.zsh
else
  echo "Error: Rick segment definition file not found" >&2
  return 1
fi

# Load conditional display settings
if [[ -f ~/.p10k-rick-conditional.zsh ]]; then
  source ~/.p10k-rick-conditional.zsh
fi

# Add to prompt elements if not already present
if (( ! ${+POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS} )); then
  # Safety check if variable isn't defined yet
  return
fi

# Only add if not already present
if (( ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)my_rick]} == 0 )); then
  # Add to beginning of right prompt
  POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    my_rick
    "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]}"
  )
  
  # Set styling parameters
  typeset -g POWERLEVEL9K_MY_RICK_FOREGROUND="green"
  typeset -g POWERLEVEL9K_MY_RICK_BACKGROUND="clear"
  
  # Make sure these core elements are enabled
  # Check if they're in the array, if not add them after my_rick
  local core_elements=("status" "command_execution_time" "background_jobs")
  for element in "${core_elements[@]}"; do
    if (( ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)$element]} == 0 )); then
      # Element is not in the array, add it after my_rick
      local index=${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)my_rick]}
      POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
        "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[1,$index]}"
        "$element"
        "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[$((index+1)),-1]}"
      )
    fi
  done
fi

# Reload p10k if possible (but don't force it)
if typeset -f p10k &>/dev/null; then
  p10k reload 2>/dev/null || true
fi 