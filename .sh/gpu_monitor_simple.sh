#!/bin/bash

echo "GPU Clock Monitor - Running nvidia-smi dmon"
echo "Shows: GPU, Power (W), Temp (C), Mem Temp (C), SM%, MEM%, Clock MHz"
echo "=================================================================="
echo ""

nvidia-smi dmon -s pucvmet
