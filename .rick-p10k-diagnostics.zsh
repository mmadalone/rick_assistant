#!/usr/bin/env zsh

# Rick Assistant Powerlevel10k Diagnostics
# This file helps diagnose issues with the Powerlevel10k integration

# Terminal colors
RED=$(tput setaf 1 2>/dev/null || echo '')
GREEN=$(tput setaf 2 2>/dev/null || echo '')
YELLOW=$(tput setaf 3 2>/dev/null || echo '')
BLUE=$(tput setaf 4 2>/dev/null || echo '')
BOLD=$(tput bold 2>/dev/null || echo '')
RESET=$(tput sgr0 2>/dev/null || echo '')

# Helpers
print_header() {
  echo "${BLUE}${BOLD}$1${RESET}"
  echo "${BLUE}$(printf '=%.0s' {1..50})${RESET}"
  echo
}

print_subheader() {
  echo "${BLUE}$1${RESET}"
  echo "${BLUE}$(printf '-%.0s' {1..50})${RESET}"
}

print_success() {
  echo "${GREEN}✓${RESET} $1"
}

print_error() {
  echo "${RED}✗${RESET} $1"
}

print_warning() {
  echo "${YELLOW}!${RESET} $1"
}

print_info() {
  echo "${BLUE}i${RESET} $1"
}

# Check environment
check_environment() {
  print_subheader "Environment Check"
  
  # Check ZSH
  if [[ -n "$ZSH_VERSION" ]]; then
    print_success "ZSH Version: $ZSH_VERSION"
    
    # Check ZSH version compatibility
    if [[ "$ZSH_VERSION" == 5.<8->* || "$ZSH_VERSION" == <6->* ]]; then
      print_success "ZSH version is compatible"
    else
      print_warning "ZSH version is older than recommended (5.8+)"
    fi
  else
    print_error "Cannot detect ZSH version"
  fi
  
  # Check Powerlevel10k
  if [[ -f ~/.p10k.zsh ]]; then
    print_success "Powerlevel10k: Installed"
  else
    print_error "Powerlevel10k configuration not found at ~/.p10k.zsh"
  fi
  
  # Check if p10k is defined
  if typeset -f p10k >/dev/null 2>&1; then
    print_success "Powerlevel10k is detected"
  else
    print_error "Powerlevel10k function not found"
  fi

  # Check p10k command
  if command -v p10k >/dev/null 2>&1; then
    print_success "p10k command: Available"
  else
    print_warning "p10k command not found in PATH"
  fi
  
  # Test p10k command functionality
  if typeset -f p10k >/dev/null 2>&1 && p10k -h >/dev/null 2>&1; then
    print_success "p10k command is functional"
  else
    print_error "p10k command seems broken"
  fi
}

# Check configuration files
check_configuration() {
  print_subheader "Configuration Files"
  
  # Check if .p10k.zsh exists
  if [[ -f ~/.p10k.zsh ]]; then
    print_success "~/.p10k.zsh: Found"
  else
    print_error "~/.p10k.zsh: Not found"
  fi
  
  # Check if .p10k.zsh is sourced in .zshrc
  if grep -q "source.*\.p10k\.zsh" ~/.zshrc 2>/dev/null; then
    print_success "p10k.zsh sourcing in ~/.zshrc"
  else
    print_error "No p10k.zsh sourcing in ~/.zshrc"
  fi
  
  # Check if our segment is defined in p10k.zsh
  if grep -q "prompt_my_rick_metrics" ~/.p10k.zsh 2>/dev/null; then
    print_success "Rick segment found in p10k.zsh"
  else
    print_info "Rick segment not found in p10k.zsh (expected with our non-invasive approach)"
  fi
  
  # Check for our integration files
  for file in ~/.rick-p10k-{segment,integration}.zsh ~/.rick-{wsl-fix,distro-detect}.zsh; do
    if [[ -f "$file" ]]; then
      print_success "$(basename $file): Found"
    else
      print_error "$(basename $file): Not found"
    fi
  done
  
  # Check if our integration is in .zshrc
  if grep -q "source.*rick-p10k-integration\.zsh" ~/.zshrc 2>/dev/null; then
    print_success "Integration script sourced in ~/.zshrc"
  else
    print_warning "Integration script not found in ~/.zshrc"
  fi
}

# Check prompt elements
check_prompt_elements() {
  print_subheader "Prompt Elements Check"
  
  # Check if prompt elements include our segment
  if (( ${+POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS} )); then
    if (( ${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(I)my_rick_metrics]} )); then
      print_success "my_rick_metrics is in right prompt elements"
    else
      print_error "my_rick_metrics not found in right prompt elements"
    fi
    
    # List all right prompt elements for reference
    echo "Current right prompt elements:"
    for element in "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]}"; do
      echo "  - $element"
    done
  else
    print_error "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS is not defined"
  fi
}

# Test segment rendering
test_segment_rendering() {
  print_subheader "Segment Rendering Test"
  
  # Check if our segment function is defined
  if typeset -f prompt_my_rick_metrics >/dev/null; then
    print_success "prompt_my_rick_metrics function: Defined"
    
    # Try to capture segment output without executing p10k segment directly
    # This avoids the "can be called only during prompt rendering" error
    echo "Segment would display metrics in the format:"
    echo "  CPU:x.x% | RAM:x.x% | 🌀 C-137 | 🧪 <rick phrase>"
  else
    print_error "prompt_my_rick_metrics function: Not defined"
  fi
}

# Run WSL detection
check_wsl() {
  print_subheader "WSL Environment Check"
  
  # Check for WSL indicators
  if [[ -n "$WSL_DISTRO_NAME" || -f /proc/sys/fs/binfmt_misc/WSLInterop ]]; then
    print_info "Running in WSL: Yes (${WSL_DISTRO_NAME:-Unknown})"
    
    # Check path order (ensure Linux paths come first)
    local path_start=$(echo $PATH | cut -d: -f1)
    if [[ "$path_start" == /usr/* || "$path_start" == /bin* ]]; then
      print_success "PATH order: Linux paths have priority"
    else
      print_warning "PATH order: Linux paths don't have priority"
      echo "  First path entry: $path_start"
    fi
  else
    print_info "Running in WSL: No"
  fi
}

# Check command availability for metrics collection
check_commands() {
  print_subheader "Command Availability Check"
  
  # Check essential commands used in metrics collection
  for cmd in grep awk cat sed uname; do
    if command -v $cmd >/dev/null 2>&1; then
      print_success "$cmd: Available"
    else
      print_error "$cmd: Not found"
    fi
  done
}

# Run distribution detection
check_distribution() {
  print_subheader "Distribution Detection"
  
  if typeset -f detect_distribution >/dev/null 2>&1; then
    local distro=$(detect_distribution)
    print_info "Detected distribution: $distro"
  else
    if [[ -f /etc/os-release ]]; then
      local distro=$(grep -oP '^ID=\K.*' /etc/os-release | tr -d '"')
      print_info "Distribution (from os-release): $distro"
    else
      print_warning "Could not detect distribution"
    fi
  fi
}

# Summary and recommendations
print_summary() {
  print_header "Summary and Recommendations"
  
  # Check for main integration files
  local missing_files=()
  for file in ~/.rick-p10k-{segment,integration}.zsh ~/.rick-{wsl-fix,distro-detect}.zsh; do
    if [[ ! -f "$file" ]]; then
      missing_files+=("$(basename $file)")
    fi
  done
  
  if (( ${#missing_files[@]} > 0 )); then
    print_error "Missing files: ${missing_files[*]}"
    echo "Please recreate the missing files to ensure proper integration."
  fi
  
  # Check for segment issues
  if ! typeset -f prompt_my_rick_metrics >/dev/null; then
    print_error "Rick segment function is not defined"
    echo "Try re-sourcing the segment definition file:"
    echo "  source ~/.rick-p10k-segment.zsh"
  fi
  
  # Check if integration is in .zshrc
  if ! grep -q "source.*rick-p10k-integration\.zsh" ~/.zshrc 2>/dev/null; then
    print_error "Integration script not found in ~/.zshrc"
    echo "Add this line to your ~/.zshrc after the line that sources ~/.p10k.zsh:"
    echo "  [[ -f ~/.rick-p10k-integration.zsh ]] && source ~/.rick-p10k-integration.zsh"
  fi
  
  # Provide general recommendations
  echo
  echo "If you're still having issues:"
  echo "1. Run 'p10k configure' to reset your Powerlevel10k configuration"
  echo "2. Make sure you source ~/.rick-p10k-integration.zsh AFTER ~/.p10k.zsh"
  echo "3. Enable debug mode: export RICK_P10K_DEBUG=true"
  echo "4. Reload your shell with: exec zsh"
  echo
}

# Main diagnostic function
run_diagnostics() {
  print_header "Rick Assistant Powerlevel10k Diagnostics"
  
  check_environment
  echo
  check_configuration
  echo
  check_prompt_elements
  echo
  test_segment_rendering
  echo
  check_wsl
  echo
  check_commands
  echo
  check_distribution
  echo
  print_summary
}

# Run diagnostics when script is executed
run_diagnostics 