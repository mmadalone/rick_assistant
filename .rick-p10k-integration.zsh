#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Integration Script
# This file adds the Rick metrics segment to Powerlevel10k properly

# Ensure our segment script is available
if [[ ! -f ~/.oh-my-zsh/custom/plugins/rick_assistant/.rick-p10k-segment.zsh ]]; then
  echo "Error: Segment definition script not found at ~/.oh-my-zsh/custom/plugins/rick_assistant/.rick-p10k-segment.zsh"
  echo "Please ensure the segment script exists before running this integration"
  return 1
fi

# Source our segment script to make the function available
source ~/.oh-my-zsh/custom/plugins/rick_assistant/.rick-p10k-segment.zsh

# Function to add our segment to Powerlevel10k configuration
_rick_integrate_p10k() {
  local integration_succeeded=0
  local error_messages=""
  
  # First, check if Powerlevel10k is loaded
  if ! typeset -f p10k >/dev/null 2>&1; then
    error_messages="Powerlevel10k not loaded in this shell session!\n"
    error_messages="${error_messages}Try running: source ~/.zshrc\n"
    error_messages="${error_messages}Then run this script again.\n"
    integration_succeeded=0
  else
    # echo "✅ Powerlevel10k is loaded"
    integration_succeeded=1
  
    # Check if our segment function is available
    if ! typeset -f prompt_my_rick_metrics >/dev/null 2>&1; then
      error_messages="Segment function not loaded properly!\n"
      integration_succeeded=0
    else
      # echo "✅ Rick segment function is loaded"
      
      # Set styling parameters for our segment
      typeset -g POWERLEVEL9K_MY_RICK_METRICS_FOREGROUND="green"
      typeset -g POWERLEVEL9K_MY_RICK_METRICS_BACKGROUND="clear"
      
      # Disable default path segment to avoid duplication
      typeset -g POWERLEVEL9K_DIR_BACKGROUND="none"
      typeset -g POWERLEVEL9K_DIR_FOREGROUND="none"
      typeset -g POWERLEVEL9K_DIR_VISUAL_IDENTIFIER_COLOR="none"
      
      # Check if top_left elements are defined
      if ! typeset -p POWERLEVEL9K_LEFT_PROMPT_ELEMENTS >/dev/null 2>&1; then
        echo "Creating default POWERLEVEL9K_LEFT_PROMPT_ELEMENTS array"
        typeset -g -a POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(dir vcs)
      fi
      
      # First, make sure the clock is preserved if it exists
      local has_time=0
      if [[ "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(r)time]}" == "time" ]]; then
        has_time=1
        # echo "Clock segment detected - will preserve it"
      fi
      
      # Add to beginning of left prompt for status bar at top
      if [[ "${POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[(r)my_rick_metrics]}" != "my_rick_metrics" ]]; then
        # Save original elements but filter out 'dir' (path) element
        local new_elements=()
        for element in "${POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[@]}"; do
          if [[ "$element" != "dir" ]]; then
            new_elements+=("$element")
          fi
        done
        
        # Create new array with our segment at beginning
        POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(
          my_rick_metrics
          "${new_elements[@]}"
        )
        # echo "✅ Rick segment added to Powerlevel10k left prompt elements (top position)"
      else
        echo "ℹ️ Rick segment was already in left prompt elements"
      fi
      
      # If clock was detected but missing in right prompt, add it back
      if [[ $has_time -eq 1 && "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(r)time]}" != "time" ]]; then
        POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=(time)
        # echo "✅ Restored clock to right prompt elements"
      fi
      
      # Reload Powerlevel10k
      if p10k reload; then
        # echo "✅ Powerlevel10k reloaded successfully"
        true
      else
        error_messages="${error_messages}Failed to reload Powerlevel10k\n"
        integration_succeeded=0
      fi
    fi
  fi
  
  # Print integration status
  echo ""
  if [[ $integration_succeeded -eq 1 ]]; then
    true
    # Echo statements removed to avoid potential quote issues
  else
    echo "❌ INTEGRATION FAILED"
    echo "The following errors were encountered:"
    echo $error_messages
    echo ""
    echo "Troubleshooting tips:"
    echo "1. Make sure Powerlevel10k is properly installed and configured"
    echo "2. Ensure your .zshrc loads Powerlevel10k before running this script"
    echo "3. Try running 'source ~/.zshrc' to reload your shell configuration"
    echo "4. Run 'p10k configure' to reset your Powerlevel10k configuration"
  fi
}

# Run the integration function
_rick_integrate_p10k
