from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union


@dataclass
class DispatchResult:
  status: str = "success"
  provider: str = "default"
  payload: Any = None
  metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerLog:
  worker_id: str
  message: str
  level: str = "INFO"


def clean_payload(payload: Union[Dict[str, Any], str]) -> Union[Dict[str, Any], str]:
  """Sanitizes and normalizes execution payloads."""
  if isinstance(payload, dict):
    return {k: v for k, v in payload.items() if v is not None}
  if isinstance(payload, str):
    return payload.strip()
  return payload


def refine(
    payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
  """Refines execution payloads or state parameters."""
  refined = dict(payload)
  if context:
    refined.update(context)
  return refined


def dispatch(
    payload: Union[Dict[str, Any], str], provider: str = "default", **kwargs: Any
) -> DispatchResult:
  """Dispatches payload to target provider with execution wrapping."""
  cleaned = clean_payload(payload)
  return DispatchResult(
      status="success",
      provider=provider,
      payload=cleaned,
      metadata=kwargs,
  )
