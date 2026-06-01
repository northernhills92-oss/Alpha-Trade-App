import random


def detect_whale_activity():

    spike = random.choice([
        True,
        False,
        False
    ])

    if spike:
        return "WHALE ACTIVITY DETECTED"

    return "NORMAL"
