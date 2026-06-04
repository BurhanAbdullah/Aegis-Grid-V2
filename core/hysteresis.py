JOIN_THRESHOLD = 0.70
LEAVE_THRESHOLD = 0.50

def update_membership(active, trust):
    if not active and trust > JOIN_THRESHOLD:
        return True
    if active and trust < LEAVE_THRESHOLD:
        return False
    return active
