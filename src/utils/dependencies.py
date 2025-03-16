"""
Dependency Registry Module for Rick Assistant ZSH Plugin

This module maintains a registry of component dependencies and provides
utilities for dependency management, visualization, and validation.

"Listen Morty, d-dependencies are like *burp* relationships. 
They're messy, complicated, and if you don't manage them right, 
everything turns into a giant cluster**bleep**."
"""

import os
import sys
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.path_safety import (
    normalize_path,
    is_path_within_safe_directories,
    ensure_safe_directory,
    safe_atomic_write
)

# Logger for this module
logger = get_logger(__name__)

# Define project phases to organize components
PHASES = {
    1.1: "Plugin Entry Point",
    1.2: "Logging System",
    1.3: "Error Handling System",
    1.4: "Configuration Management",
    1.5: "State Management",
    1.6: "Command Processor",
    # Add more phases as needed
}

# Define the dependency map structure
# Format: "component_path": ["dependency1", "dependency2", ...]
DEPENDENCY_MAP: Dict[str, List[str]] = {
    # Phase 1.1: Plugin Entry Point
    "rick_assistant.plugin.zsh": [],  # Main plugin script, no dependencies
    
    # Phase 1.2: Logging System
    "src/utils/logger.py": ["rick_assistant.plugin.zsh"],
    
    # Phase 1.3: Core Infrastructure
    "src/core/setup.py": ["src/utils/logger.py"],
    "src/core/hooks.py": ["src/utils/logger.py"],
    "src/core/prompt.py": ["src/utils/logger.py"],
    "src/core/commands.py": ["src/utils/logger.py", "src/core/hooks.py"],
    
    # Additional components will be added as they are implemented
    # Future phases will follow the same pattern
}

# Component to phase mapping
COMPONENT_PHASES: Dict[str, float] = {
    "rick_assistant.plugin.zsh": 1.1,
    "src/utils/logger.py": 1.2,
    "src/core/setup.py": 1.3,
    "src/core/hooks.py": 1.3,
    "src/core/prompt.py": 1.3,
    "src/core/commands.py": 1.3,
    # Add more components as they are implemented
}

def get_dependencies(component: str) -> List[str]:
    """
    Get direct dependencies of a component.
    
    Args:
        component: Path to the component file
    
    Returns:
        List of component dependencies
        
    Example:
        >>> get_dependencies("src/core/commands.py")
        ['src/utils/logger.py', 'src/core/hooks.py']
    """
    if component not in DEPENDENCY_MAP:
        logger.warning(f"Component '{component}' not found in dependency map")
        return []
    
    return DEPENDENCY_MAP[component]

def get_dependency_chain(component: str, visited: Optional[Set[str]] = None) -> List[str]:
    """
    Get the full dependency chain for a component (recursive).
    
    Args:
        component: Path to the component file
        visited: Set of already visited components (for recursion)
    
    Returns:
        List of all dependencies in order
    
    Example:
        >>> get_dependency_chain("src/core/commands.py")
        ['rick_assistant.plugin.zsh', 'src/utils/logger.py', 'src/core/hooks.py']
    """
    if visited is None:
        visited = set()
    
    if component not in DEPENDENCY_MAP:
        logger.warning(f"Component '{component}' not found in dependency map")
        return []
    
    result = []
    
    for dependency in DEPENDENCY_MAP.get(component, []):
        if dependency not in visited:
            visited.add(dependency)
            chain = get_dependency_chain(dependency, visited)
            for dep in chain:
                if dep not in result:
                    result.append(dep)
            if dependency not in result:
                result.append(dependency)
    
    return result

def detect_circular_dependencies() -> List[Tuple[str, str]]:
    """
    Detect circular dependencies in the dependency map.
    
    Returns:
        List of tuples representing circular dependencies
    
    Example:
        >>> detect_circular_dependencies()
        [('src/a.py', 'src/b.py'), ('src/b.py', 'src/a.py')]
    """
    circular_deps = []
    
    def check_circular(component, path=None):
        if path is None:
            path = []
        
        if component in path:
            # Found circular dependency
            circular_index = path.index(component)
            cycle = path[circular_index:] + [component]
            for i in range(len(cycle) - 1):
                circular_deps.append((cycle[i], cycle[i+1]))
            return True
        
        path = path + [component]
        
        for dependency in DEPENDENCY_MAP.get(component, []):
            if check_circular(dependency, path):
                return True
        
        return False
    
    for component in DEPENDENCY_MAP:
        check_circular(component)
    
    return circular_deps

def visualize_dependencies(component: Optional[str] = None) -> str:
    """
    Generate an ASCII representation of the dependency graph.
    
    Args:
        component: If provided, show only this component's dependencies
                  If None, show the entire dependency graph
    
    Returns:
        ASCII representation of the dependency graph
    
    Example:
        >>> print(visualize_dependencies("src/core/commands.py"))
        src/core/commands.py
        ├── src/utils/logger.py
        │   └── rick_assistant.plugin.zsh
        └── src/core/hooks.py
            └── src/utils/logger.py
                └── rick_assistant.plugin.zsh
    """
    if component and component not in DEPENDENCY_MAP:
        logger.warning(f"Component '{component}' not found in dependency map")
        return f"Component '{component}' not found in dependency map"
    
    components = [component] if component else sorted(DEPENDENCY_MAP.keys())
    result = []
    
    def draw_tree(comp, prefix="", is_last=True):
        branch = "└── " if is_last else "├── "
        result.append(f"{prefix}{branch}{comp}")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        deps = DEPENDENCY_MAP.get(comp, [])
        
        for i, dep in enumerate(deps):
            is_last_dep = i == len(deps) - 1
            draw_tree(dep, new_prefix, is_last_dep)
    
    if component:
        result.append(component)
        deps = DEPENDENCY_MAP.get(component, [])
        for i, dep in enumerate(deps):
            is_last_dep = i == len(deps) - 1
            draw_tree(dep, "", is_last_dep)
    else:
        for comp in components:
            result.append(f"\n{comp}")
            deps = DEPENDENCY_MAP.get(comp, [])
            for i, dep in enumerate(deps):
                is_last_dep = i == len(deps) - 1
                draw_tree(dep, "", is_last_dep)
    
    return "\n".join(result)

def is_component_implemented(component: str) -> bool:
    """
    Check if a component is implemented (exists in the filesystem).
    
    Args:
        component: Path to the component file
    
    Returns:
        True if the component exists, False otherwise
    
    Example:
        >>> is_component_implemented("src/utils/logger.py")
        True
    """
    if component == "rick_assistant.plugin.zsh":
        # Special case for the main plugin script
        component = "rick_assistant.plugin.zsh"
    
    # Get the project root directory
    project_root_dir = Path(__file__).parent.parent.parent
    
    # Normalize and validate the component path
    component_path = normalize_path(project_root_dir / component)
    
    # Check if the path is valid and exists
    return component_path is not None and component_path.exists()

def get_components_by_phase(phase: float) -> List[str]:
    """
    Get all components in a specific phase.
    
    Args:
        phase: Phase number (e.g., 1.1, 1.2, etc.)
    
    Returns:
        List of component paths for the given phase
    
    Example:
        >>> get_components_by_phase(1.2)
        ['src/utils/logger.py']
    """
    components = []
    
    for component, component_phase in COMPONENT_PHASES.items():
        if component_phase == phase:
            components.append(component)
    
    return components

def sort_components_by_dependency() -> List[str]:
    """
    Order components based on dependency resolution (topological sort).
    Components with no dependencies come first, followed by components
    that depend only on already-listed components.
    
    Returns:
        Ordered list of components
    
    Example:
        >>> sort_components_by_dependency()
        ['rick_assistant.plugin.zsh', 'src/utils/logger.py', 'src/core/hooks.py', 'src/core/commands.py']
    """
    # Create a copy of the dependency map
    temp_map = {k: list(v) for k, v in DEPENDENCY_MAP.items()}
    result = []
    
    # Find all components with no dependencies
    def find_no_deps():
        return [c for c in temp_map if not temp_map[c]]
    
    # Process until all components are sorted
    while temp_map:
        no_deps = find_no_deps()
        
        # If there are circular dependencies, we won't find components with no dependencies
        if not no_deps:
            logger.error("Circular dependencies detected, cannot sort components")
            # Add remaining components to the result to avoid infinite loop
            result.extend(temp_map.keys())
            break
        
        # Add components with no dependencies to the result
        result.extend(no_deps)
        
        # Remove these components from the map
        for component in no_deps:
            temp_map.pop(component)
        
        # Remove these components from other components' dependencies
        for deps in temp_map.values():
            for component in no_deps:
                if component in deps:
                    deps.remove(component)
    
    return result

def generate_dependency_documentation(output_path: Optional[str] = None) -> str:
    """
    Generate Markdown documentation of the dependency structure.
    
    Args:
        output_path: Optional path to save the documentation
    
    Returns:
        Markdown string documenting the dependency structure
    
    Example:
        >>> doc = generate_dependency_documentation("docs/dependencies.md")
    """
    lines = ["# Rick Assistant Dependency Documentation", ""]
    
    # Add phase information
    lines.append("## Project Phases")
    lines.append("")
    for phase, description in sorted(PHASES.items()):
        lines.append(f"### Phase {phase}: {description}")
        components = get_components_by_phase(phase)
        for component in components:
            implemented = "✅" if is_component_implemented(component) else "❌"
            lines.append(f"- {implemented} `{component}`")
        lines.append("")
    
    # Add dependency information
    lines.append("## Component Dependencies")
    lines.append("")
    for component in sort_components_by_dependency():
        lines.append(f"### `{component}`")
        if component in DEPENDENCY_MAP:
            dependencies = DEPENDENCY_MAP[component]
            if dependencies:
                lines.append("")
                lines.append("Dependencies:")
                for dep in dependencies:
                    implemented = "✅" if is_component_implemented(dep) else "❌"
                    lines.append(f"- {implemented} `{dep}`")
            else:
                lines.append("")
                lines.append("No dependencies.")
        
        # Include reverse dependencies (what depends on this)
        reverse_deps = []
        for comp, deps in DEPENDENCY_MAP.items():
            if component in deps:
                reverse_deps.append(comp)
        
        if reverse_deps:
            lines.append("")
            lines.append("Required by:")
            for rev_dep in reverse_deps:
                implemented = "✅" if is_component_implemented(rev_dep) else "❌"
                lines.append(f"- {implemented} `{rev_dep}`")
        
        lines.append("")
    
    # Add implementation order suggestion
    lines.append("## Suggested Implementation Order")
    lines.append("")
    lines.append("Based on dependency analysis, components should be implemented in this order:")
    lines.append("")
    for i, component in enumerate(sort_components_by_dependency(), 1):
        implemented = "✅" if is_component_implemented(component) else "❌"
        lines.append(f"{i}. {implemented} `{component}`")
    
    markdown_content = "\n".join(lines)
    
    # If output path is provided, save the documentation to file
    if output_path:
        try:
            # Normalize the output path
            output_file_path = normalize_path(output_path)
            
            if output_file_path and is_path_within_safe_directories(output_file_path):
                # Ensure parent directory exists
                parent_dir = output_file_path.parent
                if ensure_safe_directory(parent_dir, create=True):
                    # Write the documentation safely
                    safe_atomic_write(
                        path=output_file_path,
                        content=markdown_content,
                        mode='w',
                        encoding='utf-8'
                    )
                    logger.info(f"Dependency documentation saved to {output_file_path}")
                else:
                    logger.error(f"Failed to create directory for {output_file_path}")
            else:
                logger.error(f"Invalid or unsafe output path: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save dependency documentation: {str(e)}")
    
    return markdown_content

# When run as a script, print dependency documentation
if __name__ == "__main__":
    print("Rick's Dependency Analyzer 🧪")
    print("=========================")
    
    # Check for circular dependencies
    circular = detect_circular_dependencies()
    if circular:
        print("\n❌ Circular dependencies detected!")
        for src, dst in circular:
            print(f"  {src} → {dst}")
    else:
        print("\n✅ No circular dependencies detected")
    
    # Print visualization
    print("\nDependency Visualization:")
    print(visualize_dependencies())
    
    # Print implementation order
    print("\nSuggested Implementation Order:")
    for i, component in enumerate(sort_components_by_dependency(), 1):
        implemented = "✅" if is_component_implemented(component) else "❌"
        print(f"{i}. {implemented} {component}")
    
    # Save documentation to file if argument provided
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        generate_dependency_documentation(output_file)
        print(f"\nDocumentation saved to {output_file}")
