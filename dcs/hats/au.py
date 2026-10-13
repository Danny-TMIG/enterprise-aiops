"""AU — audio. WAV header for PCM 16-bit mono."""

import struct  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def wav_header(n_samples: int, rate: int = 44_100, channels: int = 1, width: int = 2) -> bytes:  # pragma: no cover
    data_size = n_samples * channels * width
    return (  # pragma: no cover
        b"RIFF"
        + struct.pack("<I", 36 + data_size)
        + b"WAVE"
        + b"fmt "
        + struct.pack(
            "<IHHIIHH", 16, 1, channels, rate, rate * channels * width, channels * width, width * 8
        )
        + b"data"
        + struct.pack("<I", data_size)
    )


@requirement(
    id="DCS-AU-001",
    title="WAV header has RIFF/WAVE/fmt/data chunks",
    section="AU.audio",
    hats=["AU"],
    criticality="MUST",
)
def test():  # pragma: no cover
    h = wav_header(1000)
    for marker in (b"RIFF", b"WAVE", b"fmt ", b"data"):
        assert marker in h
