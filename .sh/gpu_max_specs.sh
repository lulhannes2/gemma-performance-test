#!/bin/bash

echo "========================================================================"
echo "NVIDIA A100 GPU - Maximum Specs & Current Limits"
echo "========================================================================"
echo ""

# Full GPU info
echo "[GPU INFO]"
nvidia-smi -i 0 -q | head -20
echo ""

# Max clocks
echo "========================================================================"
echo "[MAX CLOCK SPEEDS]"
echo "========================================================================"
nvidia-smi -i 0 -q | grep -A 10 "Max Clocks"
echo ""

# Current clock settings
echo "========================================================================"
echo "[CURRENT CLOCK SPEEDS]"
echo "========================================================================"
nvidia-smi -i 0 -q | grep -A 10 "Current Clocks"
echo ""

# Power limits
echo "========================================================================"
echo "[POWER SETTINGS]"
echo "========================================================================"
nvidia-smi -i 0 -q | grep -A 5 "Power Draw\|Power Limit\|Power Warnings"
echo ""

# Thermal settings
echo "========================================================================"
echo "[THERMAL SETTINGS]"
echo "========================================================================"
nvidia-smi -i 0 -q | grep -i "temperature\|thermal\|max temp\|shutdown"
echo ""

# Performance modes
echo "========================================================================"
echo "[PERFORMANCE STATE (P-State)]"
echo "========================================================================"
echo "P0 = Maximum Performance (highest clock)"
echo "P2 = Balance"
echo "P8 = Minimum Performance (lowest clock/power)"
echo ""
nvidia-smi -i 0 -q | grep -A 5 "Clocks Policy\|Driver Model\|Persistence Mode"
echo ""

# GPU Memory
echo "========================================================================"
echo "[MEMORY INFO]"
echo "========================================================================"
nvidia-smi -i 0 -q | grep -A 10 "Memory Usage"
echo ""

# Full detailed query
echo "========================================================================"
echo "[FULL DETAILED INFO]"
echo "========================================================================"
nvidia-smi -i 0 -q
