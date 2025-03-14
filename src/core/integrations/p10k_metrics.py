#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Powerlevel10k Metrics Script for Rick Assistant

This script outputs formatted system metrics for use in Powerlevel10k prompt.
It's designed to be called directly from the p10k ZSH integration.
"""

import sys
import os
import random
import argparse

# Define colors directly to avoid dependency issues
COLORS = {
    "green": "green",
    "yellow": "yellow",
    "red": "red",
    "cyan": "cyan",
    "reset": "reset"
}

def format_with_color(text, color, use_colors=True):
    """Format text with p10k color syntax."""
    if not use_colors:
        return text
    return f"%F{{{COLORS.get(color, 'green')}}}{text}%f"

def get_system_metrics(use_colors=True):
    """Get formatted system metrics for p10k prompt."""
    try:
        import psutil
        
        # Get CPU usage with a small interval
        cpu = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        mem = psutil.virtual_memory().percent
        
        # Determine colors based on thresholds
        cpu_color = "green"
        if cpu > 70:
            cpu_color = "red"
        elif cpu > 40:
            cpu_color = "yellow"
            
        mem_color = "green"
        if mem > 70:
            mem_color = "red"
        elif mem > 40:
            mem_color = "yellow"
        
        # Format metrics with colors if enabled
        cpu_text = format_with_color(f"CPU:{cpu:.1f}%", cpu_color, use_colors)
        mem_text = format_with_color(f"MEM:{mem:.1f}%", mem_color, use_colors)
        
        return f"{cpu_text} {mem_text}"
    except ImportError:
        return "psutil not installed"
    except Exception as e:
        return f"Error: {str(e)}"

def get_rick_phrase():
    """Get a random Rick phrase."""
    try:
        # Try to import from Rick Assistant
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from src.core.prompt import get_rick_phrase
        phrase = get_rick_phrase()
        if phrase:
            return phrase
    except:
        pass
    
    # Fallback phrases
    phrases = [
        "🧪 *burp* What now?",
        "🧪 I'm working here, Morty!",
        "🧪 *burp* Science!",
        "🧪 Wubba Lubba Dub Dub!"
    ]
    return random.choice(phrases)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Rick Assistant p10k prompt content')
    parser.add_argument('--plain', action='store_true', 
                        help='Use plain text without color formatting')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug information')
    return parser.parse_args()

def main():
    """Main function to output formatted prompt content."""
    try:
        # Parse command line arguments
        args = parse_args()
        use_colors = not args.plain
        
        # Show debug info if requested
        if args.debug:
            sys.stderr.write(f"Debug: Using colors: {use_colors}\n")
            sys.stderr.write(f"Debug: Python path: {sys.path}\n")
        
        # Get Rick phrase
        rick_phrase = get_rick_phrase()
        
        # Get system metrics if available
        metrics = get_system_metrics(use_colors)
        
        # Combine content
        if rick_phrase and metrics:
            print(f"{rick_phrase} {metrics}")
        elif metrics:
            print(metrics)
        else:
            print(rick_phrase)
            
    except Exception as e:
        # Ensure we don't crash the prompt
        print(f"🧪 Error: {str(e)}")

if __name__ == "__main__":
    main() 