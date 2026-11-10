#!/usr/bin/env python3
"""
GPU Monitor Daemon
- Displays real-time GPU stats
- Updates every 2 seconds
- Shows memory, utilization, temperature
- Runs in separate terminal
"""

import subprocess
import sys
from datetime import datetime
import time

def get_gpu_stats():
    """Parse nvidia-smi output into readable format"""
    try:
        result = subprocess.run(
            [
                'nvidia-smi',
                '--query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu',
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
            if len(parts) >= 7:
                gpus.append({
                    'index': parts[0],
                    'name': parts[1][:30],  # Truncate name
                    'util': parts[2],
                    'mem_util': parts[3],
                    'mem_used': parts[4],
                    'mem_total': parts[5],
                    'temp': parts[6],
                })
        
        return gpus
    except Exception as e:
        print(f"Error querying GPU: {e}")
        return None

def clear_screen():
    """Clear terminal"""
    subprocess.run(['clear'], check=False)

def print_header():
    """Print table header"""
    print("=" * 120)
    print(f"GPU Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)
    print(f"{'GPU':<4} {'Name':<30} {'Util %':<10} {'Mem Util %':<12} {'Mem Used':<15} {'Temp °C':<10}")
    print("-" * 120)

def print_gpu_stats(gpus):
    """Print GPU stats in table format"""
    if not gpus:
        print("No GPU data available")
        return
    
    for gpu in gpus:
        try:
            util = float(gpu['util'])
            mem_util = float(gpu['mem_util'])
            mem_used = float(gpu['mem_used'])
            mem_total = float(gpu['mem_total'])
            temp = float(gpu['temp'])
            
            # Color coding based on usage
            util_color = "🔴" if util > 80 else "🟡" if util > 50 else "🟢"
            temp_color = "🔴" if temp > 80 else "🟡" if temp > 60 else "🟢"
            
            print(
                f"{gpu['index']:<4} "
                f"{gpu['name']:<30} "
                f"{util_color} {util:>6.1f}%    "
                f"{mem_util:>6.1f}%      "
                f"{mem_used:>6.1f}GB / {mem_total:>6.1f}GB  "
                f"{temp_color} {temp:>6.1f}°C"
            )
        except (ValueError, TypeError):
            print(f"GPU {gpu['index']}: Error parsing stats")

def main():
    """Main monitoring loop"""
    print("Starting GPU Monitor...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            clear_screen()
            print_header()
            
            gpus = get_gpu_stats()
            if gpus:
                print_gpu_stats(gpus)
            else:
                print("Waiting for GPU data...")
            
            print("-" * 120)
            print("🟢 = Good (<50%)  |  🟡 = Caution (50-80%)  |  🔴 = High (>80%)")
            print("Press Ctrl+C to exit")
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\nGPU Monitor stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
