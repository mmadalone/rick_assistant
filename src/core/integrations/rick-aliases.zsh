#!/usr/bin/env zsh
# rick-aliases.zsh - Rick-themed aliases for common commands
#
# This module provides sarcastic Rick-themed aliases for common commands

# Ensure the core module is loaded
(( ${+functions[rick_core_module_load]} )) || source "${0:A:h}/rick-core.zsh"

# Register this module
rick_core_module_load "aliases" "${0:A}" || return 1

# Check if we should enable the aliases
typeset -gi RICK_ENABLE_ALIASES=0
rick_core_get_config "aliases" "enabled" "0" RICK_ENABLE_ALIASES

# Only create aliases if enabled
if (( RICK_ENABLE_ALIASES )); then
  # Define Rick-themed aliases
  alias ls="ls --color=auto; echo 'Look at all this *burp* useless stuff!'"
  alias cd="cd_with_rick_comment"
  alias grep="grep --color=auto; echo 'Searching for stuff like a *burp* desperate person, huh?'"
  alias mkdir="mkdir_with_rick_comment"
  
  # Define functions for aliases that need special handling
  cd_with_rick_comment() {
    # Store original directory
    local old_dir="$PWD"
    
    # Execute cd with all arguments
    builtin cd "$@"
    local cd_status=$?
    
    # If successful and not the same directory, add a Rick comment
    if [[ $cd_status -eq 0 && "$old_dir" != "$PWD" ]]; then
      local comments=(
        "Oh great, another *burp* directory. So original."
        "Wow, you changed directories. You must be *burp* SO proud of yourself."
        "Nice directory. Did your mommy pick it *burp* out for you?"
        "Oh look, we're in $PWD now. *burp* Amazing."
      )
      local random_index=$(( RANDOM % ${#comments[@]} + 1 ))
      echo "${comments[$random_index]}"
    fi
    
    return $cd_status
  }
  
  mkdir_with_rick_comment() {
    # Execute mkdir with all arguments
    command mkdir "$@"
    local mkdir_status=$?
    
    # If successful, add a Rick comment
    if [[ $mkdir_status -eq 0 ]]; then
      local comments=(
        "Wow, you created a directory. *burp* Want a medal?"
        "Great, another useless folder to *burp* store your junk."
        "Directory created. I'm sure it'll be *burp* super important."
        "Oh boy, a new directory! *burp* The excitement is killing me."
      )
      local random_index=$(( RANDOM % ${#comments[@]} + 1 ))
      echo "${comments[$random_index]}"
    fi
    
    return $mkdir_status
  }
fi

# Command to enable/disable aliases
_rick_aliases_toggle() {
  if (( RICK_ENABLE_ALIASES )); then
    # Disable aliases
    unalias ls cd grep mkdir 2>/dev/null
    unfunction cd_with_rick_comment mkdir_with_rick_comment 2>/dev/null
    RICK_ENABLE_ALIASES=0
    rick_core_set_config "aliases" "enabled" "0"
    echo "Rick-themed aliases disabled."
  else
    # Enable aliases by reloading this module
    RICK_ENABLE_ALIASES=1
    rick_core_set_config "aliases" "enabled" "1"
    source "${0:A}"
    echo "Rick-themed aliases enabled. Prepare for sarcasm!"
  fi
}

# Register the command for the rick command
rick_core_register_command "aliases" "_rick_aliases_toggle"

# Debug output
if (( RICK_DEBUG )); then
  if (( RICK_ENABLE_ALIASES )); then
    print "Rick Assistant: Aliases module loaded (enabled)"
  else
    print "Rick Assistant: Aliases module loaded (disabled)"
  fi
fi

# Return success
return 0 