import random, os
def create_shuffled_burst(encrypted_data):
    """L4: Hides real data in a burst of 8"""
    burst = [os.urandom(32).hex() for _ in range(7)]
    burst.append(encrypted_data)
    random.shuffle(burst)
    return burst, burst.index(encrypted_data)
