#!/usr/bin/env zsh

# Rick Assistant WSL Fixes
# This file contains fixes for common WSL issues that can affect Powerlevel10k integration

# Detect if running in WSL
_is_wsl() {
  [[ -n "$WSL_DISTRO_NAME" || -f /proc/sys/fs/binfmt_misc/WSLInterop ]]
}

# Fix PATH issues in WSL
_fix_wsl_path() {
  # Ensure Linux paths have priority over Windows paths
  export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
  
  # Remove potential problematic Windows paths that might conflict
  local win_paths=()
  local new_path=()
  
  # Split PATH and identify Windows paths
  for p in ${(s/:/)PATH}; do
    if [[ "$p" == /mnt/* ]]; then
      win_paths+=("$p")
    else
      new_path+=("$p")
    fi
  done
  
  # Add Windows paths at the end to avoid conflicts
  for p in "${win_paths[@]}"; do
    new_path+=("$p")
  done
  
  # Set the new PATH
  export PATH="${(j/:/)new_path}"
}

# Fix environment issues for command resolution
_fix_wsl_env() {
  # Fix for common WSL issues with TERM and locale
  export TERM="${TERM:-xterm-256color}"
  export LC_ALL="${LC_ALL:-C.UTF-8}"
  export LANG="${LANG:-C.UTF-8}"
  
  # Fix for command resolution issues
  alias python='python3'
  alias pip='pip3'
}

# Ensure specific important commands are available
_ensure_commands() {
  # Create function wrappers for potentially problematic commands
  for cmd in uname grep awk sed cat; do
    if ! command -v $cmd >/dev/null 2>&1; then
      # If command not found, create function to use full path
      # Use ZSH's functions array instead of eval for safer function definition
      functions[$cmd]="() { /usr/bin/$cmd \"\$@\" }"
    fi
  done
}

# Main function to apply all WSL fixes
fix_wsl_environment() {
  if _is_wsl; then
    _fix_wsl_path
    _fix_wsl_env
    _ensure_commands
    return 0
  fi
  return 1
}

# Apply fixes if running in WSL
fix_wsl_environment 