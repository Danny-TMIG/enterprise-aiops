"""
GOV-KRN-001: Governance Object Model and Registry
"""
class GovernanceRegistry:
    def __init__(self):
        self.objects = {}

    def register_object(self, object_id: str, obj_data: dict) -> bool:
        if object_id in self.objects:
            return False
        self.objects[object_id] = obj_data
        return True

    def get_object(self, object_id: str) -> dict:
        return self.objects.get(object_id, {})
