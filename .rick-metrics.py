#!/usr/bin/env python3
"""
Rick Assistant Metrics Script - WSL Safe Version
Collects system metrics in a way that's compatible with WSL environments
"""

import sys
import os
import time

def get_safe_metrics():
    """Get system metrics in a WSL-safe way with multiple fallback mechanisms"""
    try:
        # Try to use psutil first (most reliable)
        import psutil
        
        # Get CPU usage with a small interval to ensure fresh data
        cpu = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        
        return f"CPU:{cpu:.1f}% RAM:{ram_percent:.1f}%"
    
    except ImportError:
        # If psutil is not available, try using /proc filesystem (Linux-specific)
        try:
            # CPU load from /proc/loadavg
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
            
            # Memory info from /proc/meminfo
            mem_info = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    key, value = line.split(':', 1)
                    mem_info[key.strip()] = value.strip()
            
            total_mem = int(mem_info['MemTotal'].split()[0])
            free_mem = int(mem_info['MemFree'].split()[0])
            buffers = int(mem_info.get('Buffers', '0').split()[0])
            cached = int(mem_info.get('Cached', '0').split()[0])
            
            used_mem = total_mem - free_mem - buffers - cached
            mem_percent = (used_mem / total_mem) * 100
            
            return f"Load:{load:.2f} RAM:{mem_percent:.1f}%"
        
        except Exception as e:
            # Last resort fallback using external commands
            try:
                # Try using external commands
                import subprocess
                
                # Get CPU load using uptime
                uptime_output = subprocess.check_output(['uptime'], text=True)
                load_parts = uptime_output.split('load average:')[1].strip().split(',')
                load = float(load_parts[0])
                
                # Get memory using free
                free_output = subprocess.check_output(['free'], text=True)
                lines = free_output.strip().split('\n')
                mem_line = lines[1].split()
                total = float(mem_line[1])
                used = float(mem_line[2])
                mem_percent = (used / total) * 100
                
                return f"Load:{load:.2f} RAM:{mem_percent:.1f}%"
            
            except Exception:
                # Ultimate fallback - just return a Rick-style message
                return "🧪 Wubba Lubba Dub Dub!"

if __name__ == "__main__":
    try:
        metrics = get_safe_metrics()
        print(metrics)
    except Exception as e:
        # Absolutely fail-safe output
        print("🧪 *burp*")
        # Optionally log the error if debug is enabled
        if os.environ.get('RICK_P10K_DEBUG') == 'true':
            sys.stderr.write(f"[RICK_METRICS_ERROR] {str(e)}\n")
        sys.exit(1) 