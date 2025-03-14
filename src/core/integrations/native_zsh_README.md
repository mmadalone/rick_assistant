# Rick Assistant Native Zsh Components

This directory contains native Zsh implementations of key Rick Assistant components, designed to significantly improve performance by eliminating Python startup overhead.

## Overview

The native Zsh components provide faster alternatives to Python-based functionality, particularly for frequently used features. 
While Python offers excellent flexibility and maintainability, for some operations the overhead of starting the Python interpreter
outweighs the benefits, especially on slower systems or systems with limited resources.

These native implementations:
- Eliminate Python interpreter startup delay
- Reduce memory usage
- Provide faster response times
- Maintain feature compatibility with Python versions
- Automatically fall back to Python implementations when native versions aren't available

## Components

### Temperature Monitoring (`zsh_native_temp.zsh`)

A pure Zsh implementation of the temperature monitoring system that:

- Checks CPU temperature across Linux, macOS and Windows (WSL) platforms
- Provides threshold-based alerts (warning, critical, emergency)
- Stores temperature history
- Implements cooldown periods between repeated alerts
- Formats output with Rick-themed messages

#### Functions

- `rick_check_temperature` - Main function to check temperature and issue alerts if needed
- `rick_temperature_status` - Display current temperature status
- Platform-specific implementations: `_rick_get_linux_temperature`, `_rick_get_macos_temperature`, `_rick_get_windows_temperature`

#### Performance Improvement

The temperature monitoring system is called frequently during shell usage. By implementing this in native Zsh:

- Alert checks no longer require ~200-500ms Python startup time
- Temperature monitoring no longer breaks instant prompt
- Alerts appear instantly when thresholds are exceeded

### Menu System (`zsh_native_menu.zsh`)

A pure Zsh implementation of the menu system that:

- Provides an interactive menu with keyboard navigation
- Supports Unicode symbols with ASCII fallbacks
- Includes color support with graceful degradation for limited terminals
- Maintains key Rick-styled UI elements
- Includes a message box implementation for alerts and notifications

#### Functions

- `rick_menu` - Display an interactive menu with multiple options
- `rick_message_box` - Display a simple message box
- `_rick_impl_menu` - Implementation of the rick menu command

#### Performance Improvement

The menu system is less frequently used than temperature monitoring, but it benefits greatly from the native implementation:

- Menus appear instantly instead of after a ~500ms Python startup delay
- Terminal capability detection is more accurate
- The implementation uses less memory

## Usage

These components are automatically used by Rick Assistant when available. The plugin will:

1. Check for the presence of native Zsh implementations
2. Load them if available
3. Fall back to Python implementations if not available

This ensures backward compatibility while providing better performance when possible.

## Testing

Use the `test_zsh_native.sh` script in the root directory to test these components:

```bash
./test_zsh_native.sh
```

This script will run tests on each native component to verify functionality.

## Development

When modifying these native components, follow these guidelines:

1. Maintain feature parity with Python implementations
2. Preserve all user-facing text and behavior
3. Implement proper error handling with fallbacks
4. Test on multiple platforms when possible
5. Keep the code readable with comments explaining complex logic
6. Avoid external dependencies beyond standard Zsh and core Unix utilities

## Integration

The native components are integrated in the main `rick_assistant.plugin.zsh` file, which handles:

1. Detecting available native components
2. Loading them at the appropriate time
3. Setting up compatibility shims between native and Python code
4. Providing a consistent user experience regardless of which implementation is active 