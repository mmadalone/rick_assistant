# Rick Assistant Menu Troubleshooting Guide

This guide provides information about the Rick Assistant menu system architecture, common issues, and how to resolve them. The menu system includes both Python and ZSH implementations with enhanced fallback mechanisms.

## Menu Architecture Overview

The Rick Assistant menu system has two implementations:

1. **Python Implementation**
   - **Location**: `src/ui/menu.py`, `src/ui/input.py`
   - **Features**: More visually advanced, with colors and animations
   - **Entry Point**: Called via the `rick menu` command
   - **Fall Back**: If Python implementation fails, will fall back to ZSH implementation

2. **ZSH Implementation**
   - **Location**: `functions/_rick_menu_*`, `rick-menu.zsh`
   - **Features**: More reliable across different terminal types
   - **Entry Point**: Can be called directly via `zsh_menu.sh`
   - **Fall Back**: Used when Python is unavailable or when explicitly configured

## Latest Fixes (2025-03-17)

We've implemented additional fixes to address key input detection issues:

1. **Readchar Library Version Compatibility**:
   - Fixed compatibility issues with different versions of the readchar library
   - Added robust detection of the ESC key that works across all readchar versions
   - Improved handling of escape sequences in different terminal environments
   - Enhanced key testing tool with better display of key information

2. **Enhanced Menu Key Handling**:
   - Added support for more key shortcuts in the menu system
   - Improved handling of raw escape sequences for better arrow key detection
   - Added type checking to prevent errors with different key input types
   - Expanded the set of navigation keys for more intuitive menu control

3. **Diagnostic Tool Improvements**:
   - Completely rewrote the key testing tool for better diagnostics
   - Added ASCII/Unicode value display for better key identification
   - Improved categorization of different key types
   - Enhanced formatting for better readability

## Latest Fixes (2025-03-16)

We've implemented significant fixes to address terminal input problems:

1. **Arrow Key Detection Fix**: 
   - Fixed the escape sequence detection in `src/ui/input.py`
   - Added proper timeout-based detection for multi-byte sequences
   - Prevented single characters like 'A', 'B', 'C', 'D' from being misinterpreted as regular input when they are part of arrow key sequences
   - Added comprehensive debug logging for key detection issues

2. **Menu Launcher Improvements**:
   - Enhanced terminal setup in `rick_menu.py`
   - Improved error handling and diagnostics
   - Added automatic terminal capability detection

3. **Testing Tools**:
   - Added `test_keys.py` for testing terminal key input handling
   - Improved diagnostics logging throughout the menu system

## Common Issues

### 1. Menu Exits Immediately

**Symptom**: You run `rick menu` and it immediately exits or returns to the shell prompt.

**Possible Causes**:
- Terminal input handling errors with arrow keys being misinterpreted
- Python environment issues
- Configuration problems

**Solutions**:
- **Try the Updated Python Implementation**: We've fixed the key handling issues in the latest update
- **Try the ZSH Implementation**: Run `./zsh_menu.sh` to use the ZSH implementation directly
- **Run with Debug Mode**: `RICK_DEBUG=1 rick menu` to see detailed error information
- **Test Key Handling**: Run `./test_keys.py` to check if your terminal's arrow keys are properly detected

### 2. Navigation Issues

**Symptom**: Arrow keys don't work correctly or exit the menu unexpectedly.

**Possible Causes**:
- Terminal sending non-standard escape sequences
- Input handling not correctly parsing escape sequences
- Terminal capability detection issues

**Solutions**:
- Use our new key testing tool: `python test_keys.py` to see how your terminal sends arrow keys
- Use the ZSH implementation: `./zsh_menu.sh`
- Install and configure an appropriate terminal emulator
- Set the TERM environment variable appropriately

### 3. Display Issues

**Symptom**: Menu displays incorrectly, with misaligned text or missing characters.

**Possible Causes**:
- Terminal does not support required capabilities
- Encoding issues
- Terminal width detection problems

**Solutions**:
- Try setting a different TERM value: `export TERM=xterm-256color`
- Check your terminal's Unicode support
- Use the ZSH implementation which has simpler display requirements

## Menu Configuration

You can configure which menu implementation to use:

1. **Python First (Default)**: Tries Python implementation first, falls back to ZSH if needed
   ```zsh
   echo "RICK_MENU_IMPLEMENTATION=python" >> ~/.zshrc
   ```

2. **ZSH Only**: Always uses the ZSH implementation
   ```zsh
   echo "RICK_MENU_IMPLEMENTATION=zsh" >> ~/.zshrc
   ```

3. **Auto Detect (Recommended)**: Uses the most appropriate implementation based on your terminal
   ```zsh
   echo "RICK_MENU_IMPLEMENTATION=auto" >> ~/.zshrc
   ```

## Enhanced Fallback System

The menu system now includes an improved fallback handling system:

1. Automatic detection of terminal capabilities
2. Graceful error handling and recovery
3. Automatic switching between implementations when needed
4. Detailed logging to help diagnose issues

This ensures you always have a working menu interface, regardless of your terminal environment.

## Testing Both Implementations

### Python Implementation Test

```zsh
# Run with debugging info
RICK_DEBUG=1 rick menu

# Or run the enhanced menu launcher directly
python rick_menu.py
```

### ZSH Implementation Test

```zsh
# Direct access to ZSH implementation
./zsh_menu.sh
```

## Advanced Debugging

For detailed diagnostics, run:

```zsh
# Key testing tool - helps debug arrow key issues
python test_keys.py

# Full terminal diagnostics
python src/utils/terminal_diagnostics.py

# Menu with full debugging
RICK_DEBUG=1 rick menu
```

## Key Handling Test Tool

We've created a new key testing tool to help diagnose input issues:

1. Run the test tool:
   ```zsh
   chmod +x test_keys.py
   ./test_keys.py
   ```

2. Press various keys including arrows, enter, escape, etc.

3. The tool will show you exactly what sequences your terminal sends for each key press.

This is particularly useful for troubleshooting arrow key detection problems, which were the root cause of many menu issues.

## Reporting Issues

If you continue to experience issues, please report them with:

1. The output from the key testing tool
2. Your terminal type (`echo $TERM`)
3. The exact command you ran
4. The error messages received

## Key Input Detection Issues

### Problem: Readchar version compatibility issues

**Symptoms:**
- Error messages about `'ESCAPE'` attribute not found
- Key testing tool crashes when trying to detect the ESC key
- Arrow keys or ESC key not properly detected despite readchar being installed

**Solution:**
We've implemented a more robust approach to key detection that works across different readchar library versions:

1. **Version-agnostic key detection** - The key handling code now checks for multiple possible attribute names and uses direct character codes as a fallback.

2. **Improved detection logic** - Added support for both `readchar.key.ESCAPE` and `readchar.key.ESC` attributes, with a fallback to the raw `'\x1b'` character.

3. **Enhanced type safety** - Added stricter type checking to prevent errors when handling different key types.

4. **Better escape sequence handling** - Improved detection of raw escape sequences for terminals that send non-standard key codes.

### Problem: Arrow keys not working or showing as A, B, C, D

**Symptoms:**
- Arrow keys aren't recognized or show as raw characters like `^[[A` 
- Menu navigation doesn't respond to arrow keys
- Pressing arrow keys causes menu to exit

**Solution:**
We've completely overhauled our approach to key input detection using the **readchar** library:

1. **New Library Implementation** - The `getch()` function now uses the `readchar` library which properly handles all terminal escape sequences without manual parsing.

2. **Automatic Terminal Compatibility** - The readchar library automatically works with different terminal types and configurations.

3. **Robust Fallback System** - If readchar isn't available, we provide a simplified fallback system that still works better than our original implementation.

4. **Clear Error Messages** - Added better logging and error reporting to help troubleshoot any remaining issues.

### Problem: ESC key causes immediate exit

**Symptoms:**
- Pressing ESC immediately exits the menu
- ESC doesn't work as expected for backing out of submenus

**Solution:**
The readchar library properly distinguishes between the ESC key and other escape sequences, fixing issues with ESC key handling.

## Diagnostic Tools

### Key Testing Tool

We've enhanced our diagnostic tool to use the readchar library:

```bash
# Run the key testing tool
python3 test_keys.py
```

This tool now:
- Detects and uses readchar if available
- Shows clear information about the terminal environment
- Provides accurate key name interpretation
- Helps identify any remaining issues with key detection

## Logger Configuration Issues

### Problem: Logger setup error in rick_menu.py

**Symptoms:**
- Debug logging not working correctly
- Logger configuration errors in terminal

**Solution:**
Fixed parameter mismatch in the `setup_logger()` function call:
- Changed from `setup_logger(debug=debug_mode)` to `setup_logger(level=logging_level)` to match the function definition

## Installation Requirements

For optimal key detection, you need the readchar library:

```bash
# Install readchar
pip install readchar
```

The menu will use readchar when available and fall back to a simpler implementation if it's not installed.

## General Troubleshooting Steps

If you encounter menu issues:

1. **Install readchar** - This is the most important step:
   ```
   pip install readchar
   ```

2. **Run the Key Testing Tool** - Verify arrow keys are properly detected:
   ```
   python3 test_keys.py
   ```

3. **Check Terminal Compatibility** - Some very old or unusual terminals may still have issues

4. **Enable Debug Logging** - Run with debug mode to see detailed key input information:
   ```
   RICK_DEBUG=1 python3 rick_menu.py
   ```

5. **Try Alternative Key Mappings** - The menu also responds to vi-style keys:
   - Up: k
   - Down: j
   - Left: h
   - Right: l
   - Select: Enter
   - Exit: q or ESC

6. **Report Persistent Issues** - If problems persist, provide the output from:
   ```
   python3 test_keys.py > key_test_output.txt
   ```

## Rick Assistant Menu Troubleshooting

### Menu System Improvements

#### Expandable Categories Implementation

The Rick Assistant menu system has been refactored to properly support expandable categories. This resolves the error related to the `MenuCategory` class not accepting an `expanded` parameter.

**Problem:**
```
TypeError: __init__() got an unexpected keyword argument 'expanded'
```

This error occurred because the `create_ricktastic_menu()` function was trying to create `MenuCategory` instances with an `expanded` parameter, but the `MenuCategory` class did not support this parameter.

**Solution:**
We implemented a proper class hierarchy by:

1. Creating a new `ExpandableMenuCategory` class that extends `MenuCategory`
2. Adding proper support for the `expanded` parameter in this new class
3. Updating the menu navigation logic to handle expansion/collapse functionality
4. Adding key commands (Space key) for toggling category expansion

Now you can expand and collapse categories in the menu using the Space key when a category is selected.

#### Key Input Detection Improvements

The menu input handling has been enhanced to support the space key for toggling expandable categories:

- **UP/DOWN arrows**: Navigate between menu items
- **ENTER**: Select an item
- **SPACE**: Expand/collapse a category
- **ESC**: Exit the menu

The controls displayed at the bottom of the menu will dynamically show the appropriate options based on whether the current selection is an expandable category.

### Key Input Detection Issues

The key input detection system has been improved with the `readchar` library to provide more reliable handling of special keys and escape sequences.

**Problem:**
Arrow keys were not working in some terminal environments, or would show as raw escape sequences (like `^[[A` for UP arrow).

**Solution:**
- Implemented the `readchar` library for better key detection
- Added automatic terminal compatibility detection
- Created a robust fallback system for terminals that don't support all features
- Added clearer error messages and logging

The ESC key is now properly detected and distinguished from other escape sequences.

### Diagnostic Tools

The key testing tool (`test_keys.py`) has been enhanced to provide better key detection and interpretation:

- It now uses the `readchar` library for optimal key detection
- It shows detailed information about detected keys
- It provides terminal environment information for troubleshooting

Run the tool to diagnose key input issues:
```
python src/tools/test_keys.py
```

### Logger Configuration Issues

A fix was applied to the logger setup in `rick_menu.py`, changing the parameter from `setup_logger(debug=debug_mode)` to `setup_logger(level=logging_level)`.

### Installation Requirements

The menu system now has a dependency on the `readchar` library. Install it using:

```
pip install readchar
```

### General Troubleshooting Steps

If you encounter issues with the menu system:

1. Ensure `readchar` is installed
2. Run the key testing tool to verify key detection
3. Check if your terminal supports the required features
4. Enable debug logging for more detailed information
5. Try alternative key mappings if certain keys don't work
6. Report persistent issues with details about your terminal environment

## Conclusion

With the latest fixes, the menu system should now work correctly across most terminal environments. If you encounter any issues, use the testing tools to gather diagnostic information, then try the alternative implementation. 