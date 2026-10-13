from typing import Any


class DoubleDouble:
  """Represents high-precision double-double arithmetic or state wrapper."""

  def __init__(self, high: float = 0.0, low: float = 0.0):
    self.high = high
    self.low = low

  def __repr__(self) -> str:
    return f"DoubleDouble({self.high}, {self.low})"


def shard(data: list[Any], chunks: int = 2) -> list[list[Any]]:
  """Shards a dataset or payload into chunks."""
  if chunks <= 0 or not data:
    return [data]
  k, m = divmod(len(data), chunks)
  return [
      data[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
      for i in range(chunks)
  ]
