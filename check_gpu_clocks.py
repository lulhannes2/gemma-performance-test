#!/usr/bin/env python3
"""
GPU Clock Speed Monitor
- Shows current vs max GPU clocks
- Detects thermal throttling
- Alerts if underclocking during load
"""

import subprocess
import sys
import time
from datetime import datetime

def get_gpu_info():
    """Get GPU clock speeds and limits"""
    try:
        # Get current clocks
        result = subprocess.run(
            [
                'nvidia-smi',
                '--query-gpu=index,name,clocks.current.graphics,clocks.current.memory,temperature.gpu,power.draw,power.limit,pstate',
                '--format=csv,noheader,nounits'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        lines = result.stdout.strip().split('\n')
        gpus = []
        
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                gpus.append({
                    'index': parts[0],
                    'name': parts[1][:25],
                    'gpu_clock': parts[2],
                    'mem_clock': parts[3],
                    'temp': parts[4],
                    'power_draw': parts[5],
                    'power_limit': parts[6],
                    'pstate': parts[7],  # Performance state (P0=max, P8=min)
                })
        
        return gpus
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_max_clocks():
    """Get max supported GPU clocks"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '-i', '0', '-q'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        max_gpu_clock = None
        max_mem_clock = None
        
        for line in result.stdout.split('\n'):
            if 'Max Clocks' in line:
                # Next lines have the clock info
                continue
            if 'Graphics' in line and 'MHz' in line:
                max_gpu_clock = line.split(':')[-1].strip().split()[0]
            if 'Memory' in line and 'MHz' in line:
                max_mem_clock = line.split(':')[-1].strip().split()[0]
        
        return max_gpu_clock, max_mem_clock
    except:
        return None, None

def main():
    """Main monitoring loop"""
    print("GPU Clock Speed Monitor")
    print("=" * 100)
    print("Press Ctrl+C to exit\n")
    
    max_gpu_clock, max_mem_clock = get_max_clocks()
    print(f"Max GPU Clock: {max_gpu_clock} MHz")
    print(f"Max Memory Clock: {max_mem_clock} MHz")
    print("-" * 100)
    
    try:
        iteration = 0
        while True:
            gpus = get_gpu_info()
            
            if gpus:
                iteration += 1
                print(f"\n[{iteration}] {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'GPU':<4} {'GPU Clock':<15} {'Mem Clock':<15} {'Temp':<8} {'Power':<15} {'P-State':<8} {'Status':<30}")
                print("-" * 100)
                
                for gpu in gpus:
                    try:
                        gpu_clock = int(gpu['gpu_clock'])
                        mem_clock = int(gpu['mem_clock'])
                        temp = int(gpu['temp'])
                        power_draw = gpu['power_draw']
                        power_limit = gpu['power_limit']
                        pstate = gpu['pstate']
                        
                        # Check if underclocked
                        max_clock_int = int(max_gpu_clock) if max_gpu_clock else 0
                        
                        if gpu_clock < max_clock_int * 0.9:
                            if temp > 80:
                                status = "🔴 THERMAL THROTTLE"
                            elif pstate != 'P0':
                                status = f"⚠️ LOW PERF STATE ({pstate})"
                            else:
                                status = "❓ UNDERCLOCKED?"
                        elif pstate == 'P0':
                            status = "✅ FULL BOOST"
                        else:
                            status = f"🟡 {pstate} State"
                        
                        print(
                            f"{gpu['index']:<4} "
                            f"{gpu_clock:>5} / {max_gpu_clock:<5} MHz  "
                            f"{mem_clock:>5} MHz         "
                            f"{temp:>3}°C    "
                            f"{power_draw:>5} / {power_limit:<5} W  "
                            f"{pstate:<8} "
                            f"{status:<30}"
                        )
                    except (ValueError, TypeError) as e:
                        print(f"GPU {gpu['index']}: Parse error - {e}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
