==========================================
PCIe Diagnostic & Fix Attempts
==========================================

[1] Current PCIe Configuration:
---

[2] Checking BIOS PCIe Settings:
---
./diagnose_pcie.sh: line 17: [: too many arguments
Cannot access BIOS via sysfs (may need physical/IPMI access)

[3] Attempting PCIe Link Reset:
---
Trying to reset PCIe slot...
[sudo] password for dgx43019: 
pcilib: sysfs_write: write failed: Operation not permitted
Reset command sent. Waiting for GPU to re-enumerate...
[4] PCIe Status After Reset:
---
        GPU Link Info
            PCIe Generation
                Max                                    : 1
                Current                                : 1
                Device Current                         : 1
                Device Max                             : 5
                Host Max                               : 5
            Link Width
                Max                                    : 16x
                Current                                : 1x
        Bridge Chip
            Type                                       : N/A
            Firmware                                   : N/A
        Replays Since Reset                            : 0
        Replay Number Rollovers                        : 0
        Tx Throughput                                  : N/A
        Rx Throughput                                  : N/A
        Atomic Caps Outbound                           : FETCHADD_32 FETCHADD_64 SWAP_32 SWAP_64 CAS_32 CAS_64 

[5] NVIDIA Driver Info:
---
Tue Nov 10 14:56:23 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.178.04             Driver Version: 580.178.04     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |

[6] Reloading NVIDIA Driver:
---
Attempting graceful driver reload...
        GPU Link Info
            PCIe Generation
                Max                                    : 1
                Current                                : 1
                Device Current                         : 1
                Device Max                             : 5
                Host Max                               : 5
            Link Width
                Max                                    : 16x
                Current                                : 1x
        Bridge Chip
            Type                                       : N/A
            Firmware                                   : N/A
        Replays Since Reset                            : 0
        Replay Number Rollovers                        : 0
        Tx Throughput                                  : N/A
        Rx Throughput                                  : N/A
        Atomic Caps Outbound                           : FETCHADD_32 FETCHADD_64 SWAP_32 SWAP_64 CAS_32 CAS_64 

==========================================
Diagnosis Complete
==========================================

If link is still 1x, you likely need:
  1. Physical access to re-seat GPU in slot
  2. BIOS reset (need IPMI or physical console)
  3. Check if slot is configured for x1 in BIOS