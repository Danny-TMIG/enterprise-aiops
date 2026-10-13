class Object:
    def __init__(self, name: str, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

class Morphism:
    def __init__(self, source: Object, target: Object, name: str, **kwargs):
        self.source = source
        self.target = target
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

class Category:
    def __init__(self, **kwargs):
        self.objects = []
        self.morphisms = []
        for k, v in kwargs.items():
            setattr(self, k, v)

class Diagram:
    def __init__(self, category: Category, **kwargs):
        self.category = category
        for k, v in kwargs.items():
            setattr(self, k, v)
