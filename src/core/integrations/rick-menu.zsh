#!/usr/bin/env zsh
# rick-menu.zsh - Menu system for Rick Assistant using autoloadable functions
#
# This module provides a terminal-based menu system for the Rick Assistant.
# It relies on autoloadable functions for component functionality.

# Ensure the core module is loaded
(( ${+functions[rick_core_module_load]} )) || source "${0:A:h}/rick-core.zsh"

# Register this module
rick_core_module_load "menu" "${0:A}" || return 1

# Register autoloadable functions - core utilities
rick_core_register_function "_rick_menu_colorize" "private"
rick_core_register_function "_rick_menu_clear" "private"
rick_core_register_function "_rick_menu_symbol" "private"
rick_core_register_function "_rick_menu_centered" "private"
rick_core_register_function "_rick_menu_separator" "private"
rick_core_register_function "_rick_menu_item" "private"
rick_core_register_function "_rick_menu_detect_terminal" "private"
rick_core_register_function "_rick_menu_read_key" "private"
rick_core_register_function "_rick_menu_handle_key" "private"
rick_core_register_function "_rick_utils" "private"

# Load utility functions
if (( ${+functions[_rick_utils]} )); then
  _rick_utils
else
  echo "Warning: _rick_utils not found, some menu functions may not work" >&2
fi

# Register utility functions 
rick_core_register_function "get_cpu_usage" "public"
rick_core_register_function "get_ram_usage" "public"
rick_core_register_function "get_temperature" "public"
rick_core_register_function "get_rick_quote" "public"
rick_core_register_function "get_config_value" "public"
rick_core_register_function "set_config_value" "public"

# Register autoloadable functions - menu navigation
rick_core_register_function "_rick_menu_navigate" "private"
rick_core_register_function "_rick_menu" "private"

# Register menu screens
rick_core_register_function "_rick_menu_main" "private"
rick_core_register_function "_rick_menu_settings" "private"
rick_core_register_function "_rick_menu_status" "private"
rick_core_register_function "_rick_menu_help" "private"
rick_core_register_function "_rick_menu_brain" "private"
rick_core_register_function "_rick_menu_shell" "private"
rick_core_register_function "_rick_menu_monitoring" "private"
rick_core_register_function "_rick_menu_general_settings" "private"
rick_core_register_function "_rick_menu_ui_settings" "private"
rick_core_register_function "_rick_menu_personality_settings" "private"

# Terminal capabilities - global to maintain state between calls
typeset -gi _RICK_MENU_SUPPORTS_COLOR=0
typeset -gi _RICK_MENU_SUPPORTS_UNICODE=0
typeset -gi _RICK_MENU_WIDTH=60
typeset -gi _RICK_MENU_HEIGHT=10

# For backward compatibility
typeset -gi RICK_MENU_WIDTH=60
typeset -gi RICK_MENU_HEIGHT=10

# Color definitions (for menu styling)
typeset -gA RICK_MENU_COLORS=(
  "header"   "\033[1;36m"  # Bright cyan
  "title"    "\033[1;32m"  # Bright green
  "selected" "\033[1;33m"  # Bright yellow
  "normal"   "\033[0m"     # Normal
  "help"     "\033[0;36m"  # Cyan
  "error"    "\033[1;31m"  # Bright red
  "success"  "\033[1;32m"  # Bright green
  "warning"  "\033[1;33m"  # Bright yellow
  "info"     "\033[0;37m"  # White
  "reset"    "\033[0m"     # Reset
)

# Unicode symbols (with ASCII fallbacks)
typeset -gA RICK_MENU_SYMBOLS=(
  "arrow"     "→"
  "selected"  "●"
  "unselected" "○"
  "checkbox_on" "☒"
  "checkbox_off" "☐"
  "corner_tl" "┌"
  "corner_tr" "┐"
  "corner_bl" "└"
  "corner_br" "┘"
  "line_h"    "─"
  "line_v"    "│"
)

typeset -gA RICK_MENU_ASCII=(
  "arrow"     "->"
  "selected"  "*"
  "unselected" "o"
  "checkbox_on" "[X]"
  "checkbox_off" "[ ]"
  "corner_tl" "+"
  "corner_tr" "+"
  "corner_bl" "+"
  "corner_br" "+"
  "line_h"    "-"
  "line_v"    "|"
)

# Define the menu function for external use
menu() {
  _rick_menu "$@"
}

# Register menu function and command
rick_core_register_function "menu" "public"
rick_core_register_command "menu" "_rick_menu"

# Initialize module
if (( RICK_DEBUG )); then
  print "Rick Assistant Menu Module loaded"
fi 