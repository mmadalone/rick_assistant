# Security Troubleshooting Guide

This guide provides solutions for common security-related issues that you might encounter when working with Rick Assistant.

## Common Issues and Solutions

### 1. Path Validation Failures

#### Symptoms
- Functions return `None` or `False` unexpectedly
- Log messages about "Path is outside safe directories"
- `PathError` exceptions with "Invalid path format" messages

#### Possible Causes and Solutions

1. **Path contains traversal attempts (`..`)**
   ```
   # Problematic path
   "../config/settings.json"
   ```
   **Solution**: Use absolute paths or paths relative to a validated base directory.
   ```python
   base_dir = ensure_safe_directory(Path.home() / ".rick_assistant")
   if base_dir:
       path = base_dir / "config" / "settings.json"
   ```

2. **Path is outside allowed directories**
   ```
   # Problematic path
   "/etc/passwd"
   ```
   **Solution**: Ensure paths are within allowed directories (home, temporary directory, app directory).
   ```python
   path_obj = normalize_path(path)
   if path_obj and is_path_within_safe_directories(path_obj):
       # Use the path
   ```

3. **Path is not properly normalized**
   ```
   # Problematic usage
   path = user_input  # Could contain relative paths, symlinks, etc.
   ```
   **Solution**: Always normalize paths before use.
   ```python
   path_obj = normalize_path(user_input)
   if path_obj:
       # Use the normalized path
   ```

### 2. Permission Issues

#### Symptoms
- "Permission denied" errors
- Log messages about "No write permission"
- Operations fail silently

#### Possible Causes and Solutions

1. **Directory not writable**
   **Solution**: Check permissions before operations and create directories with appropriate permissions.
   ```python
   dir_path = ensure_safe_directory(path, create=True, mode=0o755)
   if dir_path and validate_path_permissions(dir_path, os.W_OK):
       # Directory exists and is writable
   ```

2. **File not readable/writable**
   **Solution**: Verify permissions explicitly before operations.
   ```python
   if validate_path_permissions(file_path, os.R_OK | os.W_OK):
       # File has read/write permissions
   ```

3. **Running with insufficient privileges**
   **Solution**: Handle permission errors gracefully and provide clear user feedback.
   ```python
   try:
       result = operation_that_needs_permissions()
   except PermissionError:
       logger.error("Insufficient permissions to perform operation")
       return {"success": False, "error": "Permission denied"}
   ```

### 3. Circular Import Issues

#### Symptoms
- ImportError with "cannot import name X from partially initialized module Y"
- Modules fail to load properly
- Unexpected `AttributeError` exceptions

#### Possible Causes and Solutions

1. **Direct circular dependency**
   ```python
   # module_a.py imports from module_b.py
   # module_b.py imports from module_a.py
   ```
   
   **Solution**: Implement basic functionality without cross-imports and use late imports.
   ```python
   # In module_a.py
   def _basic_implementation():
       # Implementation without importing module_b
       pass
   
   # Try to import the full implementation at module end
   try:
       from module_b import better_implementation
       implementation_to_use = better_implementation
   except ImportError:
       implementation_to_use = _basic_implementation
   ```

2. **Indirect circular dependency**
   
   **Solution**: Restructure modules to break dependency cycles or use dependency injection.
   ```python
   # Instead of importing a function, accept it as a parameter
   def process_file(path, validator=None):
       if validator is None:
           # Use a simple default validator
           validator = lambda p: True
       
       if validator(path):
           # Process the file
   ```

### 4. File Write Failures

#### Symptoms
- Files not being created or updated
- Log messages about "Failed to write to file"
- `safe_atomic_write` returning `False`

#### Possible Causes and Solutions

1. **Parent directory doesn't exist**
   
   **Solution**: Explicitly create parent directories before writing.
   ```python
   parent_dir = ensure_safe_directory(file_path.parent, create=True)
   if parent_dir:
       success = safe_atomic_write(file_path, content)
   ```

2. **Insufficient disk space**
   
   **Solution**: Handle disk space errors explicitly.
   ```python
   try:
       success = safe_atomic_write(file_path, content)
   except OSError as e:
       if "No space left on device" in str(e):
           logger.error("Disk space is full, cannot write file")
       else:
           logger.error(f"File write error: {e}")
   ```

3. **Temporary directory issues**
   
   **Solution**: Ensure the temporary directory is accessible and writable.
   ```python
   temp_dir = ensure_safe_directory(Path(tempfile.gettempdir()))
   if not temp_dir:
       logger.error("Cannot access temporary directory")
       # Use alternative approach
   ```

### 5. Permission Boundary Issues

#### Symptoms
- Operations fail with "Path is outside safe directories"
- Security exceptions during normal operations
- Functions unexpectedly returning `None` or `False`

#### Possible Causes and Solutions

1. **Working with files outside of home directory**
   
   **Solution**: Consider if the operation is truly necessary, and if so, explicitly whitelist the directory.
   ```python
   # Add to SAFE_DIRS in path_safety.py or extend at runtime
   additional_safe_dir = "/path/to/needed/directory"
   if os.path.exists(additional_safe_dir) and os.path.isdir(additional_safe_dir):
       SAFE_DIRS.append(additional_safe_dir)
   ```

2. **Temporary operations outside safe directories**
   
   **Solution**: Create a temporary directory within a safe location.
   ```python
   safe_temp_dir = ensure_safe_directory(
       Path.home() / ".rick_assistant" / "temp",
       create=True
   )
   if safe_temp_dir:
       # Use safe_temp_dir for temporary operations
   ```

## Debugging Security Issues

### Enabling Detailed Logging

For security investigations, enable DEBUG level logging:

```python
from src.utils.logger import set_log_level
import logging

# Enable debug logging for security-related modules
set_log_level(logging.DEBUG, "path_safety")
set_log_level(logging.DEBUG, "validation")
set_log_level(logging.DEBUG, "errors")
```

### Testing Path Safety

To verify if a path is considered safe:

```python
from src.utils.path_safety import normalize_path, is_path_within_safe_directories
from pathlib import Path

def debug_path_safety(path):
    print(f"Original path: {path}")
    
    # Normalize the path
    path_obj = normalize_path(path)
    print(f"Normalized path: {path_obj}")
    
    # Check if within safe directories
    is_safe = path_obj is not None and is_path_within_safe_directories(path_obj)
    print(f"Is within safe directories: {is_safe}")
    
    # If not safe, check why
    if not is_safe:
        if path_obj is None:
            print("Path could not be normalized")
        elif ".." in str(path):
            print("Path contains traversal attempts (..) which are blocked")
        else:
            print("Path is outside safe directories, which include:")
            from src.utils.path_safety import SAFE_DIRS
            for safe_dir in SAFE_DIRS:
                print(f"  - {safe_dir}")
                
    return is_safe
```

### Checking Permissions

To verify file and directory permissions:

```python
from src.utils.path_safety import validate_path_permissions
import os

def debug_permissions(path):
    print(f"Checking permissions for: {path}")
    
    # Check if path exists
    if not os.path.exists(path):
        print("Path does not exist")
        return
    
    # Get path type
    path_type = "Directory" if os.path.isdir(path) else "File"
    print(f"Path type: {path_type}")
    
    # Check permissions
    readable = validate_path_permissions(path, os.R_OK)
    writable = validate_path_permissions(path, os.W_OK)
    executable = validate_path_permissions(path, os.X_OK)
    
    print(f"Readable: {readable}")
    print(f"Writable: {writable}")
    print(f"Executable: {executable}")
    
    # Show actual permission bits
    try:
        mode = os.stat(path).st_mode
        print(f"Permission bits: {oct(mode & 0o777)}")
    except Exception as e:
        print(f"Error getting permission bits: {e}")
```

## Security Best Practices

1. **Always check return values**
   Security functions return `None`, `False`, or empty strings on failure rather than raising exceptions.
   
2. **Don't bypass security for convenience**
   Even for "quick fixes" or temporary code, always use the security functions.
   
3. **Use the checklist**
   Refer to the security checklist in `docs/security_checklist.md` before submitting changes.
   
4. **When in doubt, be restrictive**
   If you're unsure if an operation is safe, default to the more restrictive approach.
   
5. **Test with malicious inputs**
   Try path traversal attempts and other security edge cases to verify your code handles them correctly.

## Getting Help

If you encounter security issues that aren't covered in this guide, please:

1. Review the security improvements documentation in `docs/security_improvements.md`.
2. Check the test cases in `tests/utils/test_path_safety.py` for examples.
3. Consult with the security team before implementing workarounds.
4. Report potential security issues through the appropriate channels rather than in public discussions. 