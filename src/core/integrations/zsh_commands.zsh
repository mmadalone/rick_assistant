#!/usr/bin/env zsh
# -*- mode: zsh; sh-indentation: 2; indent-tabs-mode: nil; sh-basic-offset: 2; -*-
# vim: ft=zsh sw=2 ts=2 et
#
# Rick Assistant - Optimized Command Framework
# Provides a streamlined approach to defining and executing commands

# Command registry
typeset -gA _RICK_COMMANDS        # Maps command names to implementation functions
typeset -gA _RICK_COMMAND_HELP    # Maps command names to help text
typeset -gA _RICK_COMMAND_TYPE    # Maps command names to command types (native, python, etc.)
typeset -gA _RICK_COMMAND_USAGE   # Maps command names to usage text
typeset -g _RICK_COMMANDS_LOADED=0 # Whether commands have been loaded

# Command types
typeset -g RICK_CMD_TYPE_NATIVE="native"   # Pure Zsh implementation
typeset -g RICK_CMD_TYPE_PYTHON="python"   # Python implementation
typeset -g RICK_CMD_TYPE_HYBRID="hybrid"   # Hybrid implementation (Zsh wrapper around Python)
typeset -g RICK_CMD_TYPE_ALIAS="alias"     # Alias to another command

# Add fallback utility functions for testing in isolation
# These will only be defined if they don't already exist
if ! typeset -f _rick_error >/dev/null 2>&1; then
  _rick_error() {
    echo "ERROR: $*" >&2
  }
fi

if ! typeset -f _rick_debug >/dev/null 2>&1; then
  _rick_debug() {
    [[ -n "$RICK_ASSISTANT_DEBUG" ]] && echo "DEBUG: $*" >&2
  }
fi

# Initialize command framework
_rick_init_commands() {
  # Check if already initialized
  if [[ $_RICK_COMMANDS_LOADED -eq 1 ]]; then
    return 0
  fi
  
  # Ensure the autoload system is available
  if ! typeset -f rick_register_autoload >/dev/null 2>&1; then
    if [[ -f "${RICK_ASSISTANT_SCRIPT_DIR}/src/core/integrations/zsh_autoload.zsh" ]]; then
      source "${RICK_ASSISTANT_SCRIPT_DIR}/src/core/integrations/zsh_autoload.zsh"
    else
      _rick_error "Autoload system not available"
      return 1
    fi
  fi
  
  # Register built-in commands
  _rick_register_builtin_commands
  
  # Mark as loaded
  _RICK_COMMANDS_LOADED=1
  
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && _rick_debug "Command framework initialized"
  return 0
}

# Register a command
# Usage: rick_register_command name implementation help [usage] [type]
rick_register_command() {
  local name="$1"
  local implementation="$2"
  local help_text="$3"
  local usage_text="${4:-}"
  local cmd_type="${5:-$RICK_CMD_TYPE_NATIVE}"
  
  # Register the command
  _RICK_COMMANDS[$name]="$implementation"
  _RICK_COMMAND_HELP[$name]="$help_text"
  _RICK_COMMAND_TYPE[$name]="$cmd_type"
  
  # Set usage text if provided
  if [[ -n "$usage_text" ]]; then
    _RICK_COMMAND_USAGE[$name]="$usage_text"
  else
    _RICK_COMMAND_USAGE[$name]="rick $name"
  fi
  
  [[ -n "$RICK_ASSISTANT_DEBUG" ]] && _rick_debug "Registered command: $name ($cmd_type)"
  return 0
}

# Register a Python-based command
# Usage: rick_register_python_command name script_path help [usage]
rick_register_python_command() {
  local name="$1"
  local script_path="$2"
  local help_text="$3"
  local usage_text="${4:-}"
  
  # Create the implementation function
  local func_name="_rick_cmd_$name"
  local func_content="$func_name() {
    if [[ ! -f \"${RICK_ASSISTANT_SCRIPT_DIR}/$script_path\" ]]; then
      echo \"Error: Script not found: $script_path\" >&2
      return 1
    fi
    
    if command -v python3 >/dev/null 2>&1; then
      PYTHONPATH=\"${RICK_ASSISTANT_SCRIPT_DIR}:\${PYTHONPATH:-}\" python3 \"${RICK_ASSISTANT_SCRIPT_DIR}/$script_path\" \"\$@\"
      return \$?
    else
      echo \"Error: Python 3 not found\" >&2
      return 1
    fi
  }"
  
  # Register the function for autoloading
  rick_register_autoload "$func_name" "$func_content"
  
  # Register the command
  rick_register_command "$name" "$func_name" "$help_text" "$usage_text" "$RICK_CMD_TYPE_PYTHON"
  return 0
}

# Register a command alias
# Usage: rick_register_command_alias alias target help [usage]
rick_register_command_alias() {
  local alias_name="$1"
  local target_name="$2"
  local help_text="$3"
  local usage_text="${4:-}"
  
  # Check if target command exists
  if [[ -z "${_RICK_COMMANDS[$target_name]}" ]]; then
    _rick_error "Cannot create alias to non-existent command: $target_name"
    return 1
  fi
  
  # Create the implementation function
  local func_name="_rick_cmd_alias_${alias_name}"
  local func_content="$func_name() {
    # Forward to target command
    ${_RICK_COMMANDS[$target_name]} \"\$@\"
    return \$?
  }"
  
  # Register the function for autoloading
  rick_register_autoload "$func_name" "$func_content"
  
  # Register the command
  rick_register_command "$alias_name" "$func_name" "$help_text" "$usage_text" "$RICK_CMD_TYPE_ALIAS"
  return 0
}

# Execute a command
# Usage: rick_execute_command name [args...]
rick_execute_command() {
  local name="$1"
  shift
  
  # Check if command exists
  if [[ -z "${_RICK_COMMANDS[$name]}" ]]; then
    echo "Unknown command: $name"
    echo "Try 'rick help' for a list of commands."
    return 1
  fi
  
  # Get the implementation function
  local implementation="${_RICK_COMMANDS[$name]}"
  
  # Execute the command
  "$implementation" "$@"
  return $?
}

# Get help for a command
# Usage: rick_get_command_help name
rick_get_command_help() {
  local name="$1"
  
  # Check if command exists
  if [[ -z "${_RICK_COMMANDS[$name]}" ]]; then
    echo "Unknown command: $name"
    return 1
  fi
  
  # Print help text
  echo "${_RICK_COMMAND_HELP[$name]}"
  
  # Print usage if available
  if [[ -n "${_RICK_COMMAND_USAGE[$name]}" ]]; then
    echo ""
    echo "Usage: ${_RICK_COMMAND_USAGE[$name]}"
  fi
  
  return 0
}

# List all available commands
# Usage: rick_list_commands [pattern]
rick_list_commands() {
  local pattern="${1:-}"
  
  echo "Rick Assistant Commands:"
  echo "------------------------"
  
  # Filter commands by pattern if provided
  local commands
  if [[ -n "$pattern" ]]; then
    commands=(${(k)_RICK_COMMANDS[(I)$pattern*]})
  else
    commands=(${(k)_RICK_COMMANDS})
  fi
  
  # Sort commands
  commands=(${(o)commands})
  
  # Print commands and help text
  for cmd in $commands; do
    local type="${_RICK_COMMAND_TYPE[$cmd]}"
    local type_marker=""
    
    # Add type marker for non-native commands
    if [[ "$type" != "$RICK_CMD_TYPE_NATIVE" ]]; then
      type_marker=" ($type)"
    fi
    
    printf "  %-15s %s%s\n" "$cmd" "${_RICK_COMMAND_HELP[$cmd]}" "$type_marker"
  done
  
  return 0
}

# Register built-in commands
_rick_register_builtin_commands() {
  # help command
  local help_cmd='_rick_cmd_help() {
    local cmd="$1"
    
    if [[ -z "$cmd" ]]; then
      rick_list_commands
      echo ""
      echo "Type \"rick help <command>\" for command-specific help."
    else
      rick_get_command_help "$cmd"
    fi
    return 0
  }'
  rick_register_autoload "_rick_cmd_help" "$help_cmd"
  rick_register_command "help" "_rick_cmd_help" "Show help information for Rick Assistant commands" "rick help [command]"
  
  # version command
  local version_cmd='_rick_cmd_version() {
    echo "Rick Assistant ZSH Plugin v0.1.0"
    return 0
  }'
  rick_register_autoload "_rick_cmd_version" "$version_cmd"
  rick_register_command "version" "_rick_cmd_version" "Show Rick Assistant version"
  
  # status command
  local status_cmd='_rick_cmd_status() {
    if command -v python3 >/dev/null 2>&1; then
      if [[ -f "${RICK_ASSISTANT_SCRIPT_DIR}/src/main.py" ]]; then
        python3 -c "from src.utils.config import get_config_value; print(f\"Rick is {\"enabled\" if get_config_value(\"general.enabled\", True) else \"disabled\"}\")" 2>/dev/null || echo "Rick is... uh... not feeling so good right now."
      else
        echo "Rick is missing his main script. Did something go wrong with the portal gun?"
      fi
    else
      echo "Rick can'\''t find Python 3. He needs it for his experiments!"
    fi
    return 0
  }'
  rick_register_autoload "_rick_cmd_status" "$status_cmd"
  rick_register_command "status" "_rick_cmd_status" "Check Rick's status"
  
  # debug command
  local debug_cmd='_rick_cmd_debug() {
    if [[ -n "$RICK_ASSISTANT_DEBUG" ]]; then
      unset RICK_ASSISTANT_DEBUG
      echo "Rick is now being quiet and mysterious (debug mode off)."
    else
      export RICK_ASSISTANT_DEBUG=1
      echo "Rick is now sharing all his secrets (debug mode on)."
    fi
    return 0
  }'
  rick_register_autoload "_rick_cmd_debug" "$debug_cmd"
  rick_register_command "debug" "_rick_cmd_debug" "Toggle debug mode"
  
  # commands command - list available commands with type information
  local commands_cmd='_rick_cmd_commands() {
    rick_list_commands "$@"
    
    echo ""
    echo "Command types:"
    echo "  native - Pure Zsh implementation"
    echo "  python - Python implementation"
    echo "  hybrid - Hybrid implementation (Zsh wrapper around Python)"
    echo "  alias - Alias to another command"
    
    # Print statistics
    local native_count=0
    local python_count=0
    local hybrid_count=0
    local alias_count=0
    
    for cmd in ${(k)_RICK_COMMAND_TYPE}; do
      case "${_RICK_COMMAND_TYPE[$cmd]}" in
        "$RICK_CMD_TYPE_NATIVE") ((native_count++)) ;;
        "$RICK_CMD_TYPE_PYTHON") ((python_count++)) ;;
        "$RICK_CMD_TYPE_HYBRID") ((hybrid_count++)) ;;
        "$RICK_CMD_TYPE_ALIAS") ((alias_count++)) ;;
      esac
    done
    
    echo ""
    echo "Command statistics:"
    echo "  Total: ${#_RICK_COMMANDS}"
    echo "  Native: $native_count"
    echo "  Python: $python_count"
    echo "  Hybrid: $hybrid_count"
    echo "  Alias: $alias_count"
    
    return 0
  }'
  rick_register_autoload "_rick_cmd_commands" "$commands_cmd"
  rick_register_command "commands" "_rick_cmd_commands" "List all available commands" "rick commands [pattern]"
  
  # autoload command - show autoload statistics
  local autoload_cmd='_rick_cmd_autoload() {
    rick_list_autoload_status
    return 0
  }'
  rick_register_autoload "_rick_cmd_autoload" "$autoload_cmd"
  rick_register_command "autoload" "_rick_cmd_autoload" "Show autoload system statistics"
  
  # temperature_status command
  if typeset -f rick_temperature_status >/dev/null 2>&1; then
    rick_register_command "temperature_status" "rick_temperature_status" "Check CPU temperature"
  else
    rick_register_python_command "temperature_status" "src/utils/temperature_alerts.py status" "Check CPU temperature"
  fi
  
  # Register menu command
  if typeset -f _rick_impl_menu >/dev/null 2>&1; then
    rick_register_command "menu" "_rick_impl_menu" "Open Rick's interactive menu" "rick menu [menu_type]"
  else
    local menu_cmd='_rick_cmd_menu() {
      local menu_type=${1:-"main"}
      _rick_run_python_script "${RICK_ASSISTANT_SCRIPT_DIR}/src/core/menu_launcher.py" "$menu_type" "$@"
      return $?
    }'
    rick_register_autoload "_rick_cmd_menu" "$menu_cmd"
    rick_register_command "menu" "_rick_cmd_menu" "Open Rick's interactive menu" "rick menu [menu_type]" "$RICK_CMD_TYPE_PYTHON"
  fi
  
  return 0
}

# Initialize the command system
_rick_init_commands 