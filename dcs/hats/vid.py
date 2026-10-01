"""VID — video. Frame plan for a target fps/duration."""

from dcs.generate import requirement


def plan_frames(duration_s: float, fps: int) -> list[int]:
    if fps <= 0:
        raise ValueError("fps must be positive")
    return list(range(int(duration_s * fps)))


@requirement(
    id="DCS-VID-001",
    title="2s @ 30fps → 60 frames",
    section="VID.video",
    hats=["VID"],
    criticality="MUST",
)
def test():
    assert plan_frames(2.0, 30) == list(range(60))
