# Rick Assistant - User Configurable Options

This document provides a comprehensive list of all user configurable options available in the Rick Assistant ZSH plugin. Options marked with 🚧 are planned but not yet fully implemented.

## 🧠 BRAIN MODULE

### 🧠 FAKE RICK
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `personality.character` | Character to simulate | rick | rick, morty, meeseeks, jerry, beth, summer |
| `personality.sass_level` | Level of sass in responses | 7 | 1-10 (integer) |
| `personality.burp_frequency` | Frequency of burps in responses | 0.3 | 0.0-1.0 (float) |
| `personality.catchphrase_frequency` | Frequency of catchphrases | 0.2 | 0.0-1.0 (float) |
| `personality.scientific_reference_level` | Frequency of scientific references | 5 | 0-10 (integer) |
| `personality.custom_catchphrases` | List of custom catchphrases | [] | Array of strings |

### 🤖 AI INTEGRATION 🚧
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `ai.enabled` 🚧 | Whether AI integration is enabled | false | true, false |
| `ai.model` 🚧 | AI model to use | local | local, openai |
| `ai.api_key` 🚧 | API key for AI service | "" | string |
| `ai.max_tokens` 🚧 | Maximum tokens for AI response | 150 | integer |
| `ai.temperature` 🚧 | Randomness in AI responses | 0.7 | 0.0-1.0 (float) |
| `ai.show_thinking` 🚧 | Show AI thinking process | false | true, false |

## 💻 RICK CMDS
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `commands.intercept_dangerous` | Intercept dangerous commands | true | true, false |
| `commands.intercept_typos` | Intercept and suggest corrections for typos | true | true, false |
| `commands.intercept_suggestions` | Show command suggestions | true | true, false |

## ⚙️ SETTINGS

### ⚙️ GENERAL OPTIONS
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `general.enabled` | Enable Rick Assistant globally | true | true, false |
| `general.log_level` | Logging level | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `general.show_welcome_message` | Show welcome message on startup | true | true, false |
| `general.show_exit_message` | Show exit message when exiting | true | true, false |
| `debug_mode` | Enable debug mode | false | true, false |
| `performance_mode` | Optimize for performance | true | true, false |

### 🌀 UNIVERSE SETTINGS 🚧
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `user.universe` | Current Rick universe | C-137 | string |
| `universe.switching.enabled` 🚧 | Enable automatic universe switching | true | true, false |
| `universe.switching.trigger` 🚧 | Event that triggers universe switching | chdir | chdir, interval, manual |
| `universe.switching.interval` 🚧 | Interval for automatic switching (seconds) | 0 | integer |
| `universe.display.format` 🚧 | Format for universe display | short | short, long, full |
| `universe.display.color` 🚧 | Use colors for universe display | true | true, false |
| `universe.universe_pool.canonical` 🚧 | Use canonical universes | true | true, false |
| `universe.universe_pool.custom` 🚧 | Custom universe names | [] | Array of strings |

## 🛡️ SAFETY

### 🛡️ SAFETY
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `safety.confirm_dangerous_commands` | Confirm potentially dangerous commands | true | true, false |
| `safety.warning_level` | Level of security warnings | medium | low, medium, high |
| `safety.command_whitelist` | Whitelisted commands patterns | [] | Array of strings |
| `safety.path_whitelist` | Whitelisted path patterns | [] | Array of strings |
| `safety.secure_mode` | Enable additional security features | true | true, false |

## 🎨 UI SETTINGS

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `ui.theme` / `ui___theme` | UI theme | portal | portal, science, classic, dark |
| `ui.animations` | Enable UI animations | true | true, false |
| `ui___menu___animations_enabled` | Enable menu animations | false | true, false |
| `ui.prompt_style` | Style of prompt | classic | classic, minimal, verbose |
| `ui___menu___use_static_portal` | Use static portal background | true | true, false |
| `ui___menu___terminal_compatibility_mode` | Enable terminal compatibility mode | false | true, false |
| `ui.show_metrics` | Show system metrics | true | true, false |
| `ui___menu___use_python_implementation` | Use Python menu implementation | false | true, false, auto |
| `ui___color_scheme` | UI color scheme | default | default, dark, light, custom |
| `ui.prompt_integration.mode` | Prompt integration mode | auto | auto, powerlevel10k, oh-my-zsh, standalone |
| `ui.prompt_integration.display_style` | How to display in prompt | command_output | segment, right_prompt, command_output, custom_position |
| `ui.prompt_integration.segment_position` | Segment position in P10k | right | left, right, prefix, suffix |
| `ui.prompt_integration.segment_priority` | Priority of segment in P10k | 10 | integer |
| `ui.prompt_integration.segment_content` | Components to show in segment | ["personality", "system_status"] | Array of strings |
| `ui.prompt_integration.show_personality` | Show personality in prompt | true | true, false |
| `ui.prompt_integration.personality_frequency` | How often Rick's comments appear | 0.7 | 0.0-1.0 (float) |
| `ui.prompt_integration.status_indicators` | Status indicators to show | ["cpu", "memory", "temperature"] | Array of strings |
| `ui.status_bar_elements` | Elements to show in status bar | ["path", "metrics", "catchphrase"] | Array of strings |
| `ui.colors.primary` | Primary UI color | green | string (color name) |
| `ui.colors.secondary` | Secondary UI color | blue | string (color name) |
| `ui.colors.accent` | Accent UI color | yellow | string (color name) |
| `ui.colors.error` | Error UI color | red | string (color name) |

## 🔧 ADVANCED OPTIONS

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `system.metrics_refresh_rate` | Refresh rate for system metrics (seconds) | 5 | integer |
| `system.show_cpu_usage` | Show CPU usage in metrics | true | true, false |
| `system.show_memory_usage` | Show memory usage in metrics | true | true, false |
| `system.show_disk_space` | Show disk space in metrics | false | true, false |
| `system.show_temperature` | Show temperature in metrics | false | true, false |
| `system.command_history_size` | Number of commands to keep in history | 1000 | integer |
| `system.cache_ttl` | Cache time-to-live (seconds) | 2.0 | float |
| `system.startup_timeout` | Timeout for startup operations (seconds) | 1.0 | float |
| `system.max_log_size_mb` | Maximum log file size (MB) | 5.0 | float |

## Configuration File Locations
- Primary configuration: `~/.rick_assistant/config.json`
- Legacy configuration: `~/.rick_config.json`

## Configuration Methods
1. **Direct File Editing**: Edit the JSON configuration files directly
2. **Command Line**: Use `rick config set <key> <value>` command
3. **Configuration Menu**: Use `rick-menu` or `!config` command for an interactive menu

## Notes
- Configuration options are automatically migrated between versions
- Some options have multiple naming formats for backward compatibility
- Configuration files are backed up automatically before changes
- The plugin will attempt to repair corrupted configuration files
