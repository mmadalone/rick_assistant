#!/usr/bin/env zsh
# Rick Assistant - Menu system

# Check if running with sufficient permissions
if [[ -z "$ZSH_VERSION" ]]; then
  echo "Error: This script must be run with zsh."
  return 1
fi

# Global variable to track if menu is running
typeset -g _RICK_MENU_RUNNING=0

# Thorough cleanup function to reset terminal state
_rick_menu_cleanup() {
  # Only perform cleanup if the menu is running
  if [[ $_RICK_MENU_RUNNING -eq 1 ]]; then
    # Reset flag
    _RICK_MENU_RUNNING=0
    
    # Reset terminal state completely
    stty sane
    
    # Force terminal into canonical mode
    stty icanon echo
    
    # Ensure cursor is visible
    tput cnorm
    
    # Clear screen
    clear
    
    # Force ZLE reset if available
    if typeset -f zle >/dev/null 2>&1; then
      zle -R
      # Reset line editor if active
      zle -I
    fi
    
    # Additional terminal reset sequence
    echo -ne "\033c\033]104\007"
    
    # Indicate cleanup was performed
    echo "Terminal state has been reset."
  fi
}

# Define menu command
rick-menu() {
  # Set flag that menu is running
  _RICK_MENU_RUNNING=1
  
  # Set cleanup trap for various signals
  trap '_rick_menu_cleanup; return 0' EXIT INT TERM HUP QUIT
  
  # Check if executed with arguments
  if [[ $# -gt 0 ]]; then
    case "$1" in
      "help")
        echo "Rick Assistant Menu"
        echo "-------------------"
        echo "Usage: rick menu [command]"
        echo
        echo "Commands:"
        echo "  help      Display this help message"
        echo "  version   Display version information"
        echo "  settings  Open settings menu directly"
        echo "  brain     Open brain module menu directly"
        echo "  shell     Open shell commands menu directly"
        echo "  monitor   Open system monitoring directly"
        _RICK_MENU_RUNNING=0
        return 0
        ;;
      "version")
        local version=$(grep 'version' "${${(%):-%x}:A:h}/rick_assistant.plugin.zsh" | cut -d '"' -f2)
        echo "Rick Assistant Menu v${version:-unknown}"
        _RICK_MENU_RUNNING=0
        return 0
        ;;
      "settings")
        _rick_menu_settings_simple_arrows
        local ret=$?
        _RICK_MENU_RUNNING=0
        return $ret
        ;;
      "brain")
        _rick_menu_brain_simple_arrows
        local ret=$?
        _RICK_MENU_RUNNING=0
        return $ret
        ;;
      "shell")
        _rick_menu_shell_simple_arrows
        local ret=$?
        _RICK_MENU_RUNNING=0
        return $ret
        ;;
      "monitor")
        _rick_menu_monitoring_simple_arrows
        local ret=$?
        _RICK_MENU_RUNNING=0
        return $ret
        ;;
      *)
        echo "Unknown command: $1"
        echo "Run 'rick menu help' for usage information."
        _RICK_MENU_RUNNING=0
        return 1
        ;;
    esac
  fi
  
  # Check if menu functions are available
  if ! type _rick_menu_main >/dev/null 2>&1; then
    echo "Error: Menu functions not found."
    _RICK_MENU_RUNNING=0
    return 1
  fi
  
  # Run the main menu
  _rick_menu_main
  local ret=$?
  _RICK_MENU_RUNNING=0
  return $ret
}

# Create safe alias function to ensure proper cleanup
rickm() {
  # Execute the menu function and capture return value
  rick-menu "$@"
  local ret=$?
  
  # Ensure terminal state is restored
  _rick_menu_cleanup
  
  # Return the original return value
  return $ret
}

# Export the functions
export -f rick-menu
export -f rickm
export -f _rick_menu_cleanup 