#!/usr/bin/env zsh
#
# Rick Assistant - Prompt Integration Modes
# 
# This file defines functions for different prompt integration modes:
# - segment: Adds Rick as a Powerlevel10k segment
# - right_prompt: Places Rick in the right prompt
# - command_output: Shows Rick's comments as command output (least intrusive)
# - custom_position: Places Rick at a custom position in the prompt
#

# Variables to store original prompt settings
typeset -g RICK_ORIGINAL_PROMPT=""
typeset -g RICK_ORIGINAL_RPROMPT=""
typeset -g RICK_DISPLAY_MODE=""
typeset -g RICK_INTEGRATION_ACTIVE=0

# Source Powerlevel10k integration if available
if [[ -f "${0:A:h}/powerlevel10k.zsh" ]]; then
  source "${0:A:h}/powerlevel10k.zsh"
fi

# Function to get Rick's content for display
rick_get_prompt_content() {
  # Use Rick Assistant's Python module to get content if available
  if command -v python3 >/dev/null 2>&1; then
    local content=$(python3 -c 'from src.core.prompt import get_prompt_content; print(get_prompt_content())' 2>/dev/null)
    if [[ -n "$content" ]]; then
      echo "$content"
      return 0
    fi
  fi
  
  # Fallback to a simple output if Python fails
  local phrases=(
    "🧪 *burp* What now?"
    "🧪 I'm working here, Morty!"
    "🧪 This dimension's terminals are primitive"
    "🧪 *burp* Science!"
  )
  echo "${phrases[$((RANDOM % ${#phrases[@]} + 1))]}"
}

# Handle segment mode (Powerlevel10k integration)
_rick_handle_segment_mode() {
  # Check if Powerlevel10k is available
  if typeset -f _rick_add_p10k_segment >/dev/null 2>&1; then
    _rick_add_p10k_segment
    
    # For PowerLevel10k, also use the direct integration approach (belt and suspenders)
    if [[ -f "$HOME/.p10k.zsh" ]]; then
      # Use different script depending on what's available
      if [[ -f "${0:A:h}/p10k_setup.zsh" ]]; then
        # Source the advanced setup script
        ${0:A:h}/p10k_setup.zsh "right"
      elif [[ -f "${0:A:h}/p10k_direct.zsh" ]]; then
        # Source the direct integration script
        source "${0:A:h}/p10k_direct.zsh"
      fi
    fi
    
    RICK_DISPLAY_MODE="segment"
    RICK_INTEGRATION_ACTIVE=1
    return 0
  fi
  
  # Fallback if Powerlevel10k not available
  echo "Powerlevel10k not detected. Falling back to command_output mode."
  _rick_handle_command_output_mode
  return 1
}

# Handle right prompt mode
_rick_handle_right_prompt_mode() {
  # Store original RPROMPT if not already saved
  if [[ -z "$RICK_ORIGINAL_RPROMPT" ]]; then
    RICK_ORIGINAL_RPROMPT="$RPROMPT"
  fi
  
  # Set up the right prompt with Rick's content
  RPROMPT='${RICK_ORIGINAL_RPROMPT:+$RICK_ORIGINAL_RPROMPT }$(rick_get_prompt_content)'
  
  RICK_DISPLAY_MODE="right_prompt"
  RICK_INTEGRATION_ACTIVE=1
  return 0
}

# Handle command output mode
_rick_handle_command_output_mode() {
  # This uses precmd hook to occasionally output Rick's comments
  # Add our hook if not already in place
  if ! typeset -f _rick_original_precmd >/dev/null 2>&1; then
    # Save original precmd if it exists
    if typeset -f precmd >/dev/null 2>&1; then
      # Use ZSH's native function copying instead of eval
      functions[_rick_original_precmd]=$functions[precmd]
    else
      _rick_original_precmd() { :; }
    fi
    
    # Define new precmd with Rick's occasional comments
    precmd() {
      _rick_original_precmd "$@"
      
      # Check if we should display a comment (based on frequency)
      if (( RANDOM % 10 < 3 )); then  # ~30% chance
        # Get comment from Rick
        local comment=$(rick_get_prompt_content)
        if [[ -n "$comment" ]]; then
          # Print with newlines before and after
          echo ""
          echo "$comment"
          echo ""
        fi
      fi
    }
  fi
  
  RICK_DISPLAY_MODE="command_output"
  RICK_INTEGRATION_ACTIVE=1
  return 0
}

# Handle custom position mode
_rick_handle_custom_position_mode() {
  # Get custom position index from configuration
  local position_index=2
  if command -v python3 >/dev/null 2>&1; then
    position_index=$(python3 -c 'from src.utils.config import get_config_value; print(get_config_value("prompt_integration.custom_position_index", 2))' 2>/dev/null)
  fi
  
  # For Powerlevel10k, we can use our setup script for easier positioning
  if [[ -f "$HOME/.p10k.zsh" ]] && [[ -f "${0:A:h}/p10k_setup.zsh" ]]; then
    # Use the left position for custom position as it's easier to control with position_index
    ${0:A:h}/p10k_setup.zsh "dir"
    RICK_DISPLAY_MODE="custom_position"
    RICK_INTEGRATION_ACTIVE=1
    return 0
  elif typeset -f _rick_check_p10k >/dev/null 2>&1 && _rick_check_p10k; then
    # Remove first if already present
    _rick_remove_p10k_segment
    
    # Get left elements array and insert at specific position
    local left_elements=("${POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[@]}")
    local new_left_elements=()
    
    # Insert at specified position
    local i=1
    for element in "${left_elements[@]}"; do
      if [[ $i -eq $position_index ]]; then
        new_left_elements+=("rick_assistant")
      fi
      new_left_elements+=("$element")
      ((i++))
    done
    
    # If position is beyond the array length, append at the end
    if [[ $position_index -gt ${#left_elements[@]} ]]; then
      new_left_elements+=("rick_assistant")
    fi
    
    # Set the new array
    POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=("${new_left_elements[@]}")
    
    RICK_DISPLAY_MODE="custom_position"
    RICK_INTEGRATION_ACTIVE=1
    return 0
  else
    # Fallback for other prompt systems or if Powerlevel10k not detected
    echo "Custom position mode requires Powerlevel10k. Falling back to right_prompt mode."
    _rick_handle_right_prompt_mode
    return 1
  fi
}

# Cleanup previous integration
_rick_cleanup_prompt_integration() {
  # Only cleanup if integration is active
  if [[ "$RICK_INTEGRATION_ACTIVE" -eq 0 ]]; then
    return 0
  fi
  
  case "$RICK_DISPLAY_MODE" in
    "segment")
      # Remove segment from Powerlevel10k
      if typeset -f _rick_remove_p10k_segment >/dev/null 2>&1; then
        _rick_remove_p10k_segment
      fi
      ;;
    "right_prompt")
      # Restore original right prompt
      RPROMPT="$RICK_ORIGINAL_RPROMPT"
      ;;
    "command_output")
      # Restore original precmd if we saved it
      if typeset -f _rick_original_precmd >/dev/null 2>&1; then
        # Use ZSH's native function copying instead of eval
        functions[precmd]=$functions[_rick_original_precmd]
        unset -f _rick_original_precmd
      fi
      ;;
    "custom_position")
      # Remove from custom position
      if typeset -f _rick_remove_p10k_segment >/dev/null 2>&1; then
        _rick_remove_p10k_segment
      fi
      ;;
  esac
  
  RICK_INTEGRATION_ACTIVE=0
  RICK_DISPLAY_MODE=""
  return 0
}

# Mode switcher function
rick_switch_prompt_mode() {
  local mode="$1"
  
  # Clean up existing integrations first
  _rick_cleanup_prompt_integration
  
  # Apply the selected mode
  case "$mode" in
    "segment")
      _rick_handle_segment_mode
      ;;
    "right_prompt")
      _rick_handle_right_prompt_mode
      ;;
    "command_output")
      _rick_handle_command_output_mode
      ;;
    "custom_position")
      _rick_handle_custom_position_mode
      ;;
    *)
      # Default to command_output as least intrusive
      echo "Unknown mode: $mode. Defaulting to command_output mode."
      _rick_handle_command_output_mode
      ;;
  esac
  
  # Save the mode selection if we have access to the Python module
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "from src.utils.config import set_config_value; set_config_value('prompt_integration.display_style', '$mode')" 2>/dev/null
  fi
  
  return 0
}

# Auto-detection function to determine the best mode based on environment
rick_detect_prompt_system() {
  # Check for Powerlevel10k
  if typeset -f _rick_check_p10k >/dev/null 2>&1 && _rick_check_p10k; then
    echo "powerlevel10k"
    return 0
  fi
  
  # Check for oh-my-zsh
  if [[ -n "$ZSH_VERSION" && -n "$ZSH" && -d "$ZSH/oh-my-zsh.sh" ]]; then
    echo "oh-my-zsh"
    return 0
  fi
  
  # Default fallback
  echo "standalone"
  return 0
}

# Auto-select the best mode based on environment
rick_auto_select_mode() {
  local system=$(rick_detect_prompt_system)
  
  case "$system" in
    "powerlevel10k")
      rick_switch_prompt_mode "segment"
      ;;
    "oh-my-zsh")
      rick_switch_prompt_mode "right_prompt"
      ;;
    *)
      rick_switch_prompt_mode "command_output"
      ;;
  esac
  
  return 0
} 