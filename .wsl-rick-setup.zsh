#!/usr/bin/env zsh

# WSL-specific setup for Rick Assistant
# Fixes common issues with PATH and command execution in WSL environments

# Only apply these fixes in WSL environments
if [[ -n "$WSL_DISTRO_NAME" || -f /proc/sys/fs/binfmt_misc/WSLInterop ]]; then
  # Fix common WSL PATH issues by ensuring Linux paths come first
  # This helps with command resolution problems
  export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
  
  # Fix for Python module issues in WSL
  # This ensures Python can find modules regardless of WSL/Windows conflicts
  if command -v python3 >/dev/null 2>&1; then
    export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"
  fi
  
  # Avoid using Windows Python in WSL environment
  # This prevents accidental use of Windows Python which can cause compatibility issues
  alias python='python3'
  alias pip='pip3'
fi

# Create a function to check if psutil is installed and install it if needed
rick_ensure_psutil() {
  if ! python3 -c "import psutil" 2>/dev/null; then
    echo "Installing psutil for Rick Assistant..."
    pip3 install --user psutil 2>/dev/null || sudo pip3 install psutil 2>/dev/null
  fi
}

# Try to ensure psutil is available, but don't force it
rick_ensure_psutil &>/dev/null & disown 