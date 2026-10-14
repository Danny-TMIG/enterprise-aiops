from app.dispatchpatch.evidence.base import DispatchEvidence


class NovaFabricEvidence(DispatchEvidence):
    def validate(self) -> bool:
        return super().validate() and "novafabric" in self.payload
