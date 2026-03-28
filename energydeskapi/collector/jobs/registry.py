from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, List, Optional

from energydeskapi.collector.models import JobMessage, JobSchedule

JobHandler = Callable[[JobMessage], Awaitable[dict]]

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
