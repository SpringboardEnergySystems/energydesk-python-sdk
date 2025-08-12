from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import time
from redis.client import StrictRedis

def summarize_failures(
    failures: List[Dict[str, Any]],
    top_n_types: int = 5,
    sample_per_type: int = 5,
    max_trace_chars: int = 300,
) -> Dict[str, Any]:
    """
    Turn a list of cpactor failure events into a compact summary for notifications/logs.

    Each failure dict may contain: 'job_id', 'error_type', 'error_msg', 'traceback', 'params_hash', 'attempt'
    The function is defensive against missing keys.
    """
    total = len(failures)
    by_type_bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for f in failures:
        et = (f.get("error_type") or "UnknownError").strip() or "UnknownError"
        by_type_bucket[et].append(f)

    # Rank error types by frequency
    counts = [(et, len(items)) for et, items in by_type_bucket.items()]
    counts.sort(key=lambda x: x[1], reverse=True)

    # Build per-type samples
    top_types = []
    for et, cnt in counts[:top_n_types]:
        items = by_type_bucket[et]
        # pick a few distinct job_ids
        job_ids = []
        msgs = []
        for it in items:
            job_id = str(it.get("job_id", "unknown"))
            msg = str(it.get("error_msg", "")).strip() or "(no message)"
            tb = (it.get("traceback") or "")[:max_trace_chars]
            if job_id not in job_ids and len(job_ids) < sample_per_type:
                job_ids.append(job_id)
            if msg not in msgs and len(msgs) < sample_per_type:
                msgs.append(msg if not tb else f"{msg}\nTB: {tb}")
        top_types.append({
            "error_type": et,
            "count": cnt,
            "sample_job_ids": job_ids,
            "example_messages": msgs,
        })

    # High-level digest line
    unique_job_ids = len({str(f.get("job_id", "unknown")) for f in failures})
    common = ", ".join([f"{et}×{cnt}" for et, cnt in counts[:3]])
    digest = (
        f"{total} failures across {unique_job_ids} jobs"
        + (f" — top: {common}" if common else "")
    )

    return {
        "total": total,
        "unique_job_ids": unique_job_ids,
        "by_type": top_types,
        "digest": digest,
        # Flatten a short text block you can drop straight into a Teams/email body:
        "human_text": _format_human_text(digest, top_types)
    }


def _format_human_text(digest: str, by_type: List[Dict[str, Any]]) -> str:
    lines = [f"**{digest}**"]
    for t in by_type:
        head = f"- {t['error_type']}: {t['count']} failure(s)"
        samples = []
        if t.get("sample_job_ids"):
            samples.append(f"job_ids: {', '.join(map(str, t['sample_job_ids']))}")
        if t.get("example_messages"):
            # include only first 1–2 example messages for brevity
            ex = t["example_messages"][:2]
            samples.append("examples: " + " | ".join(ex))
        if samples:
            head += f" ({'; '.join(samples)})"
        lines.append(head)
    return "\n".join(lines) if len(lines) > 1 else lines[0]

def should_send_alert(
    r: StrictRedis,
    key: str,
    ttl_seconds: int = 900,
    *,
    now: int | None = None,
) -> bool:
    """
    Soft rate-limiter / de-duper using Redis. Returns True if we should send,
    and sets a TTL marker so repeats within ttl_seconds return False.

    Implementation uses SET NX EX for atomicity. If Redis is unavailable,
    returns True 
    """
    try:
        # Use current epoch seconds as value
        value = str(int(now if now is not None else time.time()))
        # name=<key>, NX=create only if not exists, EX=expire
        return bool(r.set(name=key, value=value, nx=True, ex=ttl_seconds))
    except Exception:
        # If Redis is down or misconfigured, don't suppress alerts.
        return True
