#!/usr/bin/env zsh

# This file ensures that our Rick segment and status elements are always visible
# regardless of terminal size or other conditions

# Make sure the Rick segment is always shown
typeset -g POWERLEVEL9K_MY_RICK_SHOW_ON_COMMAND=false

# Make sure the system status elements are always visible
typeset -g POWERLEVEL9K_STATUS_VERBOSE=true
typeset -g POWERLEVEL9K_STATUS_SHOW_PIPESTATUS=true
typeset -g POWERLEVEL9K_STATUS_OK=true
typeset -g POWERLEVEL9K_STATUS_OK_VISUAL_IDENTIFIER_EXPANSION='✓'
typeset -g POWERLEVEL9K_STATUS_OK_FOREGROUND=green
typeset -g POWERLEVEL9K_STATUS_OK_BACKGROUND=clear

# Make command execution time always visible
typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_THRESHOLD=0
typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_PRECISION=1
typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND=yellow
typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_BACKGROUND=clear

# Make background jobs always visible
typeset -g POWERLEVEL9K_BACKGROUND_JOBS_VERBOSE=true
typeset -g POWERLEVEL9K_BACKGROUND_JOBS_FOREGROUND=cyan
typeset -g POWERLEVEL9K_BACKGROUND_JOBS_BACKGROUND=clear

# Force p10k to reload after configuration changes
if typeset -f p10k &>/dev/null; then
  p10k reload 2>/dev/null || true
fi 