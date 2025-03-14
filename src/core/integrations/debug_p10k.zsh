#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Debug Script
#

echo "Sourcing powerlevel10k.zsh..."
[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh

echo "[RICK_P10K_DEBUG] Loading Rick Assistant P10k integration module"

# Check if p10k is available
if type p10k > /dev/null 2>&1; then
  echo "[RICK_P10K_DEBUG] Powerlevel10k integration module loaded"
  echo "✅ p10k function is available"
else
  echo "[RICK_P10K_DEBUG] Powerlevel10k not detected, cannot add segment"  
  echo "❌ p10k function is NOT available"
fi

# Check if Rick foreground color is set
if typeset -p POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND > /dev/null 2>&1; then
  echo "✅ POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND is set"
else
  echo "❌ POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND is NOT set"
fi

# Check if prompt_rick_assistant function is defined
if typeset -f prompt_rick_assistant > /dev/null 2>&1; then
  echo "✅ prompt_rick_assistant function is defined"
else
  echo "❌ prompt_rick_assistant function is NOT defined"
fi

# Check if Rick segment is in prompt elements
if typeset -p POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS > /dev/null 2>&1; then
  if echo ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]} | grep -q "rick_assistant"; then
    echo "✅ rick_assistant is in POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS"
  else
    echo "❌ rick_assistant is NOT in POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS"
    echo "[RICK_P10K_DEBUG] Attempting to add Rick segment to Powerlevel10k"
    POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=("rick_assistant")
    echo "Added rick_assistant to prompt elements"
  fi
else
  echo "❌ POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS is NOT defined"
fi

# Test getting prompt content
echo "[RICK_P10K_DEBUG] Getting prompt content"
if command -v python3 >/dev/null 2>&1; then
  echo "[RICK_P10K_DEBUG] Python module content: '$(python3 -c '
try:
    from src.core.prompt import get_rick_phrase
    print(get_rick_phrase())
except Exception as e:
    print(f"Error: {str(e)}")
' 2>&1)'"
fi

# Try to generate the content directly
if typeset -f prompt_rick_assistant > /dev/null 2>&1; then
  prompt_content=$(prompt_rick_assistant)
  echo "Prompt content: '$prompt_content'"
fi

echo "Debug completed"

# The script should be sourced, not executed
# Usage: RICK_P10K_DEBUG=1 source src/core/integrations/debug_p10k.zsh 