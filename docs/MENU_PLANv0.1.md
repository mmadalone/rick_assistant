# Rick Assistant Menu System Revamp Plan v0.1

## Overview

This plan outlines the approach to revamp the existing menu code to match the visual style and functionality shown in ricktastic_menu.md, while ensuring all USER_CONFIGURABLES.md options are included. The implementation will keep the existing Python-based approach but change the visual style and navigation to match requirements.

## Key Changes

1. **Visual Style**
   - Implement the exact visual style shown in ricktastic_menu.md with slash/dash borders
   - Support configurable Unicode box-drawing characters with ASCII fallback
   - Update the color scheme to green/cyan with user customization options
   - Remove system metrics from the footer

2. **Menu Structure**
   - Maintain the existing class structure (Menu, MenuItem, etc.)
   - Create menu categories matching ricktastic_menu.md
   - Mark "coming soon" items with 🚧 
   - Support up to 4 levels of nesting

3. **Navigation**
   - Support both arrow key navigation and number selection
   - Implement wraparound navigation
   - No persistence of menu state

4. **Error Handling**
   - Keep the `safe_execute` decorator for robust error handling
   - Use the established pattern in the codebase for consistency

5. **Performance**
   - Minimize screen redrawing for better performance

## Implementation Phases

### Phase 1: Core Visual Update
- Update the border, header, and footer styling
- Implement the basic visual appearance

### Phase 2: Navigation Update
- Implement number selection
- Add wraparound navigation
- Ensure Arrow key navigation works correctly

### Phase 3: Menu Structure
- Build the complete menu hierarchy from ricktastic_menu.md
- Ensure all USER_CONFIGURABLES.md options are included
- Add coming soon markers where appropriate

### Phase 4: UI Customization
- Add style customization options
- Implement adaptive terminal capability detection
- Ensure minimum terminal size requirements are met

### Phase 5: Testing and Refinement
- Test across different terminal types
- Optimize performance
- Ensure consistent behavior

## Detailed Code Implementations

### 1. Menu Border Style Update

```python
def create_menu_border(width: int, height: int, style: str = "slash") -> List[str]:
    """
    Create menu border with specified style.
    
    Args:
        width: Width of the border
        height: Height of the border
        style: Border style ('slash', 'unicode', 'simple')
        
    Returns:
        List[str]: Lines of the border
    """
    # Available border styles
    styles = {
        "slash": {
            "top_left": "/",
            "top_right": "\\",
            "bottom_left": "\\",
            "bottom_right": "/",
            "horizontal": "―",
            "vertical": "|"
        },
        "unicode": {
            "top_left": "┌",
            "top_right": "┐",
            "bottom_left": "└",
            "bottom_right": "┘",
            "horizontal": "─",
            "vertical": "│"
        },
        "simple": {
            "top_left": "+",
            "top_right": "+",
            "bottom_left": "+",
            "bottom_right": "+",
            "horizontal": "-",
            "vertical": "|"
        }
    }
    
    # Use simple style if unicode not supported and style is unicode
    if style == "unicode" and not supports_unicode():
        style = "simple"
        
    # Get border characters for the style
    border = styles.get(style, styles["slash"])  # Default to slash style
    
    # Create border lines
    top = border["top_left"] + border["horizontal"] * (width - 2) + border["top_right"]
    middle = border["vertical"] + " " * (width - 2) + border["vertical"]
    bottom = border["bottom_left"] + border["horizontal"] * (width - 2) + border["bottom_right"]
    
    # Colorize if supported
    if supports_ansi_color():
        top = color_text(top, "green")
        middle = color_text(middle, "green")
        bottom = color_text(bottom, "green")
    
    # Create all lines
    lines = [top]
    for _ in range(height - 2):
        lines.append(middle)
    lines.append(bottom)
    
    return lines
```

### 2. Footer Updates

```python
def create_menu_footer(controls: Dict[str, str], width: int) -> List[str]:
    """
    Create footer with key controls.
    
    Args:
        controls: Dict mapping keys to actions
        width: Available width
        
    Returns:
        List[str]: Lines of the footer
    """
    # Create separator
    separator = "―" * width if supports_unicode() else "-" * width
    if supports_ansi_color():
        separator = color_text(separator, "green")
    
    # Format controls with brackets as shown in ricktastic_menu.md
    control_parts = []
    for key, action in controls.items():
        if supports_ansi_color():
            formatted = f"[ {color_text(key, 'cyan')} = {action} ]"
        else:
            formatted = f"[ {key} = {action} ]"
        control_parts.append(formatted)
    
    # Join controls with spaces
    control_text = "  ".join(control_parts)
    
    # Ensure control text fits and is centered
    if len(control_text) > width:
        # Create multiple lines of controls if needed
        control_lines = []
        current_line = []
        current_width = 0
        
        for part in control_parts:
            part_width = len(part) + 2  # +2 for spacing
            if current_width + part_width > width and current_line:
                control_lines.append("  ".join(current_line))
                current_line = [part]
                current_width = part_width
            else:
                current_line.append(part)
                current_width += part_width
                
        if current_line:
            control_lines.append("  ".join(current_line))
        
        footer_lines = [separator] + [line.center(width) for line in control_lines]
    else:
        # Single line of controls
        footer_lines = [separator, control_text.center(width)]
    
    # Add version info line 
    version_info = "YOU'RE RUNNING RICK ASSISTANT v0.1.0 - C-137 MORTY EDITION"
    if supports_ansi_color():
        version_info = color_text(version_info, "cyan")
    
    # Insert version info before controls
    footer_lines.insert(1, "")  # Blank line
    footer_lines.insert(2, version_info.center(width))
    footer_lines.append("")  # Blank line at the end
    
    return footer_lines
```

### 3. Menu Navigation Update

```python
def navigate_menu(menu: Menu, parent_menu: Menu = None, border_style: str = "slash") -> Optional[Tuple[int, Any]]:
    """
    Handle menu navigation and selection.
    
    Args:
        menu: Menu object to navigate
        parent_menu: Parent menu (for back navigation)
        border_style: Border style to use
        
    Returns:
        Optional[Tuple[int, Any]]: Selected index and item value, or None if cancelled
    """
    # Set up key controls
    controls = {
        "↑/↓": "Navigate", 
        "1-9": "Select",
        "Enter": "Select",
        "Esc": "Exit"
    }
    
    # Add back control if there's a parent menu
    if parent_menu:
        controls["B"] = "Back"
    
    # Initialize selection
    menu.selected_index = 0
    
    # Main menu navigation loop
    while not menu.exit_requested:
        try:
            # Clear screen
            clear_screen()
            
            # Create menu elements
            border = create_menu_border(menu.width, menu.height, style=border_style)
            header = create_menu_header(menu.title, menu.width)
            footer = create_menu_footer(controls, menu.width)
            
            # Get visible items
            visible_items = menu.get_visible_items()
            
            # Calculate available space for items
            available_height = menu.height - len(header) - len(footer) - 2
            
            # Handle scrolling if needed
            total_items = len(visible_items)
            
            # Add number prefixes to menu items for number selection
            numbered_items = []
            for i, item in enumerate(visible_items):
                if i < 9:  # Only number items 1-9
                    # Add number prefix to item text
                    item_text = item.text
                    if "🚧" not in item_text:
                        item.text = f"{i+1}. {item_text}"
                    else:
                        item.text = f"{i+1}. {item_text}"
                numbered_items.append(item)
            
            # Render menu
            render_menu(border, header, numbered_items, footer, menu.selected_index)
            
            # Get user input
            key = get_menu_key()
            
            # Process input
            if key == "up":
                # Wraparound navigation
                menu.selected_index = (menu.selected_index - 1) % total_items
            elif key == "down":
                # Wraparound navigation
                menu.selected_index = (menu.selected_index + 1) % total_items
            elif key == "enter":
                current_item = menu.get_current_item()
                if current_item and current_item.enabled:
                    result = menu.activate_selected()
                    if result is not None:
                        # Clean up item texts before returning
                        for item in visible_items:
                            if item.text.startswith(tuple(f"{n}. " for n in range(1, 10))):
                                item.text = item.text[3:]  # Remove the "N. " prefix
                        return menu.selected_index, result
            elif key == "escape":
                # Clean up item texts before exiting
                for item in visible_items:
                    if item.text.startswith(tuple(f"{n}. " for n in range(1, 10))):
                        item.text = item.text[3:]  # Remove the "N. " prefix
                return None
            elif key == "b" and parent_menu:
                # Clean up item texts before returning to parent
                for item in visible_items:
                    if item.text.startswith(tuple(f"{n}. " for n in range(1, 10))):
                        item.text = item.text[3:]  # Remove the "N. " prefix
                return None
            elif key in "123456789":
                # Number selection
                index = int(key) - 1
                if 0 <= index < total_items:
                    menu.selected_index = index
                    current_item = menu.get_current_item()
                    if current_item and current_item.enabled:
                        result = menu.activate_selected()
                        if result is not None:
                            # Clean up item texts before returning
                            for item in visible_items:
                                if item.text.startswith(tuple(f"{n}. " for n in range(1, 10))):
                                    item.text = item.text[3:]  # Remove the "N. " prefix
                            return menu.selected_index, result
            
            # Clean up and restore original text
            for item in visible_items:
                if item.text.startswith(tuple(f"{n}. " for n in range(1, 10))):
                    item.text = item.text[3:]  # Remove the "N. " prefix
                    
        except Exception as e:
            logger.error(f"Error in menu navigation: {str(e)}")
            time.sleep(1)  # Brief pause to show error
    
    return None
```

### 4. Coming Soon Items Support

```python
class MenuItem:
    """Individual selectable menu item"""
    
    def __init__(self, text: str, value: Any = None, enabled: bool = True, 
                 callback: Callable = None, icon: str = None, coming_soon: bool = False):
        """
        Initialize a menu item.
        
        Args:
            text: Display text for the item
            value: Value associated with the item
            enabled: Whether the item is selectable
            callback: Function to call when selected
            icon: Icon to display before the text
            coming_soon: Whether this item is coming soon (adds 🚧 marker)
        """
        self.text = text
        self.value = value
        self.enabled = enabled
        self.callback = callback
        self.icon = self._validate_icon(icon)
        self.parent = None
        self.submenu = None
        
        # Add coming soon marker if needed
        if coming_soon:
            self.text = f"{self.text} 🚧"
            self.enabled = False
```

### 5. Menu Structure Implementation

```python
def create_main_menu() -> Menu:
    """
    Create the main Rick Assistant control panel menu.
    
    Returns:
        Menu: The main menu with all categories
    """
    main_menu = Menu(title="🧪 RICK ASSISTANT CONTROL PANEL 🧪")
    
    # Add main categories
    brain_module = main_menu.add_category("🧠 BRAIN MODULE")
    rick_cmds = main_menu.add_category("💻 RICK CMDS")
    settings = main_menu.add_category("⚙️ SETTINGS")
    universe = main_menu.add_category("🌀 UNIVERSE")
    safety = main_menu.add_category("🛡️ SAFETY")
    ui_settings = main_menu.add_category("🎨 UI SETTINGS")
    input_handling = main_menu.add_category("⌨️ INPUT HANDLING")
    advanced_options = main_menu.add_category("🔧 ADVANCED OPTIONS")
    monitoring = main_menu.add_category("📊 MONITORING")
    settings_backup = main_menu.add_category("📦 SETTINGS BACKUP")
    
    # Populate submenus based on ricktastic_menu.md
    # ...

    return main_menu
```

## Conclusion

This implementation plan follows the requirements while maintaining the existing Python-based structure. It updates the visual style to match ricktastic_menu.md exactly, while incorporating all configuration options from USER_CONFIGURABLES.md.

The implementation will proceed in phases with careful error handling and performance optimization at each step.
