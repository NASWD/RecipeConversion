
_wafer_map_payload = None

def submit_wafer_map(dies, origin, step, die_type="A"):
    global _wafer_map_payload
    _wafer_map_payload = {
        "dies": dies,
        "origin": origin,
        "step": step,
        "die_type": die_type
    }

def get_wafer_map():
    return _wafer_map_payload
