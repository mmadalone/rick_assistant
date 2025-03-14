# Rick Assistant Powerlevel10k Integration

This document provides information about the Powerlevel10k integration for Rick Assistant and how to troubleshoot common issues.

## Overview

The Powerlevel10k integration adds a Rick-themed segment to your Powerlevel10k prompt, showing:

- Rick-themed icon and phrase
- System metrics (CPU and memory usage with color indicators)

## Configuration Options

You can customize the behavior of the Rick Assistant Powerlevel10k integration using these environment variables:

```bash
# Disable color formatting (helps with compatibility issues)
export RICK_P10K_PLAIN_MODE=true

# Enable debug output
export RICK_P10K_DEBUG=true
```

## Common Issues and Solutions

### "Error: name 'cyan' is not defined"

If you see this error in your prompt, it means there's an issue with color handling in the P10k integration.

**Solution:**
1. Enable plain text mode:
   ```bash
   export RICK_P10K_PLAIN_MODE=true
   ```
2. Reload your shell:
   ```bash
   exec zsh
   ```

### Missing or incorrect metrics

If you're not seeing system metrics or they appear incorrect:

**Solution:**
1. Make sure psutil is installed:
   ```bash
   pip3 install psutil
   ```
2. Enable debug mode to see more information:
   ```bash
   export RICK_P10K_DEBUG=true
   ```
3. Reload your shell:
   ```bash
   exec zsh
   ```

### Segment not showing in prompt

If the Rick Assistant segment isn't visible in your prompt:

**Solution:**
1. Make sure Powerlevel10k is properly installed
2. Run the integration script again:
   ```bash
   source /path/to/rick_assistant/src/core/integrations/p10k_direct.zsh
   ```
3. Reload Powerlevel10k configuration:
   ```bash
   p10k reload
   ```

### WSL-specific issues

Windows Subsystem for Linux can have specific issues with Powerlevel10k integration:

**Solution:**
1. Enable plain text mode (especially important for WSL):
   ```bash
   export RICK_P10K_PLAIN_MODE=true
   ```
2. If using WSL1, consider upgrading to WSL2 for better compatibility
3. Ensure your terminal supports the emojis and formatting used

## Manual Edit

If you need to manually edit the integration:

1. The Rick Assistant segment function is defined in:
   ```
   ~/.p10k.rick.zsh
   ```

2. You can modify this file directly to customize the segment behavior

## Restoring Backup

If you need to revert to your original Powerlevel10k configuration:
```bash
cp ~/.p10k.zsh.rickbackup ~/.p10k.zsh
p10k reload
``` 