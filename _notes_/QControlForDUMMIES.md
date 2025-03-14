# Rick Assistant ZSH Plugin - Code Quality Check Prompts

## Overview

This document contains GitHub Copilot prompts specifically for performing code quality checks at key points during the development of the Rick Sanchez-themed AI assistant ZSH plugin. These prompts are designed to ensure the codebase adheres to Python best practices, maintains consistency, and avoids common pitfalls.

## When to Perform Code Quality Checks

For a project of this complexity, I recommend code quality checks at these strategic points:

1. **First Check**: After completing Phase 1 (Core Foundation)
   - This ensures the foundation is solid before building additional functionality
   - Catches structural issues early when they're easier to fix

2. **Second Check**: After completing Phase 3 (Enhanced User Interface & Experience)
   - This verifies that UI integration doesn't introduce performance or compatibility issues
   - Ensures growing complexity remains manageable

3. **Third Check**: After completing Phase 5 (Content Features & Media Handling)
   - Validates that media processing components meet performance standards
   - Ensures the codebase remains coherent as complexity increases

4. **Final Check**: After completing Phase 7 (Advanced Features & Polish)
   - Comprehensive review of the entire codebase
   - Ensures final product meets all quality standards

## Critical Instruction for All Code Quality Check Prompts

**IMPORTANT: For ALL prompts below, you MUST follow this workflow:**
1. First, understand the requirements and explain your approach
2. Present a detailed plan of what files you'll analyze and why
3. Outline the specific code quality metrics you'll evaluate
4. **WAIT FOR EXPLICIT CONFIRMATION** before performing the actual analysis
5. Present your findings in a clear, organized manner
6. Provide specific code improvement recommendations with examples
7. Explain how these improvements would benefit the project

**DO NOT PROCEED TO IMPLEMENTATION UNTIL INSTRUCTED TO DO SO.**

## Code Quality Check Prompts

### Check 1: Core Foundation Quality Check (After Phase 1)

```
Perform a comprehensive code quality check on the current Rick Assistant ZSH plugin foundation.

IMPORTANT: DO NOT IMPLEMENT ANY CHANGES YET. First, analyze the codebase and present a detailed plan:
1. What files you'll analyze (focus on core modules, utils, and test files)
2. What quality metrics you'll evaluate
3. How you'll prioritize issues
4. Any potential major concerns based on initial review
5. In case you cannot find required files for accurate assessment, tell me which additional files you need to see, and which files I can remove from currently shared.

Wait for explicit confirmation before proceeding with the detailed analysis.

Requirements:
1. Evaluate the foundational structure for:
   - Package organization and import structure
   - Proper use of __init__.py files
   - Circular dependency risks
   - Path handling consistency
   - ZSH compatibility concerns

2. Analyze Python style and standards compliance:
   - PEP 8 adherence (indentation, line length, naming conventions)
   - Docstring completeness (all functions, classes, modules)
   - Type hint accuracy and coverage
   - Comment quality and appropriate density
   - Consistent code style across modules

3. Scrutinize error handling:
   - Try/except block usage and specificity
   - Error recovery mechanisms
   - Graceful failure modes
   - Appropriate error messages
   - Logging implementation

4. Assess test quality:
   - Test coverage for critical functions
   - Assertion quality and specificity
   - Test isolation and independence
   - Fixture usage and organization
   - Error case testing

5. Review for security and robustness:
   - Shell injection vulnerabilities
   - File permission issues
   - Path traversal risks
   - Safe configuration handling
   - Secure default settings

Focus on identifying structural issues that would be costly to fix later.
Prioritize issues that affect the architectural integrity over minor style issues.

After analysis, provide:
1. A summary of the overall code quality
2. Top 5 critical issues requiring immediate attention
3. Specific recommendations with code examples
4. A list of positive patterns to continue using

After planning, wait for confirmation before proceeding with the comprehensive analysis.
After analysis, provide your findings in a clear, actionable format.
```

### Check 2: User Interface Integration Quality Check (After Phase 3)

```
Perform a focused code quality check on the Rick Assistant ZSH plugin UI components after Phase 3.

IMPORTANT: DO NOT IMPLEMENT ANY CHANGES YET. First, analyze the codebase and present a detailed plan:
1. What UI-related files you'll analyze
2. What specific UI quality metrics you'll evaluate
3. How you'll assess performance impact
4. Any potential terminal compatibility concerns
5. In case you cannot find required files for accurate assessment, tell me which additional files you need to see, and which files I can remove from currently shared.

Wait for explicit confirmation before proceeding with the detailed analysis.

Requirements:
1. Evaluate the UI components for:
   - Terminal compatibility (different terminals and sizes)
   - Performance optimization (render time, CPU usage)
   - Visual consistency and Rick theming
   - Graceful degradation in limited environments
   - Responsiveness and refresh rate

2. Analyze the prompt formatting for:
   - ANSI color code usage and best practices
   - Character escaping for special symbols
   - Width calculation and wrapping logic
   - Update frequency and optimization
   - ZSH prompt compatibility

3. Scrutinize the animation system:
   - Frame rate control
   - Resource efficiency
   - Terminal clearing techniques
   - Animation interrupt handling
   - Compatibility with various terminals

4. Assess input handling:
   - Key capture implementation
   - Terminal state management
   - Raw mode safety
   - Input buffering
   - Special key handling

5. Review menu implementation:
   - Navigation logic
   - Selection handling
   - Rendering efficiency
   - State management
   - Exit and recovery

Focus on identifying UI issues that would impact user experience.
Prioritize terminal compatibility and performance concerns.

After analysis, provide:
1. A summary of overall UI code quality
2. Top 5 critical UI issues requiring attention
3. Specific optimization recommendations with code examples
4. Terminal compatibility improvement suggestions

After planning, wait for confirmation before proceeding with the comprehensive analysis.
After analysis, provide your findings in a clear, actionable format with code examples.
```

### Check 3: Media Processing Quality Check (After Phase 5)

```
Conduct a specialized code quality check on the Rick Assistant ZSH plugin's media processing components after Phase 5.

IMPORTANT: DO NOT IMPLEMENT ANY CHANGES YET. First, analyze the codebase and present a detailed plan:
1. What media-related files you'll analyze
2. What specific performance metrics you'll evaluate
3. How you'll assess resource utilization
4. Any potential compatibility or dependency concerns
5. In case you cannot find required files for accurate assessment, tell me which additional files you need to see, and which files I can remove from currently shared.

Wait for explicit confirmation before proceeding with the detailed analysis.

Requirements:
1. Evaluate the media analysis module for:
   - Efficient use of mediainfo
   - Robust error handling for corrupted files
   - Output parsing efficiency
   - Memory management for large files
   - Subprocess management

2. Analyze the ASCII art and animation system for:
   - Rendering algorithm efficiency
   - Frame buffering implementation
   - Terminal capability detection
   - Memory usage over time
   - Cleanup on interruption

3. Scrutinize the ASCII video player for:
   - Frame extraction optimization
   - Frame conversion efficiency
   - Playback timing accuracy
   - Resource cleanup
   - External dependency handling

4. Assess message storage system for:
   - JSON handling efficiency
   - Message retrieval optimization
   - Category structure optimization
   - Memory footprint
   - Load/save performance

5. Review enhanced menu system for:
   - Animation performance
   - Interaction responsiveness
   - Memory leaks during extended use
   - Clean state transitions
   - Resource utilization

Focus on identifying optimization opportunities for media-heavy components.
Prioritize issues that affect performance or resource utilization.

After analysis, provide:
1. A summary of overall media processing code quality
2. Top 5 critical performance issues requiring attention
3. Specific optimization recommendations with profiling data
4. Resource utilization improvement suggestions with code examples

After planning, wait for confirmation before proceeding with the comprehensive analysis.
After analysis, provide your findings in a clear, actionable format with benchmarks and code examples.
```

### Check 4: Comprehensive Final Quality Check (After Phase 7)

```
Perform a final comprehensive code quality check on the complete Rick Assistant ZSH plugin.

IMPORTANT: DO NOT IMPLEMENT ANY CHANGES YET. First, analyze the codebase and present a detailed plan:
1. What major component areas you'll analyze
2. What integrated quality metrics you'll evaluate
3. How you'll assess the system as a whole
4. Any potential long-term maintenance concerns
5. In case you cannot find required files for accurate assessment, tell me which additional files you need to see, and which files I can remove from currently shared.

Wait for explicit confirmation before proceeding with the detailed analysis.

Requirements:
1. Perform a whole-system evaluation:
   - Overall architecture coherence
   - Component integration quality
   - Consistent coding patterns
   - Documentation completeness
   - Test coverage across components

2. Conduct a maintainability assessment:
   - Code complexity metrics (cyclomatic complexity)
   - Module coupling and cohesion
   - Consistent naming and structure
   - Comments and self-documenting code
   - Extensibility for future features

3. Execute a comprehensive performance analysis:
   - Startup time optimization
   - Memory usage profiling
   - CPU usage during normal operation
   - Latency for critical operations
   - Resource cleanup and management

4. Complete a security audit:
   - Input validation comprehensiveness
   - Command injection prevention
   - API key handling security
   - Sensitive data management
   - Authorization checks

5. Evaluate user experience coherence:
   - Consistent Rick personality throughout
   - Error message helpfulness
   - Command suggestion usefulness
   - Menu navigation intuition
   - Prompt readability and information density

Focus on assessing the plugin as a complete system rather than individual components.
Prioritize issues that affect maintainability, stability, and user experience.

After analysis, provide:
1. A comprehensive quality assessment summary
2. Top 10 issues requiring attention before release
3. Key strengths of the current implementation
4. Suggestions for future improvements beyond current scope
5. Specific code examples for critical fixes

After planning, wait for confirmation before proceeding with the comprehensive analysis.
After analysis, provide your findings in a clear, actionable format with prioritized recommendations.
```

## Code Quality Metrics Checklist

For each code quality check, evaluate these specific metrics:

### 1. Code Style & Documentation
- [ ] PEP 8 compliance
- [ ] Consistent naming conventions
- [ ] Complete docstrings (modules, classes, functions)
- [ ] Appropriate comments
- [ ] Type hints usage and accuracy

### 2. Architecture & Structure
- [ ] Proper module organization
- [ ] Appropriate class hierarchies
- [ ] Interface consistency
- [ ] Dependency management
- [ ] Configuration structure

### 3. Error Handling & Robustness
- [ ] Appropriate exception handling
- [ ] Graceful failure modes
- [ ] Input validation
- [ ] Edge case handling
- [ ] Fallback implementations

### 4. Performance & Resources
- [ ] Algorithm efficiency
- [ ] Memory usage
- [ ] I/O optimization
- [ ] Caching strategy
- [ ] Terminal impact

### 5. Security & Safety
- [ ] Command injection prevention
- [ ] Path traversal protection
- [ ] Secure credential handling
- [ ] Appropriate permissions
- [ ] Safe defaults

### 6. Testing
- [ ] Test coverage
- [ ] Edge case testing
- [ ] Mock usage appropriateness
- [ ] Test isolation
- [ ] Fixture quality

## Implementation Guidelines

For each code quality check:

1. **Start with broad analysis**
   - Run automated tools first (pylint, flake8, mypy)
   - Review package structure and dependency flows
   - Identify high-level architectural concerns

2. **Focus on critical components**
   - Prioritize components with security implications
   - Examine terminal interaction code closely
   - Review AI integration points carefully
   - Analyze performance-critical sections

3. **Look for specific anti-patterns**
   - Global state misuse
   - Circular dependencies
   - Unsafe file operations
   - Unhandled exceptions in critical paths
   - Terminal state corruption risks

4. **Recommend practical improvements**
   - Provide concrete code examples
   - Suggest specific refactoring approaches
   - Prioritize fixes by impact vs. effort
   - Consider ZSH compatibility constraints

After each quality check:
- Document findings in a structured report
- Prioritize issues from critical to minor
- Include both specific fixes and general recommendations
- Create actionable tickets for follow-up
- Verify that Rick's personality is maintained throughout recommendations