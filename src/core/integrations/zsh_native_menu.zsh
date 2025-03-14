#!/usr/bin/env zsh
# -*- mode: zsh; sh-indentation: 2; indent-tabs-mode: nil; sh-basic-offset: 2; -*-
# vim: ft=zsh sw=2 ts=2 et
#
# Zsh Native Menu System for Rick Assistant
# This replaces the Python implementation with native Zsh for better performance

# Terminal capabilities and styling
_RICK_MENU_SUPPORTS_COLOR=0
_RICK_MENU_SUPPORTS_UNICODE=0
_RICK_MENU_WIDTH=80
_RICK_MENU_HEIGHT=24

# Check if Python is available
_rick_check_python_available() {
  # Check for Python 3
  if command -v python3 >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Get config value helper
_rick_get_config_value() {
  local key="$1"
  local default="$2"
  
  # Use Python to get config value if available
  if _rick_check_python_available; then
    local value=$(python3 -c "from src.utils.config import get_config_value; print(get_config_value('$key', $default) if get_config_value('$key', $default) is not None else '$default')" 2>/dev/null)
    echo "$value"
  else
    # Return default if Python is not available
    echo "$default"
  fi
}

# Set config value helper
_rick_set_config_value() {
  local key="$1"
  local value="$2"
  
  # Use Python to set config value if available
  if _rick_check_python_available; then
    python3 -c "from src.utils.config import set_config_value; set_config_value('$key', $value)" 2>/dev/null
    return $?
  else
    # Return error if Python is not available
    return 1
  fi
}

# Color definitions
typeset -A RICK_MENU_COLORS
RICK_MENU_COLORS[header]="\033[1;36m"    # Cyan, bold
RICK_MENU_COLORS[title]="\033[1;32m"     # Green, bold
RICK_MENU_COLORS[selected]="\033[7;32m"  # Green, reverse video
RICK_MENU_COLORS[item]="\033[0;37m"      # White
RICK_MENU_COLORS[key]="\033[1;33m"       # Yellow, bold
RICK_MENU_COLORS[footer]="\033[0;36m"    # Cyan
RICK_MENU_COLORS[error]="\033[1;31m"     # Red, bold
RICK_MENU_COLORS[success]="\033[1;32m"   # Green, bold
RICK_MENU_COLORS[reset]="\033[0m"        # Reset

# Unicode symbols
typeset -A RICK_MENU_SYMBOLS
RICK_MENU_SYMBOLS[arrow]="→"
RICK_MENU_SYMBOLS[portal]="⊙"
RICK_MENU_SYMBOLS[checkbox_on]="✓"
RICK_MENU_SYMBOLS[checkbox_off]="✗"
RICK_MENU_SYMBOLS[bullet]="•"
RICK_MENU_SYMBOLS[bar_start]="┌"
RICK_MENU_SYMBOLS[bar_end]="┐"
RICK_MENU_SYMBOLS[footer_start]="└"
RICK_MENU_SYMBOLS[footer_end]="┘"

# ASCII fallbacks
typeset -A RICK_MENU_ASCII
RICK_MENU_ASCII[arrow]="->"
RICK_MENU_ASCII[portal]="O"
RICK_MENU_ASCII[checkbox_on]="[X]"
RICK_MENU_ASCII[checkbox_off]="[ ]"
RICK_MENU_ASCII[bullet]="*"
RICK_MENU_ASCII[bar_start]="+"
RICK_MENU_ASCII[bar_end]="+"
RICK_MENU_ASCII[footer_start]="+"
RICK_MENU_ASCII[footer_end]="+"

# Initialize menu system
_rick_menu_init() {
  # Detect terminal capabilities
  _rick_menu_detect_capabilities

  # Get terminal dimensions
  _rick_menu_get_terminal_size
  
  # Debug output
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && _rick_debug "Menu system initialized (color: $_RICK_MENU_SUPPORTS_COLOR, unicode: $_RICK_MENU_SUPPORTS_UNICODE, size: ${_RICK_MENU_WIDTH}x${_RICK_MENU_HEIGHT})"
}

# Detect terminal capabilities
_rick_menu_detect_capabilities() {
  # Check for color support
  if [[ -t 1 && -n "$TERM" && "$TERM" != "dumb" ]]; then
    local colors
    colors=$(tput colors 2>/dev/null || echo 0)
    if (( colors >= 8 )); then
      _RICK_MENU_SUPPORTS_COLOR=1
    fi
  fi
  
  # Check for Unicode support
  if [[ "$(locale charmap 2>/dev/null)" == *"UTF-8"* || "$LC_ALL" == *"UTF-8"* || "$LC_CTYPE" == *"UTF-8"* || "$LANG" == *"UTF-8"* ]]; then
    _RICK_MENU_SUPPORTS_UNICODE=1
  fi
  
  # Debug output
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && _rick_debug "Terminal capabilities: color=$_RICK_MENU_SUPPORTS_COLOR, unicode=$_RICK_MENU_SUPPORTS_UNICODE"
}

# Get terminal size
_rick_menu_get_terminal_size() {
  # Use "stty size" to get terminal dimensions
  if (( $+commands[stty] )); then
    local stty_output
    stty_output=$(stty size 2>/dev/null || echo "24 80")
    _RICK_MENU_HEIGHT=$(echo $stty_output | cut -d' ' -f1)
    _RICK_MENU_WIDTH=$(echo $stty_output | cut -d' ' -f2)
  # Alternative method using tput
  elif (( $+commands[tput] )); then
    _RICK_MENU_HEIGHT=$(tput lines 2>/dev/null || echo 24)
    _RICK_MENU_WIDTH=$(tput cols 2>/dev/null || echo 80)
  # Default fallback
  else
    _RICK_MENU_HEIGHT=24
    _RICK_MENU_WIDTH=80
  fi
  
  # Ensure values are reasonable
  (( _RICK_MENU_WIDTH < 40 )) && _RICK_MENU_WIDTH=40
  (( _RICK_MENU_HEIGHT < 10 )) && _RICK_MENU_HEIGHT=10
}

# Get a symbol (Unicode or ASCII fallback)
_rick_menu_symbol() {
  local symbol=$1
  
  if (( _RICK_MENU_SUPPORTS_UNICODE )); then
    echo -n "${RICK_MENU_SYMBOLS[$symbol]}"
  else
    echo -n "${RICK_MENU_ASCII[$symbol]}"
  fi
}

# Colorize text if color support is enabled
_rick_menu_colorize() {
  # Parameter validation
  if [[ $# -lt 2 ]]; then
    echo -n "$2"  # Just output the text if not enough parameters
    return 1
  fi
  
  local rick_color="$1"
  local rick_text="$2"
  
  if [[ -n "${_RICK_MENU_SUPPORTS_COLOR}" ]]; then
    # Ensure we're accessing the array properly with proper quoting
    echo -n "${RICK_MENU_COLORS[$rick_color]}${rick_text}${RICK_MENU_COLORS[reset]}"
  else
    echo -n "$rick_text"
  fi
}

# Clear screen
_rick_menu_clear() {
  # Use printf instead of echo for better compatibility with escape sequences
  printf "\033[H\033[2J\033[3J"
}

# Print a separator line
_rick_menu_separator() {
  local width=${1:-$_RICK_MENU_WIDTH}
  local char=${2:-"-"}
  local start_char=$(_rick_menu_symbol bar_start)
  local end_char=$(_rick_menu_symbol bar_end)
  
  # Print separator
  printf "$start_char"
  printf "%${width}s" | tr " " "$char"
  printf "$end_char\n"
}

# Print a separator line for footer
_rick_menu_footer_separator() {
  local width=${1:-$_RICK_MENU_WIDTH}
  local char=${2:-"-"}
  local start_char=$(_rick_menu_symbol footer_start)
  local end_char=$(_rick_menu_symbol footer_end)
  
  # Print separator
  printf "$start_char"
  printf "%${width}s" | tr " " "$char"
  printf "$end_char\n"
}

# Print centered text
_rick_menu_centered() {
  local text=$1
  local color=${2:-""}
  local width=${3:-$_RICK_MENU_WIDTH}
  
  # Calculate padding
  local text_length=${#text}
  local padding=$(( (width - text_length) / 2 ))
  
  # Print centered text
  printf "%${padding}s" ""
  if [[ -n "$color" ]]; then
    _rick_menu_colorize "$color" "$text"
  else
    echo -n "$text"
  fi
  printf "%${padding}s\n" ""
}

# Read a single keypress
_rick_menu_read_key() {
  local key=""
  local stty_settings=""
  
  # Prevent prompt expansion interference
  local -a precmd_functions
  local -a preexec_functions
  local PROMPT_COMMAND=""
  
  # Set errno to a non-EINTR value to prevent infinite loop in ZSH's sysread
  # This fixes a known bug in ZSH where errno=EINTR causes an infinite loop
  typeset -g errnoval=0
  
  # Standard pattern for guaranteed TTY state preservation
  {
    # Save terminal settings
    stty_settings=$(stty -g)
    
    # Set terminal to raw mode with explicit parameters to ensure predictable state
    stty raw -echo -icanon min 0 time 0
    
    # Flush input buffer first (discard any pending input)
    zle -I # Force ZLE input flush
    while read -t 0 -k 1 discard_input; do : ; done
    
    # Use a timeout to prevent hanging
    local -i i=0
    local read_success=0
    
    # Now perform the actual read with explicit timeout and multiple retries
    while (( i < 3 )) && (( read_success == 0 )); do
      # Try with progressively longer timeouts
      if read -t 0.$((i+1)) -k 1 key; then
        read_success=1
      fi
      ((i++))
    done
    
    # Handle empty reads with explicit default
    if [[ -z "$key" ]]; then
      key="TIMEOUT"
    fi
    
  } always {
    # Guaranteed terminal state restoration regardless of how function exits
    stty "$stty_settings"
    # Additional cleanup to ensure ZLE state is reset
    zle -R
  }
  
  # Handle escape sequences with proper timeout handling
  if [[ "$key" == $'\e' ]]; then
    # Read potential escape sequence
    local seq=''
    local seq2=''
    
    # Read with explicit timeout and error handling
    if ! read -t 0.1 -k 1 seq 2>/dev/null; then
      key="escape"
    elif [[ "$seq" == "[" ]]; then
      if ! read -t 0.1 -k 1 seq2 2>/dev/null; then
        key="escape"
      else
        case "$seq2" in
          A) key="up" ;;
          B) key="down" ;;
          C) key="right" ;;
          D) key="left" ;;
          H) key="home" ;;
          F) key="end" ;;
          3) 
            local seq3=''
            read -t 0.1 -k 1 seq3 2>/dev/null || true
            [[ "$seq3" == "~" ]] && key="delete" || key="escape"
            ;;
          *) key="escape" ;;
        esac
      fi
    else
      key="M-$seq"
    fi
  elif [[ "$key" == $'\n' ]]; then
    key="enter"
  elif [[ "$key" == $'\b' || "$key" == $'\177' ]]; then
    key="backspace"
  elif [[ "$key" == $'\t' ]]; then
    key="tab"
  elif [[ "$key" == $'\x20' ]]; then
    key="space"
  elif [[ "$key" == "TIMEOUT" ]]; then
    # Handle timeout/empty read explicitly
    key="timeout"
  fi
  
  # Return key
  echo "$key"
}

# Display a menu and get selection
rick_menu() {
  local title=$1
  shift
  
  # Parse menu items from arguments
  # Format: "key:label:command"
  local -a menu_items=("$@")
  local num_items=${#menu_items[@]}
  local selected=1
  local running=1
  local result=""
  
  # Initialize the menu system if needed
  _rick_menu_init
  
  # Display menu and handle interaction
  while (( running )); do
    # Clear screen
    _rick_menu_clear
    
    # Print Rick ASCII art banner
    cat <<'RICK'
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢰⠀⢀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢲⠶⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠈⣍⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⡄⠈⠑⠢⢄⡀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⣀⣤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⢵⠀⠀⠀⠀⠈⠓⠤⣤⠄⡼⠀⠀⠀⠀⠀⠘⣿⣿⣿⠤⠄⠀⣠⠴⠊⢡⣿⠀⠠⠤⣤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠈⠲⠃⠀⠀⠀⠀⠀⠀⢻⣿⡿⠗⠒⠉⠀⠀⠀⣾⣏⣠⣴⣾⡏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠂⠤⠄⣈⠁⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⡤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⢄⠀⠀⠀⠀⣼⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀
⠔⡀⠉⠉⠉⠉⠈⠉⠉⠉⠀⢀⠎⠀⠀⠀⠀⣀⠤⢒⡠⠖⠂⠀⣀⣀⣀⠱⡀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠑⣤⡀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠠⠄⠋⠒⢈⡠⠄⠒⣈⠡⠤⠐⠚⠁⠙⡄⠀⠙⠛⠛⠻⢿⡶⠓⢶⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠙⢢⡀⠀⠀⠀⠀⢰⢁⡤⠐⠒⠒⢊⣉⡠⠔⠚⠉⡀⠀⠀⠀⠈⠒⢄⠰⡀⠀⠀⠀⣠⠞⢀⣴⣯⣅⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠓⠤⡀⠀⠀⢸⠈⢉⠁⠉⠉⠀⠉⠢⡀⠀⡘⠀⢀⣀⣠⡤⠀⠘⢇⢣⠀⠀⣴⣭⣶⣿⣿⣿⣿⣿⡿⠟⠁
⠀⠀⠀⠀⠀⠀⠀⣀⠼⠃⠀⢸⣠⠃⠀⠀⠀⣀⡠⠤⠼⡀⢻⠉⠁⠀⠉⠀⠀⠀⡼⠸⡀⠀⠈⠻⢿⣿⣿⣿⠟⠉⠀⠀⠀
⠀⠀⢠⣠⠤⠒⠊⠁⠀⠀⠀⠈⡏⡦⠒⠈⠙⠃⠀⠀⢠⠇⠈⠢⣀⠀⠀⠀⣀⠔⠁⠀⣇⠀⠀⠀⢀⡽⠛⣿⣦⣀⡀⠀⠀
⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⢇⠘⢆⡀⠀⠀⢀⡠⠊⡄⠀⢰⠀⠉⠉⠉⣠⣴⠏⠀⣻⠒⢄⢰⣏⣤⣾⣿⣿⣿⣦⣄⠀
⠀⠀⠀⠀⠀⠀⠙⢻⣷⣦⡀⠀⢸⡀⠀⡈⠉⠉⢁⡠⠂⢸⠀⠀⡇⠙⠛⠛⠋⠁⠀⠀⣿⡇⢀⡟⣿⣿⣿⣿⣿⣿⠟⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⡴⠇⠀⠈⠉⠉⠀⠀⠀⠀⢣⣠⠇⠀⠀⠀⠀⠀⠀⠀⣿⣿⡟⠀⢻⠻⣿⡟⠉⠉⠉⠁⠀
⠀⠀⠀⠀⠀⠀⢀⡠⠖⠁⠀⢸⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠐⢶⣿⢷⣯⣭⣤⣶⣿⣿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠒⠛⠒⠒⠤⠤⢲⠑⠦⢧⠀⠀⠀⠀⢀⡤⢖⠂⠉⠉⡸⠁⠀⠀⠀⢀⣾⣾⠈⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠾⣿⠀⠀⠈⢆⠸⣄⠊⠁⠀⠀⡉⢆⠀⡆⣀⠀⠀⠀⣰⢿⣷⣶⣾⣿⣿⣏⠉⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠠⠴⢞⣿⢦⠀⠀⠀⠀⠀⠛⠀⠉⠁⠛⠃⢀⣴⣿⣾⣿⣿⣿⣿⡿⠿⠆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶⡷⢄⡀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⣿⠷⡖⠢⠤⠔⠒⠻⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢉⡩⢽⢻⠗⠤⢀⣀⣀⡠⢿⣿⣿⠿⣏⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠊⠁⢠⠊⣸⠀⠀⠀⠀⠀⠀⠀⢻⠈⢖⠂⢉⠒⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀

RICK
    
    # Print title
    _rick_menu_centered "$title" "title"
    
    # Print menu items
    local i
    for (( i = 1; i <= num_items; i++ )); do
      local item="${menu_items[$i]}"
      local key="${item%%:*}"
      local label="${${item#*:}%%:*}"
      
      # Format menu item
      if (( i == selected )); then
        # Selected item
        echo -n " "
        _rick_menu_colorize "selected" " $(_rick_menu_symbol arrow) [$key] $label "
        echo ""
      else
        # Unselected item
        echo -n "   "
        echo -n "["
        _rick_menu_colorize "key" "$key"
        echo -n "] "
        _rick_menu_colorize "item" "$label"
        echo ""
      fi
    done
    
    # Print footer with instructions
    echo ""
    _rick_menu_centered "Use arrow keys to navigate, Enter to select" "footer"
    _rick_menu_centered "Press q to quit" "footer"
    
    # Read key
    local key=$(_rick_menu_read_key)
    
    # Handle timeout explicitly
    if [[ "$key" == "timeout" ]]; then
      # If we get too many timeouts in a row, break the loop
      (( timeout_count = ${timeout_count:-0} + 1 ))
      if (( timeout_count > 5 )); then
        clear
        echo "Too many empty responses - exiting menu"
        running=0
        result=""
        break
      fi
      # Just continue the loop on timeout
      continue
    fi
    
    # Reset timeout counter on successful key
    timeout_count=0
    
    # Handle key
    case "$key" in
      up|k)
        # Move selection up
        (( selected-- ))
        (( selected < 1 )) && selected=$num_items
        ;;
      down|j)
        # Move selection down
        (( selected++ ))
        (( selected > num_items )) && selected=1
        ;;
      enter|space)
        # Select item
        local selected_item="${menu_items[$selected]}"
        local command="${selected_item##*:}"
        
        # Execute command or return result
        if [[ -n "$command" ]]; then
          result="$command"
          running=0
        fi
        ;;
      q|Q)
        # Quit
        result=""
        running=0
        ;;
      *)
        # Check for hotkey matches
        local i
        for (( i = 1; i <= num_items; i++ )); do
          local item="${menu_items[$i]}"
          local item_key="${item%%:*}"
          
          if [[ "$key" == "$item_key" ]]; then
            local command="${item##*:}"
            result="$command"
            running=0
            break
          fi
        done
        ;;
    esac
  done
  
  # Clear screen before returning
  _rick_menu_clear
  
  # Return result
  echo "$result"
}

# Display a simple message box
rick_message_box() {
  local title=$1
  local message=$2
  local type=${3:-"info"}  # info, success, error, warning
  
  # Initialize the menu system if needed
  _rick_menu_init
  
  # Clear screen
  _rick_menu_clear
  
  # Determine color based on message type
  local color
  case "$type" in
    error) color="error" ;;
    success) color="success" ;;
    warning) color="key" ;;
    *) color="title" ;;
  esac
  
  # Print title
  _rick_menu_centered "$title" "$color"
  
  # Print separator
  echo ""
  
  # Print message (handle multi-line)
  echo "$message" | while IFS= read -r line; do
    _rick_menu_centered "$line" "item"
  done
  
  # Print footer
  echo ""
  _rick_menu_centered "Press any key to continue" "footer"
  
  # Wait for key press
  _rick_menu_read_key >/dev/null
  
  # Clear screen before returning
  _rick_menu_clear
}

# Implementation of rick menu command
_rick_impl_menu() {
  local menu_type="${1:-main}"
  
  # Only shift if we have parameters
  if [[ $# -gt 0 ]]; then
    shift 1
  fi
  
  case "$menu_type" in
    main)
      # Call our new main menu implementation
      _rick_menu_main
      ;;
    settings)
      # Call our new settings menu implementation
      _rick_menu_settings
      ;;
    status)
      # Status menu
      _rick_menu_status
      ;;
    help)
      echo "Rick menu system:"
      echo "Available types: main, settings, status, help"
      ;;
    *)
      # Default to main menu
      _rick_menu_main
      ;;
  esac
}

# Command for displaying temperature status
rick_temperature_status() {
  # Get temperature based on platform
  local temp=""
  local platform=$(uname -s)
  
  case "$platform" in
    Linux)
      if [[ -n "$(uname -r | grep -i microsoft)" ]]; then
        # Windows WSL
        temp=$(_rick_get_windows_temperature)
      else
        # Native Linux
        temp=$(_rick_get_linux_temperature)
      fi
      ;;
    Darwin)
      # macOS
      temp=$(_rick_get_macos_temperature)
      ;;
  esac
  
  # If no temperature available, return message
  if [[ -z "$temp" ]]; then
    echo "Temperature monitoring not available."
    return 0
  fi
  
  # Check threshold
  local level=$(_rick_check_temp_threshold "$temp")
  
  # Format output
  echo "CPU Temperature: ${temp}°C (${(U)level})"
  
  return 0
}

# Implementation of the settings menu
_rick_menu_settings() {
    local rick_status=0
    _rick_menu_clear
    
    local menu_title="Rick Assistant Settings"
    local menu_prompt="Select a setting to change:"
    local menu_options=()
    local menu_actions=()
    
    # Get current Python preference (if we can)
    local use_python=false
    if _rick_check_python_available; then
        use_python=$(_rick_get_config_value "menu.use_python_implementation" "false")
    fi
    
    # Add menu options
    menu_options+=("Use Python Menu Implementation: ${use_python}")
    menu_actions+=("_rick_toggle_python_menu")
    
    menu_options+=("Return to main menu")
    menu_actions+=("return 0")
    
    # Display menu
    _rick_display_menu "$menu_title" "$menu_prompt" menu_options menu_actions
    return $?
}

# Toggle Python menu implementation
_rick_toggle_python_menu() {
    local current_value=$(_rick_get_config_value "menu.use_python_implementation" "false")
    
    # Toggle the value
    if [[ "$current_value" == "true" ]]; then
        _rick_set_config_value "menu.use_python_implementation" "false"
        echo "Menu implementation set to Native ZSH (faster)"
    else
        _rick_set_config_value "menu.use_python_implementation" "true"
        echo "Menu implementation set to Python (more features)"
    fi
    
    # Pause to show the message
    echo "Press any key to continue..."
    read -k 1
    
    # Return to settings menu
    _rick_menu_settings
}

# Initialize the menu system
_rick_menu_init

# Display a menu with array parameters
_rick_display_menu() {
    local title="$1"
    local prompt="$2"
    local -n options_array="$3"
    local -n actions_array="$4"
    
    # Clear screen
    _rick_menu_clear
    
    # Variables for menu state
    local selected=1
    local num_items=${#options_array[@]}
    local running=1
    local result=""
    
    # Display menu and handle interaction
    while (( running )); do
        # Clear screen
        _rick_menu_clear
        
        # Print Rick ASCII art banner
        cat <<'RICK'
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢰⠀⢀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢲⠶⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠈⣍⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⡄⠈⠑⠢⢄⡀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⣀⣤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⢵⠀⠀⠀⠀⠈⠓⠤⣤⠄⡼⠀⠀⠀⠀⠀⠘⣿⣿⣿⠤⠄⠀⣠⠴⠊⢡⣿⠀⠠⠤⣤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠈⠲⠃⠀⠀⠀⠀⠀⠀⢻⣿⡿⠗⠒⠉⠀⠀⠀⣾⣏⣠⣴⣾⡏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠂⠤⠄⣈⠁⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⡤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⢄⠀⠀⠀⠀⣼⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀
⠔⡀⠉⠉⠉⠉⠈⠉⠉⠉⠀⢀⠎⠀⠀⠀⠀⣀⠤⢒⡠⠖⠂⠀⣀⣀⣀⠱⡀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠑⣤⡀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠠⠄⠋⠒⢈⡠⠄⠒⣈⠡⠤⠐⠚⠁⠙⡄⠀⠙⠛⠛⠻⢿⡶⠓⢶⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠙⢢⡀⠀⠀⠀⠀⢰⢁⡤⠐⠒⠒⢊⣉⡠⠔⠚⠉⡀⠀⠀⠀⠈⠒⢄⠰⡀⠀⠀⠀⣠⠞⢀⣴⣯⣅⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠓⠤⡀⠀⠀⢸⠈⢉⠁⠉⠉⠀⠉⠢⡀⠀⡘⠀⢀⣀⣠⡤⠀⠘⢇⢣⠀⠀⣴⣭⣶⣿⣿⣿⣿⣿⡿⠟⠁
⠀⠀⠀⠀⠀⠀⠀⣀⠼⠃⠀⢸⣠⠃⠀⠀⠀⣀⡠⠤⠼⡀⢻⠉⠁⠀⠉⠀⠀⠀⡼⠸⡀⠀⠈⠻⢿⣿⣿⣿⠟⠉⠀⠀⠀
⠀⠀⢠⣠⠤⠒⠊⠁⠀⠀⠀⠈⡏⡦⠒⠈⠙⠃⠀⠀⢠⠇⠈⠢⣀⠀⠀⠀⣀⠔⠁⠀⣇⠀⠀⠀⢀⡽⠛⣿⣦⣀⡀⠀⠀
⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⢇⠘⢆⡀⠀⠀⢀⡠⠊⡄⠀⢰⠀⠉⠉⠉⣠⣴⠏⠀⣻⠒⢄⢰⣏⣤⣾⣿⣿⣿⣦⣄⠀
⠀⠀⠀⠀⠀⠀⠙⢻⣷⣦⡀⠀⢸⡀⠀⡈⠉⠉⢁⡠⠂⢸⠀⠀⡇⠙⠛⠛⠋⠁⠀⠀⣿⡇⢀⡟⣿⣿⣿⣿⣿⣿⠟⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⡴⠇⠀⠈⠉⠉⠀⠀⠀⠀⢣⣠⠇⠀⠀⠀⠀⠀⠀⠀⣿⣿⡟⠀⢻⠻⣿⡟⠉⠉⠉⠁⠀
⠀⠀⠀⠀⠀⠀⢀⡠⠖⠁⠀⢸⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠐⢶⣿⢷⣯⣭⣤⣶⣿⣿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠒⠛⠒⠒⠤⠤⢲⠑⠦⢧⠀⠀⠀⠀⢀⡤⢖⠂⠉⠉⡸⠁⠀⠀⠀⢀⣾⣾⠈⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠾⣿⠀⠀⠈⢆⠸⣄⠊⠁⠀⠀⡉⢆⠀⡆⣀⠀⠀⠀⣰⢿⣷⣶⣾⣿⣿⣏⠉⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠠⠴⢞⣿⢦⠀⠀⠀⠀⠀⠛⠀⠉⠁⠛⠃⢀⣴⣿⣾⣿⣿⣿⣿⡿⠿⠆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶⡷⢄⡀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⣿⠷⡖⠢⠤⠔⠒⠻⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢉⡩⢽⢻⠗⠤⢀⣀⣀⡠⢿⣿⣿⠿⣏⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠊⠁⢠⠊⣸⠀⠀⠀⠀⠀⠀⠀⢻⠈⢖⠂⢉⠒⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
RICK
        
        # Print title
        _rick_menu_centered "$title" "title"
        
        # Print prompt
        echo
        _rick_menu_centered "$prompt" "prompt"
        echo
        
        # Print menu items
        local i
        for (( i = 1; i <= num_items; i++ )); do
            local item="${options_array[$i]}"
            
            # Format menu item
            if (( i == selected )); then
                # Selected item
                echo -n " "
                _rick_menu_colorize "selected" " $(_rick_menu_symbol arrow) $item "
                echo ""
            else
                # Unselected item
                echo -n "   "
                _rick_menu_colorize "item" "$item"
                echo ""
            fi
        done
        
        # Get key press
        local key
        read -sk key
        
        # Handle key press
        case "$key" in
            $'\e')  # ESC sequence
                read -sk key
                if [[ "$key" == "[" ]]; then
                    read -sk key
                    case "$key" in
                        "A")  # Up arrow
                            (( selected = selected - 1 ))
                            if (( selected < 1 )); then
                                selected=$num_items
                            fi
                            ;;
                        "B")  # Down arrow
                            (( selected = selected + 1 ))
                            if (( selected > num_items )); then
                                selected=1
                            fi
                            ;;
                    esac
                fi
                ;;
            
            "k")  # Up
                (( selected = selected - 1 ))
                if (( selected < 1 )); then
                    selected=$num_items
                fi
                ;;
            
            "j")  # Down
                (( selected = selected + 1 ))
                if (( selected > num_items )); then
                    selected=1
                fi
                ;;
            
            $'\n')  # Enter
                running=0
                # Execute the action for the selected item
                eval "${actions_array[$selected]}"
                break
                ;;
            
            "q")  # Quit
                running=0
                return 1
                ;;
        esac
    done
    
    return 0
}

# Main menu implementation
_rick_menu_main() {
    local rick_status=0
    _rick_menu_clear
    
    local menu_title="Rick Assistant Main Menu"
    local menu_prompt="Select an option, Mo*buuurp*orty:"
    local menu_options=()
    local menu_actions=()
    
    # Add menu options
    menu_options+=("Status")
    menu_actions+=("_rick_menu_status")
    
    menu_options+=("Settings")
    menu_actions+=("_rick_menu_settings")
    
    menu_options+=("Help")
    menu_actions+=("_rick_menu_help")
    
    menu_options+=("Exit")
    menu_actions+=("return 0")
    
    # Display menu
    _rick_display_menu "$menu_title" "$menu_prompt" menu_options menu_actions
    return $?
}

# Implementation of status menu
_rick_menu_status() {
    local rick_status=0
    _rick_menu_clear
    
    # Get status information
    local status_text=$(rick status)
    
    # Print status
    echo
    echo "$status_text"
    echo
    echo "Press any key to return to main menu..."
    read -sk
    
    # Return to main menu
    _rick_menu_main
    return 0
}

# Implementation of help menu
_rick_menu_help() {
    local rick_status=0
    _rick_menu_clear
    
    # Get help information
    local help_text=$(rick help)
    
    # Print help
    echo
    echo "$help_text"
    echo
    echo "Press any key to return to main menu..."
    read -sk
    
    # Return to main menu
    _rick_menu_main
    return 0
}