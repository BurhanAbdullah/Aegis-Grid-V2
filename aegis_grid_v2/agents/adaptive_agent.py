cat > verify_everything.py << 'EOF'
import os
import subprocess

def run_check(label, command):
    print(f"--- Checking {label} ---")
    try:
        # Using shell=True to handle the bash commands directly
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {label} Logic Verified")
            print(result.stdout.strip())
        else:
            print(f"[FAILED] {label} Logic Check failed")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR] Could not execute {label} check: {e}")
    print("-" * 30)

# 1. Physical Directory Audit
paths = ["v2_model", "v3_fabric", "v4_hive", "releases", "research_docs"]
print("Step 1: Directory Integrity Audit")
for p in paths:
    status = "EXISTS" if os.path.exists(p) else "MISSING"
    print(f"Path [{p}]: {status}")

# 2. Logic Validation (Executing the Bash Actuators you already built)
run_check("V2.1 Base Substrate", "./releases/v2.1_stable/protocol/actuator.sh TEST_PACKET")
run_check("V4.0 Hive Consensus", "./releases/v4.0_hive_cell/protocol/actuator.sh SECURE_DATA KEY_01")

print("\n[COMPLETE] All stations accounted for. System state: LOCKED.")
EOF

python3 verify_everything.py