from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, Optional

from energydeskapi.collector.models import JobMessage, JobSchedule

if TYPE_CHECKING:
    from energydeskapi.collector.sinks import SinkBundle

# Second arg defaults to SinkBundle() so handlers that ignore it need no change.
JobHandler = Callable[["JobMessage", "SinkBundle"], Awaitable[dict]]

@dataclass(frozen=True)
class JobDef:
    job_type: str
    source: str
    handler: JobHandler
    schedule: Optional[JobSchedule] = field(default=None)

_REGISTRY: Dict[str, JobDef] = {}

def register(job: JobDef) -> None:
    _REGISTRY[job.job_type] = job

def get(job_type: str) -> JobDef:
    if job_type not in _REGISTRY:
        return None
    return _REGISTRY[job_type]

def list_job_types() -> List[str]:
    return sorted(_REGISTRY.keys())
