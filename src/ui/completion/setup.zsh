#!/usr/bin/env zsh

# Rick Assistant Tab Completion Setup
# This script initializes the Rick Assistant tab completion system

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${(%):-%x}" )" && pwd )"
RICK_ASSISTANT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# Set environment variables
export RICK_COMPLETION_ENABLED=1
export RICK_COMPLETION_PATH="$SCRIPT_DIR"

# Enable debug output if requested and not suppressed
if [[ -n "$RICK_DEBUG" && -z "$RICK_SUPPRESS_OUTPUT" ]]; then
  echo "Rick Assistant Tab Completion: Initializing from $SCRIPT_DIR"
fi

# Function to test if our completion system works
rick_test_completion() {
  local python_cmd

  # Find Python command
  if command -v python3 &>/dev/null; then
    python_cmd="python3"
  elif command -v python &>/dev/null; then
    python_cmd="python"
  else
    if [[ -z "$RICK_SUPPRESS_OUTPUT" ]]; then
      echo "Error: Python not found. Tab completion will not work."
    fi
    return 1
  fi

  # Create a temp script to test if our completion works
  local temp_file=$(mktemp)
  cat > "$temp_file" << 'EOF'
import sys
import os
try:
    # Add the rick assistant root to path
    sys.path.insert(0, os.environ.get('RICK_ASSISTANT_DIR', '.'))
    from src.ui.completion import complete_command
    # Only print success message if output is not suppressed
    if not os.environ.get('RICK_SUPPRESS_OUTPUT'):
        print("SUCCESS: Rick Assistant tab completion is working")
    sys.exit(0)
except Exception as e:
    if not os.environ.get('RICK_SUPPRESS_OUTPUT'):
        print(f"ERROR: Rick Assistant tab completion failed: {e}")
    sys.exit(1)
EOF

  # Run the test
  if "$python_cmd" "$temp_file"; then
    if [[ -n "$RICK_DEBUG" && -z "$RICK_SUPPRESS_OUTPUT" ]]; then
      echo "Rick Assistant Tab Completion: Test successful"
    fi
    rm "$temp_file"
    return 0
  else
    if [[ -z "$RICK_SUPPRESS_OUTPUT" ]]; then
      echo "Rick Assistant Tab Completion: Test failed"
    fi
    rm "$temp_file"
    return 1
  fi
}

# Create a completion function for Rick commands
_rick_completion() {
  local python_cmd completions

  # Find Python command
  if command -v python3 &>/dev/null; then
    python_cmd="python3"
  elif command -v python &>/dev/null; then
    python_cmd="python"
  else
    return 1
  fi

  # Get the current word
  local current="${words[CURRENT]}"
  
  # Create a temporary script to get completions
  local temp_file=$(mktemp)
  cat > "$temp_file" << 'EOF'
import sys
import os
try:
    # Add the rick assistant root to path
    sys.path.insert(0, os.environ.get('RICK_ASSISTANT_DIR', '.'))
    
    from src.ui.completion import (
        complete_command, 
        complete_path, 
        get_completion_context
    )
    
    # Get the query from command line
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # Detect context
    context = get_completion_context(query)
    
    # Get completions based on context
    if context == "path" or context == "directory":
        completions = complete_path(query)
    else:
        completions = complete_command(query)
    
    # Print completions for ZSH
    for comp in completions:
        print(comp)
        
except Exception as e:
    # Just return empty results on error
    pass
EOF

  # Run the completion script
  completions=($("$python_cmd" "$temp_file" "$current"))
  rm "$temp_file"
  
  # Return the completions
  compadd -a completions
}

# Register the completion function if test passes
if rick_test_completion; then
  # Create completions for rick commands
  compdef _rick_completion rick

  # Add a message if debug is enabled and output is not suppressed
  if [[ -n "$RICK_DEBUG" && -z "$RICK_SUPPRESS_OUTPUT" ]]; then
    echo "*burp* Tab completion is locked and loaded, Morty!"
  fi
else
  # Add a message if debug is enabled and output is not suppressed
  if [[ -n "$RICK_DEBUG" && -z "$RICK_SUPPRESS_OUTPUT" ]]; then
    echo "Warning: Rick Assistant tab completion could not be initialized"
  fi
fi
