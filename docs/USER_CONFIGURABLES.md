# Rick Assistant - User Configurable Options

This document provides a comprehensive list of all configuration options available in Rick Assistant. Options marked with 🚧 are planned but not yet implemented.

## 🧠 BRAIN MODULE

### 🧠 FAKE RICK
| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `personality.character` | Character to simulate | rick | rick, morty, meeseeks, jerry, beth, summer |
| `personality.sass_level` | Level of sass in responses | 7 | 1-10 (integer) |
| `personality.burp_frequency` | Frequency of burps in responses | 0.3 | 0.0-1.0 (float) |
| `personality.catchphrase_frequency` | Frequency of catchphrases | 0.2 | 0.0-1.0 (float) |
| `personality.scientific_reference_level` | Frequency of scientific references | 5 | 0-10 (integer) |
| `personality.use_catchphrases` | Whether to use catchphrases | true | true, false |
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
| `general.username` | User's name (for personalized responses) | "" | string |
| `general.sass_enabled` | Enable sassy responses | true | true, false |

## 🌀 UNIVERSE

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
| `safety.confirmations.dangerous` 🚧 | Require confirmation for dangerous operations | true | true, false |
| `safety.confirmations.remember` 🚧 | Remember confirmation decisions | true | true, false |
| `safety.confirmations.remember_ttl` 🚧 | How long to remember confirmations (seconds) | 3600 | integer |
| `safety.sudo.warn` 🚧 | Show warning for sudo commands | true | true, false |
| `safety.sudo.always_confirm` 🚧 | Always confirm sudo commands | true | true, false |

## 🎨 UI SETTINGS

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `ui.theme` | UI theme | portal | portal, science, classic, dark |
| `ui.animations` | Enable UI animations | true | true, false |
| `ui.animations_enabled` | Enable menu animations | true | true, false |
| `ui.prompt_style` | Style of prompt | classic | classic, minimal, verbose |
| `ui.use_static_portal` | Use static portal background | true | true, false |
| `ui.terminal_compatibility_mode` | Enable terminal compatibility mode | false | true, false |
| `ui.unicode` | Enable Unicode characters | true | true, false |
| `ui.show_metrics` | Show system metrics | true | true, false |
| `ui.use_python_menu` | Use Python menu implementation | false | true, false |
| `ui.color_scheme` | UI color scheme | default | default, dark, light, custom |
| `ui.prompt.style` 🚧 | Prompt style | default | default, minimal, verbose |
| `ui.prompt.icons` 🚧 | Show icons in prompt | true | true, false |
| `ui.status_bar.enabled` 🚧 | Enable status bar | true | true, false |
| `ui.status_bar.layout` 🚧 | Status bar layout | full | full, minimal, custom |
| `ui.status_bar.path` 🚧 | Show path in status bar | true | true, false |
| `ui.status_bar.universe` 🚧 | Show universe in status bar | true | true, false |
| `ui.status_bar.catchphrase` 🚧 | Show catchphrases in status bar | true | true, false |
| `ui.status_bar.metrics` 🚧 | Show metrics in status bar | true | true, false |
| `ui.colors.primary` 🚧 | Primary UI color | green | string (color name) |
| `ui.colors.accent` 🚧 | Accent UI color | cyan | string (color name) |
| `ui.stream_speed` 🚧 | Text typing animation speed | 0.03 | float (seconds) |

## ⌨️ INPUT HANDLING

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `ui.keybindings.autosuggestions_compat` | Compatibility with ZSH autosuggestions | false | true, false |
| `ui.keybindings.enable_vi_mode` | Enable Vi-style keybindings | false | true, false |
| `ui.keybindings.trigger_key` | Key to trigger special functions | ctrl+space | string |
| `input.keybindings.custom` 🚧 | Custom keybindings | {} | JSON object |
| `input.completions.enabled` 🚧 | Enable tab completions | true | true, false |
| `input.completions.suggestions` 🚧 | Show completion suggestions | true | true, false |
| `input.history.search` 🚧 | Enable history search | true | true, false |
| `input.history.analysis` 🚧 | Enable command history analysis | true | true, false |
| `input.syntax_highlight.enabled` 🚧 | Enable syntax highlighting | true | true, false |
| `input.syntax_highlight.theme` 🚧 | Syntax highlighting theme | portal | string |
| `input.inline_suggestions.enabled` 🚧 | Enable inline suggestions | true | true, false |
| `input.inline_suggestions.auto_accept` 🚧 | Auto-accept suggestions | false | true, false |

## 🔧 ADVANCED OPTIONS

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `system.metrics_refresh_rate` | Refresh rate for system metrics (seconds) | 5 | integer |
| `system.show_cpu_usage` | Show CPU usage in metrics | true | true, false |
| `system.show_memory_usage` | Show memory usage in metrics | true | true, false |
| `system.show_disk_space` | Show disk space in metrics | false | true, false |
| `system.show_temperature` | Show temperature in metrics | false | true, false |
| `system.command_history_size` | Number of commands to keep in history | 1000 | integer |
| `system.use_daemon` | Use daemon process for background tasks | true | true, false |
| `system.cache_ttl` | Cache time-to-live (seconds) | 2.0 | float |
| `system.startup_timeout` | Timeout for startup operations (seconds) | 1.0 | float |
| `system.max_log_size_mb` | Maximum log file size (MB) | 5.0 | float |
| `hooks.precmd` 🚧 | Hooks to run before command | [] | Array of strings |
| `hooks.preexec` 🚧 | Hooks to run before execution | [] | Array of strings |
| `hooks.chpwd` 🚧 | Hooks to run when changing directory | [] | Array of strings |
| `performance.lazy_load` 🚧 | Enable lazy loading of components | true | true, false |
| `performance.cache_enabled` 🚧 | Enable caching | true | true, false |
| `debug.verbose` 🚧 | Enable verbose debug output | false | true, false |
| `debug.log_dir` 🚧 | Directory for debug logs | default | string (path) |

## 📊 MONITORING

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `monitoring.enabled` 🚧 | Enable system monitoring | true | true, false |
| `monitoring.interval` 🚧 | Monitoring interval (seconds) | 5 | integer |
| `monitoring.metrics` 🚧 | Metrics to monitor | cpu,ram,temp | Comma-separated list |
| `monitoring.alerts.enabled` 🚧 | Enable monitoring alerts | true | true, false |
| `monitoring.alerts.threshold_cpu` 🚧 | CPU usage alert threshold (%) | 90 | 0-100 (integer) |
| `monitoring.alerts.threshold_ram` 🚧 | RAM usage alert threshold (%) | 90 | 0-100 (integer) |
| `monitoring.alerts.threshold_temp` 🚧 | Temperature alert threshold (°C) | 80 | integer |

## 📦 SETTINGS BACKUP

| Option | Description | Default | Available Values |
|--------|-------------|---------|-----------------|
| `backup.enabled` 🚧 | Enable automatic backups | true | true, false |
| `backup.interval` 🚧 | Backup interval (days) | 7 | integer |
| `backup.keep_count` 🚧 | Number of backups to keep | 5 | integer |
| `backup.directory` 🚧 | Backup directory | ${HOME}/.rick_assistant/backups | string (path) |
| `backup.compression` 🚧 | Enable backup compression | true | true, false |
| `backup.include_config` 🚧 | Include configuration in backups | true | true, false |
| `backup.include_messages` 🚧 | Include messages in backups | true | true, false |
| `backup.include_history` 🚧 | Include command history in backups | true | true, false |
