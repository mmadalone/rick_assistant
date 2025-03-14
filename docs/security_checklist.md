# Security Checklist for Rick Assistant Development

This checklist provides a quick reference for verifying security compliance when developing or modifying code in the Rick Assistant project.

## File Operations

### Before opening or accessing a file:

- [ ] Path has been normalized using `normalize_path()`
- [ ] Path has been validated using `is_path_within_safe_directories()`
- [ ] Path existence is checked with proper error handling
- [ ] Parent directory is created safely if needed using `ensure_safe_directory()`

### When writing to a file:

- [ ] `safe_atomic_write()` is used instead of direct `open()` calls
- [ ] Content is properly validated before writing
- [ ] Return value is checked to verify successful write
- [ ] Error cases are handled gracefully with appropriate logging

### When handling user-provided paths:

- [ ] All user input is sanitized using `sanitize_path()`
- [ ] Path traversal attempts (containing `..`) are detected and rejected
- [ ] Symlinks are properly resolved before validation
- [ ] File extensions and types are validated if relevant

## Error Handling

- [ ] Specific exceptions are caught rather than general `Exception`
- [ ] Security-related errors are logged with appropriate severity
- [ ] Proper fallback values are returned for error cases
- [ ] User-facing error messages don't expose sensitive information
- [ ] Critical errors trigger security alerts

## Permission Management

- [ ] File permissions are validated using `validate_path_permissions()`
- [ ] Minimal necessary permissions are used when creating files
- [ ] Write operations only occur in appropriate directories
- [ ] Permissions are set explicitly with appropriate values
- [ ] Directory access boundaries are enforced

## Configuration

- [ ] Config values are validated before use
- [ ] Sensitive data is not stored in plaintext
- [ ] Default configuration is secure
- [ ] Configuration paths are restricted to safe directories
- [ ] Configuration file access uses safe operations

## Testing

- [ ] Path safety tests verify security boundaries
- [ ] Tests include path traversal attempt scenarios
- [ ] Negative test cases validate proper failure handling
- [ ] Mock fixtures are used for filesystem operations in tests
- [ ] Edge cases (empty paths, symlinks, etc.) are tested

## Logging

- [ ] Security events are properly logged
- [ ] Log files are stored in safe locations
- [ ] Log messages don't contain sensitive information
- [ ] Log file operations use safe atomic writes
- [ ] Log levels are appropriate for the information

## Development Process

- [ ] Security risks are identified in code reviews
- [ ] Changes are tested with the path safety test suite
- [ ] Security documentation is updated for relevant changes
- [ ] Backward compatibility is maintained when possible
- [ ] Circular dependencies are avoided or properly managed

## Final Review

- [ ] All direct `open()` calls are replaced with `safe_atomic_write()`
- [ ] All `os.path` functions are replaced with `pathlib.Path` operations
- [ ] All `os.makedirs()` calls are replaced with `ensure_safe_directory()`
- [ ] All path operations handle edge cases (None, empty strings)
- [ ] Return values from security functions are explicitly checked
- [ ] Tests verify the security of the changes made 