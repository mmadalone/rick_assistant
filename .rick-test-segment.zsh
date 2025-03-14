#!/usr/bin/env zsh

# Rick Assistant Segment Test Script
# This script tests the Rick Assistant segment and fixes any issues

# First, check if Powerlevel10k is loaded
echo "Checking Powerlevel10k installation..."
if ! typeset -f p10k >/dev/null 2>&1; then
  echo "❌ Powerlevel10k is not properly loaded in this shell session!"
  echo "Please ensure Powerlevel10k is installed and activated in your .zshrc"
  
  # Try to source p10k configuration if it exists
  if [[ -f ~/.p10k.zsh ]]; then
    echo "Found ~/.p10k.zsh, trying to source it..."
    source ~/.p10k.zsh
    if typeset -f p10k >/dev/null 2>&1; then
      echo "✅ Successfully loaded p10k function!"
    else
      echo "Still couldn't load p10k function. Try running 'source ~/.zshrc' first."
      echo "Then run this test script again."
      exit 1
    fi
  else
    echo "Couldn't find ~/.p10k.zsh configuration file."
    echo "Try running 'source ~/.zshrc' first, then run this test script again."
    exit 1
  fi
fi

# Source our segment definition
if [[ -f ~/.rick-p10k-segment.zsh ]]; then
  echo "Loading segment definition..."
  source ~/.rick-p10k-segment.zsh
else
  echo "Error: Segment definition file not found!"
  exit 1
fi

# Check if our segment function is defined
if typeset -f prompt_my_rick_metrics >/dev/null; then
  echo "✅ Segment function is properly defined"
else
  echo "❌ Segment function is NOT defined correctly"
  exit 1
fi

# Create a simplified test segment function
echo "Creating a simplified test segment..."

prompt_my_rick_test() {
  # Simple content for testing
  local content="🧪 RICK TEST SEGMENT IS WORKING!"
  
  # Use p10k segment with high visibility styling
  p10k segment -f red -b yellow -i "🧪" -t "$content"
}

# Add our test segment to prompt elements - fixed array check
echo "Adding test segment to prompt elements..."

# Initialize the array if not already defined
if ! typeset -p POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS >/dev/null 2>&1; then
  echo "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS array is not defined."
  echo "Creating default array..."
  typeset -g -a POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(time)
fi

# Safe way to check if element exists in array
if [[ "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[(r)my_rick_test]}" != "my_rick_test" ]]; then
  echo "Adding my_rick_test to prompt elements..."
  # Add to beginning of right prompt
  POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    my_rick_test
    "${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]}"
  )
  
  # Set styling parameters with high visibility
  typeset -g POWERLEVEL9K_MY_RICK_TEST_FOREGROUND="red"
  typeset -g POWERLEVEL9K_MY_RICK_TEST_BACKGROUND="yellow"
  
  echo "✅ Test segment added to prompt elements"
else
  echo "Test segment was already in prompt elements"
fi

# Test direct invocation of the segment function
echo ""
echo "Testing direct invocation of segment function..."
if typeset -f prompt_my_rick_test >/dev/null; then
  echo "Results from direct function call (should see output below):"
  prompt_my_rick_test
  echo ""
  echo "If you see any error messages above, there's an issue with the segment function."
fi

# Now try to reload p10k
echo "Reloading Powerlevel10k..."
if typeset -f p10k >/dev/null 2>&1; then
  p10k reload
  echo "✅ Powerlevel10k reloaded"
else
  echo "❌ p10k function not found!"
fi

echo ""
echo "Test completed. You should now see a brightly colored test segment in your prompt."
echo "If you still don't see any segment, try adding this line to your .zshrc after p10k configuration:"
echo ""
echo "  # Add rick test segment to prompt elements"
echo "  POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=(my_rick_test)"
echo ""
echo "Then run 'source ~/.zshrc' to apply changes." 