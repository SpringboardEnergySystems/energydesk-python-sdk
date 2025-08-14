# notifier.py
from __future__ import annotations
import os, time, json, smtplib, traceback as _tb
from email.message import EmailMessage
from typing import Dict, Any, Iterable, Optional
import requests

def _truncate(s: Optional[str], n: int) -> str:
    if not s: return ""
    return s if len(s) <= n else s[: n - 1] + "…"

class Notifier:
    """Interface the orchestrator will use."""
    def notify_job_failure(self, *, job_id: str, title: str, error: str | Exception,
                           tb: str = "", meta: Dict[str, Any] | None = None) -> None:
        raise NotImplementedError

    def notify_summary(self, *, job_id: str, title: str,
                       summary: str, meta: Dict[str, Any] | None = None) -> None:
        raise NotImplementedError

def build_notifier():
    # Choose what you want enabled. Start with Teams; add Email later.
    try:
        teams = TeamsNotifier()  # needs TEAMS_WEBHOOK_URL
    except Exception:
        teams = None
    try:
        email = EmailNotifier()  # needs SMTP_HOST + ALERT_TO
    except Exception:
        email = None
    # Fallback if neither is configured: a no-op notifier would also be fine.
    return MultiNotifier(*(n for n in (teams, email) if n))


class TeamsNotifier(Notifier):
    """
    Posts a simple MessageCard to a Teams channel via Incoming Webhook.
    Set TEAMS_WEBHOOK_URL in env.
    """
    def __init__(self, webhook_url: Optional[str] = None, timeout: int = 6):
        self.webhook_url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
        self.timeout = timeout
        if not self.webhook_url:
            raise ValueError("TeamsNotifier requires TEAMS_WEBHOOK_URL")

    def _post(self, card: Dict[str, Any]) -> None:
        try:
            requests.post(self.webhook_url, json=card, timeout=self.timeout).raise_for_status()
        except Exception:
            # Never crash the worker because alerts failed; log locally if you want.
            pass

    def notify_job_failure(self, *, job_id: str, title: str, error: str | Exception,
                           tb: str = "", meta: Dict[str, Any] | None = None) -> None:
        err_msg = error if isinstance(error, str) else f"{type(error).__name__}: {error}"
        facts = [
            {"name": "Job ID", "value": str(job_id)},
            {"name": "When (UTC)", "value": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())},
            {"name": "Error", "value": _truncate(str(err_msg), 500)},
        ] + ([{"name": k, "value": _truncate(str(v), 500)} for k, v in (meta or {}).items()] or [])
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Job {job_id} failed",
            "themeColor": "C43131",
            "title": f"{title}",
            "sections": [{
                "facts": facts,
                "text": f"```\n{_truncate(tb, 3000)}\n```" if tb else None,
            }],
        }
        self._post(card)

    def notify_summary(self, *, job_id: str, title: str,
                       summary: str, meta: Dict[str, Any] | None = None) -> None:
        facts = [{"name": "Job ID", "value": str(job_id)}] + \
                ([{"name": k, "value": _truncate(str(v), 500)} for k, v in (meta or {}).items()] or [])
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Job {job_id} summary",
            "themeColor": "0078D4",
            "title": f"📊 {title}",
            "sections": [{
                "facts": facts,
                "text": _truncate(summary, 6000),
            }],
        }
        self._post(card)


class EmailNotifier(Notifier):
    """
    Sends plain-text email. Configure via env:
      SMTP_HOST, SMTP_PORT (opt), SMTP_USER/SMTP_PASS (opt), ALERT_FROM, ALERT_TO (comma list)
    """
    def __init__(self,
                 smtp_host: Optional[str] = None,
                 smtp_port: int = 25,
                 smtp_user: Optional[str] = None,
                 smtp_pass: Optional[str] = None,
                 sender: Optional[str] = None,
                 recipients: Optional[Iterable[str]] = None,
                 use_tls: bool = False):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        if not self.smtp_host:
            raise ValueError("EmailNotifier requires SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", smtp_port))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
        self.use_tls = use_tls or os.getenv("SMTP_USE_TLS", "false").lower() == "true"
        self.sender = sender or os.getenv("ALERT_FROM", "alerts@localhost")
        to_env = os.getenv("ALERT_TO", "")
        self.recipients = list(recipients) if recipients else [x.strip() for x in to_env.split(",") if x.strip()]
        if not self.recipients:
            raise ValueError("EmailNotifier requires ALERT_TO recipients")

    def _send(self, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=8) as s:
                if self.use_tls:
                    s.starttls()
                if self.smtp_user and self.smtp_pass:
                    s.login(self.smtp_user, self.smtp_pass)
                s.send_message(msg)
        except Exception:
            pass

    def notify_job_failure(self, *, job_id: str, title: str, error: str | Exception,
                           tb: str = "", meta: Dict[str, Any] | None = None) -> None:
        err_msg = error if isinstance(error, str) else f"{type(error).__name__}: {error}"
        lines = [
            f"[CRITICAL] {title}",
            f"Job ID: {job_id}",
            f"When (UTC): {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}",
            f"Error: {err_msg}",
        ]
        for k, v in (meta or {}).items():
            lines.append(f"{k}: {v}")
        if tb:
            lines.append("")
            lines.append("Traceback:")
            lines.append(_truncate(tb, 8000))
        self._send(subject=f"[PFE] {title} (job {job_id})", body="\n".join(lines))

    def notify_summary(self, *, job_id: str, title: str,
                       summary: str, meta: Dict[str, Any] | None = None) -> None:
        lines = [title, f"Job ID: {job_id}"]
        for k, v in (meta or {}).items():
            lines.append(f"{k}: {v}")
        lines.append("")
        lines.append(summary)
        self._send(subject=f"[PFE] {title} (job {job_id})", body="\n".join(lines))


class MultiNotifier(Notifier):
    """Fan-out to many notifiers (e.g., Teams + Email)."""
    def __init__(self, *notifiers: Notifier):
        self._n = [n for n in notifiers if n]

    def notify_job_failure(self, **kwargs) -> None:
        for n in self._n:
            try: n.notify_job_failure(**kwargs)
            except Exception: pass

    def notify_summary(self, **kwargs) -> None:
        for n in self._n:
            try: n.notify_summary(**kwargs)
            except Exception: pass
