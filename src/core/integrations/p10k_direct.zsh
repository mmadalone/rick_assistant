#!/usr/bin/env zsh
#
# Rick Assistant - Direct Powerlevel10k Integration
#
# This script directly modifies .p10k.zsh to ensure Rick appears in the prompt
#

# Get user's p10k config file
P10K_CONFIG="$HOME/.p10k.zsh"

if [[ ! -f "$P10K_CONFIG" ]]; then
  echo "Error: $P10K_CONFIG not found. Is Powerlevel10k installed?"
  return 1
fi

# Make a backup of the current config
P10K_BACKUP="$HOME/.p10k.zsh.rickbackup"
if [[ ! -f "$P10K_BACKUP" ]]; then
  echo "Making backup of $P10K_CONFIG to $P10K_BACKUP"
  cp "$P10K_CONFIG" "$P10K_BACKUP"
fi

# Find the path to the metrics script
SCRIPT_DIR="${0:A:h}"
METRICS_SCRIPT="$SCRIPT_DIR/p10k_metrics.py"

# Configuration options
# Set to "true" to disable color formatting (helps with compatibility issues)
RICK_P10K_PLAIN_MODE="${RICK_P10K_PLAIN_MODE:-false}"

# Set to "true" to enable debug output
RICK_P10K_DEBUG="${RICK_P10K_DEBUG:-false}"

# Add our segment to the right prompt elements
echo "Adding rick_assistant segment to Powerlevel10k prompt..."

# Define the segment function in a file that will be sourced by p10k
RICK_P10K_SEGMENT="$HOME/.p10k.rick.zsh"

cat > "$RICK_P10K_SEGMENT" << EOF
# Rick Assistant segment for Powerlevel10k
function prompt_rick_assistant() {
  # Get system metrics using external script
  local content=""
  local options=""
  
  # Apply configuration options
  if [[ "$RICK_P10K_PLAIN_MODE" == "true" ]]; then
    options+=" --plain"
  fi
  
  if [[ "$RICK_P10K_DEBUG" == "true" ]]; then
    options+=" --debug"
  fi
  
  if command -v python3 >/dev/null 2>&1; then
    # Use the external Python script for better reliability
    if [[ -f "$METRICS_SCRIPT" ]]; then
      content=\$(python3 "$METRICS_SCRIPT"\$options 2>/dev/null)
      
      # Check if we got an error with 'cyan' - if so, retry with plain mode
      if [[ \$content == *"Error: name 'cyan' is not defined"* ]]; then
        content=\$(python3 "$METRICS_SCRIPT" --plain 2>/dev/null)
      fi
    else
      content="🧪 Script not found"
    fi
  else
    # Fallback if Python is not available
    content="🧪 *burp* Wubba Lubba Dub Dub!"
  fi
  
  # If something went wrong, provide a simple fallback
  if [[ -z "\$content" ]]; then
    content="🧪 Rick's here!"
  fi
  
  # Display the segment
  p10k segment -f green -i "🧪" -t "\$content"
}
EOF

# Source the segment file in .p10k.zsh if not already there
if ! grep -q "source \"$RICK_P10K_SEGMENT\"" "$P10K_CONFIG"; then
  echo "\n# Rick Assistant integration\nsource \"$RICK_P10K_SEGMENT\"" >> "$P10K_CONFIG"
fi

# Add our segment to POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS if not already there
if ! grep -q "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=.*rick_assistant" "$P10K_CONFIG"; then
  # Find the line that defines POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS
  sed -i.bak -e '/POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=/s/)/ rick_assistant)/' "$P10K_CONFIG"
  
  # Add the style settings too
  echo "# Rick Assistant segment styling
typeset -g POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND=green
typeset -g POWERLEVEL9K_RICK_ASSISTANT_BACKGROUND=clear
typeset -g POWERLEVEL9K_RICK_ASSISTANT_VISUAL_IDENTIFIER_EXPANSION='🧪'" >> "$P10K_CONFIG"
fi

echo "Rick Assistant segment added to Powerlevel10k configuration"
echo "Please reload your configuration with: p10k reload"
echo ""
echo "Configuration options:"
echo "  To use plain text mode (for compatibility): export RICK_P10K_PLAIN_MODE=true"
echo "  To enable debug output: export RICK_P10K_DEBUG=true" 