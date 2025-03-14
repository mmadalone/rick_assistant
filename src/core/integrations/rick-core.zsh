#!/usr/bin/env zsh
# rick-core.zsh - Core module for Rick Assistant
#
# This module provides the core functionality for Rick Assistant,
# including module management, function registration, and dependency handling.

# Get the absolute path of this file
RICK_CORE_FILE="${0:A}"
RICK_CORE_DIR="${RICK_CORE_FILE:h}"
RICK_ROOT_DIR="${RICK_CORE_DIR:h:h:h}"
RICK_FUNCTIONS_DIR="${RICK_ROOT_DIR}/functions"

# Add functions directory to fpath for autoloading
[[ -d "$RICK_FUNCTIONS_DIR" ]] && fpath=("$RICK_FUNCTIONS_DIR" $fpath)

# Debug flag (can be set in the environment)
typeset -gi RICK_DEBUG=${RICK_DEBUG:-0}

# Internal state
typeset -gA _RICK_LOADED_MODULES=()
typeset -gA _RICK_REGISTERED_FUNCTIONS=()
typeset -gA _RICK_REGISTERED_COMMANDS=()

# Module management
#
# Load a module and register it as loaded
rick_core_module_load() {
  local module_name="$1"
  local module_path="$2"
  
  # Validate inputs
  [[ -z "$module_name" ]] && return 1
  
  # If module is already loaded, just return success
  if (( ${+_RICK_LOADED_MODULES[$module_name]} )); then
    return 0
  fi
  
  # If module_path is provided, validate it exists
  if [[ -n "$module_path" && ! -f "$module_path" ]]; then
    (( RICK_DEBUG )) && print "Rick Core: Module $module_name not found at $module_path"
    return 1
  fi
  
  # Register the module as loaded
  _RICK_LOADED_MODULES[$module_name]="${module_path:-1}"
  
  # Debug output
  (( RICK_DEBUG )) && print "Rick Core: Module $module_name loaded from ${module_path:-"built-in"}"
  
  return 0
}

# Check if a module is loaded
rick_core_is_module_loaded() {
  local module_name="$1"
  
  # Validate inputs
  [[ -z "$module_name" ]] && return 1
  
  # Check if module is loaded
  if (( ${+_RICK_LOADED_MODULES[$module_name]} )); then
    return 0
  else
    return 1
  fi
}

# Function registration
#
# Register a function for autoloading or access
rick_core_register_function() {
  local function_name="$1"
  local visibility="${2:-public}"  # public or private
  
  # Validate inputs
  [[ -z "$function_name" ]] && return 1
  
  # If already registered, just return success
  if (( ${+_RICK_REGISTERED_FUNCTIONS[$function_name]} )); then
    return 0
  fi
  
  # Check if the function exists in the functions directory or is already loaded
  if [[ -f "$RICK_FUNCTIONS_DIR/$function_name" ]] || typeset -f "$function_name" >/dev/null 2>&1; then
    # Autoload if not already defined
    if ! typeset -f "$function_name" >/dev/null 2>&1; then
      autoload -Uz "$function_name"
    fi
    
    # Register the function
    _RICK_REGISTERED_FUNCTIONS[$function_name]="$visibility"
    
    # Debug output
    (( RICK_DEBUG )) && print "Rick Core: Function $function_name registered as $visibility"
    
    return 0
  else
    # Function not found
    (( RICK_DEBUG )) && print "Rick Core: Function $function_name not found for registration"
    return 1
  fi
}

# Check if a function is registered
rick_core_is_function_registered() {
  local function_name="$1"
  
  # Validate inputs
  [[ -z "$function_name" ]] && return 1
  
  # Check if function is registered
  if (( ${+_RICK_REGISTERED_FUNCTIONS[$function_name]} )); then
    return 0
  else
    return 1
  fi
}

# Command registration
#
# Register a command for the rick command framework
rick_core_register_command() {
  local command_name="$1"
  local handler_function="$2"
  
  # Validate inputs
  [[ -z "$command_name" || -z "$handler_function" ]] && return 1
  
  # Ensure the handler function exists
  if ! typeset -f "$handler_function" >/dev/null 2>&1; then
    (( RICK_DEBUG )) && print "Rick Core: Handler function $handler_function not found for command $command_name"
    return 1
  fi
  
  # Register the command
  _RICK_REGISTERED_COMMANDS[$command_name]="$handler_function"
  
  # Debug output
  (( RICK_DEBUG )) && print "Rick Core: Command $command_name registered with handler $handler_function"
  
  return 0
}

# Call a registered command
rick_core_call_command() {
  local command_name="$1"
  shift || true
  
  # Validate inputs
  [[ -z "$command_name" ]] && return 1
  
  # Check if command is registered
  if (( ${+_RICK_REGISTERED_COMMANDS[$command_name]} )); then
    local handler="${_RICK_REGISTERED_COMMANDS[$command_name]}"
    
    # Call the handler function with remaining arguments
    "$handler" "$@"
    return $?
  else
    (( RICK_DEBUG )) && print "Rick Core: Command $command_name not registered"
    return 1
  fi
}

# Configuration management (using zstyle)
#
# Get a configuration value
rick_core_get_config() {
  local context="$1"
  local parameter="$2"
  local default_value="$3"
  local output_var="$4"
  
  # Validate inputs
  [[ -z "$context" || -z "$parameter" ]] && return 1
  
  # Format the context to ensure it has the 'rick' namespace
  [[ "$context" != "rick:"* ]] && context="rick:$context"
  
  # Get the value using zstyle
  local value
  zstyle -s "$context" "$parameter" value || value="$default_value"
  
  # If output_var is provided, set it to the value
  if [[ -n "$output_var" ]]; then
    typeset -g "$output_var"="$value"
  else
    # Otherwise, print the value
    echo "$value"
  fi
  
  return 0
}

# Set a configuration value
rick_core_set_config() {
  local context="$1"
  local parameter="$2"
  local value="$3"
  
  # Validate inputs
  [[ -z "$context" || -z "$parameter" ]] && return 1
  
  # Format the context to ensure it has the 'rick' namespace
  [[ "$context" != "rick:"* ]] && context="rick:$context"
  
  # Set the value using zstyle
  zstyle "$context" "$parameter" "$value"
  
  return 0
}

# Register the core module itself
rick_core_module_load "core" "$RICK_CORE_FILE"

# Load compatibility layer for backward compatibility
if [[ -f "$RICK_FUNCTIONS_DIR/_rick_compatibility_layer" ]]; then
  rick_core_register_function "_rick_compatibility_layer" "private"
  _rick_compatibility_layer
fi

# Debug output
(( RICK_DEBUG )) && print "Rick Assistant Core Module loaded"

# Return success
return 0 