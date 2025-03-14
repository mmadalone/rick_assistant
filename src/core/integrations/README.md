# Rick Assistant Powerlevel10k Integration

This directory contains scripts for integrating Rick Assistant with Powerlevel10k.

## New Integration v2

The new integration method follows Powerlevel10k's official guidelines for creating custom segments and properly registers with p10k's hook system.

### Quick Setup

Add this to your `.zshrc` after the line that sources `.p10k.zsh`:

```bash
[ -f "$ZSH_CUSTOM/plugins/rick_assistant/src/core/integrations/p10k_init.zsh" ] && \
  source "$ZSH_CUSTOM/plugins/rick_assistant/src/core/integrations/p10k_init.zsh"
```

### Configuration Options

You can customize the behavior with these environment variables:

```bash
# Choose integration method (hook, direct, none)
export RICK_P10K_METHOD=hook

# Disable color formatting (helps with compatibility issues)
export RICK_P10K_PLAIN_MODE=true

# Enable debug output
export RICK_P10K_DEBUG=true
```

### Integration Methods

1. **Hook-based Integration (recommended)**
   - Doesn't modify `.p10k.zsh`
   - Uses p10k's hook system
   - More compatible with p10k updates
   - Set `RICK_P10K_METHOD=hook`

2. **Direct Integration (legacy)**
   - Modifies `.p10k.zsh` directly
   - Less resilient to p10k updates
   - May cause conflicts
   - Set `RICK_P10K_METHOD=direct`

3. **Disable Integration**
   - Set `RICK_P10K_METHOD=none`

## Troubleshooting

### Common Issues

#### "p10k segment: can be called only during prompt rendering"

This error occurs when a p10k segment function is called outside of prompt rendering.

**Solution:**
1. Use the hook-based integration method: `export RICK_P10K_METHOD=hook`
2. Make sure you source the integration script *after* sourcing `.p10k.zsh`
3. Only have one `typeset -g POWERLEVEL9K_INSTANT_PROMPT=...` line in your `.zshrc`

#### "Error: name 'cyan' is not defined"

This error occurs when there's a problem with color formatting.

**Solution:**
1. Enable plain text mode: `export RICK_P10K_PLAIN_MODE=true`
2. Restart your shell or run `exec zsh`

#### Segment not appearing in prompt

**Solution:**
1. Make sure the integration script is sourced after `.p10k.zsh`
2. Reload p10k: `p10k reload`
3. Try the direct integration method: `export RICK_P10K_METHOD=direct`

## File Overview

- `p10k_init.zsh`: Master integration script (source this from `.zshrc`)
- `p10k_hook.zsh`: Hook-based integration (recommended)
- `p10k_direct.zsh`: Direct integration (legacy approach)
- `p10k_metrics.py`: Python script for system metrics
- `p10k_README.md`: Troubleshooting documentation 