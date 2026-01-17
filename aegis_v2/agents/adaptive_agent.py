import random
import time

class AegisAgentV2:
    def __init__(self):
        self.attack_pressure = 0.0
        self.is_locked = False

    def monitor_traffic(self, packet_count, expected_rate):
        # DDoS Detection Logic
        if packet_count > (expected_rate * 2):
            self.attack_pressure += 0.2
            print(f"[ALARM] High Traffic Detected. Pressure: {self.attack_pressure:.2f}")
        
        if self.attack_pressure >= 1.0:
            self.is_locked = True
            return "TERMINAL_LOCKOUT"
        return "STABLE"

    def inject_dummies(self):
        # Shannon Entropy Mirroring: Generate noise to hide actual communication
        dummy_data = bytes([random.getrandbits(8) for _ in range(16)])
        return dummy_data.hex()
