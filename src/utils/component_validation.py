"""
Validation Engine Module for Rick Assistant ZSH Plugin

This module provides functionality to validate component dependencies,
execute integration tests, and generate validation reports.

"I'm not just smart, Morty, I'm *burp* thorough. You can't just throw
components together and hope they work! That's how you get cronenbergs!"
"""

import os
import sys
import importlib.util
import inspect
import json
import time
import logging  # Added explicit import for logging
import traceback
from typing import Dict, List, Set, Optional, Tuple, Any, Callable, Union
from pathlib import Path
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field, asdict

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.dependencies import (
    get_dependencies,
    get_dependency_chain,
    get_components_by_phase,
    is_component_implemented,
    PHASES,
)
from src.utils.path_safety import (
    normalize_path,
    is_path_within_safe_directories,
    ensure_safe_directory,
    safe_atomic_write,
    validate_path_permissions
)

# Logger for this module
logger = get_logger(__name__)

# Define validation status
class ValidationStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    WARNING = auto()
    ERROR = auto()
    SKIPPED = auto()

@dataclass
class ValidationResult:
    """Represents the result of a validation operation."""
    component: str
    dependency: Optional[str] = None
    status: ValidationStatus = ValidationStatus.SUCCESS
    message: str = "Validation passed"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    
    def is_successful(self) -> bool:
        """Check if the validation was successful.""" 
        return self.status == ValidationStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        result = asdict(self)
        result['status'] = self.status.name
        result['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return result

@dataclass
class ComponentValidationResults:
    """Container for all validation results for a component."""
    component: str
    results: List[ValidationResult] = field(default_factory=list)
    
    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result."""
        self.results.append(result)
    
    def is_successful(self) -> bool:
        """Check if all validations were successful."""
        return all(r.is_successful() for r in self.results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all results to dictionary for serialization."""
        return {
            'component': self.component,
            'success': self.is_successful(),
            'results': [r.to_dict() for r in self.results]
        }

# Registry for component integration tests
# Format: {"component": {"dependency": test_function}}
INTEGRATION_TESTS: Dict[str, Dict[str, Callable]] = {}

def register_integration_test(component: str, dependency: str, test_func: Callable) -> None:
    """
    Register an integration test function for a component-dependency pair.
    
    Args:
        component: Path to the component file
        dependency: Path to the dependency file
        test_func: Test function that returns True for success or error message for failure
    """
    if component not in INTEGRATION_TESTS:
        INTEGRATION_TESTS[component] = {}
    
    INTEGRATION_TESTS[component][dependency] = test_func
    logger.debug(f"Registered integration test: {component} -> {dependency}")

def import_module_from_path(path: str) -> Optional[Any]:
    """
    Safely import a module from a file path.
    
    Args:
        path: Path to the module file
    
    Returns:
        Imported module or None if import fails
    """
    try:
        # Normalize and validate the path
        path_obj = normalize_path(path)
        if not path_obj:
            logger.error(f"Invalid module path: {path}")
            return None
            
        # Check if path is within safe directories
        if not is_path_within_safe_directories(path_obj):
            logger.error(f"Module path '{path_obj}' is outside safe directories")
            return None
        
        # Ensure path exists
        if not path_obj.exists():
            logger.error(f"Module path does not exist: {path_obj}")
            return None
            
        # Validate read permissions
        if not validate_path_permissions(path_obj, os.R_OK):
            logger.error(f"No read permission for module: {path_obj}")
            return None
            
        # Convert component path to module path
        if str(path_obj).endswith('.py'):
            module_name = path_obj.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, str(path_obj))
                if spec is None or spec.loader is None:
                    logger.error(f"Failed to load spec for {path_obj}")
                    return None
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                
                # Execute the module
                try:
                    spec.loader.exec_module(module)
                    return module
                except Exception as e:
                    logger.error(f"Error executing module {module_name}: {str(e)}")
                    logger.debug(traceback.format_exc())
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                    return None
            except Exception as e:
                logger.error(f"Error creating module spec for {path_obj}: {str(e)}")
                logger.debug(traceback.format_exc())
                return None
        else:
            logger.error(f"Path does not point to a Python file: {path_obj}")
            return None
    except Exception as e:
        logger.error(f"Error importing module from {path}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def execute_integration_test(component: str, dependency: str) -> ValidationResult:
    """
    Run integration test between a component and its dependency.
    
    Args:
        component: Path to the component file
        dependency: Path to the dependency file
        
    Returns:
        ValidationResult with test outcome
    """
    start_time = time.time()
    
    # Check if both component and dependency are implemented
    if not is_component_implemented(component):
        return ValidationResult(
            component=component,
            dependency=dependency,
            status=ValidationStatus.SKIPPED,
            message=f"Component not implemented: {component}",
            duration=time.time() - start_time
        )
    
    if not is_component_implemented(dependency):
        return ValidationResult(
            component=component,
            dependency=dependency,
            status=ValidationStatus.SKIPPED,
            message=f"Dependency not implemented: {dependency}",
            duration=time.time() - start_time
        )
    
    # Try to import component and dependency
    component_module = import_module_from_path(component)
    dependency_module = import_module_from_path(dependency)
    
    if not component_module:
        return ValidationResult(
            component=component,
            dependency=dependency,
            status=ValidationStatus.ERROR,
            message=f"Ugh, this is embarrassing! Failed to import component: {component}",
            duration=time.time() - start_time
        )
        
    if not dependency_module:
        return ValidationResult(
            component=component,
            dependency=dependency,
            status=ValidationStatus.ERROR,
            message=f"Wake up, Morty! Failed to import dependency: {dependency}",
            duration=time.time() - start_time
        )
    
    # Check if there's a registered integration test
    if component in INTEGRATION_TESTS and dependency in INTEGRATION_TESTS[component]:
        test_func = INTEGRATION_TESTS[component][dependency]
        try:
            logger.debug(f"Running integration test: {component} -> {dependency}")
            test_result = test_func()
            
            if test_result is True:
                return ValidationResult(
                    component=component,
                    dependency=dependency,
                    status=ValidationStatus.SUCCESS,
                    message=f"Integration test passed: {component} -> {dependency}",
                    duration=time.time() - start_time
                )
            else:
                # Test returned an error message
                return ValidationResult(
                    component=component,
                    dependency=dependency,
                    status=ValidationStatus.FAILURE,
                    message=f"Test failed: {test_result}",
                    details={"error_message": str(test_result)},
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return ValidationResult(
                component=component,
                dependency=dependency,
                status=ValidationStatus.ERROR,
                message=f"Holy crap, Morty! Integration test threw an exception!",
                details={"exception": str(e), "traceback": traceback.format_exc()},
                duration=time.time() - start_time
            )
    else:
        # No specific test found, perform basic import validation
        return ValidationResult(
            component=component,
            dependency=dependency,
            status=ValidationStatus.SUCCESS,
            message=f"Basic import validation passed: {component} -> {dependency}",
            details={"note": "No specific integration test defined"},
            duration=time.time() - start_time
        )

def validate_dependency(component: str, dependency: str) -> ValidationResult:
    """
    Verify that a component works with its dependency.
    
    Args:
        component: Path to the component file
        dependency: Path to the dependency file
        
    Returns:
        ValidationResult with validation outcome
    """
    logger.info(f"Validating dependency: {component} -> {dependency}")
    return execute_integration_test(component, dependency)

def validate_dependency_chain(component: str) -> ComponentValidationResults:
    """
    Test the complete dependency chain for a component.
    
    Args:
        component: Path to the component file
        
    Returns:
        ComponentValidationResults containing results for each dependency
    """
    logger.info(f"Validating dependency chain for: {component}")
    dependencies = get_dependency_chain(component)
    results = ComponentValidationResults(component=component)
    
    if not dependencies:
        logger.info(f"No dependencies found for {component}")
        return results
    
    # First validate direct dependencies
    direct_dependencies = get_dependencies(component)
    for dependency in direct_dependencies:
        result = validate_dependency(component, dependency)
        results.add_result(result)
    
    # Then validate dependency relationships across the chain
    for i in range(len(dependencies) - 1):
        for j in range(i + 1, len(dependencies)):
            if dependencies[j] in get_dependencies(dependencies[i]):
                result = validate_dependency(dependencies[i], dependencies[j])
                results.add_result(result)
    
    return results

def validate_phase(phase_number: float) -> Dict[str, ComponentValidationResults]:
    """
    Validate all components in a specific phase.
    
    Args:
        phase_number: Phase number (e.g., 1.1, 1.2)
        
    Returns:
        Dict mapping component paths to their validation results
    """
    if phase_number not in PHASES:
        logger.warning(f"Unknown phase: {phase_number}")
        return {}
    
    logger.info(f"Validating phase {phase_number}: {PHASES[phase_number]}")
    components = get_components_by_phase(phase_number)
    
    if not components:
        logger.info(f"No components found for phase {phase_number}")
        return {}
    
    results = {}
    for component in components:
        results[component] = validate_dependency_chain(component)
    
    return results

def validate_all() -> Dict[float, Dict[str, ComponentValidationResults]]:
    """
    Validate the entire plugin across all phases.
    
    Returns:
        Dict mapping phase numbers to component validation results
    """
    logger.info("Beginning validation of entire plugin")
    results = {}
    
    for phase in sorted(PHASES.keys()):
        results[phase] = validate_phase(phase)
    
    return results

def handle_validation_failure(result: ValidationResult) -> None:
    """
    Log helpful error information for a validation failure.
    
    Args:
        result: The failed validation result
    """
    logger.error(f"Validation failed: {result.message}")
    
    if result.dependency:
        logger.error(f"Component {result.component} failed to work with {result.dependency}")
    
    if 'exception' in result.details:
        logger.error(f"Exception: {result.details['exception']}")
        logger.debug(f"Traceback: {result.details.get('traceback', 'No traceback available')}")
    
    # Log Rick-style advice
    advice = [
        "Have you tried turning it off and on again? *burp* Works 60% of the time, every time.",
        "You know what they say about dependencies, Morty? They're like in-laws. Necessary evil.",
        "This code is broken like the concept of time travel, Morty! It's a paradox!",
        "Looks like you got a real cluster*burp* on your hands. Good luck fixing that one.",
        "Did you actually test this before committing? Amateur hour over here!"
    ]
    
    import random
    logger.info(f"Rick's advice: {random.choice(advice)}")

def format_validation_results(results: Union[ValidationResult, ComponentValidationResults, Dict]) -> str:
    """
    Make validation results human-readable.
    
    Args:
        results: Validation results to format
        
    Returns:
        Formatted string representation
    """
    if isinstance(results, ValidationResult):
        status_symbol = "✅" if results.is_successful() else "❌"
        return f"{status_symbol} {results.component} → {results.dependency}: {results.message}"
    
    elif isinstance(results, ComponentValidationResults):
        lines = [f"Results for {results.component}:"]
        for result in results.results:
            lines.append(f"  {format_validation_results(result)}")
        return "\n".join(lines)
    
    elif isinstance(results, dict):
        lines = []
        for key, value in results.items():
            if isinstance(value, dict):
                lines.append(f"Phase {key}:")
                for component, comp_results in value.items():
                    lines.append(f"  {component}:")
                    formatted = format_validation_results(comp_results).split("\n")
                    lines.extend([f"    {line}" for line in formatted])
            else:
                lines.append(f"{key}: {format_validation_results(value)}")
        return "\n".join(lines)
    
    return str(results)

def log_validation_output(results: Union[ValidationResult, ComponentValidationResults, Dict]) -> None:
    """
    Record validation results to log file.
    
    Args:
        results: Validation results to log
    """
    try:
        logger.info("Validation results summary:")
        
        if isinstance(results, ValidationResult):
            level = logging.INFO if results.is_successful() else logging.ERROR
            logger.log(level, format_validation_results(results))
        
        elif isinstance(results, ComponentValidationResults):
            level = logging.INFO if results.is_successful() else logging.WARNING
            logger.log(level, f"Component {results.component}: " +
                    ("All validations passed" if results.is_successful() else "Some validations failed"))
            
            for result in results.results:
                if not result.is_successful():
                    try:
                        logger.error(f"  Failed: {result.message}")
                    except Exception as e:
                        logger.error(f"Error logging validation failure: {str(e)}")
        
        elif isinstance(results, dict):
            failures = 0
            
            for key, value in results.items():
                if isinstance(value, dict):
                    try:
                        phase_failures = sum(1 for r in value.values() if not r.is_successful())
                        if phase_failures:
                            failures += phase_failures
                            logger.warning(f"Phase {key}: {phase_failures} component(s) failed validation")
                        else:
                            logger.info(f"Phase {key}: All validations passed")
                    except Exception as e:
                        logger.error(f"Error processing phase {key}: {str(e)}")
            
            if failures:
                logger.error(f"Total failures: {failures}")
            else:
                logger.info("All validations passed successfully")
    except Exception as e:
        logger.error(f"Error in log_validation_output: {str(e)}")
        logger.debug(traceback.format_exc())

def console_output(results: Union[ValidationResult, ComponentValidationResults, Dict]) -> str:
    """
    Format validation results for terminal display.
    
    Args:
        results: Validation results to display
        
    Returns:
        Terminal-friendly formatted output
    """
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    
    def colorize(text, color):
        return f"{color}{text}{RESET}"
    
    if isinstance(results, ValidationResult):
        if results.status == ValidationStatus.SUCCESS:
            status = colorize("✅ SUCCESS", GREEN)
        elif results.status == ValidationStatus.FAILURE:
            status = colorize("❌ FAILURE", RED)
        elif results.status == ValidationStatus.WARNING:
            status = colorize("⚠️ WARNING", YELLOW)
        elif results.status == ValidationStatus.ERROR:
            status = colorize("💀 ERROR", RED)
        else:
            status = colorize("⏭️ SKIPPED", BLUE)
            
        return f"{status} {results.component} → {results.dependency}: {results.message}"
    
    elif isinstance(results, ComponentValidationResults):
        if results.is_successful():
            header = colorize(f"Results for {results.component}: ", GREEN) + colorize("ALL PASSED", GREEN)
        else:
            header = colorize(f"Results for {results.component}: ", RED) + colorize("FAILURES DETECTED", RED)
            
        lines = [header]
        for result in results.results:
            lines.append(f"  {console_output(result)}")
        return "\n".join(lines)
    
    elif isinstance(results, dict):
        lines = []
        
        if all(isinstance(v, dict) and all(r.is_successful() for r in v.values() if hasattr(r, 'is_successful')) 
               for v in results.values()):
            lines.append(colorize("ALL VALIDATIONS PASSED SUCCESSFULLY", GREEN))
        else:
            lines.append(colorize("VALIDATION FAILURES DETECTED", RED))
            
        lines.append("")
        
        for key, value in results.items():
            if isinstance(value, dict):
                if all(r.is_successful() for r in value.values() if hasattr(r, 'is_successful')):
                    phase_status = colorize("PASSED", GREEN)
                else:
                    phase_status = colorize("FAILED", RED)
                    
                if key in PHASES:
                    lines.append(f"{BOLD}Phase {key}{RESET} ({PHASES[key]}): {phase_status}")
                else:
                    lines.append(f"{BOLD}Group {key}{RESET}: {phase_status}")
                    
                for component, comp_results in value.items():
                    formatted = console_output(comp_results).split("\n")
                    lines.extend([f"  {line}" for line in formatted])
            else:
                lines.append(console_output(value))
            
            lines.append("")
            
        return "\n".join(lines)
    
    return str(results)

def generate_html_report(results: Dict[float, Dict[str, ComponentValidationResults]]) -> str:
    """
    Create a detailed HTML report of validation results.
    
    Args:
        results: Validation results to include in the report
        
    Returns:
        HTML string containing the report
    """
    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <title>Rick Assistant Validation Report</title>",
        "    <style>",
        "        body { font-family: 'Courier New', monospace; margin: 20px; background: #f0f0f0; }",
        "        h1 { color: #2c3e50; text-align: center; }",
        "        h2 { color: #2980b9; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }",
        "        h3 { color: #16a085; }",
        "        .success { color: #27ae60; }",
        "        .failure { color: #c0392b; }",
        "        .warning { color: #f39c12; }",
        "        .error { color: #e74c3c; }",
        "        .skipped { color: #7f8c8d; }",
        "        .component { margin-bottom: 20px; padding: 15px; background: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }",
        "        .result { margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }",
        "        .result.success { border-color: #27ae60; }",
        "        .result.failure { border-color: #c0392b; }",
        "        .result.warning { border-color: #f39c12; }",
        "        .result.error { border-color: #e74c3c; }",
        "        .result.skipped { border-color: #7f8c8d; }",
        "        .details { font-family: monospace; white-space: pre-wrap; background: #f9f9f9; padding: 10px; }",
        "        .summary { text-align: center; padding: 20px; margin-bottom: 20px; }",
        "        .timestamp { text-align: right; color: #7f8c8d; font-style: italic; }",
        "    </style>",
        "</head>",
        "<body>",
        f"    <h1>Rick Assistant Validation Report</h1>",
        f"    <div class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
        "    <div class='summary'>"
    ]
    
    # Calculate summary statistics
    total_components = 0
    passed_components = 0
    
    for phase_results in results.values():
        for component_result in phase_results.values():
            total_components += 1
            if component_result.is_successful():
                passed_components += 1
    
    success_rate = (passed_components / total_components * 100) if total_components > 0 else 0
    
    if success_rate == 100:
        html.append(f"        <h2 class='success'>All validations passed! ({passed_components}/{total_components})</h2>")
    elif success_rate >= 75:
        html.append(f"        <h2 class='warning'>Most validations passed. ({passed_components}/{total_components}, {success_rate:.1f}%)</h2>")
    else:
        html.append(f"        <h2 class='failure'>Multiple validation failures! ({passed_components}/{total_components}, {success_rate:.1f}%)</h2>")
        
    html.append("    </div>")
    
    # Generate detail sections
    for phase, phase_results in sorted(results.items()):
        phase_name = PHASES.get(phase, f"Phase {phase}")
        html.append(f"    <h2>Phase {phase}: {phase_name}</h2>")
        
        for component, component_results in sorted(phase_results.items(), key=lambda x: x[0]):
            component_class = "success" if component_results.is_successful() else "failure"
            html.append(f"    <div class='component'>")
            html.append(f"        <h3 class='{component_class}'>{component}</h3>")
            
            for result in component_results.results:
                status_class = result.status.name.lower()
                html.append(f"        <div class='result {status_class}'>")
                html.append(f"            <div><strong>Testing:</strong> {result.component} → {result.dependency}</div>")
                html.append(f"            <div><strong>Status:</strong> <span class='{status_class}'>{result.status.name}</span></div>")
                html.append(f"            <div><strong>Message:</strong> {result.message}</div>")
                html.append(f"            <div><strong>Duration:</strong> {result.duration:.4f} seconds</div>")
                
                if result.details:
                    html.append("            <div><strong>Details:</strong></div>")
                    html.append(f"            <pre class='details'>{json.dumps(result.details, indent=2)}</pre>")
                    
                html.append("        </div>")
                
            html.append("    </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

def generate_validation_report(results: Union[Dict, ComponentValidationResults], 
                              format: str = 'text') -> str:
    """
    Creates a detailed validation report in the specified format.
    
    Args:
        results: Validation results to include
        format: Report format ('text', 'html', 'json', 'markdown')
    
    Returns:
        Formatted report as a string
    """
    if format == 'text':
        return format_validation_results(results)
    elif format == 'html':
        return generate_html_report(results)
    elif format == 'json':
        # Convert to JSON-serializable format
        if isinstance(results, ComponentValidationResults):
            return json.dumps(results.to_dict(), indent=2)
        elif isinstance(results, dict):
            json_results = {}
            for phase, components in results.items():
                json_results[str(phase)] = {}
                for component, result in components.items():
                    json_results[str(phase)][component] = result.to_dict()
            return json.dumps(json_results, indent=2)
        else:
            return json.dumps({"error": "Unsupported results type for JSON format"})
    elif format == 'markdown':
        # Create a markdown report
        lines = ["# Rick Assistant Validation Report", ""]
        
        lines.append("## Summary")
        lines.append("")
        
        total_components = 0
        passed_components = 0
        
        for phase_results in results.values():
            for component_result in phase_results.values():
                total_components += 1
                if component_result.is_successful():
                    passed_components += 1
        
        lines.append(f"- **Total Components:** {total_components}")
        lines.append(f"- **Passed Components:** {passed_components}")
        # Fix potential division by zero by calculating success rate only when safe
        if total_components:
            success_rate = passed_components / total_components * 100
            lines.append(f"- **Success Rate:** {success_rate:.1f}%")
        else:
            lines.append("- **Success Rate:** N/A")
        lines.append("")
        
        for phase, phase_results in sorted(results.items()):
            phase_name = PHASES.get(phase, f"Phase {phase}")
            lines.append(f"## Phase {phase}: {phase_name}")
            lines.append("")
            
            for component, component_results in sorted(phase_results.items(), key=lambda x: x[0]):
                status = "✅ PASSED" if component_results.is_successful() else "❌ FAILED"
                lines.append(f"### {component} - {status}")
                lines.append("")
                
                for result in component_results.results:
                    if result.status == ValidationStatus.SUCCESS:
                        status = "✅ SUCCESS"
                    elif result.status == ValidationStatus.FAILURE:
                        status = "❌ FAILURE"
                    elif result.status == ValidationStatus.WARNING:
                        status = "⚠️ WARNING"
                    elif result.status == ValidationStatus.ERROR:
                        status = "💀 ERROR"
                    else:
                        status = "⏭️ SKIPPED"
                        
                    lines.append(f"#### {result.component} → {result.dependency}")
                    lines.append("")
                    lines.append(f"- **Status:** {status}")
                    lines.append(f"- **Message:** {result.message}")
                    lines.append(f"- **Duration:** {result.duration:.4f} seconds")
                    lines.append("")
                    
                    if result.details:
                        lines.append("**Details:**")
                        lines.append("")
                        lines.append("```json")
                        lines.append(json.dumps(result.details, indent=2))
                        lines.append("```")
                        lines.append("")
                        
            lines.append("")
            
        return "\n".join(lines)
    else:
        return f"Unsupported report format: {format}"

# When run directly, provide basic functionality
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rick's Component Validation Engine")
    parser.add_argument('--component', help='Validate a specific component')
    parser.add_argument('--dependency', help='Validate against a specific dependency')
    parser.add_argument('--phase', type=float, help='Validate all components in a phase')
    parser.add_argument('--all', action='store_true', help='Validate all components')
    parser.add_argument('--format', choices=['text', 'html', 'json', 'markdown'],
                        default='text', help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    if args.component and args.dependency:
        result = validate_dependency(args.component, args.dependency)
        output = generate_validation_report(result, args.format)
    elif args.component:
        results = validate_dependency_chain(args.component)
        output = generate_validation_report({0: {args.component: results}}, args.format)
    elif args.phase:
        results = validate_phase(args.phase)
        output = generate_validation_report({args.phase: results}, args.format)
    elif args.all:
        results = validate_all()
        output = generate_validation_report(results, args.format)
    else:
        parser.print_help()
        sys.exit(1)
    
    if args.output:
        # Use our safe file handling functions
        output_path = normalize_path(args.output)
        if not output_path:
            logger.error(f"Invalid output path: {args.output}")
            sys.exit(1)
            
        # Ensure the output path is safe
        if not is_path_within_safe_directories(output_path):
            logger.error(f"Output path is not within safe directories: {args.output}")
            sys.exit(1)
            
        # Ensure the parent directory exists
        parent_dir = ensure_safe_directory(output_path.parent, create=True)
        if not parent_dir:
            logger.error(f"Failed to create parent directory for output: {output_path.parent}")
            sys.exit(1)
            
        # Write the output safely
        if safe_atomic_write(output_path, output):
            print(f"Validation report written to {args.output}")
        else:
            logger.error(f"Failed to write output to {args.output}")
            sys.exit(1)
    else:
        print(output)
