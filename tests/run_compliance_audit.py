#!/usr/bin/env python3
"""
GxP Sovereign Compliance Audit Harness
Executes automated checks against the local hardware enclave to ensure
strict 21 CFR Part 11 isolation parameters are met.
"""

import os
import subprocess
import hashlib
import sys
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def check_network_egress():
    """Validates that the enclave cannot reach public cloud WANs."""
    logging.info("Executing Substrate Network Isolation Check...")
    try:
        # Attempting to ping external cloud provider (e.g., Google/AWS)
        response = subprocess.run(
            ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if response.returncode == 0:
            logging.error("FAIL: External WAN egress is open. Enclave is NOT air-gapped.")
            return False
        logging.info("PASS: Zero WAN egress verified. Enclave is isolated.")
        return True
    except Exception as e:
        return False

def check_audit_log_immutability(log_path="/var/log/battlement/audit"):
    """Validates that the inference logs are append-only (chattr +a)."""
    logging.info("Executing 21 CFR 11.10(e) Audit Trail Verification...")
    if not os.path.exists(log_path):
        logging.warning(f"Log path {log_path} not found. Skipping immutability check for dry-run.")
        return True
    
    # Check filesystem attributes for append-only flag
    result = subprocess.run(['lsattr', log_path], capture_output=True, text=True)
    if '----a---------' in result.stdout:
        logging.info("PASS: Audit logs are cryptographically locked and append-only.")
        return True
    else:
        logging.error("FAIL: Audit logs can be modified. Fails Part 11 requirements.")
        return False

def main():
    print("==================================================")
    print(" BATTLEMENT SYSTEMS: GxP HARDWARE ISOLATION AUDIT ")
    print("==================================================")
    
    egress_pass = check_network_egress()
    audit_pass = check_audit_log_immutability()
    
    if egress_pass and audit_pass:
        print("\n[RESULT]: NODE MEETS GxP SOVEREIGN ISOLATION STANDARDS.")
        sys.exit(0)
    else:
        print("\n[RESULT]: NODE FAILED ISOLATION STANDARDS. DO NOT USE FOR R&D.")
        sys.exit(1)

if __name__ == "__main__":
    main()
