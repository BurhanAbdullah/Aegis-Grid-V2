import sys
import importlib

# Alias aegis_v2 -> aegis_grid_v2 (runtime only)
if "aegis_v2" not in sys.modules:
    try:
        sys.modules["aegis_v2"] = importlib.import_module("aegis_grid_v2")
    except Exception:
        pass
