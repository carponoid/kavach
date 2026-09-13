import json
import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


DATA_DIR = Path(os.environ.get("APPROVER_DATA_DIR", "/data"))
REQUESTS_FILE = DATA_DIR / "requests.json"


class AccessRequest(BaseModel):
    kid: str
    domain: str
    reason: str | None = None


class Decision(BaseModel):
    decision: str
    duration_seconds: int | None = None


app = FastAPI(title="kavach-approver")


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REQUESTS_FILE.exists():
        REQUESTS_FILE.write_text("[]\n", encoding="utf-8")


def _read_requests() -> list[dict]:
    _ensure_store()
    return json.loads(REQUESTS_FILE.read_text(encoding="utf-8"))


def _write_requests(rows: list[dict]) -> None:
    REQUESTS_FILE.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


@app.on_event("startup")
def _startup() -> None:
    _ensure_store()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def block_page(domain: str = "", kid: str = "") -> str:
    safe_domain = domain or "this site"
    safe_kid = kid or "child"
    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Kavach Approval</title>
    <style>
      body {{ font-family: sans-serif; margin: 0; background: #f3f0e8; color: #222; }}
      main {{ max-width: 42rem; margin: 8vh auto; padding: 2rem; background: #fff; border-radius: 1rem; box-shadow: 0 20px 60px rgba(0,0,0,.08); }}
      h1 {{ margin-top: 0; }}
      button {{ background: #1f5f8b; color: #fff; border: 0; border-radius: .6rem; padding: .9rem 1.2rem; font-size: 1rem; cursor: pointer; }}
      input, textarea {{ width: 100%; margin: .5rem 0 1rem; padding: .8rem; border: 1px solid #c8c1b8; border-radius: .5rem; }}
      .muted {{ color: #666; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Access blocked</h1>
      <p><strong>{safe_domain}</strong> is blocked for <strong>{safe_kid}</strong>.</p>
      <p class=\"muted\">Submit a request and a parent can review it from the Kavach dashboard or automation hooks.</p>
      <form method=\"post\" action=\"/requests\">
        <label>Kid</label>
        <input name=\"kid\" value=\"{safe_kid}\" required>
        <label>Domain</label>
        <input name=\"domain\" value=\"{safe_domain}\" required>
        <label>Reason</label>
        <textarea name=\"reason\" rows=\"4\" placeholder=\"Why do you need access?\"></textarea>
        <button type=\"submit\">Request access</button>
      </form>
    </main>
  </body>
</html>
"""


@app.post("/requests")
async def create_request(
    request: Request,
    kid: str | None = Form(default=None),
    domain: str | None = Form(default=None),
    reason: str | None = Form(default=None),
) -> dict:
    if kid is None or domain is None:
        payload = AccessRequest.model_validate(await request.json())
    else:
        payload = AccessRequest(kid=kid, domain=domain, reason=reason)

    rows = _read_requests()
    entry = {
        "id": str(uuid.uuid4()),
        "kid": payload.kid,
        "domain": payload.domain,
        "reason": payload.reason,
        "created_at": int(time.time()),
        "status": "pending",
    }
    rows.append(entry)
    _write_requests(rows)
    return entry


@app.get("/requests")
def list_requests() -> list[dict]:
    return _read_requests()


@app.post("/requests/{request_id}/decision")
def decide_request(request_id: str, payload: Decision) -> dict:
    rows = _read_requests()
    for row in rows:
        if row["id"] == request_id:
            row["status"] = payload.decision
            row["duration_seconds"] = payload.duration_seconds
            row["decided_at"] = int(time.time())
            _write_requests(rows)
            return row
    raise HTTPException(status_code=404, detail="request not found")