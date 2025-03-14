# 🧪 Rick Assistant ZSH Plugin - Prompt Template System

## 📊 Overview

This document provides a complete **prompt template system** for developing the Rick Assistant ZSH plugin using GitHub Copilot with **zero coding knowledge required**. Each template is designed for direct copy-paste use.

### 🚀 How To Use This Template System

1. **Choose a component** you want to implement
2. **Copy** the corresponding template
3. **Paste** it directly to your code editor
4. Let **Copilot generate** the implementation
5. **Verify** the output visually
6. If needed, try an **alternative template** for better results

## 🔍 Template Categories

- **📁 File Creation Templates**: Create basic file structures
- **🧰 Component Implementation Templates**: Implement specific functionality
- **🔄 Enhancement Templates**: Improve existing components
- **🔎 Troubleshooting Templates**: Fix common issues

---

## 📁 File Creation Templates

### Basic Python File Template

```
Create a Python module for a Rick Sanchez-themed ZSH assistant with:

1. Import statements for required modules
2. Module-level constants and configuration
3. Main functionality functions
4. Helper utility functions
5. If __name__ == "__main__" section for testing

Add detailed docstrings explaining the purpose of the module and functions.
Include error handling with try/except blocks.
Follow Python best practices with proper function signatures.
Add Rick-themed comments where appropriate.

The module should handle [SPECIFIC_FUNCTIONALITY].
```

### Module With Class Template

```
Create a Python module with a class for a Rick Sanchez-themed ZSH assistant that:

1. Defines a [CLASS_NAME] class with:
   - __init__ method with appropriate parameters
   - Core functionality methods
   - Helper methods
   - Properties for key attributes
   - Static methods where appropriate

2. Implements these key features:
   - [FEATURE_1]
   - [FEATURE_2]
   - [FEATURE_3]

Include proper error handling throughout.
Add comprehensive docstrings for the class and methods.
Implement Rick-themed messages and personality.
Follow object-oriented best practices.

Also add a simple usage example at the end of the file.
```

### Configuration File Template

```
Create a JSON configuration file for a Rick Sanchez-themed ZSH assistant with these sections:

1. General settings:
   - Plugin activation
   - Log levels
   - Basic configuration

2. UI preferences:
   - Colors
   - Prompt style
   - Animation settings

3. Personality parameters:
   - Sass level
   - Burp frequency
   - Catchphrase frequency

4. System settings:
   - Refresh rate
   - Display options
   - Monitoring configuration

5. Command safety:
   - Warning levels
   - Confirmation settings
   - Whitelist configuration

Format the JSON with proper indentation and include comments where allowed.
Use realistic default values that create a sassy Rick personality.
```

---

## 🧰 Component Implementation Templates

### Logging System Template

```
Create a comprehensive logging module for a Rick Sanchez-themed ZSH assistant that:

1. Uses Python's standard logging module
2. Writes logs to ~/.rick_assistant/logs/
3. Implements daily log rotation with size limits
4. Includes timestamps and formatted messages
5. Prevents logging errors from crashing the terminal

Implement these specific functions:
- setup_logger(): Configure the logging system
- get_logger(name): Get a logger for a component
- log_exception(e): Log exceptions with traceback
- set_log_level(level): Change the logging level
- ensure_log_directory(): Create log directory if needed

Include Rick-themed critical error messages.
Make all functions safe with try/except blocks.
Format log messages consistently with level, timestamp, and component.
```

### Command Processor Template

```
Create a command processor module for a Rick Sanchez-themed ZSH assistant that:

1. Intercepts commands before execution
2. Distinguishes between shell and assistant commands
3. Identifies potentially dangerous commands
4. Provides command suggestions and corrections
5. Maintains Rick's personality in all interactions

Implement these specific functions:
- process_command(cmd): Main entry point for processing
- is_dangerous_command(cmd): Check for risky commands
- suggest_correction(cmd): Offer typo corrections
- execute_assistant_cmd(cmd): Handle assistant commands
- format_output(result): Format results with Rick's style

Assistant commands should start with '!' (like !help).
Include pattern matching for risky operations (rm -rf, etc.).
Add Rick-styled responses for command feedback.
Implement command history tracking for context.
```

### Menu System Template

```
Create a menu system module for a Rick Sanchez-themed ZSH assistant that:

1. Displays interactive terminal menus
2. Supports hierarchical menu structures
3. Handles keyboard navigation
4. Includes Rick-themed animations and styling
5. Adapts to different terminal sizes

Implement these core components:
- Menu: Base class for all menus
- MenuItem: Selectable menu items
- MenuCategory: Groupings of related items
- MenuAction: Items that trigger functions
- MenuToggle: On/off toggle items

Add these portal-themed visual effects:
- Portal opening animation
- Selection highlighting with glow
- Transition animations between menus
- Rick's commentary with typing effect
- Loading spinners for operations

Style all menus with green portal colors and science themes.
Make animations optional and configurable.
Include Rick's sarcastic comments throughout the menu system.
```

### AI Integration Template

```
Create an AI model framework for a Rick Sanchez-themed ZSH assistant that:

1. Defines a common interface for AI models
2. Supports OpenAI API integration
3. Handles API key management securely
4. Implements token counting and limits
5. Provides fallback to local "Fake Rick" if AI fails

Implement these specific classes:
- AIModel: Abstract base class with common methods
- OpenAIModel: Implementation for OpenAI API
- FakeRickModel: Local fallback implementation
- ModelManager: Handles model selection and fallbacks

Add these core methods:
- generate_response(prompt): Get AI-generated response
- count_tokens(text): Count tokens in text
- is_available(): Check if model is accessible
- handle_api_errors(error): Process API issues gracefully
- secure_api_key(key): Store API key securely

Make the system robust with comprehensive error handling.
Implement smooth fallback mechanisms if API fails.
Add timeout handling to prevent blocking the terminal.
Include token usage tracking and cost estimation.
```

---

## 🔄 Enhancement Templates

### Performance Optimization Template

```
Optimize the performance of [COMPONENT_NAME] for a Rick Sanchez-themed ZSH assistant by:

1. Implementing efficient caching mechanisms
2. Adding asynchronous processing where appropriate
3. Reducing unnecessary operations
4. Implementing lazy loading for resource-intensive features
5. Adding performance monitoring capabilities

Make these specific improvements:
- Add time_execution decorator to measure function performance
- Implement caching for expensive operations with TTL
- Create async versions of blocking operations
- Add resource usage monitoring and limits
- Optimize startup time and reduce overhead

Focus optimization on these critical areas:
- Prompt rendering performance
- Command processing speed
- System metric collection efficiency
- Menu rendering and animation smoothness
- AI request handling

Maintain all existing functionality while improving performance.
Add configuration options to enable/disable optimizations.
Include before/after metrics in comments to document improvements.
```

### Feature Extension Template

```
Extend [COMPONENT_NAME] for a Rick Sanchez-themed ZSH assistant with these new features:

1. Add [NEW_FEATURE_1] that:
   - Implements [FUNCTIONALITY]
   - Supports [CAPABILITY]
   - Integrates with [EXISTING_COMPONENT]

2. Enhance existing [EXISTING_FEATURE] to:
   - Improve [ASPECT]
   - Add support for [NEW_CAPABILITY]
   - Fix limitations with [LIMITATION]

3. Create new utility functions:
   - [FUNCTION_1]: [PURPOSE]
   - [FUNCTION_2]: [PURPOSE]
   - [FUNCTION_3]: [PURPOSE]

Maintain backward compatibility with existing code.
Follow the same style and error handling patterns.
Add comprehensive documentation for new features.
Ensure Rick's personality remains consistent throughout.
Include configuration options for all new features.
```

### UI Enhancement Template

```
Enhance the user interface of [COMPONENT_NAME] for a Rick Sanchez-themed ZSH assistant with:

1. Improved visual styling:
   - Add color-coding for different elements
   - Implement better spacing and layout
   - Create visual hierarchy for information
   - Add Rick-themed borders and decorations

2. New interactive elements:
   - Add keyboard shortcuts for common actions
   - Improve selection and navigation
   - Implement progressive disclosure for complex options
   - Add visual feedback for user actions

3. Adaptive layout features:
   - Implement responsive design for different terminal widths
   - Create compact mode for limited space
   - Add fullscreen mode for detailed information
   - Support different terminal capabilities

Maintain functionality while improving aesthetics.
Add configuration options for all visual elements.
Include accessibility considerations where possible.
Keep Rick's personality evident in the UI enhancements.
```

---

## 🔎 Troubleshooting Templates

### Bug Fix Template

```
Fix the bug in [COMPONENT_NAME] where [PROBLEM_DESCRIPTION]:

1. Identify the root cause:
   - Check for [POSSIBLE_ISSUE_1]
   - Verify [CONDITION]
   - Inspect [RELEVANT_CODE]

2. Implement the fix:
   - Update the affected function(s)
   - Add proper error handling
   - Fix edge cases and input validation
   - Ensure thread safety if applicable

3. Add regression prevention:
   - Add validation checks
   - Implement defensive programming techniques
   - Add comments explaining the fix
   - Create example usage to demonstrate correct behavior

Maintain all existing functionality while fixing the bug.
Add detailed comments explaining the issue and solution.
Keep Rick's personality consistent in any modified messages.
Ensure the fix is compatible with all platforms.
```

### Error Recovery Template

```
Improve error handling in [COMPONENT_NAME] for a Rick Sanchez-themed ZSH assistant:

1. Identify potential failure points:
   - External dependencies like system calls
   - File operations and IO
   - Network requests and API calls
   - User input processing
   - Resource limitations

2. Implement these error recovery mechanisms:
   - Add comprehensive try/except blocks
   - Create fallback behaviors for failures
   - Implement graceful degradation of features
   - Add self-healing capabilities where possible
   - Ensure the terminal never crashes on errors

3. Enhance error reporting:
   - Add detailed error logging
   - Create user-friendly error messages with Rick's style
   - Implement troubleshooting suggestions
   - Add error codes for documentation reference
   - Create recovery suggestions for common issues

Make error handling thorough but not disruptive.
Maintain Rick's sarcastic personality in error messages.
Ensure shell functionality continues even if Python code fails.
Add configuration options for error verbosity.
```

### Terminal Compatibility Template

```
Improve terminal compatibility of [COMPONENT_NAME] for a Rick Sanchez-themed ZSH assistant:

1. Add support for these terminal types:
   - Basic terminals with limited capabilities
   - Modern terminals with full features
   - WSL/Cygwin environments on Windows
   - macOS Terminal and iTerm2
   - Linux terminal emulators

2. Implement terminal capability detection:
   - Check for color support and adjust output
   - Detect Unicode support for special characters
   - Identify terminal width and height constraints
   - Check for animation capabilities
   - Detect key input support limitations

3. Create adaptive features:
   - Fallback formatting for limited terminals
   - Alternative navigation for restricted input
   - Simplified visuals for basic terminals
   - Text-only mode for minimal environments
   - Performance adjustments for slow terminals

Make compatibility seamless and automatic.
Maintain full functionality where possible.
Create graceful degradation for limited environments.
Add configuration options to force compatibility modes.
Include Rick-style comments about terminal limitations.
```

---

## 📝 Specialized Component Templates

### Dangerous Command Detection Template

```
Create a command safety module for a Rick Sanchez-themed ZSH assistant that:

1. Identifies high-risk shell commands using:
   - Pattern matching for dangerous operations
   - Risk assessment of command components
   - Context awareness for directory contents
   - Understanding of pipe and redirection risks
   - Detection of privilege escalation

2. Implements protection features:
   - Risk level classification (Low/Medium/High)
   - User confirmation requirements based on risk
   - Whitelist system for trusted commands
   - Detailed explanation of identified risks
   - Safety suggestions for risky commands

3. Uses these specific risk patterns:
   - File deletion: rm -rf, find with delete, etc.
   - Disk operations: dd, mkfs, fdisk, etc.
   - System modifications: chmod 777, chown, etc.
   - Network exposure: binding to 0.0.0.0, opening ports
   - Malicious redirections: overwriting system files

Make detection thorough but not annoying to users.
Include Rick-themed warnings with appropriate sarcasm.
Add configuration options for security strictness.
Allow temporary or permanent whitelisting of commands.
Log all dangerous command attempts for security auditing.
```

### Rick Personality System Template

```
Create a personality module for a Rick Sanchez-themed ZSH assistant that:

1. Implements Rick's core personality traits:
   - Sarcastic and impatient responses
   - Scientific terminology and references
   - Occasional burps in dialog (*burp*)
   - Nihilistic and cynical worldview
   - Catchphrases and mannerisms from the show

2. Supports these specific response types:
   - Greetings: "What up *burp* [username]!"
   - Command feedback: "Executing that garbage? Whatever..."
   - Errors: "You really screwed that up, didn't you?"
   - Warnings: "This command looks dangerous, even for me"
   - Catchphrases: "Wubba lubba dub dub!"

3. Includes these customization options:
   - Sass level adjustment (1-10 scale)
   - Burp frequency control (0.0-1.0)
   - Scientific reference density
   - Catchphrase frequency
   - Personality intensity overall

Make the personality feel authentic to the show.
Implement context-awareness for appropriate responses.
Add variety to prevent repetitive responses.
Include at least 20 different response templates per category.
Allow easy extension with custom responses.
```

### System Monitoring Template

```
Create a system monitoring module for a Rick Sanchez-themed ZSH assistant that:

1. Collects these system metrics:
   - CPU usage percentage
   - Memory (RAM) availability and usage
   - CPU temperature when available
   - Disk usage for the current filesystem
   - System uptime and load averages

2. Implements these specific features:
   - Cross-platform support (Linux, macOS)
   - Asynchronous updates to avoid blocking the shell
   - Efficient caching with configurable update intervals
   - Fallbacks for unavailable metrics
   - Consistent formatting with appropriate units

3. Provides these presentation options:
   - Color-coding for metrics based on thresholds
   - Formatting for status bar integration
   - Detailed view for dedicated display
   - Trend tracking for fluctuating metrics
   - Warning indicators for critical values

Use platform-specific commands and libraries appropriately.
Implement error handling for all system calls.
Create an efficient update mechanism that minimizes resource usage.
Add configuration options for refresh intervals and displayed metrics.
Include Rick-themed comments on system status when appropriate.
```

---

## 🔧 Alternative Prompt Strategies

If the standard templates don't yield desired results, try these alternative approaches:

### Step-By-Step Implementation Strategy

```
Create a [COMPONENT_NAME] module for a Rick Sanchez-themed ZSH assistant by following these exact steps:

STEP 1: Create these import statements:
- Import [MODULE_1] for [PURPOSE]
- Import [MODULE_2] for [PURPOSE]
- Import [MODULE_3] for [PURPOSE]

STEP 2: Define these constants:
- [CONSTANT_1] = [VALUE] # [PURPOSE]
- [CONSTANT_2] = [VALUE] # [PURPOSE]
- [CONSTANT_3] = [VALUE] # [PURPOSE]

STEP 3: Implement this main function:
def [FUNCTION_NAME](param1, param2, ...):
    """
    [FUNCTION_DESCRIPTION]
    
    Args:
        param1: [DESCRIPTION]
        param2: [DESCRIPTION]
    
    Returns:
        [RETURN_DESCRIPTION]
    """
    # Implement function body here
    
STEP 4: Add these helper functions:
- [HELPER_1]: [PURPOSE]
- [HELPER_2]: [PURPOSE]
- [HELPER_3]: [PURPOSE]

STEP 5: Add error handling for all functions:
- Use try/except blocks
- Add specific error types
- Include fallback behavior
- Add error logging

STEP 6: Create these Rick-themed messages:
- [MESSAGE_1]: [CONTEXT]
- [MESSAGE_2]: [CONTEXT]
- [MESSAGE_3]: [CONTEXT]

STEP 7: Add a main execution block:
if __name__ == "__main__":
    # Test code here
```

### Function-Based Implementation Strategy

```
Create a [COMPONENT_NAME] module for a Rick Sanchez-themed ZSH assistant with these specific functions:

FUNCTION 1: [FUNCTION_NAME](param1, param2)
PURPOSE: [DESCRIPTION]
IMPLEMENTATION:
- First check [CONDITION]
- Then perform [ACTION]
- Handle [EDGE_CASE]
- Return [RESULT]
ERROR HANDLING:
- Catch [ERROR_TYPE] and [ACTION]
- Ensure [SAFETY_FEATURE]

FUNCTION 2: [FUNCTION_NAME](param1, param2)
PURPOSE: [DESCRIPTION]
IMPLEMENTATION:
- First check [CONDITION]
- Then perform [ACTION]
- Handle [EDGE_CASE]
- Return [RESULT]
ERROR HANDLING:
- Catch [ERROR_TYPE] and [ACTION]
- Ensure [SAFETY_FEATURE]

FUNCTION 3: [FUNCTION_NAME](param1, param2)
PURPOSE: [DESCRIPTION]
IMPLEMENTATION:
- First check [CONDITION]
- Then perform [ACTION]
- Handle [EDGE_CASE]
- Return [RESULT]
ERROR HANDLING:
- Catch [ERROR_TYPE] and [ACTION]
- Ensure [SAFETY_FEATURE]

Also add Rick-themed messages and proper docstrings throughout.
```

### Example-Driven Implementation Strategy

```
Create a [COMPONENT_NAME] module for a Rick Sanchez-themed ZSH assistant based on these usage examples:

EXAMPLE 1:
```python
# Import the module
from src.module import function_name

# Use the primary function
result = function_name('input_parameter')

# Expected output:
# "I'm processing your garbage input, *burp* genius. Result: XYZ"
```

EXAMPLE 2:
```python
# Error handling example
try:
    result = risky_function('bad_input')
except SomeError as e:
    # Should output: "You really screwed that up, didn't you? Error: [error details]"
    handle_error(e)
```

EXAMPLE 3:
```python
# Configuration example
config = {
    'setting1': True,
    'setting2': 'value',
    'sass_level': 8
}
result = configured_function('input', config)
# Should configure behavior based on settings
```

Implement the module to make these examples work as shown.
Add proper error handling, docstrings, and Rick's personality.
```

---

## 📋 Template Customization Guide

### Key Placeholders to Replace

- `[COMPONENT_NAME]`: The specific component to create/modify
- `[FEATURE_NAME]`: A specific feature to implement
- `[FUNCTION_NAME]`: Name of a function to create
- `[DESCRIPTION]`: Detailed explanation of purpose/behavior
- `[PARAMETER]`: Function parameter or input value
- `[RETURN_VALUE]`: What a function should return
- `[ERROR_TYPE]`: Specific error to handle
- `[ACTION]`: Specific action to take
- `[CONDITION]`: Condition to check

### Template Modification Tips

1. **Be specific**: The more specific your template, the better Copilot's output
2. **Provide examples**: Include example code for critical functionality
3. **Specify error handling**: Explicitly describe how errors should be managed
4. **Include personality**: Mention Rick's personality elements for consistency
5. **Prioritize features**: List the most important functionality first

### When Copilot Struggles

If Copilot's implementation is unsatisfactory:

1. **Try again** with the same prompt (results can vary)
2. **Be more specific** about the exact implementation details
3. **Break down** complex components into smaller prompts
4. **Provide examples** of desired functionality
5. **Use alternative templates** from different sections
6. **Combine multiple templates** for complex components

---

## 🚀 Complete Project Implementation Strategy

For optimal results, implement the components in this order:

1. **Core Infrastructure**:
   - Logging System
   - Error Handling
   - Configuration Management
   - Package Initialization

2. **ZSH Integration**:
   - Hook Manager
   - Prompt Formatter
   - Command Processor

3. **Basic Functionality**:
   - Message Storage
   - "Fake Rick" Response System
   - Setup Wizard

4. **UI Components**:
   - System Information
   - Text Formatting
   - Input Handling
   - Menu System

5. **Safety Features**:
   - Dangerous Command Detection
   - Command Execution with Confirmation

6. **Advanced Features**:
   - AI Integration
   - Enhanced Command Suggestions
   - Performance Optimization

Following this sequence will ensure that each component builds on properly implemented dependencies.

---

## 📝 Final Checklist

Before considering any component complete:

- [ ] Code implements all specified functionality
- [ ] Error handling is comprehensive and prevents terminal crashes
- [ ] Rick's personality is consistently applied
- [ ] Performance is optimized for shell environment
- [ ] Configuration options are available for customization
- [ ] Cross-platform compatibility is maintained
- [ ] Documentation is clear and complete

Happy building! And remember what Rick would say: "The universe is a crazy, chaotic place. The only way to navigate it is with a system that's *burp* actually worth a damn. Let's make this one work."
