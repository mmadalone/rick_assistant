#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Diagnostics
# This script performs diagnostic checks for Rick Assistant's p10k integration
#

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}Rick Assistant Powerlevel10k Diagnostics${NC}\n"
echo -e "${BLUE}=================================================${NC}\n"

# Test system metrics
echo -e "${CYAN}Testing system metrics module${NC}"
echo -e "${BLUE}--------------------------${NC}"
if command -v python3 >/dev/null 2>&1; then
    python3 -c "
try:
    from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
    
    print('System Module Test')
    print('------------------')
    
    cpu_info = get_cpu_usage()
    print(f'CPU Usage: {cpu_info.get(\"usage\")}%')
    
    ram_info = get_ram_info()
    print(f'RAM Usage: {ram_info.get(\"percent\")}%')
    
    temp_info = get_cpu_temperature()
    print(f'Temperature Available: {temp_info.get(\"available\")}')
    if temp_info.get('available'):
        print(f'CPU Temperature: {temp_info.get(\"temperature\")}°C')
except Exception as e:
    print(f'Error testing system module: {str(e)}')
"
fi

# Environment check
echo -e "\n${CYAN}Environment Check${NC}"
echo -e "${BLUE}------------------------------------------------${NC}"
echo -e "✓ ZSH Version: $(zsh --version)"
if [[ $? -eq 0 ]]; then
    echo -e "✓ ZSH version is compatible"
else
    echo -e "✗ ZSH version check failed"
fi

# Check for Powerlevel10k
if type p10k >/dev/null 2>&1; then
    echo -e "✓ Powerlevel10k: Installed"
    echo -e "✓ Powerlevel10k is detected"
else
    echo -e "✗ Powerlevel10k not detected"
fi

# Check p10k command
if type p10k >/dev/null 2>&1; then
    echo -e "✓ p10k command: Available"
    if p10k segment-in-use dir 2>/dev/null; then
        echo -e "✓ p10k command is available"
    else
        echo -e "✗ p10k command seems broken"
    fi
fi

# Configuration files
echo -e "\n${CYAN}Configuration Files${NC}"
echo -e "${BLUE}------------------------------------------------${NC}"
if [[ -f ~/.p10k.zsh ]]; then
    echo -e "✓ ~/.p10k.zsh: Found"
    if grep -q "Rick" ~/.p10k.zsh 2>/dev/null; then
        echo -e "✓ p10k.zsh configuration file exists"
    fi
else
    echo -e "✗ ~/.p10k.zsh not found"
fi

if [[ -f ~/.zshrc ]]; then
    if grep -q "p10k.zsh" ~/.zshrc 2>/dev/null; then
        echo -e "✓ p10k source directive found"
    else
        echo -e "✗ No p10k.zsh sourcing in ~/.zshrc"
    fi
fi

# Rick segment check
if type p10k >/dev/null 2>&1; then
    if grep -q "function prompt_rick_assistant" ~/.p10k.zsh 2>/dev/null; then
        echo -e "✓ Rick segment is defined in p10k.zsh"
    else
        echo -e "✗ Rick segment not found in p10k.zsh"
    fi
fi

# Integration check
if [[ -f "${ZDOTDIR:-$HOME}/.p10k.zsh" ]]; then
    echo -e "✓ Integration script: Found"
    if [[ -f "${ZDOTDIR:-$HOME}/.rick_assistant/backups/p10k.zsh.backup."* ]]; then
        echo -e "✓ p10k_integration.zsh exists"
    fi
fi

# Prompt Elements Check
echo -e "\n${CYAN}Prompt Elements Check${NC}"
echo -e "${BLUE}------------------------------------------------${NC}"

# Check RICK_POSITION
if [[ -n "$RICK_POSITION" ]]; then
    echo -e "RICK_POSITION: ${RICK_POSITION}"
    
    # Check if the segment is in the prompt elements
    if [[ "$RICK_POSITION" == "right" ]]; then
        elements_var="POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS"
        if type -p $elements_var >/dev/null 2>&1; then
            if typeset -p $elements_var 2>/dev/null | grep -q "rick_assistant"; then
                echo -e "✓ rick_assistant is in POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS"
            else
                echo -e "✗ rick_assistant not found in right prompt elements"
            fi
        fi
    elif [[ "$RICK_POSITION" == "left" ]]; then
        elements_var="POWERLEVEL9K_LEFT_PROMPT_ELEMENTS"
        if typeset -p $elements_var 2>/dev/null | grep -q "rick_assistant"; then
            echo -e "✓ rick_assistant is in POWERLEVEL9K_LEFT_PROMPT_ELEMENTS"
        else
            echo -e "✗ rick_assistant not found in left prompt elements"
        fi
    elif [[ "$RICK_POSITION" == "dir" ]]; then
        elements_var="POWERLEVEL9K_LEFT_PROMPT_ELEMENTS"
        if typeset -p $elements_var 2>/dev/null | grep -q "rick_assistant"; then
            echo -e "✓ rick_segment is in prompt elements"
        else
            echo -e "✗ rick_assistant not found in prompt elements"
        fi
    fi
else
    echo -e "✗ RICK_POSITION is not set"
fi

# Rick Function Check
echo -e "\n${CYAN}Rick Function Check${NC}"
echo -e "${BLUE}------------------------------------------------${NC}"
if type prompt_rick_assistant >/dev/null 2>&1; then
    echo -e "✓ prompt_rick_assistant function: Defined"
else
    echo -e "✗ Rick prompt function is not defined"
fi

if command -v python3 >/dev/null 2>&1; then
    echo -e "✓ Python3: Available"
    if python3 -c "import sys; sys.exit(0)" 2>/dev/null; then
        echo -e "✓ Python3 is available"
    fi
else
    echo -e "✗ Python3 is not available"
fi

# Check if psutil is installed
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import psutil; print('✓ psutil Python module: Installed')" 2>/dev/null; then
    else
        echo -e "✗ psutil Python module is not installed"
        echo -e "  Run 'pip3 install psutil' to enable system metrics"
    fi
fi

# Check Rick module
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import sys; sys.path.append('${PWD}'); import src; print('✓ Rick module: Accessible')" 2>/dev/null; then
        echo -e "✓ Rick Python module is accessible"
    else
        echo -e "✗ Rick Python module is not accessible"
    fi
fi

# Summary and Recommendations
echo -e "\n${CYAN}Summary and Recommendations${NC}"
echo -e "${BLUE}------------------------------------------------${NC}"

# Check if all required components are present
if type p10k >/dev/null 2>&1 && [[ -f ~/.p10k.zsh ]] && type prompt_rick_assistant >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}All checks passed! Rick Assistant should be working correctly.${NC}"
    echo -e "If you're still having issues, try reloading your ZSH configuration:"
    echo -e "  source ~/.zshrc"
    echo -e "  p10k reload"
else
    echo -e "${RED}Some checks failed. Please review the issues above.${NC}"
    if ! type p10k >/dev/null 2>&1; then
        echo -e "- Powerlevel10k is not installed or not configured properly"
    fi
    if ! [[ -f ~/.p10k.zsh ]]; then
        echo -e "- p10k.zsh configuration file is missing"
    fi
    if ! type prompt_rick_assistant >/dev/null 2>&1; then
        echo -e "- Rick prompt function is not defined"
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "- Python3 is not available"
    fi
fi 