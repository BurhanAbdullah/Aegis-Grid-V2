import json
import platform
import time


def write_signature():

    data = {

        "timestamp": time.time(),
        "python": platform.python_version(),
        "platform": platform.platform()

    }

    with open("experiments/metadata/run_signature.json", "w") as f:

        json.dump(data, f, indent=2)
