memory = {}

def save_state(key, value):
    memory[key] = value

def get_state(key):
    return memory.get(key)