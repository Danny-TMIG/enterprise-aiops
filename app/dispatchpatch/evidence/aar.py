from app.dispatchpatch.evidence.base import DispatchEvidence


class AAREvidence(DispatchEvidence):
    def validate(self) -> bool:
        return super().validate() and "aar" in self.payload
