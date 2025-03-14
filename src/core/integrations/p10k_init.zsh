#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Master Integration Script
#
# Single entry point for p10k integration that handles all setup details.
#

# Check if p10k is available
if ! command -v p10k >/dev/null 2>&1; then
  echo "Warning: Powerlevel10k not found. Rick Assistant p10k integration skipped."
  return 0
fi

# Find our directory
SCRIPT_DIR="${0:A:h}"

# Integration method selection (hook-based is recommended)
RICK_P10K_METHOD="${RICK_P10K_METHOD:-hook}"  # hook, direct, or none

# Handle different integration methods
case "$RICK_P10K_METHOD" in
  # Hook-based integration (recommended) - doesn't modify p10k.zsh directly
  hook)
    source "${SCRIPT_DIR}/p10k_hook.zsh" >/dev/null 2>&1
    ;;
    
  # Direct integration - modifies p10k.zsh directly (legacy approach)
  direct)
    source "${SCRIPT_DIR}/p10k_direct.zsh" >/dev/null 2>&1
    ;;
    
  # Disable integration
  none)
    echo "Rick Assistant p10k integration disabled via RICK_P10K_METHOD=none"
    ;;
    
  # Unknown method
  *)
    echo "Unknown integration method: $RICK_P10K_METHOD"
    echo "Valid options: hook, direct, none"
    echo "Using default method: hook"
    source "${SCRIPT_DIR}/p10k_hook.zsh" >/dev/null 2>&1
    ;;
esac

# Print available configuration options
# Handled in the individual integration scripts

# Export function to reload the integration
function rick_p10k_reload() {
  echo "Reloading Rick Assistant p10k integration..."
  source "${SCRIPT_DIR}/p10k_init.zsh"
  p10k reload
} 