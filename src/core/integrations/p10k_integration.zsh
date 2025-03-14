#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Integration
# This script integrates Rick Assistant with Powerlevel10k
#

# Debug mode flag - set to 1 to enable debug output
RICK_DEBUG=0

# Define colors for output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[0;33m'
blue='\033[0;34m'
nc='\033[0m' # No Color

# Debug function - only prints when debug is enabled and output not suppressed
rick_debug() {
  # Skip output if RICK_SUPPRESS_OUTPUT is set
  if [[ -n "$RICK_SUPPRESS_OUTPUT" ]]; then
    return 0
  fi
  
  if [[ "$RICK_DEBUG" == "1" ]]; then
    echo -e "${blue}[RICK_DEBUG]${nc} $1" >&2
  fi
}

# Info output function - respects suppression flag
rick_info() {
  # Skip output if RICK_SUPPRESS_OUTPUT is set
  if [[ -n "$RICK_SUPPRESS_OUTPUT" ]]; then
    return 0
  fi
  
  echo -e "${green}[RICK]${nc} $1" >&2
}

# Warning output function - respects suppression flag
rick_warn() {
  # Skip output if RICK_SUPPRESS_OUTPUT is set
  if [[ -n "$RICK_SUPPRESS_OUTPUT" ]]; then
    return 0
  fi
  
  echo -e "${yellow}[RICK_WARN]${nc} $1" >&2
}

# Error output function - always shown regardless of suppression flag
rick_error() {
  echo -e "${red}[RICK_ERROR]${nc} $1" >&2
}

# Location of p10k.zsh configuration
P10K_CONFIG="${ZDOTDIR:-$HOME}/.p10k.zsh"
BACKUP_DIR="${ZDOTDIR:-$HOME}/.rick_assistant/backups"

# Setup backup directory
if [[ ! -d "$BACKUP_DIR" ]]; then
  mkdir -p "$BACKUP_DIR" || {
    rick_error "Failed to create backup directory: $BACKUP_DIR"
    exit 1
  }
fi

# Backup current p10k.zsh configuration
backup_p10k_config() {
  if [[ -f "$P10K_CONFIG" ]]; then
    local timestamp=$(date +"%Y%m%d%H%M%S")
    local backup_file="$BACKUP_DIR/p10k.zsh.backup.$timestamp"
    cp "$P10K_CONFIG" "$backup_file" || {
      rick_error "Failed to backup p10k.zsh to $backup_file"
      return 1
    }
    rick_debug "Created backup of p10k.zsh at $backup_file"
    rick_info "Backed up p10k.zsh to $backup_file"
    return 0
  else
    rick_error "Error: $P10K_CONFIG not found"
    return 1
  fi
}

# Check if the Rick Assistant segment is already defined in p10k.zsh
is_rick_segment_defined() {
  if [[ -f "$P10K_CONFIG" ]]; then
    grep -q "function prompt_rick_assistant" "$P10K_CONFIG"
    return $?
  fi
  return 1
}

# Add Rick Assistant segment to p10k.zsh
add_rick_segment() {
  if [[ ! -f "$P10K_CONFIG" ]]; then
    rick_error "Error: p10k.zsh not found"
    return 1
  fi
  
  # Find the setup file in multiple possible locations
  local setup_file=""
  local possible_paths=(
    "${ZDOTDIR:-$HOME}/.oh-my-zsh/custom/plugins/rick_assistant/src/core/integrations/p10k_setup.zsh"
    "${PWD}/src/core/integrations/p10k_setup.zsh"
    "${0:A:h}/p10k_setup.zsh" # Directory of this script
  )
  
  for path in "${possible_paths[@]}"; do
    if [[ -f "$path" ]]; then
      setup_file="$path"
      break
    fi
  done
  
  if [[ -z "$setup_file" ]]; then
    rick_error "Error: p10k_setup.zsh not found in any expected location"
    return 1
  fi
  
  rick_debug "Found setup file at: $setup_file"
  
  # Add the functions to p10k.zsh
  cat "$setup_file" >> "$P10K_CONFIG" || {
    rick_error "Failed to append setup content to p10k.zsh"
    return 1
  }
  
  rick_info "Added Rick Assistant segment to p10k.zsh"
  return 0
}

# Update prompt elements to include Rick Assistant
update_prompt_elements() {
  local position="$1"
  if [[ ! -f "$P10K_CONFIG" ]]; then
    rick_error "Error: p10k.zsh not found"
    return 1
  fi
  
  # Set default position if not specified
  position="${position:-right}"
  
  # Export the position for use in the segment
  export RICK_POSITION="$position"
  
  rick_debug "Setting RICK_POSITION to $position"
  
  # Different logic based on position
  if [[ "$position" == "right" ]]; then
    # Add to right prompt elements
    if grep -q "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(" "$P10K_CONFIG"; then
      # Check if rick_assistant is already in the array
      if ! grep -q "rick_assistant" "$P10K_CONFIG"; then
        # Add rick_assistant to right prompt elements
        sed -i.bak 's/POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(/POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(\n    rick_assistant/' "$P10K_CONFIG" || {
          rick_error "Failed to update right prompt elements"
          return 1
        }
      fi
    fi
  elif [[ "$position" == "left" ]]; then
    # Add to left prompt elements
    if grep -q "POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(" "$P10K_CONFIG"; then
      # Check if rick_assistant is already in the array
      if ! grep -q "rick_assistant" "$P10K_CONFIG"; then
        # Add rick_assistant to left prompt elements
        sed -i.bak 's/POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(/POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(\n    rick_assistant/' "$P10K_CONFIG" || {
          rick_error "Failed to update left prompt elements"
          return 1
        }
      fi
    fi
  elif [[ "$position" == "dir" || "$position" == "custom_position" ]]; then
    # Replace dir segment with rick_assistant
    if grep -q "POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(" "$P10K_CONFIG"; then
      # Remove existing rick_assistant if there
      sed -i.bak '/rick_assistant/d' "$P10K_CONFIG" || {
        rick_error "Failed to remove existing rick_assistant references"
        return 1
      }
      
      # Replace dir with rick_assistant
      sed -i.bak 's/\bdir\b/rick_assistant/' "$P10K_CONFIG" || {
        rick_error "Failed to replace dir with rick_assistant"
        return 1
      }
    fi
  else
    rick_error "Error: Invalid position '$position'. Use 'left', 'right', or 'dir'."
    return 1
  fi
  
  # Cleanup backup files
  rm -f "$P10K_CONFIG.bak" 2>/dev/null
  
  rick_info "Updated prompt elements to include Rick Assistant in the $position position"
  return 0
}

# Configure p10k with Rick Assistant
configure_rick_assistant() {
  local position="$1"
  
  # Validate p10k is installed
  if ! command -v p10k &> /dev/null; then
    rick_error "Error: Powerlevel10k not installed"
    rick_info "Run: git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \${ZSH_CUSTOM:-\$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
    rick_info "Then set ZSH_THEME=\"powerlevel10k/powerlevel10k\" in your .zshrc"
    return 1
  fi
  
  # Backup current configuration
  backup_p10k_config || return 1
  
  # Check if segment is already defined
  if ! is_rick_segment_defined; then
    # Add Rick Assistant segment
    add_rick_segment || return 1
  else
    rick_warn "Rick Assistant segment already defined in p10k.zsh"
  fi
  
  # Update prompt elements
  update_prompt_elements "$position" || return 1
  
  # Save the position to configuration if Python is available
  if command -v python3 &> /dev/null; then
    python3 -c "
try:
    from src.utils.config import set_config_value
    set_config_value('powerlevel10k.position', '$position')
    print('[RICK] Saved position setting to config')
except Exception as e:
    print(f'[RICK_ERROR] Failed to save position to config: {str(e)}')
" 2>/dev/null
  fi
  
  # Reload p10k configuration
  if command -v p10k &> /dev/null; then
    p10k reload || {
      rick_warn "Failed to reload p10k configuration"
      rick_info "Please restart your shell to see the changes"
    }
    rick_info "Powerlevel10k configuration reloaded"
  else
    rick_warn "Please reload your shell to see the changes"
  fi
  
  rick_info "Rick Assistant successfully integrated with Powerlevel10k!"
  rick_info "You can now see Rick's wisdom in your ${position} prompt"
  rick_info "To change position, run: rick p10k [left|right|dir]"
  rick_info "To run diagnostics, run: rick diagnose"
  
  # Success
  return 0
}

# Main function
main() {
  local position="$1"
  
  # Check for debug flag
  if [[ "$position" == "--debug" ]]; then
    RICK_DEBUG=1
    position="$2"
    rick_debug "Debug mode enabled"
  fi
  
  # Show help if requested
  if [[ "$position" == "help" ]]; then
    echo "Usage: rick p10k [position]"
    echo ""
    echo "Positions:"
    echo "  left           Add Rick Assistant to the left prompt"
    echo "  right          Add Rick Assistant to the right prompt (default)"
    echo "  dir            Replace the directory segment with Rick Assistant"
    echo "  custom_position Same as dir but a different command name"
    echo "  help           Show this help message"
    echo ""
    echo "Options:"
    echo "  --debug        Enable debug output"
    return 0
  fi
  
  # Configure Rick Assistant
  configure_rick_assistant "$position"
  return $?
}

# Call main function with all arguments
main "$@" 