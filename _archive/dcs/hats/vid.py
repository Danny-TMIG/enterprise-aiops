"""VID — video. Frame plan for a target fps/duration."""

from dcs.generate import requirement  # pragma: no cover


def plan_frames(duration_s: float, fps: int) -> list[int]:  # pragma: no cover
    if fps <= 0:  # pragma: no cover
        raise ValueError("fps must be positive")  # pragma: no cover
    return list(range(int(duration_s * fps)))  # pragma: no cover


@requirement(
    id="DCS-VID-001",
    title="2s @ 30fps → 60 frames",
    section="VID.video",
    hats=["VID"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert plan_frames(2.0, 30) == list(range(60))
