#!/usr/bin/env zsh

# Rick Assistant Distribution Detection
# This file helps detect the Linux distribution and apply specific fixes

# Detect Linux distribution
detect_distribution() {
  local distro=""
  
  # First check for WSL
  if [[ -n "$WSL_DISTRO_NAME" ]]; then
    distro="wsl-$WSL_DISTRO_NAME"
  # Then check for /etc/os-release (most modern distros)
  elif [[ -f /etc/os-release ]]; then
    distro=$(grep -oP '^ID=\K.*' /etc/os-release | tr -d '"')
  # Check for older Red Hat based systems
  elif [[ -f /etc/redhat-release ]]; then
    distro="rhel"
  # Check for older Debian systems
  elif [[ -f /etc/debian_version ]]; then
    distro="debian"
  # Check for SuSE
  elif [[ -f /etc/SuSE-release ]]; then
    distro="suse"
  # Check for Arch Linux
  elif [[ -f /etc/arch-release ]]; then
    distro="arch"
  # Check for Gentoo
  elif [[ -f /etc/gentoo-release ]]; then
    distro="gentoo"
  # Check for macOS
  elif [[ "$(uname)" == "Darwin" ]]; then
    distro="macos"
  # Fallback to generic linux
  else
    distro="linux"
  fi
  
  echo "$distro"
}

# Apply distribution-specific fixes
apply_distro_fixes() {
  local distro=$(detect_distribution)
  
  case "$distro" in
    wsl-*)
      # WSL distros need special handling
      source ~/.rick-wsl-fix.zsh
      ;;
    debian|ubuntu|mint)
      # Debian-based distros fixes
      ;;
    fedora|rhel|centos)
      # Red Hat family fixes
      ;;
    arch|manjaro)
      # Arch family fixes
      ;;
    suse|opensuse*)
      # SUSE family fixes
      ;;
    alpine)
      # Alpine Linux fixes
      # Handle BusyBox differences
      ;;
    macos)
      # macOS specific fixes
      ;;
    *)
      # Generic Linux fixes
      ;;
  esac
  
  # Return the detected distro
  echo "$distro"
}

# Get detailed system information
get_system_info() {
  {
    echo "Distribution: $(detect_distribution)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    if [[ -f /proc/version ]]; then
      echo "Proc Version: $(cat /proc/version)"
    fi
    echo "Shell: $SHELL"
    echo "ZSH Version: $ZSH_VERSION"
    if command -v p10k &>/dev/null; then
      echo "Powerlevel10k: Available"
    else
      echo "Powerlevel10k: Not found"
    fi
  } 2>/dev/null
} 