# Rick Assistant ZSH Plugin - Code Quality Check Prompts

## Overview

This document contains GitHub Copilot prompts for performing code quality checks at strategic points during the development of the Rick Sanchez-themed AI assistant ZSH plugin. These prompts should be integrated into the main development workflow after completing specific phases.

## Critical Instruction for All Code Quality Check Prompts

**IMPORTANT: For ALL prompts below, you MUST follow this workflow:**
1. First, analyze the codebase and explain your approach
2. Present a detailed plan of what files you'll review and what issues you'll look for
3. Outline the specific quality metrics you'll evaluate
4. **WAIT FOR EXPLICIT CONFIRMATION** before performing the detailed analysis
5. Present your findings in a clear, organized manner
6. Provide specific code improvement recommendations with examples
7. **In case you cannot find required files for accurate assessment, tell me which additional files you need to see, and which files I can remove from currently shared.**

**DO NOT PROCEED TO ANALYSIS UNTIL INSTRUCTED TO DO SO.**

## WSL Compatibility Considerations

For each code quality check, verify these WSL compatibility issues:

1. System Information Module:
   - Graceful fallback when temperature sensors unavailable
   - Correct handling of mounted Windows drives (/mnt/c/, etc.)
   - Alternative methods for CPU/RAM stats when standard Linux tools give inaccurate results
   - Path conversion between Windows and Linux formats when necessary

2. Terminal Integration:
   - Testing in Windows Terminal, VS Code terminal, and other common WSL terminals
   - Verification of ANSI color code support across terminal types
   - Screen clearing and cursor positioning compatible with WSL terminals
   - Animation frame rates adjusted for WSL performance characteristics

3. Process & Performance:
   - Avoid frequent file operations across WSL/Windows boundary
   - Appropriate timeouts for system operations that might be slower in WSL
   - Asynchronous operations that don't block the terminal in WSL's performance profile
   - Resource cleanup compatible with WSL process handling

## Phase 1: Core Foundation Quality Check

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

5. Check WSL compatibility:
   - Path handling for WSL environments
   - Terminal compatibility across Windows and Linux
   - Fallbacks for unavailable system metrics in WSL
   - Appropriate error handling for WSL-specific issues

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

## Phase 3: UI & Experience Quality Check

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

5. Check WSL compatibility:
   - Input handling in Windows Terminal
   - ANSI color support across WSL terminals
   - Animation performance in WSL environment
   - Terminal size detection in WSL
   - Screen clearing and cursor positioning in WSL

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

## Phase 5: Media Processing Quality Check

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

5. Check WSL compatibility:
   - External tools availability in WSL (mediainfo, ffmpeg)
   - Performance of media operations in WSL
   - File path handling for Windows/WSL path conversion
   - Terminal compatibility for media display
   - Process management in WSL environment

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

## Phase 7: Final Code Quality Review

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

5. Evaluate WSL compatibility:
   - Full compatibility across all components
   - Special case handling for WSL-specific behaviors
   - Performance in WSL vs native Linux
   - Installation and configuration issues in WSL
   - Recommended settings for optimal WSL experience

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

## How to Integrate These Quality Checks

Add these code quality check prompts at the end of their respective phase sections in the main plan.md file:

1. Add "1.6: Core Foundation Quality Check" after "1.5: Phase 1 Test Files"
2. Add "3.8: UI & Experience Quality Check" after "3.7: Phase 3 Test Files" 
3. Add "5.8: Media Handling Quality Check" after "5.7: Phase 5 Test Files"
4. Add "7.7: Final Code Quality Review" after "7.6: Final Phase 7 Test Files"

In the "Implementation Guidelines" section, add this note:

```
5. **Run quality checks before advancing phases**
   - Complete thorough code quality reviews at the end of phases 1, 3, 5, and 7
   - Address all critical issues before moving to the next phase
   - Document quality improvements in done.md
   - Update tests to prevent regression of fixed issues
```

## Additional Quality Check Guidance

For the most effective code quality checks:

1. **Focus on patterns, not just instances**: Look for recurring anti-patterns across the codebase.

2. **Prioritize ruthlessly**: Address architectural and security issues first, style issues later.

3. **WSL compatibility is critical**: Always verify that code works in WSL environments, especially for system metrics and terminal interactions.

4. **Look for performance cliffs**: Identify operations that might be fine in small scale but problematic at scale.

5. **Verify Rick's personality**: Ensure code quality doesn't compromise the distinct Rick Sanchez personality throughout the plugin.