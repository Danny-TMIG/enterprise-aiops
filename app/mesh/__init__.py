def get_mesh(*args, **kwargs):
    return None

class Node:
    def __init__(self, *args, **kwargs): pass

class MeshGraph:
    def __init__(self, *args, **kwargs): pass

def route(*args, **kwargs):
    def decorator(fn):
        return fn
    return decorator

__all__ = ["get_mesh", "Node", "MeshGraph", "route"]
