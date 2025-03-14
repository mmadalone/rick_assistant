#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Hook Integration
#
# This script registers hooks with p10k to add Rick Assistant to the prompt
# without modifying .p10k.zsh directly
#

# Configuration
SCRIPT_DIR="${0:A:h}"

# Source the base integration which defines prompt_rick_assistant()
source "${SCRIPT_DIR}/p10k_integration_v2.zsh" >/dev/null 2>&1

# Define a function that runs when p10k configuration is loaded
function _p10k_rick_assistant_config() {
  # Add rick_assistant to POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS
  # This happens when p10k loads its configuration
  if [[ -n "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS}" ]]; then
    if (( ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)rick_assistant]} == 0 )); then
      POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=([rick_assistant])
    fi
  fi
  
  # Set up styling parameters
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND=green
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_BACKGROUND=clear
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_VISUAL_IDENTIFIER_EXPANSION='🧪'
  
  # Don't show Rick in transient prompts (helps with performance)
  typeset -g POWERLEVEL9K_TRANSIENT_PROMPT_ELEMENTS=(
    ${POWERLEVEL9K_TRANSIENT_PROMPT_ELEMENTS:#rick_assistant}
  )
}

# Register our function with p10k instant prompt's post-load hooks if available
if typeset -f p10k-instant-prompt-finalize >/dev/null; then
  autoload -Uz add-zsh-hook
  add-zsh-hook precmd _p10k_rick_assistant_config
fi

# Register config function to run when p10k loads its configuration
if [[ -n "$POWERLEVEL9K_CONFIG_HOOKS" ]]; then
  POWERLEVEL9K_CONFIG_HOOKS+=(_p10k_rick_assistant_config)
elif [[ -z "$_RICK_P10K_HOOK_INSTALLED" ]]; then
  # Only add the hook once
  export _RICK_P10K_HOOK_INSTALLED=1
  autoload -Uz add-zsh-hook
  add-zsh-hook precmd _p10k_rick_assistant_config
fi

# Force p10k to reload if it's already loaded
if typeset -f p10k >/dev/null; then
  p10k reload
fi 