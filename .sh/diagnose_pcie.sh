#!/bin/bash

echo "=========================================="
echo "PCIe Diagnostic & Fix Attempts"
echo "=========================================="
echo ""

# 1. Check current PCIe config
echo "[1] Current PCIe Configuration:"
echo "---"
lspci -vv -s 0000000F:01:00.0 | grep -A 20 "Link Cap\|Link Sta"
echo ""

# 2. Check BIOS settings (if accessible)
echo "[2] Checking BIOS PCIe Settings:"
echo "---"
if [ -r /sys/class/pci_bus/*/device/config ]; then
    echo "BIOS accessible via sysfs"
else
    echo "Cannot access BIOS via sysfs (may need physical/IPMI access)"
fi
echo ""

# 3. Try to reset PCIe link
echo "[3] Attempting PCIe Link Reset:"
echo "---"
echo "Trying to reset PCIe slot..."
sudo setpci -s 0000000F:01:00.0 e5.b=40
sleep 2
echo "Reset command sent. Waiting for GPU to re-enumerate..."
sleep 5

# 4. Check again
echo "[4] PCIe Status After Reset:"
echo "---"
nvidia-smi -i 0 -q | grep -A 10 "PCIe\|Link"
echo ""

# 5. Check NVIDIA driver version
echo "[5] NVIDIA Driver Info:"
echo "---"
nvidia-smi | head -5
echo ""

# 6. Try driver reload
echo "[6] Reloading NVIDIA Driver:"
echo "---"
echo "Attempting graceful driver reload..."
sudo rmmod nvidia_uvm 2>/dev/null
sudo rmmod nvidia 2>/dev/null
sleep 2
sudo modprobe nvidia 2>/dev/null
sleep 5
nvidia-smi -i 0 -q | grep -A 10 "PCIe\|Link"
echo ""

echo "=========================================="
echo "Diagnosis Complete"
echo "=========================================="
echo ""
echo "If link is still 1x, you likely need:"
echo "  1. Physical access to re-seat GPU in slot"
echo "  2. BIOS reset (need IPMI or physical console)"
echo "  3. Check if slot is configured for x1 in BIOS"
echo ""
