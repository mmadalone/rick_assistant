#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k One-Time Setup
#
# This script adds a line to .zshrc that ensures Rick appears in the prompt
#

# Path to zshrc
ZSHRC="$HOME/.zshrc"

# Check if position was passed as parameter
POSITION=${1:-"right"}
if [[ "$POSITION" != "right" && "$POSITION" != "left" && "$POSITION" != "dir" ]]; then
  POSITION="right"
fi

echo "Setting up Rick Assistant for Powerlevel10k (position: $POSITION)..."

# Check if line already exists
if grep -q "POWERLEVEL9K_.*PROMPT_ELEMENTS+=.*rick_assistant" "$ZSHRC"; then
  # Remove existing lines first to update position
  grep -v "POWERLEVEL9K_.*PROMPT_ELEMENTS+=.*rick_assistant" "$ZSHRC" > "$ZSHRC.tmp"
  mv "$ZSHRC.tmp" "$ZSHRC"
  echo "Updated Rick Assistant position in $ZSHRC"
fi

# Backup zshrc
cp "$ZSHRC" "$ZSHRC.rickbackup"

# Add to zshrc to ensure it runs after p10k configures prompt
cat << 'EOT' >> "$ZSHRC"

# Rick Assistant Powerlevel10k integration
# This line adds Rick to your prompt, regardless of theme settings
if typeset -p POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS >/dev/null 2>&1; then
  # Configure Rick Assistant segment
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_FOREGROUND="green"
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_BACKGROUND="clear" 
  typeset -g POWERLEVEL9K_RICK_ASSISTANT_VISUAL_IDENTIFIER_EXPANSION="🧪"
  
  # Add segment to the requested position
  if [[ "${RICK_POSITION:-'"${POSITION}"'}" == "left" ]]; then
    POWERLEVEL9K_LEFT_PROMPT_ELEMENTS+=("rick_assistant")
  elif [[ "${RICK_POSITION:-'"${POSITION}"'}" == "dir" ]]; then
    # Replace the dir element with rick_assistant 
    # This places Rick in the path position
    for i in "${(k)POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[@]}"; do
      if [[ "${POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[$i]}" == "dir" ]]; then
        POWERLEVEL9K_LEFT_PROMPT_ELEMENTS[$i]="rick_assistant"
        break
      fi
    done
  else
    POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=("rick_assistant")
  fi
fi

# Define Rick segment if not already defined
if ! typeset -f prompt_rick_assistant >/dev/null 2>&1; then
  function prompt_rick_assistant() {
    # Get the current directory path if we're in dir replacement mode
    local dir_path=""
    if [[ "$RICK_POSITION" == "dir" ]]; then
      dir_path="${PWD/#$HOME/~}"
    fi

    # Run Python command to get the content
    local content=""
    if command -v python3 >/dev/null 2>&1; then
      # Call Python with proper error handling and clear p10k flag
      content=$(python3 -c "
try:
    import sys
    import os
    
    # Add the current directory to the path to ensure we can import src
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath('$(pwd)'))))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # Import the needed functions
    from src.core.prompt import get_rick_phrase
    from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
    
    # Get Rick's phrase with p10k flag
    is_p10k = True  # Flag to indicate p10k context
    phrase = get_rick_phrase(is_p10k)
    
    # Get system metrics
    cpu_info = get_cpu_usage()
    ram_info = get_ram_info()
    temp_info = get_cpu_temperature()
    
    # Format the metrics with p10k color syntax
    cpu_usage = cpu_info.get('usage', 0)
    cpu_state = cpu_info.get('state', 'normal')
    ram_percent = ram_info.get('percent', 0)
    ram_state = ram_info.get('state', 'normal')
    
    # Color coding based on state
    cpu_color = 'green'
    if cpu_state == 'warning':
        cpu_color = 'yellow'
    elif cpu_state == 'critical':
        cpu_color = 'red'
        
    ram_color = 'green'
    if ram_state == 'warning':
        ram_color = 'yellow'
    elif ram_state == 'critical':
        ram_color = 'red'
    
    # Format CPU and RAM with color
    cpu_str = f\"🖥️ CPU:%F{{{cpu_color}}}{cpu_usage:.1f}%%f\"
    ram_str = f\"🔧 RAM:%F{{{ram_color}}}{ram_percent:.1f}%%f\"
    
    # Add temperature if available
    temp_str = ''
    if temp_info.get('available', False):
        temp = temp_info.get('temperature', 0)
        temp_state = temp_info.get('state', 'normal')
        
        # Color coding based on temperature state
        temp_color = 'green'
        if temp_state == 'warning':
            temp_color = 'yellow'
        elif temp_state == 'critical':
            temp_color = 'red'
            
        temp_str = f\" | 🌡️ TEMP:%F{{{temp_color}}}{temp:.1f}°C%f\"
    
    # Format the final output - handle dir replacement mode specially
    if os.environ.get('RICK_POSITION') == 'dir':
        dir_path = os.environ.get('PWD', '').replace(os.environ.get('HOME', ''), '~')
        print(f\"📁 {dir_path} | {cpu_str} | {ram_str}{temp_str} | {phrase} | %F{{cyan}}🌀 C-137%f\") 
    else:
        print(f\"{cpu_str} | {ram_str}{temp_str} | {phrase} | %F{{cyan}}🌀 C-137%f\")
        
except Exception as e:
    print(f\"%F{{yellow}}*burp*%f Error: {str(e)}\")
" 2>/dev/null)
    else
      content="%F{yellow}*burp*%f Python3 not found"
    fi

    # Set segment content - use p10k segment_main for proper rendering
    if [[ -n "$content" ]]; then
      p10k segment_main "$0" "$1" "$2" content="$content"
    else
      p10k segment_main "$0" "$1" "$2" content="%F{red}*burp*%f Error getting content"
    fi
  }
fi
EOT

echo "Rick Assistant segment added to your .zshrc"
echo "Please restart your shell or run: source $ZSHRC" 