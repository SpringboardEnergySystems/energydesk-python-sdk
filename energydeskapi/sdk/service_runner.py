import os

import uvicorn


def run_uvicorn(app, port: int, host: str = "0.0.0.0", **kwargs):
    """Runs a FastAPI app under uvicorn with logging wired into the root
    logger instead of uvicorn's own stdout-only handlers.

    `log_config=None` stops uvicorn installing its own handlers, so
    `uvicorn`/`uvicorn.access`/`uvicorn.error` propagate to root and go
    through whatever `setup_service_logging()` configured (console, file,
    Logstash) — including uvicorn access logs, which otherwise never leave
    the pod's stdout.

    `forwarded_allow_ips` defaults to `*` so `client_addr` on the access log
    reflects the real client IP behind the ingress rather than the ingress
    pod's IP; restrict via `FORWARDED_ALLOW_IPS` if the service is also
    reachable without going through the ingress.
    """
    kwargs.setdefault("log_config", None)
    kwargs.setdefault("forwarded_allow_ips", os.environ.get("FORWARDED_ALLOW_IPS", "*"))
    kwargs.setdefault("proxy_headers", True)
    uvicorn.run(app, host=host, port=port, **kwargs)
