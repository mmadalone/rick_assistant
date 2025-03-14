#!/usr/bin/env zsh
#
# Rick Assistant - Powerlevel10k Integration Test
# This script tests if the Rick Assistant segment works correctly with Powerlevel10k
#

# Define colors for output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[0;33m'
blue='\033[0;34m'
cyan='\033[0;36m'
nc='\033[0m' # No Color

# Header
echo -e "\n${cyan}Rick Assistant Powerlevel10k Test${nc}\n"
echo -e "${blue}==================================${nc}\n"

# Check if p10k is installed
if ! command -v p10k &> /dev/null; then
    echo -e "${red}Error: Powerlevel10k is not installed${nc}"
    echo "Please install Powerlevel10k to use this integration."
    exit 1
fi

# Check if the p10k.zsh file exists
P10K_CONFIG="${ZDOTDIR:-$HOME}/.p10k.zsh"
if [[ ! -f "$P10K_CONFIG" ]]; then
    echo -e "${red}Error: $P10K_CONFIG not found${nc}"
    echo "Run 'p10k configure' to create it."
    exit 1
fi

# Check if Rick Assistant segment is defined
if ! grep -q "function prompt_rick_assistant" "$P10K_CONFIG"; then
    echo -e "${red}Error: Rick Assistant segment not defined in p10k.zsh${nc}"
    echo "Run 'rick p10k right' to add it."
    exit 1
fi

echo -e "${green}✓${nc} Powerlevel10k is installed"
echo -e "${green}✓${nc} p10k.zsh file exists"
echo -e "${green}✓${nc} Rick Assistant segment is defined"

# Test Python environment
echo -e "\n${cyan}Testing Python Environment${nc}"
echo -e "${blue}------------------------${nc}"

if ! command -v python3 &> /dev/null; then
    echo -e "${red}Error: Python3 is not installed${nc}"
    echo "Python3 is required for Rick Assistant to work."
    exit 1
fi

echo -e "${green}✓${nc} Python3 is installed"

# Test psutil installation
if python3 -c "import psutil" &> /dev/null; then
    echo -e "${green}✓${nc} psutil module is installed"
else
    echo -e "${yellow}Warning: psutil module is not installed${nc}"
    echo "Some system metrics may not be available."
    echo "Run 'pip install psutil' to enable all features."
fi

# Test Rick module imports
if python3 -c "
import sys
import os
try:
    # Add current directory to path to find modules
    sys.path.append('$(pwd)')
    from src.core.prompt import get_rick_phrase
    from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
" | grep -q "SUCCESS"; then
    echo -e "${green}✓${nc} Rick module imports work correctly"
else
    echo -e "${red}Error: Failed to import Rick modules${nc}"
    echo "There may be an issue with the Python path or module structure."
    exit 1
fi

# Test segment rendering
echo -e "\n${cyan}Testing Segment Rendering${nc}"
echo -e "${blue}------------------------${nc}"

# Set position for testing
export RICK_POSITION="right"

# Test the segment function directly
echo -e "Testing sample output:"
echo -e "${blue}----------------${nc}"

if typeset -f prompt_rick_assistant &> /dev/null; then
    # Create a mock p10k segment_main function if not in p10k context
    if ! typeset -f p10k &> /dev/null; then
        p10k() {
            if [[ "$1" == "segment_main" ]]; then
                local segment="$2"
                local -i state="$3"
                shift 3
                local content=""
                local -A parameters=("${@[@]}")
                content="${parameters[content]}"
                echo "Segment: $segment, State: $state, Content: $content"
            fi
        }
    fi
    
    # Make a direct call to the segment function
    # This outputs what would be sent to p10k
    output=$(prompt_rick_assistant)
    if [[ -n "$output" ]]; then
        echo -e "${green}Segment renders output:${nc}"
        echo -e "$output"
    else
        echo -e "${red}Error: No output from segment function${nc}"
    fi
else
    echo -e "${red}Error: prompt_rick_assistant function not defined${nc}"
    echo "The segment may not be properly installed in p10k.zsh."
    exit 1
fi

# Test direct Python generation
echo -e "\n${cyan}Testing Direct Python Generation${nc}"
echo -e "${blue}-----------------------------${nc}"

python3 -c "
try:
    import sys
    import os
    
    # Add current directory to path to find modules
    sys.path.append('$(pwd)')
    
    # Import functions
    from src.core.prompt import get_rick_phrase
    from src.utils.system import get_cpu_usage, get_ram_info, get_cpu_temperature
    
    # Test them directly
    print('Direct function test output:')
    print('---------------------------')
    print(f'Rick phrase: {get_rick_phrase(for_p10k=True)}')
    
    # Get metrics
    cpu = get_cpu_usage()
    ram = get_ram_info()
    temp = get_cpu_temperature()
    
    print(f'CPU: {cpu.get(\"usage\", \"N/A\")}% ({cpu.get(\"state\", \"unknown\")})')
    print(f'RAM: {ram.get(\"percent\", \"N/A\")}% ({ram.get(\"state\", \"unknown\")})')
    if temp.get('available', False):
        print(f'Temperature: {temp.get(\"temperature\", \"N/A\")}°C ({temp.get(\"state\", \"unknown\")})')
    else:
        print('Temperature: Not available')
    
except Exception as e:
    print(f'Error during Python test: {str(e)}')
"

# Summary
echo -e "\n${cyan}Summary${nc}"
echo -e "${blue}-------${nc}"
echo -e "All tests completed. If you see any errors above, check the following:"
echo -e "1. Ensure Powerlevel10k is properly installed"
echo -e "2. Ensure Rick Assistant is properly installed"
echo -e "3. Ensure Python3 and required modules are installed"
echo -e "4. Run 'rick diagnose' for full diagnostics"
echo -e "5. Run 'rick p10k right' to reinstall the segment"

echo -e "\nIf everything looks good, reload your shell with:"
echo -e "  ${yellow}source ~/.zshrc${nc}"
echo -e "  ${yellow}p10k reload${nc}" 