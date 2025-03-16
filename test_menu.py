#!/usr/bin/env python3
"""
Test script for the Rick Assistant paginated menu.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration utils
def get_config_value(key, default=None):
    """Mock config getter for testing"""
    print(f"Getting config value: {key} (default: {default})")
    return default

def set_config_value(key, value):
    """Mock config setter for testing"""
    print(f"Setting config value: {key} = {value}")
    return True

def toggle_config_value(key, default=False):
    """Mock config toggle for testing"""
    current = get_config_value(key, default)
    new_value = not current
    set_config_value(key, new_value)
    return new_value

# Define Rick & Morty themed color palettes
PORTAL_COLORS = {
    "normal": {"fg": "green", "bg": "black"},
    "highlight": {"fg": "cyan", "bg": "black"},
    "selected": {"fg": "black", "bg": "green"},
    "disabled": {"fg": "white", "bg": "black"},
    "header": {"fg": "green", "bg": "black"},
    "footer": {"fg": "cyan", "bg": "black"},
    "border": {"fg": "green", "bg": "black"},
    "error": {"fg": "red", "bg": "black"},
    "success": {"fg": "green", "bg": "black"},
    "warning": {"fg": "yellow", "bg": "black"}
}

# Default theme
DEFAULT_THEME = PORTAL_COLORS

# Base class for menu items
class MenuItem:
    """Base class for menu items."""
    
    def __init__(self, text, action=None, enabled=True, 
                 key=None, coming_soon=False, 
                 item_type="standard"):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.key = key
        self.coming_soon = coming_soon
        self.parent = None
        self.item_type = item_type
    
    def activate(self):
        """Activate this item."""
        if not self.enabled:
            return None
            
        if self.coming_soon:
            return "coming_soon"
            
        if callable(self.action):
            return self.action()
            
        return None
        
    def get_display_text(self):
        """Get display text for the item."""
        text = self.text
        
        if self.coming_soon:
            text = f"{text} 🚧"
            
        return text

class Menu:
    """Menu class for navigable menus."""
    
    def __init__(self, title="Menu", items=None, parent=None, 
                 border_style="single", theme=None):
        self.title = title
        self.items = items or []
        self.parent = parent
        self.border_style = border_style
        self.theme = theme or DEFAULT_THEME
        self.current_page = 0
        self.items_per_page = 10
        
        # Build breadcrumb path if parent is provided
        self.breadcrumbs = []
        if parent:
            # Start with parent's breadcrumbs
            self.breadcrumbs = parent.breadcrumbs.copy() if hasattr(parent, 'breadcrumbs') else []
            
            # Add parent's title if not already in breadcrumbs
            if parent.title and (not self.breadcrumbs or self.breadcrumbs[-1] != parent.title):
                self.breadcrumbs.append(parent.title)
    
    def add_item(self, item):
        """Add an item to the menu."""
        item.parent = self
        self.items.append(item)
    
    def get_page_count(self):
        """Get the number of pages."""
        if not self.items:
            return 1
            
        return (len(self.items) + self.items_per_page - 1) // self.items_per_page
    
    def get_current_page_items(self):
        """Get items on the current page."""
        if not self.items:
            return []
            
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        
        return self.items[start_idx:end_idx]
    
    def next_page(self):
        """Go to the next page."""
        page_count = self.get_page_count()
        if self.current_page < page_count - 1:
            self.current_page += 1
        return self.current_page
    
    def prev_page(self):
        """Go to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
        return self.current_page
    
    def get_breadcrumbs(self):
        """Get breadcrumb path for this menu."""
        return self.breadcrumbs + [self.title]

class MenuCategory(MenuItem):
    """Category menu item that can contain sub-items."""
    
    def __init__(self, text, items=None, expanded=False, enabled=True):
        super().__init__(text, None, enabled, None, False, "category")
        self.items = items or []
        self.expanded = expanded
        
        # Set parent reference for all items
        for item in self.items:
            item.parent = self
            
    def add_item(self, item):
        """Add an item to this category."""
        item.parent = self
        self.items.append(item)
        
    def activate(self):
        """Activate this category (toggle expansion)."""
        if not self.enabled:
            return None
            
        self.expanded = not self.expanded
        return "expanded" if self.expanded else "collapsed"
        
    def get_display_text(self):
        """Get display text with expansion indicator."""
        indicator = "▼" if self.expanded else "▶"
        return f"{indicator} {self.text}"

    def create_submenu(self):
        """Create a submenu from this category."""
        # Create submenu with this category's title and items
        submenu = Menu(title=self.text, parent=self.parent)
        
        # Add all items to the submenu
        for item in self.items:
            submenu.add_item(item)
            
        return submenu

class MenuToggle(MenuItem):
    """Toggleable menu item."""
    
    def __init__(self, text, key, default=False, enabled=True):
        super().__init__(text, None, enabled, key, False, "toggle")
        self.default = default
        
    def get_state(self):
        """Get the current toggle state."""
        if self.key:
            return get_config_value(self.key, self.default)
        return self.default
        
    def toggle(self):
        """Toggle the state."""
        new_state = not self.get_state()
        
        if self.key:
            set_config_value(self.key, new_state)
            
        return new_state
        
    def activate(self):
        """Activate (toggle) this item."""
        if not self.enabled:
            return None
            
        return self.toggle()
        
    def get_display_text(self):
        """Get display text with toggle state."""
        state = self.get_state()
        indicator = "[X]" if state else "[ ]"
        return f"{indicator} {self.text}"

class MultiOptionMenuItem(MenuItem):
    """Menu item with multiple selectable options."""
    
    def __init__(self, text, key, options, default=None, enabled=True):
        super().__init__(text, None, enabled, key, False, "multi_option")
        self.options = options
        self.default = default or (options[0] if options else "")
        
    def get_current_option(self):
        """Get the currently selected option."""
        if self.key:
            return get_config_value(self.key, self.default)
        return self.default
        
    def next_option(self):
        """Select the next option."""
        if not self.options:
            return self.default
            
        current = self.get_current_option()
        try:
            index = self.options.index(current)
            new_index = (index + 1) % len(self.options)
            new_option = self.options[new_index]
        except (ValueError, IndexError):
            new_option = self.options[0] if self.options else self.default
            
        if self.key:
            set_config_value(self.key, new_option)
            
        return new_option
        
    def activate(self):
        """Activate (cycle) this item."""
        if not self.enabled:
            return None
            
        return self.next_option()
        
    def get_display_text(self):
        """Get display text with current option."""
        option = self.get_current_option()
        return f"{self.text}: {option}"

def create_test_menu():
    """Create a test menu with various item types."""
    main_menu = Menu(title="Rick Assistant Test Menu")
    
    # Add some menu items
    brain_items = [
        MenuToggle("Enable Brain Module", "brain.enabled", True),
        MultiOptionMenuItem("Active Brain Model", "brain.model", 
                          ["Default", "OpenAI", "Ollama", "Anthropic"]),
        MenuToggle("Enhanced Context", "brain.enhanced_context", True)
    ]
    brain_category = MenuCategory("Brain Module", brain_items)
    main_menu.add_item(brain_category)
    
    # Add more categories
    cmd_items = [
        MenuToggle("Enable Command Suggestions", "commands.suggestions", True),
        MenuToggle("Shell Command Enhancement", "commands.shell_enhancement", True)
    ]
    cmd_category = MenuCategory("Commands", cmd_items)
    main_menu.add_item(cmd_category)
    
    # Add simple items
    main_menu.add_item(MenuItem("Help", lambda: print("Help selected")))
    main_menu.add_item(MenuItem("Exit", lambda: "exit"))
    
    return main_menu

def test_pagination():
    """Test pagination functionality."""
    # Create a menu with many items
    menu = Menu(title="Pagination Test")
    
    # Add 25 items to test pagination (with default of 10 per page)
    for i in range(1, 26):
        menu.add_item(MenuItem(f"Item {i}", lambda i=i: print(f"Selected item {i}")))
    
    # Check page count
    page_count = menu.get_page_count()
    print(f"Total pages: {page_count}")
    
    # Test navigation
    print("\nPage 1 items:")
    for item in menu.get_current_page_items():
        print(f"- {item.get_display_text()}")
    
    # Go to next page
    menu.next_page()
    print("\nPage 2 items:")
    for item in menu.get_current_page_items():
        print(f"- {item.get_display_text()}")
    
    # Go to next page again
    menu.next_page()
    print("\nPage 3 items:")
    for item in menu.get_current_page_items():
        print(f"- {item.get_display_text()}")
    
    # Go back to previous page
    menu.prev_page()
    print("\nBack to Page 2 items:")
    for item in menu.get_current_page_items():
        print(f"- {item.get_display_text()}")

def test_menu_structure():
    """Test the menu structure with various item types."""
    menu = create_test_menu()
    
    # Print menu structure
    print(f"Menu: {menu.title}")
    print("Items:")
    
    for item in menu.items:
        print(f"- {item.get_display_text()}")
        
        if isinstance(item, MenuCategory):
            print("  Subitems:")
            for subitem in item.items:
                print(f"  - {subitem.get_display_text()}")

def test_breadcrumbs():
    """Test breadcrumb generation for nested menus."""
    main_menu = Menu(title="Main Menu")
    
    # Create a category
    category = MenuCategory("Settings")
    main_menu.add_item(category)
    
    # Create a submenu from the category
    submenu = category.create_submenu()
    
    # Add a subcategory to the submenu
    subcategory = MenuCategory("Advanced Settings")
    submenu.add_item(subcategory)
    
    # Create a sub-submenu from the subcategory
    subsubmenu = subcategory.create_submenu()
    
    # Test breadcrumb paths
    print(f"Main menu breadcrumbs: {main_menu.get_breadcrumbs()}")
    print(f"Submenu breadcrumbs: {submenu.get_breadcrumbs()}")
    print(f"Sub-submenu breadcrumbs: {subsubmenu.get_breadcrumbs()}")

def main():
    """Run all tests."""
    print("=== Testing Menu Structure ===")
    test_menu_structure()
    
    print("\n=== Testing Pagination ===")
    test_pagination()
    
    print("\n=== Testing Breadcrumbs ===")
    test_breadcrumbs()

if __name__ == "__main__":
    main() 