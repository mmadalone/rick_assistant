#!/usr/bin/env zsh
#
# Rick Assistant - A Rick Sanchez-themed AI assistant for ZSH
# GitHub: [Your GitHub URL]
# License: MIT
#

# Check for P10k Instant Prompt (must be at the top)
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Define plugin directory
RICK_ASSISTANT_DIR="${0:A:h}"
RICK_ASSISTANT_VERSION="1.0.0"

# Define functions directory
RICK_ASSISTANT_FUNCTIONS_DIR="${RICK_ASSISTANT_DIR}/functions"

# Add functions directory to fpath
fpath=("${RICK_ASSISTANT_FUNCTIONS_DIR}" $fpath)

# Save original rm alias state if it exists
if alias rm &>/dev/null; then
  _RICK_ORIGINAL_RM_ALIAS=$(alias rm)
else
  _RICK_ORIGINAL_RM_ALIAS=""
fi

# Temporarily unalias rm during plugin loading to avoid interactive prompts
unalias rm 2>/dev/null || true

# Get the absolute path to this script
if [[ -n "$RICK_ASSISTANT_SCRIPT_DIR" && -d "$RICK_ASSISTANT_SCRIPT_DIR" ]]; then
  # Use existing script dir path if already set
  :
else
  # Detect script directory with ZSH-specific approach
  RICK_ASSISTANT_SCRIPT_DIR="${0:A:h}"
fi

# Add the script directory to path if not already there
if [[ ":$PATH:" != *":$RICK_ASSISTANT_SCRIPT_DIR:"* ]]; then
  export PATH="$PATH:$RICK_ASSISTANT_SCRIPT_DIR"
fi

# Debug mode detection (from environment or zstyle)
if [[ -n "$RICK_ASSISTANT_DEBUG" ]]; then
  # Debug already enabled from environment
  :
else
  # Check for debug setting in zstyle
  zstyle -t ':plugin:rick' debug && RICK_ASSISTANT_DEBUG=1
fi

# Set RICK_DEBUG for compatibility with new architecture
typeset -gi RICK_DEBUG=${RICK_ASSISTANT_DEBUG:-0}

# Debug information
if (( RICK_DEBUG )); then
  print -P "%F{cyan}Rick Assistant:%f Loading plugin from $RICK_ASSISTANT_SCRIPT_DIR"
  print -P "%F{cyan}Rick Assistant:%f Debug mode enabled"
fi

# Source utility files
if [[ -f "${RICK_ASSISTANT_DIR}/rick-utils.zsh" ]]; then
  source "${RICK_ASSISTANT_DIR}/rick-utils.zsh"
else
  print -P "%F{yellow}Rick WARNING:%f Could not find rick-utils.zsh"
fi

# Autoload all functions in the functions directory
if [[ -d "${RICK_ASSISTANT_FUNCTIONS_DIR}" ]]; then
  for func_file in "${RICK_ASSISTANT_FUNCTIONS_DIR}/_rick_"*; do
    if [[ -f "$func_file" ]]; then
      func_name=$(basename "$func_file")
      autoload -U "$func_name"
    fi
  done
fi

# Function to check if Python is available
_rick_has_python() {
  # First try with 'python3' command
  if command -v python3 >/dev/null 2>&1; then
    # Verify it actually works by trying to run a simple command
    if python3 -c "print('test')" >/dev/null 2>&1; then
      return 0
    fi
  fi
  
  # Then try with just 'python' command
  if command -v python >/dev/null 2>&1; then
    # Verify it actually works by trying to run a simple command
    if python -c "print('test')" >/dev/null 2>&1; then
      return 0
    fi
  fi
  
  # Python is not available or doesn't work
  return 1
}

# Function to get config value
_rick_get_config() {
  local key="$1"
  local default="$2"
  local config_file="${HOME}/.rick_assistant/config.json"
  
  # Use Python if available for more robust config parsing
  if _rick_has_python; then
    local value=$(python3 -c "
import json, os, sys
try:
    config_file = os.path.expanduser('$config_file')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(config.get('$key', '$default'))
    else:
        print('$default')
except Exception as e:
    print('$default')
    " 2>/dev/null)
    echo "$value"
  else
    # Simple fallback if Python isn't available
    if [[ -f "$config_file" ]]; then
      local value=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$config_file" | grep -o "[^\"]*\"$" | tr -d '"' 2>/dev/null)
      if [[ -n "$value" ]]; then
        echo "$value"
      else
        echo "$default"
      fi
    else
      echo "$default"
    fi
  fi
}

# Function to determine the best menu implementation
_rick_determine_menu_implementation() {
  local config_value=$(_rick_get_config "ui___menu___use_python_implementation" "auto")
  local has_python=$(_rick_has_python && echo "true" || echo "false")
  
  # If Python is explicitly requested but not available, show warning
  if [[ "$config_value" == "true" && "$has_python" == "false" ]]; then
    echo "Warning: Python implementation requested but Python is not available. Using ZSH native menu." >&2
    return 1
  fi
  
  # If Python is explicitly disabled, use ZSH native
  if [[ "$config_value" == "false" ]]; then
    return 1
  fi
  
  # If setting is 'auto', use Python if available, otherwise ZSH native
  if [[ "$config_value" == "auto" ]]; then
    if [[ "$has_python" == "true" ]]; then
      return 0
    else
      # No warning needed for auto mode
      return 1
    fi
  fi
  
  # Handle explicit "true" when Python is available
  if [[ "$config_value" == "true" && "$has_python" == "true" ]]; then
    return 0
  fi
  
  # Default fallback to ZSH native
  return 1
}

# Register the main commands
rick() {
  local cmd="${1:-help}"
  shift 2>/dev/null || true

  case "$cmd" in
    menu)
      # Determine which menu implementation to use
      if _rick_determine_menu_implementation; then
        # Use Python implementation
        if [[ -f "${RICK_ASSISTANT_SCRIPT_DIR}/src/core/menu_launcher.py" ]]; then
          python3 "${RICK_ASSISTANT_SCRIPT_DIR}/src/core/menu_launcher.py" "$@"
        else
          # Fallback to ZSH implementation with warning
          echo "Warning: Python menu requested but menu_launcher.py not found. Using ZSH implementation."
          _rick_menu_main "$@" || echo "⚠️ Menu closed unexpectedly. Please check RICK_DEBUG=1 for more details."
        fi
      else
        # Use ZSH native implementation
        
        # Run the menu with error handling
        if ! _rick_menu_main "$@" 2>/dev/null; then
          if (( RICK_DEBUG )); then
            echo "⚠️ Error in menu navigation. Try running with RICK_DEBUG=1 for more details."
          else
            # Rickified error message
            echo "Ugh, *buuurp* looks like the ZSH menu got lost in a parallel dimension. Try with RICK_DEBUG=1 for more info."
          fi
        fi
      fi
      ;;
    help)
      echo "Rick Assistant Help"
      echo "------------------"
      echo "menu      - Open the Rick Assistant menu"
      echo "help      - Show this help message"
      echo "version   - Show version information"
      ;;
    version)
      echo "Rick Assistant v${RICK_ASSISTANT_VERSION}"
      ;;
    *)
      rick help
      ;;
  esac
}

# Alias for rick menu
alias rickm='rick menu'

# Print welcome message
if [[ -z $RICK_ASSISTANT_QUIET ]]; then
  echo "Rick Assistant v${RICK_ASSISTANT_VERSION} loaded. Wubba lubba dub dub!"
fi

# Restore rm alias if it was temporarily unaliased
if [[ -n "$_RICK_ORIGINAL_RM_ALIAS" ]]; then
  eval "$_RICK_ORIGINAL_RM_ALIAS"
fi

# Export key variables
export RICK_ASSISTANT_VERSION
export RICK_ASSISTANT_SCRIPT_DIR

# Register completions
if [[ -f "${RICK_ASSISTANT_SCRIPT_DIR}/functions/completion/_rick" ]]; then
  compdef _rick rick
fi

# Return success
return 0
