# 🧪 Rick Assistant ZSH Plugin - Non-Coder Cursor Plan

## 📊 Project Overview

This document provides a **Cursor-optimized development plan** for creating a Rick Sanchez-themed ZSH plugin with zero coding knowledge required. Each section contains **copy-paste ready Cursor prompts** designed for direct use.

### 🎯 Development Approach
- **100% Cursor-Driven**: All code generation handled by AI
- **Copy & Paste Workflow**: Simple prompt-to-editor workflow
- **Visual Validation**: Clear indicators of correct implementation
- **Non-Technical Success Criteria**: Easily verifiable outputs
- **Dual Implementation Strategy**: Both Python and pure ZSH implementations with automatic fallbacks
  - Python implementation for enhanced functionality when available
  - ZSH native implementation for maximum compatibility
  - Seamless runtime detection and switching between implementations
  - User-configurable preference settings

### 🚀 How To Use This Plan
1. **Copy** a numbered prompt from this document
2. **Paste** it directly to your code editor with Cursor
3. **Wait** for Cursor to generate the implementation
4. **Visually verify** the output matches expectations
5. **Save** the file if correct, or try an alternative prompt

---

## 🏗️ Dual Implementation Architecture

This project implements a dual architecture approach that provides both Python-based and pure ZSH implementations of key functionality:

### 📊 Implementation Strategy

1. **Automatic Runtime Detection**:
   - The plugin automatically detects whether Python is available on the system
   - Falls back gracefully to ZSH native implementations when Python is unavailable

2. **User-Configurable Preferences**:
   - Users can explicitly choose their preferred implementation:
     - `ui___menu___use_python_implementation: true` - Use Python implementation when available
     - `ui___menu___use_python_implementation: false` - Always use ZSH native implementation
     - `ui___menu___use_python_implementation: auto` - Automatically select based on availability (default)

3. **Implementation Differences**:
   - **Python Implementation**:
     - Richer user interface with more visual elements
     - More sophisticated menu navigation
     - Better unicode and color support
   
   - **ZSH Native Implementation**:
     - Faster startup time
     - No external dependencies
     - Works in environments without Python
     - Lighter weight with minimal overhead

4. **Switching Between Implementations**:
   - Users can toggle between implementations via settings menu
   - Changes take effect immediately without plugin reload
   - Implementation-specific preferences are preserved

This architecture ensures maximum compatibility across different environments while allowing enhanced functionality where possible.

---

## 📝 Phase 0: Project Setup

### 0.1: Environment Preparation
Before starting development, create these directories where you'll store the project files:

```
mkdir -p ~/.oh-my-zsh/custom/plugins/rick_assistant/src/{core,ui,ai,utils,config}
mkdir -p ~/.oh-my-zsh/custom/plugins/rick_assistant/tests
cd ~/.oh-my-zsh/custom/plugins/rick_assistant
```

### 0.2: File Creation Guide
For each implementation prompt:
1. Navigate to the correct directory
2. Create the file using a text editor or `touch` command
3. Paste the corresponding Cursor prompt
4. Let Cursor generate the implementation
5. Save the file

---

## 📦 Phase 1: Core Foundation

### 1.1: Main Plugin Entry Point (DONE 08/03@17:33)

**📄 File**: rick_assistant.plugin.zsh`

**✅ Success Indicators**:
- File contains ZSH functions for hook integration
- Includes Python environment detection
- References the correct directory structure
- Contains Powerlevel10k integration code

### 1.2: Logging System (DONE 08/03@20:33)

**📄 File**: src/utils/logger.py

**🔤 Cursor Prompt**:
```
Create a Python logging module for a Rick Sanchez-themed ZSH assistant with these features:
1. Write logs to ~/.rick_assistant/logs/
2. Support multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. Implement log rotation with daily files and 5MB size limits, keeping 10 backups
4. Include timestamps and formatted log messages
5. Create these functions:
   - setup_logger(): Initialize the logging system
   - get_logger(name): Get a logger for a specific component
   - log_exception(e): Log exception details with traceback
   - set_log_level(level): Change the current log level

Use Python's standard logging module. Ensure the logging directory is created if it doesn't exist.
Make all functions safe with try/except blocks to prevent terminal crashes.
Add Rick-themed messages for critical errors.

The main usage should be:
```python
from src.utils.logger import get_logger
logger = get_logger("component_name")
logger.info("Information message")
logger.error("Something went wrong")
```

**✅ Success Indicators**:
- Contains setup_logger() and get_logger() functions
- Includes code to create the logs directory
- Implements log rotation using RotatingFileHandler
- Contains error handling with try/except blocks

### 1.3: Error Handling System (DONE 08/03@21:45)

**📄 File**: src/utils/errors.py

**🔤 Cursor Prompt**:
```
Create an error handling module for a Rick Sanchez-themed ZSH assistant with these features:

1. Define these custom exception classes:
   - RickAssistantError: Base exception for all plugin errors
   - ConfigError: Configuration related errors
   - ShellError: Shell integration errors
   - AIError: AI-related errors
   - ResourceError: System resource issues

2. Create a safe_execute decorator function that:
   - Takes a function as input
   - Wraps the function in try/except
   - Catches all exceptions and logs them
   - Returns a safe default value on error
   - Adds Rick-themed error messages
   - Prevents terminal crashes

3. Implement helper functions:
   - format_error(e): Creates user-friendly error messages with Rick's personality
   - handle_exception(e): Central exception handler
   - is_critical_error(e): Determines if an error is severe
   - get_error_fallback(func_name): Gets appropriate fallback values

Use Rick's sarcastic tone for error messages like:
"Wow, you really broke it this time, *burp* genius. {error_msg}"
"That's about as functional as Jerry's *burp* career. {error_msg}"

Include extensive try/except blocks to make everything bulletproof.
```

**✅ Success Indicators**:
- Contains custom exception classes
- Includes safe_execute decorator function
- Implements helper functions for error handling
- Contains Rick-themed error messages

### 1.4: Configuration Management System (DONE 08/03@22:01)

**📄 File**: src/utils/config.py

**🔤 Cursor Prompt**:
```
Create a configuration management module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core functions:
   - load_config(): Load config from ~/.rick_assistant/config.json
   - save_config(config): Save config to file with safe atomic write
   - get_default_config(): Generate default configuration
   - validate_config(config): Ensure config has required fields
   - get_config_value(key, default=None): Safely get config value with fallback

2. Support these configuration categories:
   - general: Plugin activation, log levels
   - ui: Colors, prompt style, animation settings
   - personality: Sass level, burp frequency, catchphrase frequency
   - system: Refresh rate, display options, metrics to show
   - safety: Warning levels, confirmation settings for dangerous commands

3. Add these utility functions:
   - ensure_config_dir(): Create config directory if it doesn't exist
   - repair_config(): Fix corrupted configuration files
   - reset_to_defaults(): Reset configuration to defaults
   - config_exists(): Check if configuration file exists

Make all functions safe with try/except to prevent terminal crashes.
Use atomic write operations to prevent corrupted config files.
Have the default configuration create a "sassy" Rick personality.

Default config should look like:
```json
{
  "general": {
    "enabled": true,
    "log_level": "INFO"
  },
  "ui": {
    "theme": "portal",
  },
  "personality": {
    "sass_level": 7,
    "burp_frequency": 0.3
  }
}
```
```

**✅ Success Indicators**:
- Contains functions for loading and saving configuration
- Includes default configuration generation
- Implements validation and error handling
- Contains atomic write operations for config safety
```

### 1.5: Path/File Validation System (DONE 08/03@22:01)

**📄 File**: src/utils/validation.py

**🔤 Cursor Prompt**:
```
Create a validation module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement path and file validation functions:
   - is_valid_path(path): Check if a path is valid and accessible
   - sanitize_path(path): Clean and normalize a path
   - ensure_directory(path): Create directory if it doesn't exist
   - is_safe_file_operation(path, operation): Check if file operation is safe

2. Add input validation functions:
   - validate_string(value, min_length=0, max_length=None): Validate string
   - validate_integer(value, min_value=None, max_value=None): Validate integer
   - validate_boolean(value): Validate boolean value
   - validate_enum(value, valid_values): Validate value is in allowed options

3. Create command safety validation:
   - is_dangerous_command(cmd): Check if a command is potentially dangerous
   - contains_suspicious_pattern(text, patterns): Check for suspicious patterns
   - is_sudo_command(cmd): Check if command requires elevated privileges

4. Add type conversion functions:
   - safe_int(value, default=0): Safely convert to int with fallback
   - safe_float(value, default=0.0): Safely convert to float with fallback
   - safe_bool(value, default=False): Safely convert to boolean with fallback
   - safe_list(value, default=None): Safely convert to list with fallback

Add detailed docstrings explaining each function's purpose and parameters.
Make all functions extremely safe with thorough error handling.
```

**✅ Success Indicators**:
- Contains path and file validation functions
- Includes input validation for different data types
- Implements command safety validation
- Contains type conversion with fallbacks

### 1.6: Package Initialization (DONE 09/03@03:33)

**📄 File**: /src/__init__.py

**🔤 Cursor Prompt**:
```
Create a Python package initialization file for a Rick Sanchez-themed ZSH assistant with:

1. Version information:
   - __version__ = "0.1.0"
   - __author__ = "Your Name"
   - __description__ = "Rick Sanchez-themed ZSH assistant"

2. Package metadata as a dictionary:
   - METADATA = {
       "name": "rick_assistant",
       "version": __version__,
       "description": __description__,
       "author": __author__,
       "github": "https://github.com/yourusername/rick_assistant"
   }

3. Basic initialization code:
   - Initialize logging
   - Set up package structure
   - Create placeholder for plugin instance

Add a detailed module docstring explaining the purpose of the package.
Include a brief ASCII art of Rick for fun.

Example usage:
```python
from rick_assistant import METADATA
print(f"Running {METADATA['name']} version {METADATA['version']}")
```
```

**✅ Success Indicators**:
- Contains version and metadata information
- Includes ASCII art of Rick
- Contains docstring explaining package purpose
```
---

## 🖥️ Phase 2: ZSH Integration & Basic Functionality

### 2.1: ZSH Hook Manager (DONE 09/03@03:33)

**📄 File**: src/core/hooks.py

**🔤 Cursor Prompt**:
```
Create a ZSH hook manager module for a Rick Sanchez-themed assistant with these features:

1. Implement these core hook functions:
   - register_precmd_hook(callback): Register function to run before prompt
   - register_preexec_hook(callback): Register function to run before command execution
   - register_chpwd_hook(callback): Register function to run when directory changes
   - safe_execute_hook(hook_type, *args): Safely execute registered hook

2. Create these hook handler functions:
   - precmd_handler(): Called before displaying the prompt
   - preexec_handler(command): Called before executing a command
   - chpwd_handler(): Called when changing directories

3. Add these utility functions:
   - initialize_hooks(): Set up all hook registrations
   - cleanup_hooks(): Clean up hooks on plugin deactivation
   - is_hook_registered(hook_type, callback): Check if hook is registered

4. Implement these safety features:
   - Catch and log all exceptions in hook execution
   - Prevent shell crashes if Python code fails
   - Provide fallback behavior for hook failures
   - Include timeout mechanism for long-running hooks

Make all hook functions extremely safe - if Python crashes, the user's shell must continue working.
Include detailed logging for debugging.

Sample usage:
```python
def my_precmd_function():
    print("Running before prompt")

register_precmd_hook(my_precmd_function)
```
```

**✅ Success Indicators**:
- Contains hook registration functions
- Includes handler functions for precmd, preexec, and chpwd
- Implements safety features to prevent shell crashes
- Contains utility functions for hook management
```

### 2.2: Prompt Formatter (DONE 09/03@04:20)

**📄 File**: src/core/prompt.py

**🔤 Cursor Prompt**:
```
Create a prompt formatter module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these prompt generator functions:
   - format_rick_prompt(): Create the Rick prompt ("🧪 Rick> ")
   - format_user_prompt(username): Create user prompt ("👹 Username> ")
   - format_status_bar(path, catchphrase): Create status bar with path and catchphrase
   - get_prompt_structure(): Combine all elements into complete prompt

2. Add these prompt components:
   - get_username(): Detect and return current username
   - format_current_directory(path): Format directory for display
   - truncate_path(path, max_length): Shorten long paths intelligently
   - get_random_catchphrase(): Get random Rick catchphrase

3. Include these formatting utilities:
   - add_color(text, color): Add ANSI color to text
   - escape_special_chars(text): Escape ZSH special characters
   - get_terminal_width(): Get current terminal width
   - adapt_to_width(content, width): Adjust content to fit terminal

4. Create these Powerlevel10k integration functions:
   - prompt_rick_assistant(): P10k segment function
   - register_with_powerlevel10k(): Register segment with P10k
   - format_p10k_segment(status): Format content for P10k segment

Follow this prompt structure:
```
🧪 Rick> _
📁 <path> | 🧪 <catchphrase>
👹 Username> _
```

Include at least 10 different Rick catchphrases like "Wubba lubba dub dub!" and "That's the way the news goes!"
Make all functions safe with error handling.
```

**✅ Success Indicators**:
- Contains prompt generator functions
- Includes component functions for username, directory, etc.
- Implements formatting utilities with ANSI color support
- Contains Powerlevel10k integration functions

### 2.3: Command Processor (DONE 09/03@04:20)

**📄 File**: src/core/commands.py

**🔤 Cursor Prompt**:
```
Create a command processor module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these command processing functions:
   - process_command(cmd): Main entry point for command processing
   - is_dangerous_command(cmd): Check if command is potentially risky
   - suggest_correction(cmd): Offer corrections for command typos
   - execute_assistant_cmd(cmd): Handle assistant-specific commands
   - format_command_output(result): Format command output with Rick's style

2. Add these command processing utilities:
   - parse_command(cmd): Parse command into components
   - get_command_type(cmd): Determine if shell or assistant command
   - get_command_context(path, history): Get context for the command
   - log_command_execution(cmd): Log command for history
   - should_intercept_command(cmd): Determine if command needs special handling

3. Create these basic command safety features:
   - check_rm_rf_command(cmd): Check for dangerous deletion commands
   - check_destructive_redirect(cmd): Check for dangerous redirections
   - confirm_dangerous_command(cmd): Show confirmation for risky commands
   - create_warning_message(cmd, reason): Create Rick-styled warning

4. Add these suggestion capabilities:
   - detect_common_typos(cmd): Detect common command typos
   - suggest_command_improvement(cmd): Suggest better command options
   - format_suggestion(original, suggestion): Format with Rick's sarcasm
   - remember_user_preference(cmd, accept_suggestion): Track user preferences

Make all functions handle edge cases gracefully.
Include Rick's personality with sarcastic comments.
Assistant-specific commands should start with '!'.

Examples of assistant commands:
- !help: Show assistant help
- !rick: Show Rick quote
- !config: Open configuration
```

**✅ Success Indicators**:
- Contains command processing functions
- Includes safety features for dangerous commands
- Implements suggestion capabilities for typos
- Contains Rick-styled formatting for outputs

### 2.4: Message Storage System (DONE 09/03@04:20)

**📄 File**: src/core/messages.py

**🔤 Cursor Prompt**:
```
Create a message storage module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these message management functions:
   - load_messages(): Load messages from ~/.rick_assistant/messages.json
   - get_message(category, context): Get appropriate message for context
   - format_message(template, **kwargs): Substitute variables in template
   - add_burp(message, frequency=0.3): Add random burps to messages
   - save_custom_message(category, message): Add user-defined message

2. Include these message categories as constants:
   - GREETING_MESSAGES: Welcome and startup messages
   - RESPONSE_MESSAGES: Replies to user actions
   - ERROR_MESSAGES: Error messages with Rick's sarcasm
   - SUGGESTION_MESSAGES: Command suggestions and tips
   - CATCHPHRASE_MESSAGES: Random Rick sayings for status bar

3. Add these helper functions:
   - get_random_message(category): Get random message from category
   - track_used_messages(category, message): Track to avoid repetition
   - create_default_messages(): Generate default message set
   - ensure_message_file(): Create message file if it doesn't exist

4. Implement these message formatting features:
   - add_science_references(message): Add scientific terminology
   - adjust_sass_level(message, level): Adjust sarcasm intensity
   - add_variable_substitution(message, variables): Replace placeholders
   - escape_special_chars(message): Escape special characters

Create a rich set of Rick-styled messages with variable placeholders like {username}, {command}, etc.
Include at least 5 messages per category with Rick's characteristic phrases.
Make all functions safe with error handling to prevent crashes.
```

**✅ Success Indicators**:
- Contains message management functions
- Includes different message categories
- Implements helper functions for message handling
- Contains Rick-styled messages with variable substitution

### 2.5: "Fake Rick" Response System (DONE 09/03@04:36)

**📄 File**: src/core/rick.py

**🔤 Cursor Prompt**:
```
Create a "Fake Rick" response module for a Rick Sanchez-themed ZSH assistant that provides Rick-style responses without requiring AI:

1. Implement these core response functions:
   - get_response(context, **params): Get contextual Rick response
   - add_burp(text, frequency=0.3): Add random burps to text
   - set_sass_level(level): Adjust personality intensity (1-10)
   - get_catchphrase(): Get random catchphrase for status bar
   - customize_response(template, **kwargs): Create personalized response

2. Add these response categories as dictionaries:
   - GREETINGS: "What up *burp* {username}!", "Oh great, you're back..."
   - COMMAND_FEEDBACK: "Executing that garbage? Whatever...", "Fine, I'll run your {command}..."
   - ERRORS: "You really screwed that up, didn't you?", "That's about as functional as Jerry's *burp* career"
   - WARNINGS: "This command looks dangerous, even for me", "Whoa, you're about to wreck your system, genius"
   - CATCHPHRASES: "Wubba lubba dub dub!", "And that's the waaaay the news goes!"

3. Create response selection logic:
   - select_response(category, context): Pick appropriate response
   - track_recent_responses(category, response): Avoid repetition
   - adjust_tone(success): Adjust tone based on command success
   - insert_context_details(template, context): Add command details
   - apply_personality_parameters(response, params): Apply sass level

4. Add these utility functions:
   - initialize_response_system(): Set up the response system
   - save_custom_responses(category, responses): Add user responses
   - get_response_categories(): List available categories
   - suggest_response_for_command(command): Suggest relevant response

Include at least 10 responses per category with Rick's characteristic sarcasm and scientific references.
Make responses feel random and varied to avoid repetition.
Add occasional burps with "*burp*" in the text.
```

**✅ Success Indicators**:
- Contains response generation functions
- Includes different response categories
- Implements response selection logic
- Contains Rick-styled responses with burps and scientific references

### 2.6: Setup Wizard (DONE 09/03@12:12)

**📄 File**: src/core/setup.py

**🔤 Cursor Prompt**:
```
Create a first-time setup wizard module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these setup functions:
   - is_first_run(): Check if this is the first plugin run
   - run_setup_wizard(): Main entry point for the setup wizard
   - create_directory_structure(): Create required directories
   - initialize_config(): Create default configuration
   - get_user_info(): Collect basic user information

2. Add these interactive components:
   - show_welcome_screen(): Display ASCII art welcome with Rick portal
   - get_user_preferences(): Ask for preferred prompt style
   - select_personality_level(): Choose sass level (1-10)
   - confirm_setup_choices(): Show summary and confirm
   - show_completion_message(): Show setup complete message

3. Create these helper functions:
   - print_portal_animation(): Show animated portal ASCII art
   - print_rick_dialog(text): Show text as Rick dialog
   - get_validated_input(prompt, validator): Get and validate user input
   - show_progress(step, total): Show setup progress
   - save_user_preferences(preferences): Save user choices

4. Include these filesystem operations:
   - create_config_directory(): Create ~/.rick_assistant/
   - create_logs_directory(): Create logs folder
   - create_messages_file(): Create default messages file
   - set_directory_permissions(): Ensure correct permissions
   - create_backup_directory(): Create backups folder

Make the wizard entertaining with Rick's personality throughout.
Include ASCII art portal animation for the welcome screen.
Add Rick-style commentary on user choices like "Only a {sass_level}? What are you, Jerry?"
Ensure the wizard completes successfully even if some steps fail.
```

**✅ Success Indicators**:
- Contains setup wizard functions
- Includes interactive components with ASCII art
- Implements helper functions for user input
- Contains filesystem operations for directory creation

---

## 🎨 Phase 3: Enhanced User Interface & Experience

### 3.1: System Information Monitor DONE (09/03@12:39)

**📄 File**: src/utils/system.py

**🔤 Cursor Prompt**:
```
Create a system information module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these system monitoring functions:
   - get_cpu_usage(): Get CPU usage percentage
   - get_ram_info(): Get memory usage statistics
   - get_cpu_temperature(): Get CPU temperature when available
   - get_disk_usage(path): Get disk usage for current path
   - get_system_uptime(): Get system uptime information

2. Add these monitoring utilities:
   - format_metric(value, unit, warning_threshold): Format with color based on value
   - cache_metric(name, value, ttl=60): Cache metrics to reduce checks
   - refresh_background_metrics(): Update metrics asynchronously
   - get_cached_metric(name): Get cached metric value
   - format_all_metrics(): Get all metrics formatted for display

3. Create these platform-specific implementations:
   - _get_linux_cpu_usage(): Linux-specific CPU monitoring
   - _get_macos_cpu_usage(): macOS-specific CPU monitoring
   - _get_linux_temperature(): Linux-specific temperature monitoring
   - _get_macos_temperature(): macOS-specific temperature monitoring
   - _detect_platform(): Determine current platform

4. Implement these caching features:
   - initialize_cache(): Set up metrics cache
   - set_update_interval(seconds): Configure update frequency
   - start_background_updater(): Start async updates
   - stop_background_updater(): Stop background updates
   - is_cache_stale(metric_name): Check if cache needs refresh

Make all functions cross-platform with appropriate fallbacks.
Handle missing or unavailable metrics gracefully.
Use color coding for critical values (green/yellow/red).
Implement efficient caching to avoid excessive system calls.
```

**✅ Success Indicators**:
- Contains system monitoring functions for CPU, RAM, etc.
- Includes platform-specific implementations
- Implements caching system for metrics
- Contains formatted output with color coding

### 3.2: Enhanced Prompt Formatter DONE (09/03@12:49)

**📄 File**: src/core/prompt.py (update)

**🔤 Cursor Prompt**:
```
Enhance the prompt formatter module for a Rick Sanchez-themed ZSH assistant with these new features:

1. Update the prompt structure to include system metrics:
```
🧪 Rick> _
📁 <path> | 🖥️ CPU:<cpu>% | 🔧 RAM: <ram>% | 🌡️ TEMP: <temp> | 🧪 <catchphrase>
👹 Username> _
```

2. Add these new prompt components:
   - add_system_metrics(status_bar): Add CPU, RAM, and temperature metrics
   - add_ai_model_info(status_bar): Add AI model placeholder information
   - truncate_status_bar(status_bar, width): Smart truncation for small terminals
   - colorize_metrics(metric, value): Color-code metrics based on value

3. Improve existing components:
   - cache_expensive_metrics(): Cache system metrics to improve performance
   - optimize_prompt_rendering(): Reduce prompt generation time
   - add_custom_prompt_elements(elements): Support user-defined elements
   - prioritize_elements(width): Show important elements on small terminals

4. Enhance Powerlevel10k integration:
   - extend_p10k_segment(segment): Add detailed system information
   - add_p10k_styling_options(segment): Add custom styling options
   - create_conditional_segment(condition): Show/hide based on condition
   - enhance_segment_icons(): Add more detailed icons for segments

Maintain performance while adding these new features.
Include intelligent truncation for different terminal widths.
Add configuration options to enable/disable different prompt elements.
Ensure compatibility with different terminal types.
```

**✅ Success Indicators**:
- Contains updated prompt structure with system metrics
- Includes new component functions for metrics display
- Implements caching and optimization for performance
- Contains enhanced Powerlevel10k integration

### 3.3: Text Formatting Utilities DONE (09/03@13:02)

**📄 File**: src/ui/text.py

**🔤 Cursor Prompt**:
```
Create a text formatting module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core formatting functions:
   - format_text(text, width): Format and wrap text to width
   - format_code(code, language): Format code with syntax highlighting
   - format_list(items): Create formatted bullet lists
   - format_table(data): Generate aligned table output
   - color_text(text, color): Apply ANSI color codes to text

2. Create a streaming text system:
   - stream_text(text, speed=0.03): Output text character-by-character
   - add_rick_speech_patterns(text): Add Rick's speech patterns and pauses
   - add_random_burps(text, frequency=0.3): Add burps at random intervals
   - vary_typing_speed(text, mood): Vary speed based on content
   - handle_streaming_interruption(): Allow interrupting output

3. Add these specialized formatters:
   - format_error(message): Format error messages with Rick style
   - format_warning(message): Create warning messages
   - format_success(message): Display success messages
   - format_info(message): Show informational content
   - format_catchphrase(phrase): Format Rick's catchphrases

4. Include these utility functions:
   - get_terminal_width(): Detect terminal width
   - get_terminal_height(): Detect terminal height
   - supports_ansi_color(): Check if terminal supports color
   - supports_unicode(): Check if terminal supports Unicode
   - clear_screen(): Clear terminal screen

Support different terminal widths and adjust formatting accordingly.
Handle ANSI color codes properly for different terminal types.
Make the streaming text system look natural with appropriate timing.
Add configuration options for text styling and speed preferences.
```

**✅ Success Indicators**:
- Contains core formatting functions for text, code, lists, etc.
- Includes streaming text system with character-by-character output
- Implements specialized formatters for different message types
- Contains utility functions for terminal detection

### 3.4: Input Handling System (done 10/03@11:40)

**📄 File**: src/ui/input.py

**🔤 Cursor Prompt**:
```
Create an input handling module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these input handler functions:
   - get_input(prompt): Get user input with formatted prompt
   - get_single_key(): Get a single keypress without Enter
   - get_selection(options): Get selection from a list of options
   - get_confirmation(prompt): Get yes/no response (y/n)
   - get_password(prompt): Get masked password input

2. Add these input utilities:
   - handle_ctrl_c(): Handle interrupt signals gracefully
   - save_term_state(): Save terminal state before changes
   - restore_term_state(): Restore terminal state after input
   - enable_raw_mode(): Set terminal to raw input mode
   - disable_raw_mode(): Restore normal terminal mode

3. Create these completion functions:
   - complete_command(partial): Complete partial shell commands
   - complete_path(partial): Complete file paths with tab
   - complete_option(partial, options): Complete from option list
   - format_completions(options): Format completion display
   - handle_tab_key(): Process tab key for completion

4. Implement these safety features:
   - handle_terminal_resize(): Adapt to terminal size changes
   - recover_from_input_errors(): Handle input exceptions
   - validate_input(input_value, validator): Validate user input
   - set_input_timeout(seconds): Add timeout for input
   - provide_input_help(context): Show context-sensitive help

Make the input system work consistently across different terminal types.
Implement proper terminal state management to avoid broken states.
Handle special characters and key combinations appropriately.
Support command history navigation with up/down arrows.
```

**✅ Success Indicators**:
- Contains input handler functions for different input types
- Includes terminal state management functions
- Implements completion functions for tab completion
- Contains safety features for error recovery

### 3.5: Menu System

**📄 File**: src/ui/menu.py

**🔤 Cursor Prompt**:
```
Create a menu system module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core menu components:
   - Menu: Base class for all menus
   - MenuItem: Individual selectable menu items
   - MenuCategory: Grouping of related items
   - MenuAction: Item that triggers a function
   - MenuToggle: On/off toggle menu item

2. Add these animation effects:
   - animate_portal_open(): Show portal opening animation
   - animate_item_selection(item): Highlight selected item
   - animate_transition(from_menu, to_menu): Transition between menus
   - animate_typing(text): Show typing animation for text
   - create_spinner(message): Show loading spinner animation

3. Create these menu utility functions:
   - display_menu(title, items): Show a menu with items
   - get_selection(menu): Get user selection from menu
   - show_message(text): Display message with animation
   - confirm_action(prompt): Get yes/no confirmation
   - show_progress(operation, steps): Show progress indicator

4. Implement these visual elements:
   - create_menu_border(width, height): Create Rick-themed border
   - create_portal_background(): Create portal background effect
   - create_menu_header(title): Create styled menu header
   - create_menu_footer(controls): Create footer with key controls
   - highlight_selection(item, selected=True): Highlight current item

Style all menus with Rick & Morty portal theme (green/blue colors).
Adapt menu display to different terminal sizes.
Add Rick-style comments in menus like "What are you looking at? Just pick something!"

5. Allow for ZSH native implementation:
   - Design functions to have ZSH equivalents in the functions/ directory
   - Include compatibility layer for seamless switching between implementations
   - Support automatic fallback to ZSH native when Python is unavailable
   - Preserve state when switching between implementations
```

**✅ Success Indicators**:
- Contains menu components for different item types
- Includes animation functions for visual effects
- Implements utility functions for menu display
- Contains Rick-themed visual elements and styling
- Supports dual implementation with Python and ZSH native versions
- Includes mechanism for switching between implementations

**📄 Additional File**: functions/_rick_menu_main

**🔤 Cursor Prompt**:
```
Create a ZSH native implementation of the main menu function for Rick Assistant with these features:

1. Implement a pure ZSH menu system that replicates the Python version's core functionality:
   - Display menu items with selection highlighting
   - Handle keyboard navigation (up/down/enter/escape)
   - Process user selections and execute appropriate actions
   - Support submenus and back navigation

2. Include these essential menu elements:
   - Menu header with Rick-themed styling
   - Selectable menu items with highlighting
   - Footer with navigation instructions
   - Basic animations using ZSH capabilities
   - Support for toggle items and actions

3. Add support for:
   - Terminal size detection and adaptation
   - Color support detection with fallbacks
   - Unicode support detection with ASCII fallbacks
   - Error handling for all user inputs
   - Configuration options matching Python version

Style all elements with Rick & Morty theme using ZSH-compatible approaches.
Ensure the implementation works in environments without Python.
Make the interface consistent with the Python implementation.
Add appropriate error handling to prevent terminal crashes.

This function will be used as a fallback when Python is unavailable or when the user prefers the ZSH native implementation.
```

**✅ Success Indicators**:
- Implements a ZSH native menu system with core functionality
- Handles terminal capabilities detection and adapts accordingly
- Provides consistent experience with the Python implementation
- Includes proper error handling to prevent terminal crashes

### 3.6: Status Bar Manager VERY IMPORTANT: ASK ME FOR DETAILED QUESTIONS WHILE PROPOSING THIS IMPLEMENTATION!!!

**📄 File**: src/ui/status.py

**🔤 Cursor Prompt**:
```
Create a status bar manager module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core status bar functions:
   - create_status_bar(components): Create full status bar from components
   - register_component(component): Add component to status bar
   - update_component(name, value): Update component value
   - format_status_bar(): Format complete status bar
   - get_available_width(): Get terminal width for status bar

2. Create these status components:
   - PathComponent: Show current directory
   - SystemComponent: Show system metrics (CPU, RAM, temp)
   - AIComponent: Show AI model information
   - CatchphraseComponent: Show Rick catchphrases
   - UniverseComponent: Show portal universe indicator - ASK ME ABOUT THIS!

3. Add these layout options:
   - create_full_layout(): Complete status bar with all components
   - create_compact_layout(): Condensed version for narrow terminals
   - create_minimal_layout(): Essential info only for tiny terminals
   - prioritize_components(width): Show important components first
   - auto_select_layout(width): Choose layout based on terminal width

4. Implement these update mechanisms:
   - update_async(component): Update component asynchronously
   - schedule_update(component, interval): Schedule periodic updates
   - update_on_event(component, event): Update on specific events
   - refresh_all_components(): Force refresh of all components
   - stop_all_updates(): Stop all background updates

Support different status bar formats:
- Default: `📁 <path> | 🔬 LM:<model> | 🖥️ CPU:<cpu>% | 🔧 RAM:<ram>% | 🌡️ <temp> | 🧪 <catchphrase> | 🌀 C-137`
- Compact: `📁 <dir>|🖥️<cpu>%|🔧<ram>%|🧪<catchphrase>|🌀C-137`

Update components asynchronously to avoid blocking the shell.
Implement intelligent truncation for limited terminal widths.
Include configuration options to enable/disable components.
```

**✅ Success Indicators**:
- Contains core status bar creation and formatting functions
- Includes different component implementations
- Implements layout options for different terminal widths
- Contains update mechanisms for component values

### 3.7: Portal Universe Indicator VERY IMPORTANT: ASK ME FOR DETAILED QUESTIONS WHILE PROPOSING THIS IMPLEMENTATION!!!

**📄 File**: src/ui/universe.py

**🔤 Cursor Prompt**:
```
Create a Portal Universe indicator module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these universe functions:
   - get_current_universe(): Get current universe designation (e.g., C-137)
   - switch_universe(): Change to a new random universe
   - format_universe(designation): Format universe for display
   - is_canonical_universe(designation): Check if from the show
   - get_universe_description(designation): Get universe info

2. Create a universe database with:
   - CANONICAL_UNIVERSES: Universes from the show (C-137, etc.)
   - RANDOM_UNIVERSE_PATTERNS: Patterns for generating universes
   - UNIVERSE_DESCRIPTIONS: Flavor text for different universes
   - SPECIAL_UNIVERSES: Universes with unique properties
   - UNIVERSE_CATEGORIES: Types (safe, dangerous, etc.)

3. Add these status bar integration functions:
   - format_universe_indicator(): Format "🌀 C-137" for status bar
   - update_universe_on_event(event): Change universe on event
   - colorize_universe(designation): Color-code by universe type
   - get_universe_tooltip(designation): Get info for tooltip
   - set_fixed_universe(designation): Set fixed universe

4. Implement these utility functions:
   - generate_random_universe(): Create new universe designation
   - parse_universe_designation(designation): Parse universe components
   - is_universe_dangerous(designation): Check if dangerous universe
   - get_universe_characteristics(designation): Get universe traits
   - save_visited_universes(): Track visited universes

Follow the show's universe naming conventions (C-xxx, etc.).
Include Easter eggs from the show for special universes.
Add configuration option to fix a universe or enable random switching.
Change universes on certain events (directory change, time interval, etc.).
```

**✅ Success Indicators**:
- Contains universe generation and management functions
- Includes database of canonical and random universes
- Implements status bar integration with formatting
- Contains utility functions for universe characteristics

---

## 🔒 Phase 4: Command Processing & Safety Features (make sure preious implementations and fixes!!)

### 4.1: Dangerous Command Detection

**📄 File**: src/core/safety.py

**🔤 Cursor Prompt**:
```
Create a command safety module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these risk detection functions:
   - is_dangerous(command): Check if command is risky
   - get_risk_level(command): Get risk assessment (Low/Medium/High)
   - need_confirmation(command): Determine if confirmation needed
   - get_confirmation_prompt(command): Create Rick-style warning
   - add_whitelist_entry(pattern): Whitelist safe command pattern

2. Add these pattern matchers for high-risk operations:
   - check_file_deletion(cmd): Check rm/rmdir commands
   - check_disk_operations(cmd): Check dd, mkfs, fdisk, etc.
   - check_system_modifications(cmd): Check chmod, chown, etc.
   - check_network_exposure(cmd): Check binding to 0.0.0.0
   - check_suspicious_pipes(cmd): Check potentially dangerous pipes

3. Create a user confirmation system:
   - request_confirmation(cmd, risk): Show confirmation prompt
   - format_confirmation_options(): Format [Y]es/[N]o/[E]dit options
   - process_confirmation_response(response): Handle user response
   - remember_confirmation(cmd): Remember for this session
   - log_confirmation_request(cmd, response): Log for security

4. Add these utility functions:
   - load_dangerous_patterns(): Load pattern database
   - add_custom_pattern(pattern, risk_level): Add user-defined pattern
   - is_whitelisted(command): Check if command is whitelisted
   - sanitize_command_display(cmd): Clean command for display
   - explain_risk(command): Explain why command is risky

Make the detection thorough but not annoying.
Use Rick's personality in warnings with humor like:
"Whoa there, *burp* genius! This command will nuke your system. You sure about this?"
Create a whitelist system for trusted commands.
Log all dangerous command attempts for security auditing.
```

**✅ Success Indicators**:
- Contains risk detection functions with different levels
- Includes pattern matchers for various risky operations
- Implements user confirmation system with options
- Contains whitelist functionality and custom patterns

### 4.2: Enhanced Command Processing

**📄 File**: src/core/commands.py (update)

**🔤 Cursor Prompt**:
```
Enhance the command processor module for a Rick Sanchez-themed ZSH assistant with these improvements:

1. Update these command processing functions:
   - parse_command(input): Parse and categorize command by type
   - execute_command(cmd): Safely execute with timeout
   - get_command_history(): Retrieve and analyze recent commands
   - analyze_command(cmd): Provide detailed command insights
   - format_results(output): Format command output with Rick's style

2. Add these command categories:
   - ShellCommand: Normal terminal commands
   - AssistantCommand: Commands for assistant (starting with !)
   - RickCommand: Special Rick-themed commands
   - ConfigCommand: Settings and configuration management
   - HelpCommand: Documentation and assistance

3. Enhance the suggestion system:
   - improve_suggestion_accuracy(cmd): Better typo correction
   - add_context_awareness(cmd, path): Suggestions based on context
   - suggest_performance_improvements(cmd): Efficiency suggestions
   - format_suggestion_with_personality(suggestion): Rick-style tips
   - learn_from_user_patterns(cmd): Remember command patterns

4. Add these utility functions:
   - create_command_context(cmd, history): Create context object
   - track_command_metrics(cmd, runtime): Track command performance
   - detect_command_pattern(history): Identify user patterns
   - suggest_command_sequence(pattern): Suggest command chains
   - format_complex_output(result): Handle multi-line output

Maintain performance while adding more sophisticated processing.
Implement improved pattern matching for better command analysis.
Add intelligent suggestions based on command context and history.
Keep Rick's personality in all interactions with sarcastic comments.
```

**✅ Success Indicators**:
- Contains updated command processing functions
- Includes different command category implementations
- Implements enhanced suggestion system with context awareness
- Contains utility functions for command analysis

### 4.3: Command Execution with Confirmation

**📄 File**: src/core/executor.py

**🔤 Cursor Prompt**:
```
Create a command execution module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these execution functions:
   - execute_with_confirmation(cmd): Execute with user confirmation
   - execute_with_timeout(cmd, timeout): Add execution timeout
   - capture_output(cmd): Capture STDOUT and STDERR
   - format_output(result): Format results for display
   - handle_execution_error(error): Manage execution failures

2. Create a confirmation workflow:
   - show_command_with_risk(cmd, risk_level): Display command and risk
   - present_options(): Show [Y]es/[E]dit/[N]o options
   - handle_edit_option(cmd): Allow command editing before execution
   - process_user_choice(choice, cmd): Process user selection
   - handle_confirmation_timeout(cmd): Handle timeout with default

3. Add sudo handling capabilities:
   - detect_sudo_command(cmd): Identify commands needing privileges
   - verify_sudo_access(): Check if user has sudo access
   - warn_about_sudo(cmd): Show clear warnings for sudo
   - handle_sudo_password(cmd): Manage password prompts
   - secure_sudo_execution(cmd): Follow security best practices

4. Implement these safety features:
   - sanitize_command(cmd): Remove potentially dangerous elements
   - validate_command_syntax(cmd): Check command for validity
   - set_execution_limits(limits): Set resource limits for execution
   - monitor_execution(cmd, pid): Monitor running command
   - terminate_hung_process(pid): Kill processes that hang

Use Rick's voice for all confirmations and messages.
Add timeout handling to prevent hanging the terminal.
Provide detailed feedback on execution results.
Log all command executions for reference.
```

**✅ Success Indicators**:
- Contains execution functions with confirmation
- Includes confirmation workflow with Y/E/N options
- Implements sudo handling with security checks
- Contains safety features for command execution

---

## 🤖 Phase 5: Expanded Fake Rick & Content Features VERY IMPORTANT: ASK ME FOR DETAILED QUESTIONS WHILE PROPOSING THIS IMPLEMENTATION!!!

### 5.1: Expanded Personalities

**📄 File**: src/core/personalities.py

**🔤 Cursor Prompt**:
```
Create a personalities module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these personality management functions:
   - get_active_personality(): Get current active personality
   - switch_personality(name): Change to different personality
   - get_response(context): Get personality-specific response
   - format_prompt(personality): Style prompt for personality
   - get_catchphrase(personality): Get character catchphrase

2. Create these Rick & Morty character personalities:
   - RickSanchez: Sarcastic, impatient genius scientist (default)
   - MrMeeseeks: Eager helper who gets distressed with complex tasks
   - Morty: Nervous, uncertain but well-meaning
   - Jerry: Clueless optimist who misunderstands commands
   - Summer: Sarcastic teenager with attitude
   - Beth: Intelligent and practical professional
   - MrPoopybutthole: Polite and cheerful character

3. Add these personality-specific elements:
   - catchphrases: Dictionary of character-specific expressions
   - speech_patterns: Unique speaking styles for each
   - response_templates: Character-appropriate replies
   - error_messages: Personalized error handling
   - prompt_styles: Character-themed prompts

4. Implement these personality traits:
   - sassiness: Controls sarcasm level (1-10)
   - helpfulness: Willingness to assist (1-10)
   - scientific: Use of technical terminology (1-10)
   - burp_frequency: Frequency of *burps* (0.0-1.0)
   - catchphrase_frequency: Use of catchphrases (0.0-1.0)

Make each personality feel authentic to the show.
Include at least 10 catchphrases and responses per character.
Add smooth transitions when switching personalities.
Allow configuration of personality characteristics.
```

**✅ Success Indicators**:
- Contains personality management functions
- Includes multiple character implementations
- Implements personality-specific elements
- Contains configurable personality traits

### 5.2: Backup & Restore System

**📄 File**: src/utils/backup.py

**🔤 Cursor Prompt**:
```
Create a backup and restore module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these backup functions:
   - create_backup(comment=None): Create new backup with comment
   - list_backups(): List available backup files with details
   - restore_backup(backup_id): Restore from specific backup
   - verify_backup(backup_id): Check backup integrity
   - delete_backup(backup_id): Remove specific backup

2. Add these backup management features:
   - schedule_automatic_backup(interval): Set automatic backups
   - set_max_backups(count): Limit maximum backup count
   - compress_backup(backup_id): Compress to save space
   - validate_backup_file(path): Check file validity
   - repair_corrupted_backup(backup_id): Attempt to fix backup

3. Create a restore system:
   - preview_backup_contents(backup_id): Show before restoration
   - create_safety_backup(): Create backup before restoration
   - restore_specific_settings(backup_id, settings): Selective restore
   - validate_compatibility(backup_id): Check version compatibility
   - handle_restore_errors(error): Manage restoration failures

4. Add these utility functions:
   - get_backup_directory(): Get/create backup directory
   - format_backup_name(comment): Create timestamped name
   - get_backup_metadata(backup_id): Get backup information
   - compare_backups(backup1, backup2): Show differences
   - export_backup(backup_id, path): Export to external location

Store backups in ~/.rick_assistant/backups/ with timestamps.
Use JSON format for backup files with metadata.
Implement rotation to remove old backups when limit reached.
Add compression to save space for large configurations.
Include Rick-style messages during backup/restore operations.
```

**✅ Success Indicators**:
- Contains backup creation and management functions
- Includes rotation and compression features
- Implements restore system with previews
- Contains utility functions for backup handling

### 5.3: Enhanced Menu System with Popups

**📄 File**: src/ui/menu.py (update)

**🔤 Cursor Prompt**:
```
Enhance the menu system module for a Rick Sanchez-themed ZSH assistant with popup functionality:

1. Add these popup components:
   - CheckboxPopup: Multiple selection with toggles
   - RadioPopup: Single selection from options
   - FormPopup: Text and value input collection
   - ConfirmPopup: Enhanced confirmation dialog
   - InfoPopup: Information display with formatting

2. Create these portal-themed visual effects:
   - create_floating_window(title, content): Create overlay window
   - animate_portal_entrance(window): Animate popup appearance
   - create_dimensional_swirl(): Transition animation between popups
   - add_glowing_selection(item): Add glow effect to selection
   - create_rick_styled_border(width, height): Theme popup borders

3. Implement these popup utility functions:
   - show_checkbox_popup(title, options): Show multi-select popup
   - show_radio_popup(title, options): Show single-select popup
   - show_form_popup(title, fields): Show input form popup
   - show_confirm_popup(title, message): Show confirmation dialog
   - show_info_popup(title, content): Show information popup

4. Add these interaction features:
   - handle_checkbox_toggle(item): Toggle checkbox selection
   - validate_form_input(field, value): Validate form fields
   - navigate_popup_items(direction): Move between popup items
   - close_popup_on_action(action): Close popup after action
   - handle_popup_resize(): Adjust popup on terminal resize

Make all popups have Rick-styled commentary and visuals.
Add smooth animations that don't disrupt usability.
Ensure popups handle terminal resizing properly.
Support keyboard navigation for all popup types.
Add Rick quotes when selecting options like "Oh, you're picking THAT option? Real genius move."
```

**✅ Success Indicators**:
- Contains popup component implementations
- Includes portal-themed visual effects
- Implements popup utility functions
- Contains interaction features for popups

### 5.4: Media Analysis Module

**📄 File**: src/utils/media.py

**🔤 Cursor Prompt**:
```
Create a media analysis module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core analysis functions:
   - analyze_file(path): Main entry point for file analysis
   - get_media_type(path): Determine file media type
   - format_video_info(data): Format video details
   - format_audio_info(data): Format audio details
   - format_image_info(data): Format image details

2. Add mediainfo integration:
   - check_mediainfo_installed(): Verify mediainfo availability
   - execute_mediainfo(path, format): Run mediainfo command
   - parse_mediainfo_output(output): Parse command output
   - extract_stream_info(data): Get stream details
   - get_installation_instructions(): Help install dependencies

3. Create these specialized formatters:
   - format_video_metadata(metadata): Format video info
   - format_audio_metadata(metadata): Format audio info
   - format_image_metadata(metadata): Format image info
   - format_container_info(container): Format container details
   - format_stream_info(stream): Format stream information

4. Add these helper utilities:
   - format_duration(seconds): Format time nicely
   - format_bitrate(bits): Format bitrate with units
   - format_size(bytes): Format file size with units
   - detect_file_corruption(data): Check for file issues
   - suggest_media_optimizations(data): Suggest improvements

Present information in Rick's sarcastic style with comments like:
"This video is encoded with *burp* H.264. Not the worst choice you've made today."
"44.1kHz audio? What is this, a podcast for ants?"

Handle missing mediainfo gracefully with installation instructions.
Support various media formats (video, audio, images).
Format output in an easy-to-read style with colors.
```

**✅ Success Indicators**:
- Contains core analysis functions for different media types
- Includes mediainfo integration with parsing
- Implements specialized formatters for metadata
- Contains helper utilities for formatting

---

## 🧠 Phase 6: AI Integration & Advanced Features VERY IMPORTANT: ASK ME FOR DETAILED QUESTIONS WHILE PROPOSING THIS IMPLEMENTATION!!!

### 6.1: AI Model Framework

**📄 File**: src/ai/models.py

**🔤 Cursor Prompt**:
```
Create an AI model framework for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core AI model classes:
   - AIModel: Abstract base class for all AI models
   - OpenAIModel: Implementation for OpenAI API
   - FakeRickModel: Local fallback model
   - ModelManager: Handles model selection and fallback

2. Add these common model methods:
   - generate_response(prompt): Get AI model response
   - count_tokens(text): Count tokens in text
   - get_model_info(): Get model information
   - is_available(): Check if model is available
   - get_fallback(): Get fallback mechanism

3. Create OpenAI API integration:
   - handle_api_key(key): Process and secure API key
   - select_model(model_name): Choose GPT model
   - format_request(prompt, params): Format API request
   - handle_api_errors(error): Process API errors
   - implement_retry_logic(request): Retry on failure

4. Add these utility functions:
   - initialize_ai_models(): Set up available models
   - select_best_model(config): Choose appropriate model
   - format_model_status(): Get model status for display
   - estimate_request_tokens(prompt): Estimate request size
   - log_model_usage(model, tokens): Track usage statistics

Make AI integration robust with proper error handling.
Store API key securely with appropriate permissions.
Include timeout handling to prevent blocking the terminal.
Implement seamless fallback to "Fake Rick" if AI fails.
Add comprehensive logging for troubleshooting API issues.
```

**✅ Success Indicators**:
- Contains AI model abstract base class
- Includes OpenAI API integration
- Implements fallback mechanisms
- Contains utility functions for model management

### 6.2: AI-Driven Rick Personality

**📄 File**: src/ai/personality.py

**🔤 Cursor Prompt**:
```
Create an AI-driven personality module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these prompt engineering functions:
   - create_rick_prompt(context, query): Create Rick-styled prompt
   - add_personality_markers(prompt): Add character traits
   - format_ai_response(response): Enhance AI output with Rick style
   - maintain_context(history, query): Manage conversation state
   - adjust_personality_strength(response, level): Control intensity

2. Add these personality elements:
   - CHARACTER_TRAITS: Dictionary of personality characteristics
   - SPEECH_PATTERNS: Rick's speech pattern definitions
   - CONTEXT_TEMPLATES: Templates for different scenarios
   - SCIENTIFIC_TERMS: Science terminology to insert
   - RESPONSE_GUIDELINES: Rules for response formatting

3. Create these utility functions:
   - filter_response(text): Ensure appropriate content
   - add_burps(text): Insert characteristic burps
   - enhance_scientific_content(text): Add scientific terminology
   - check_personality_consistency(text): Verify Rick's voice
   - get_context_prompt(history): Generate context for AI

4. Implement these multi-character support functions:
   - switch_prompt_personality(personality): Change prompt style
   - get_personality_traits(name): Get character traits
   - format_response_as_character(text, character): Apply character style
   - blend_personalities(main, secondary, ratio): Mix two personalities
   - detect_personality_in_response(text): Identify character voice

Maintain Rick's sarcastic, impatient, scientifically-minded personality.
Include proper context management for conversation flow.
Add configuration options to adjust personality strength (1-10).
Enhance AI responses with Rick's speech patterns without compromising content.
```

**✅ Success Indicators**:
- Contains prompt engineering functions
- Includes personality elements and traits
- Implements utility functions for response formatting
- Contains multi-character support

### 6.3: Configuration Menu System

**📄 File**: src/ui/settings.py

**🔤 Cursor Prompt**:
```
Create a settings menu module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these core menu functions:
   - render_settings_menu(): Display the main settings menu
   - process_setting_change(setting, value): Update setting
   - validate_setting(setting, value): Check value validity
   - save_settings(): Write changes to config file
   - reset_to_defaults(): Restore default settings

2. Create these menu categories:
   - BRAIN_SETTINGS: AI model and personality options
   - INTERFACE_SETTINGS: Status bar and display preferences
   - SYSTEM_SETTINGS: Security and operational settings
   - BACKUP_SETTINGS: Configuration management
   - PLUGIN_SETTINGS: General plugin configuration

3. Add these submenu options:
   - AI_SETTINGS: Model selection, API key, response style, timeout
   - PERSONALITY_SETTINGS: Character, sass level, burp frequency
   - DISPLAY_SETTINGS: Colors, animations, prompt style
   - SAFETY_SETTINGS: Warning levels, confirmations, whitelist
   - SYSTEM_METRICS: Refresh rate, displayed metrics

4. Implement these menu utilities:
   - format_setting_option(name, value): Format setting display
   - highlight_current_value(value): Highlight selected value
   - validate_input_for_setting(setting, input): Validate changes
   - show_setting_help(setting): Display setting description
   - apply_setting_immediately(setting, value): Apply without save

Design menu with Rick & Morty portal theme styling.
Implement smooth navigation between menu categories.
Add proper validation for all input with helpful error messages.
Provide visual feedback when settings are changed.
Include Rick-style commentary on settings like "Only a 5 for sass level? You're such a Jerry."
```

**✅ Success Indicators**:
- Contains settings menu functions
- Includes different menu categories
- Implements submenu options for settings
- Contains menu utilities for display and navigation

### 6.4: Token Management System

**📄 File**: src/ai/tokens.py

**🔤 Cursor Prompt**:
```
Create a token management module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these token counting functions:
   - count_tokens(text): Estimate token count for text
   - estimate_cost(model, tokens): Calculate request cost
   - track_request(model, prompt, response): Record usage
   - get_session_usage(): Get current session stats
   - get_historical_usage(): Get usage over time

2. Add these status bar integration functions:
   - format_token_count(count): Format for status display
   - format_cost(amount): Format cost with currency
   - update_status_bar(usage): Update status bar with usage
   - get_usage_indicator(usage, limit): Get visual indicator
   - show_usage_warning(usage, limit): Show warning when near limit

3. Create these tracking functions:
   - initialize_token_tracker(): Set up token tracking
   - save_usage_history(): Save usage to history file
   - load_usage_history(): Load historical usage data
   - reset_session_counter(): Clear session statistics
   - generate_usage_report(): Create detailed usage report

4. Implement these utility functions:
   - set_token_budget(limit): Set maximum token budget
   - check_budget_warning(usage): Warn on approaching limit
   - optimize_prompt(prompt): Reduce token count
   - calculate_average_usage(): Get average daily usage
   - predict_monthly_cost(): Estimate monthly cost

Make the token management system lightweight and efficient.
Implement proper cost estimation using current API pricing.
Include configuration options for token display and warnings.
Track usage across different AI models with appropriate adjustments.
Store historical data in a compact, JSON format.
```

**✅ Success Indicators**:
- Contains token counting and cost estimation functions
- Includes status bar integration for usage display
- Implements usage tracking and history management
- Contains utility functions for budget management

### 6.5: Advanced Settings Module

**📄 File**: src/utils/advanced_settings.py

**🔤 Cursor Prompt**:
```
Create an advanced settings module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these implementation-selection functions:
   - get_preferred_implementation(): Get user's implementation preference
   - set_preferred_implementation(choice): Set implementation preference
   - detect_available_implementations(): Check which implementations are available
   - toggle_implementation(): Switch between Python and ZSH implementations
   - describe_implementation_differences(): Show differences between implementations

2. Create these implementation-specific settings:
   - get_python_settings(): Get Python-specific configuration options
   - get_zsh_settings(): Get ZSH-specific configuration options
   - sync_settings_between_implementations(): Synchronize shared settings
   - migrate_settings(from_impl, to_impl): Migrate settings between implementations
   - validate_implementation_compatibility(): Check if settings are compatible

3. Add these UI elements for implementation management:
   - show_implementation_selection_ui(): Display implementation selection interface
   - format_implementation_status(): Format current implementation status
   - show_implementation_capabilities(): Show features available in each implementation
   - compare_implementations(): Show side-by-side comparison
   - recommend_implementation(): Suggest best implementation based on environment

4. Implement these system information functions:
   - check_python_version(): Get installed Python version
   - check_zsh_version(): Get installed ZSH version
   - check_terminal_capabilities(): Analyze terminal capabilities
   - benchmark_implementations(): Compare performance of implementations
   - generate_environment_report(): Create detailed environment report

Make the module support seamless switching between implementations.
Ensure settings are properly synchronized when switching.
Provide clear information about the capabilities of each implementation.
Include benchmarking to help users decide which implementation to use.
Store implementation preference in configuration file.
```

**✅ Success Indicators**:
- Contains implementation selection and management functions
- Includes settings synchronization between implementations
- Implements UI elements for displaying implementation information
- Contains system information and benchmarking functions

---

## 🔧 Phase 7: Advanced Features & Polish

### 7.1: Performance Optimization

**📄 File**: src/utils/performance.py

**🔤 Cursor Prompt**:
```
Create a performance optimization module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these monitoring functions:
   - time_execution(func): Decorator for timing functions
   - profile_function(func): Detailed performance profiling
   - monitor_memory_usage(): Track memory consumption
   - log_performance_metrics(metrics): Record performance data
   - identify_bottlenecks(log): Find slow operations

2. Add these optimization strategies:
   - run_async(func): Run function asynchronously
   - cache_result(key, ttl): Cache function results
   - lazy_load_module(module_name): Load modules on demand
   - pool_expensive_resources(resource_type): Manage resources
   - reduce_startup_overhead(): Optimize plugin initialization

3. Create a caching system:
   - initialize_cache(): Set up centralized cache
   - cache_system_metrics(ttl=60): Cache system metrics
   - cache_expensive_calculation(key, value, ttl): Cache values
   - get_cached_value(key, default=None): Get with fallback
   - invalidate_cache(pattern): Clear cached values

4. Add these performance utilities:
   - optimize_imports(): Reduce import overhead
   - set_background_priority(task, priority): Set task priority
   - rate_limit_operation(func, limit): Prevent excessive calls
   - batch_operations(operations): Group operations together
   - stagger_updates(components): Distribute update load

Focus optimization on the most critical parts:
- Prompt rendering
- Command processing
- System metrics collection
- AI request handling

Use proper profiling to identify actual bottlenecks.
Include configuration options to enable/disable optimizations.
Implement measurable improvements with before/after metrics.
```

**✅ Success Indicators**:
- Contains performance monitoring functions
- Includes optimization strategies for different scenarios
- Implements caching system with TTL support
- Contains performance utilities for common operations

### 7.2: Advanced Input Handling

**📄 File**: src/ui/input.py (update)

**🔤 Cursor Prompt**:
```
Enhance the input handling module for a Rick Sanchez-themed ZSH assistant with these features:

1. Add these advanced input features:
   - buffer_input(): Store input during ongoing operations
   - handle_key_combination(keys): Process complex key combos
   - add_custom_keybinding(keys, action): Define custom keys
   - set_input_context(context): Context-sensitive handling
   - suggest_input_completion(partial): Show completion suggestions

2. Improve keybinding support:
   - detect_multi_key_sequence(keys): Detect key sequences
   - register_keybinding_profile(profile): Group key bindings
   - handle_modifier_keys(event): Process Ctrl, Alt, etc.
   - map_terminal_specific_keys(): Handle terminal differences
   - create_keybinding_help(): Generate key binding help

3. Enhance the completion system:
   - improve_context_awareness(context): Context-based completions
   - handle_special_chars_in_completion(): Handle special chars
   - show_rich_completion_options(options): Better completion display
   - add_plugin_specific_completions(): Custom completions
   - learn_from_completion_usage(): Track frequent completions

4. Add these advanced features:
   - implement_history_search(query): Search command history
   - add_syntax_highlighting(command): Highlight during typing
   - validate_input_inline(input): Show validation while typing
   - display_typing_suggestions(): Show suggestions during typing
   - add_clipboard_integration(): Support copy/paste operations

Maintain compatibility with different terminal types.
Implement proper terminal state management for all operations.
Add configuration options for all input features.
Ensure seamless integration with ZSH's existing completion.
Maintain performance and responsiveness throughout.
```

**✅ Success Indicators**:
- Contains advanced input buffering and handling
- Includes improved keybinding with multi-key support
- Implements enhanced completion with context awareness
- Contains history search and syntax highlighting

### 7.3: Enhanced Command Suggestions

**📄 File**: src/core/suggestions.py

**🔤 Cursor Prompt**:
```
Create an enhanced command suggestion module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these suggestion functions:
   - suggest_command_correction(cmd): Fix command typos
   - suggest_efficient_alternative(cmd): Suggest better commands
   - suggest_based_on_directory(cmd, path): Context-aware suggestions
   - suggest_from_history(cmd): Suggest from past commands
   - suggest_command_completion(partial): Complete partial commands

2. Add these suggestion strategies:
   - analyze_user_patterns(history): Learn from command history
   - detect_project_type(path): Project-specific suggestions
   - identify_command_intention(cmd): Determine command purpose
   - detect_common_mistakes(cmd): Find mistakes and pitfalls
   - suggest_command_flags(cmd): Suggest helpful command flags

3. Enhance suggestion presentation:
   - highlight_command_difference(old, new): Show what changed
   - add_suggestion_explanation(suggestion): Explain benefits
   - show_inline_suggestion(suggestion): Display during typing
   - create_keyboard_shortcut(suggestion): Add key to accept
   - format_with_rick_personality(suggestion): Add Rick's style

4. Create learning capabilities:
   - track_suggestion_acceptance(suggestion): Track accepted suggestions
   - learn_user_preferences(cmd, actions): Learn preferences
   - adapt_to_suggestion_rejections(suggestion): Reduce unwanted tips
   - build_user_profile(history, preferences): Create user profile
   - export_learned_preferences(): Export learning data

Format suggestions in Rick's style:
"Wow, you really typed that wrong. Did you mean 'cd ~/projects'?"
"There's a *burp* way more efficient command for that, genius: 'git log --oneline'"

Implement learning mechanisms that aren't intrusive.
Add configuration options for suggestion frequency.
Make suggestions genuinely helpful while maintaining Rick's personality.
```

**✅ Success Indicators**:
- Contains enhanced suggestion functions
- Includes different suggestion strategies
- Implements improved suggestion presentation
- Contains learning capabilities for personalization

### 7.4: AI-Powered Error Analysis

**📄 File**: src/ai/errors.py

**🔤 Cursor Prompt**:
```
Create an AI-powered error analysis module for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these error analysis functions:
   - analyze_error(error): Main entry point for error analysis
   - generate_error_prompt(error): Create AI prompt for error
   - format_explanation(analysis): Format explanation for display
   - suggest_solution(error, analysis): Offer potential fixes
   - explain_last_error(): Command to explain recent error

2. Create an error processing pipeline:
   - capture_command_error(cmd, error): Capture error output
   - categorize_error(error): Classify error by type
   - extract_key_information(error): Get important error details
   - prepare_for_ai_analysis(error): Format error for AI
   - fallback_to_static_explanation(error): Use static database if AI unavailable

3. Add these user experience features:
   - add_command_explain(cmd): Add !explain command
   - set_explanation_verbosity(level): Configure detail level
   - enable_teach_mode(): More detailed explanations
   - show_error_history(): Browse past errors
   - offer_solution_execution(solution): Run suggested fix

4. Implement these utility functions:
   - load_common_errors_database(): Load known error patterns
   - match_error_pattern(error, patterns): Match error to known pattern
   - format_error_card(error, explanation): Format visual error card
   - generate_fix_command(error, solution): Create command to fix issue
   - log_error_explanation(error, explanation): Track explanations

Use Rick's sarcastic personality for explanations:
"You're getting this error because, *burp*, you forgot to close that parenthesis, genius."
"Even Jerry could see that you're trying to access a directory that doesn't exist."

Include a database of common errors and solutions for quick responses.
Implement proper AI integration with fallbacks for offline use.
Make error messages more understandable while keeping Rick's character.
```

**✅ Success Indicators**:
- Contains error analysis and explanation functions
- Includes processing pipeline for different error types
- Implements user experience features like !explain
- Contains utility functions for error handling

### 7.5: Documentation & Deployment

**📄 File**: docs/README.md`

**🔤 Cursor Prompt**:
```
Create a comprehensive README for a Rick Sanchez-themed ZSH assistant with these sections:

1. Project Overview:
   - Brief description of Rick Assistant
   - Key features and capabilities
   - Screenshots of the assistant in action
   - Installation requirements

2. Installation Instructions:
   - Step-by-step installation process
   - Oh My Zsh integration
   - Dependencies and prerequisites
   - Configuration options

3. Usage Guide:
   - Basic commands and syntax
   - Available features
   - Customization options
   - Troubleshooting common issues

4. Configuration:
   - Available settings
   - Personality customization
   - UI preferences
   - Security options

5. Advanced Features:
   - AI integration
   - Custom commands
   - Plugin extensions
   - Scripting capabilities

Include Rick-themed humor throughout the documentation.
Add clear installation instructions for different platforms.
Include troubleshooting section for common issues.
Add ASCII art header for the README.
Format with proper Markdown including code blocks and screenshots.
```

**📄 File**: setup.py

**🔤 Cursor Prompt**:
```
Create an installation script for a Rick Sanchez-themed ZSH assistant with these features:

1. Implement these installation functions:
   - check_requirements(): Verify prerequisites
   - install_dependencies(): Install required packages
   - create_directory_structure(): Set up plugin directories
   - configure_zshrc(): Update .zshrc configuration
   - initialize_plugin(): Run first-time setup

2. Add these helper utilities:
   - detect_platform(): Identify OS for platform-specific steps
   - check_python_version(): Verify Python version
   - check_zsh_installation(): Confirm ZSH is installed
   - backup_existing_files(): Backup existing configuration
   - verify_installation(): Check installation was successful

3. Create these update features:
   - check_for_updates(): Check for new versions
   - update_plugin_files(): Update plugin safely
   - preserve_user_config(): Keep custom configurations
   - backup_before_update(): Backup before updating
   - rollback_on_failure(): Revert to previous version

4. Implement these utility scripts:
   - rick_assistant_check.sh: Validate environment
   - rick_assistant_doctor.sh: Diagnose problems
   - rick_assistant_uninstall.sh: Clean removal

Make the installation process simple and user-friendly.
Include detailed output explaining each step.
Add error handling for common installation issues.
Include Rick-themed messages during installation.
Create rollback mechanisms for failed installations or updates.
```

**✅ Success Indicators**:
- Contains comprehensive documentation with installation guide
- Includes setup and installation scripts
- Implements update and verification functions
- Contains utility scripts for maintenance

## 🚀 Final Implementation Steps

Once you've implemented all phases, perform these final actions:

1. Ensure all files have proper permissions:
```
chmod +x ~/.oh-my-zsh/custom/plugins/rick_assistant/rick_assistant.plugin.zsh
chmod +x ~/.oh-my-zsh/custom/plugins/rick_assistant/setup.py
```

2. Add the plugin to your `.zshrc`:
```
# Add this to ~/.zshrc
plugins=(... rick_assistant)
```

3. Reload your ZSH configuration:
```
source ~/.zshrc
```

4. Run the setup wizard to complete installation:
```
rick_assistant_setup
```

5. Enjoy your Rick Sanchez-themed ZSH assistant!

---

## 📋 Implementation Checklist

- [x] Phase 1: Core Foundation
  - [x] 1.1: Main Plugin Entry Point
  - [x] 1.2: Logging System
  - [x] 1.3: Error Handling System
  - [x] 1.4: Configuration Management
  - [x] 1.5: Path/File Validation 
  - [x] 1.6: Package Initialization

- [x] Phase 2: ZSH Integration & Basic Functionality
  - [x] 2.1: ZSH Hook Manager
  - [x] 2.2: Prompt Formatter
  - [x] 2.3: Command Processor
  - [x] 2.4: Message Storage System
  - [x] 2.5: "Fake Rick" Response System
  - [x] 2.6: Setup Wizard

- [ ] Phase 3: Enhanced User Interface & Experience
  - [x] 3.1: System Information Monitor
  - [x] 3.2: Enhanced Prompt Formatter
  - [x] 3.3: Text Formatting Utilities
  - [x] 3.4: Input Handling System
  - [ ] 3.5: Menu System with Animations
  - [ ] 3.6: Status Bar Manager
  - [ ] 3.7: Portal Universe Indicator

- [ ] Phase 4: Command Processing & Safety Features
  - [ ] 4.1: Dangerous Command Detection
  - [ ] 4.2: Enhanced Command Processing
  - [ ] 4.3: Command Execution with Confirmation

- [ ] Phase 5: Expanded Fake Rick & Content Features
  - [ ] 5.1: Expanded Personalities
  - [ ] 5.2: Backup & Restore System
  - [ ] 5.3: Enhanced Menu System with Popups
  - [ ] 5.4: Media Analysis Module

- [ ] Phase 6: AI Integration & Advanced Features
  - [ ] 6.1: AI Model Framework
  - [ ] 6.2: AI-Driven Rick Personality
  - [ ] 6.3: Configuration Menu System
  - [ ] 6.4: Token Management System

- [ ] Phase 7: Advanced Features & Polish
  - [ ] 7.1: Performance Optimization
  - [ ] 7.2: Advanced Input Handling
  - [ ] 7.3: Enhanced Command Suggestions
  - [ ] 7.4: AI-Powered Error Analysis
  - [ ] 7.5: Documentation & Deployment
