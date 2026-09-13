# Port Registry

> **Single source of truth** for all host-exposed ports across the AIStack on `shambala`.
>
> Every service that binds a port on the host MUST be registered here.
> Pod-internal ports (container-to-container within a pod) are listed
> separately for reference but don't conflict with host ports.

---

## Port Scheme

All host-exposed ports follow the **`2426X`** pattern — derived from
**Feb 2026**, the month the AIStack was born.

```
2426 X
│    └── Service number (1, 2, 3, ... incrementing)
└────── AIStack prefix — February 2026
```

---

## Live Map (verified June 2026)

Legend:
- **active** — process listening right now
- **configured** — systemd unit exists, currently inactive
- **planned** — code/docs exist, never deployed
- **free** — slot available for reuse (previous tenant retired)

| Port | Service | Pod / Process | State | Notes |
|------|---------|----------------|-------|-------|
| **24261** | Dify (nginx entry point) | `dify` pod | **obsolete** | service retired |
| **24262** | MCP Web (SearXNG + Crawl4AI) | `mcp-web` pod | **obsolete** | service retired |
| **24263** | WAHA (WhatsApp HTTP API) | `aistack-bridges` pod (host net) | **obsolete** | service retired |
| **24264** | Vaayaadi WA Bridge | `aistack-bridges` pod (host net) | **obsolete** | service retired |
| **24265** | **Hermes Dashboard** | `hermes-dashboard.service` (mcp-svc user unit) | **active** ✓ | bound `0.0.0.0`; auth gate is bundled `self-hosted` OIDC provider → CF Zero Trust SaaS/OIDC app (single SSO via GitHub) |
| **24266** | Grafana MCP Gateway (SSE) | `mcp-grafana` pod | configured | unit enabled, currently inactive |
| **24267** | Webhook Receiver (ingestion) | `webhook-receiver` pod | planned | not deployed |
| **24268** | _free_ | — | free | used 2026-06-27 for the LiteLLM soak container; previously `mcp-email` |
| **24269** | **LiteLLM Proxy** | `litellm-proxy` container (host network) | **active** ✓ | unified OpenAI-compatible LLM gateway with adaptive routing — see [ADR-014](ADR-014.md). Replaced Bifrost on this port 2026-06-27 |
| **24270** | **Hermes Bridge MCP** | `hermes-bridge.service` (mcp-svc user unit) | **active** ✓ | streamable-http `/mcp`; local `127.0.0.1:24270`, public via CF Access on `mcp-shambala.thepkb.in` |
| **24271** | SearXNG (search) | `searxng` container (publishes 8080→24271) | **active ✓** | standalone metasearch on shambala; former TEI-embedding port — TEI now runs on server.jgk (`jgk-tei`) |
| **24272** | ~~APISIX Gateway (data plane)~~ | — | **obsolete** | APISIX migration abandoned before cutover per [ADR-014](ADR-014.md); slot free |
| **24273** | vLLM Runtime (ROCm) | `vllm-openai` container | **standby** | demoted from primary 2026-06-29 — see [vllm/MODELS-FP8.md](../vllm/MODELS-FP8.md). Configured-but-stopped; reactivate for multi-tenant / FP4 workloads |
| **24274** | llama.cpp Runtime (Vulkan) — via **llama-swap** post-ADR-017 | `llamacpp-server` container (Phase 1 of ADR-017 replaces raw llama-server with llama-swap on same port) | **active ✓ (primary)** | local model serving — current: `Qwen3-Coder-30B-A3B-Instruct-Q5_K_M` (alias `qwen3-coder-30b`); post-ADR-017 also serves `qwen3-thinker-30b` via hot-swap |
| **24275** | **jgk-TEI (bge-m3 embeddings)** | `jgk-tei` container on **server.jgk** | **planned** ([ADR-017](ADR-017.md) Phase 3) | multilingual embeddings incl. Indic; ring-fenced 2G/2G/no-swap; replaces shambala CPU TEI at scale |
| **24276** | **jgk-llama-swap (Gemma3-4B — vision + Indic chat)** | `jgk-llama-swap` container on **server.jgk** | **planned** ([ADR-017](ADR-017.md) Phase 4) | on-demand, 5-min TTL; ring-fenced 5G/5G/no-swap |
| **24277** | **jgk-TEI reranker (bge-reranker-v2-m3)** | `jgk-tei-rerank` container on **server.jgk** | **planned/deferred** ([ADR-017](ADR-017.md) Phase 5) | load-on-demand cross-encoder for RAG re-scoring |
| **24278** | **Kavach — AdGuard Home UI** | `kavach-adguard` container | **planned** ([ADR-019](ADR-019.md)) | admin UI / API only |
| **24279** | **Kavach — Traccar** (location tracking) | `kavach-traccar` container | **planned** ([ADR-019](ADR-019.md)) | GPS server + geofences; OwnTracks/Traccar-Client |
| **24280** | **Kavach — FMD Server** (find/ring/lock) | `kavach-fmd` container | **planned** ([ADR-019](ADR-019.md)) | self-hosted find-my-device, E2E-encrypted |
| **24281** | **Kavach — Headwind MDM** (Android device mgmt) | `kavach-mdm` pod (+ internal PostgreSQL) | **planned** ([ADR-019](ADR-019.md)) | app push/whitelist, kiosk, device-owner provisioning |
| **24282** | **Kavach — Approver** (request-access block page + approve flow) | `kavach-approver` container | **planned** ([ADR-019](ADR-019.md)) | AdGuard Custom-IP block page; parent approves via Telegram/Hermes → per-client allowlist via AdGuard API |
| **24283** | **Kavach — AdGuard DoH origin** | `kavach-adguard` container | **planned** ([ADR-019](ADR-019.md)) | loopback-only HTTPS origin for `dns-kavach.thepkb.in/dns-query` via Cloudflare Tunnel |
| **24284** | **Kavach — Dashboard Portal** | `kavach-dashboard` container | **planned** ([ADR-019](ADR-019.md)) | central launcher at `kavach.thepkb.in` linking all Layer-1 apps |
| **24285–24299** | _free_ | — | free | reserved for future |

---

## Rules

1. **All host ports stay in the `24261–24299` range.** Nothing else.
2. **Sequential assignment** — next service gets the next free number. Free slots above (24268, 24270, 24272+) are reusable.
3. **Register here FIRST, deploy second.** If it's not in this file, it shouldn't be on the host.
4. **Pod-internal ports are free** — containers in the same pod talk via `localhost` on any port. Only host-exposed ports are registered.
5. **No common ports** — never use 3000, 5000, 8000, 8080, 8888, etc. on the host. Those collide with dev tools.

---

## Detailed Assignments

### 24261 — Dify

| | |
|---|---|
| **Pod** | `dify` |
| **Container** | `dify-nginx` |
| **Container port** | 80 |
| **Host port** | **24261** |
| **State** | Configured (unit `aistack-dify.service` disabled) |
| **Cloudflare Tunnel** | `https://dify.thepkb.in` → `http://localhost:24261` |
| **Health check** | `curl http://localhost:24261/health` |

### 24262 — MCP Web (Search & Crawl)

| | |
|---|---|
| **Pod** | `mcp-web` |
| **Container** | `gateway` |
| **Container port** | 8000 |
| **Host port** | **24262** |
| **State** | Configured (unit `aistack-mcp-web.service` disabled) |
| **SSE endpoint** | `http://localhost:24262/sse` |
| **Health check** | `curl http://localhost:24262/health` |

### 24263 — WAHA (WhatsApp HTTP API)

| | |
|---|---|
| **Pod** | `aistack-bridges` (host network) |
| **Container** | `waha` |
| **Host port** | **24263** |
| **State** | Configured (unit `aistack-bridges.service` enabled, currently inactive) |
| **Dashboard** | `http://localhost:24263` |
| **Health check** | `curl http://localhost:24263/api/sessions` |

### 24264 — Vaayaadi WhatsApp Bridge

| | |
|---|---|
| **Pod** | `aistack-bridges` (host network) |
| **Container** | `vaayaadi-bridge` |
| **Host port** | **24264** |
| **State** | Configured (same unit as WAHA) |
| **Health check** | `curl http://localhost:24264/health` |

### 24265 — Hermes Dashboard

| | |
|---|---|
| **Process** | `hermes dashboard` (FastAPI web UI for agent management) |
| **Owner** | `mcp-svc` systemd user unit: `hermes-dashboard.service` |
| **Command** | `hermes dashboard --port 24265 --host 0.0.0.0 --no-open --skip-build` |
| **Bind** | `0.0.0.0:24265` (all interfaces — gate is the bundled OIDC provider, see below) |
| **State** | **Active** ✓ (systemd user unit enabled) |
| **Cloudflare Tunnel** | `https://oc.thepkb.in` → `http://localhost:24265`. **No HTTP Host Header override; no CF Access self-hosted app.** |
| **Public auth** | Bundled `self-hosted` OIDC provider (`plugins/dashboard_auth/self_hosted/`) → **Cloudflare Zero Trust SaaS/OIDC application** `hermes-dashboard`. Same GitHub identity policy as the rest of the platform (single SSO — user is never prompted twice). |
| **Health check** | `curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:24265/` → `302` to `/auth/login?provider=self-hosted&next=%2F` |
| **Features** | Kanban board for task management, agent configuration, API key management, session browsing |
| **Venv** | `/var/lib/mcp-svc/.hermes/hermes-agent/venv/` |

**OIDC config (mcp-svc `.env`):**

```env
HERMES_DASHBOARD_OIDC_ISSUER=https://pkb.cloudflareaccess.com/cdn-cgi/access/sso/oidc/<uuid>
HERMES_DASHBOARD_OIDC_CLIENT_ID=<uuid>
HERMES_DASHBOARD_OIDC_CLIENT_SECRET=<from CF SaaS app>
HERMES_DASHBOARD_OIDC_SCOPES=openid profile email
HERMES_DASHBOARD_PUBLIC_URL=https://oc.thepkb.in
```

**Jun-2026 hardening (post `hermes-0day` MCP-persistence campaign):**

- `--insecure` is a **no-op**. Any non-loopback bind (`--host 0.0.0.0`) refuses to start unless a `DashboardAuthProvider` is registered — the OIDC provider above satisfies that check.
- Loopback binds enforce a hardcoded `Host` allowlist and a matching WS `Origin` guard — that's the trap the old `--host 127.0.0.1 + CF Host override` design fell into (HTTP worked, WS at `/api/events` closed with 4403, dashboard showed "events feed disconnected"). Binding `0.0.0.0` puts `bound_host` outside the loopback set and `_is_accepted_host` accepts any Host/Origin.
- See `skills/pkb-shambala/troubleshooting.md` for the full diagnosis recipe and browser-observable symptoms.

### 24266 — Grafana MCP Gateway

| | |
|---|---|
| **Pod** | `mcp-grafana` |
| **Container** | `gateway` |
| **Container port** | 8000 → 24266 |
| **Host port** | **24266** |
| **State** | Configured (unit `aistack-grafana-mcp.service` enabled, currently inactive) |
| **Transport** | MCP over SSE |
| **SSE endpoint** | `http://localhost:24266/sse` |
| **Config** | `/ai/grafana-mcp/config/env` (host volume, secrets) |
| **Health check** | `curl http://localhost:24266/sse` |

### 24267 — Webhook Receiver (planned)

| | |
|---|---|
| **Pod** | `webhook-receiver` (planned) |
| **Host port** | **24267** |
| **State** | Planned — not deployed |
| **Cloudflare Tunnel** | (planned) `https://hooksonshambala.thepkb.in` → `http://localhost:24267` |
| **Source** | `ingestion/webhook/` |

### 24269 — LiteLLM Proxy

| | |
|---|---|
| **Container** | `litellm-proxy` (host network, no pod) |
| **Image** | `localhost/litellm-proxy:latest` (built from `ghcr.io/berriai/litellm:main-latest`) |
| **Host port** | **24269** |
| **State** | **Active** ✓ (unit `aistack-litellm.service` enabled) |
| **API base** | `http://localhost:24269/v1` |
| **Wiki** | [LiteLLM](LiteLLM.md) |
| **Health check** | `curl http://localhost:24269/health/liveliness` |
| **Decision** | [ADR-014](ADR-014.md) — resurrected with adaptive routing |
| **Predecessor** | Bifrost (retired 2026-06-27, rollback preserved — see [Bifrost](Bifrost.md)) |

### 24270 — Hermes Bridge MCP

| | |
|---|---|
| **Process** | `python server.py` (FastMCP, streamable-http) |
| **Owner** | `mcp-svc` user unit `hermes-bridge.service` |
| **Source** | [`mcp/hermes/`](../mcp/hermes/) (server.py + unit + README) |
| **Bind** | `127.0.0.1:24270` local process; externally reached through Cloudflare Tunnel + Access policy |
| **State** | **Active** ✓ on shambala |
| **MCP server name** | `hermes` (runtime instructions include actual hostname) |
| **Tool exposed** | `exec(prompt)` — runs `hermes run <prompt>` and returns summary |
| **MCP endpoint (local)** | `http://127.0.0.1:24270/mcp` |
| **MCP endpoint (public)** | `https://mcp-shambala.thepkb.in/mcp` (Access-gated) |
| **Config env** | `HERMES_BRIDGE_HOST` (default `0.0.0.0`), `HERMES_BRIDGE_PORT` (default `24270`) |
| **AI Controls role** | Registered as upstream server `shambala-mcp` and attached to PKB MCP Portal |

### 24271 — SearXNG (search)

| | |
|---|---|
| **Container** | `searxng` (publishes container 8080 → host 24271) |
| **Host port** | **24271** |
| **State** | active ✓ (unit `aistack-searxng.service` enabled) |
| **Note** | This port formerly hosted the local TEI embedding server; TEI has moved to server.jgk (`jgk-tei`). |
| **Wiki** | [TEI](TEI.md) (embeddings now on jgk) |

### 24273 — vLLM Runtime (ROCm)

| | |
|---|---|
| **Container** | `vllm-openai` (no pod) |
| **Host port** | **24273** (localhost only) |
| **State** | **Standby** (managed by `vllm-ctl`) — demoted from primary 2026-06-29 |
| **API base** | `http://127.0.0.1:24273/v1` |
| **Model cache** | `/ai/vllm/hf-cache` |
| **Wiki** | [vLLM Runtime](vLLM-Runtime.md) — quant/FP8 picks: [MODELS-FP8.md](../vllm/MODELS-FP8.md) |
| **Reactivate when** | multi-tenant load (batch ≥ 4), prefill-heavy workloads, RDNA4 FP4 experiments |
| **Health check** | `curl http://127.0.0.1:24273/health` |

### 24274 — llama.cpp Runtime (Vulkan / ROCm)  — **PRIMARY**

| | |
|---|---|
| **Container** | `llamacpp-server` (no pod) |
| **Host port** | **24274** (localhost only) |
| **State** | **Active ✓ — primary local LLM runtime** (managed by `llama-ctl`) |
| **Backend** | `ghcr.io/ggml-org/llama.cpp:server-vulkan` (default); ROCm image available |
| **API base** | `http://127.0.0.1:24274/v1` |
| **Slots probe** | `http://127.0.0.1:24274/slots` (live capacity inspection) |
| **Prometheus** | `http://127.0.0.1:24274/metrics` |
| **Model cache** | `/ai/llamacpp/models/` (GGUF files) |
| **Current model** | `Devstral-Small-2505-Q5_K_M` (Mistral 24B dense, agent-tuned, Apache-2.0, 128K ctx, alias `devstral-small-2505`) |
| **Swap** | `llama-ctl switch <gguf-file>` — auto-derives alias, updates `.env`, patches LiteLLM config (live + git), restarts `litellm-proxy` |
| **LiteLLM model name** | `llamacpp-local` (direct pin) **AND** `smart-auto` local member |
| **Wiki** | [llamacpp/README.md](../llamacpp/README.md) |
| **Health check** | `curl http://127.0.0.1:24274/health` |

### 24272 / 24275 — APISIX (abandoned)

APISIX migration was selected by ADR-013 (2026-06-25) and abandoned before any
production cutover by [ADR-014](ADR-014.md) (2026-06-27). Slots 24272 (data
plane) and 24275 (dashboard) remain free. Slot 24274 (originally APISIX admin)
was reclaimed 2026-06-29 for the llama.cpp runtime. The APISIX scaffolding
(`apisix/`, declarative configs, `ARD-LLM-Gateway-Comparison.md`) remains on
disk for a future re-pivot.

---

## Retired Services

These ports are **free for reassignment**. Wiki pages are kept for historical context.

| Port | Former service | Retired | Reason | Reference |
|------|----------------|---------|--------|-----------|
| 24268 | `mcp-email` | May 2026 | No longer needed — scope dropped | [MCP-Email](mcp/MCP-Email.md), [ADR-006](ADR-006.md) |
| 24269 | Bifrost gateway | Jun 27 2026 | Replaced by resurrected LiteLLM on the same port | [Bifrost](Bifrost.md), [ADR-014](ADR-014.md) |
| 24272 / 24275 | APISIX (planned) | Jun 27 2026 | Migration abandoned before implementation (24274 reclaimed for llama.cpp) | [ADR-014](ADR-014.md) |

> Port **24270** was previously `mcp-ssh` (retired May 2026, [ADR-009](ADR-009.md)); reassigned to **Hermes Bridge MCP** in June 2026.

---

## Pod-Internal Ports (Reference Only)

These are container-to-container within a pod. They do NOT bind to the host.

### Dify Pod

| Port | Service | Notes |
|------|---------|-------|
| 80 | nginx | Entry point → mapped to host 24261 |
| 5001 | api | Flask backend |
| 3000 | web | React frontend |
| 8194 | sandbox | Code execution |

### MCP Web Pod

| Port | Service | Notes |
|------|---------|-------|
| 8000 | gateway | FastMCP → mapped to host 24262 |
| 8888 | searxng | Metasearch engine |

### Shared Infra (`aistack-infra`)

PostgreSQL and Redis run as standalone containers used by host-network containers
(LiteLLM, Dify) and bridge pods. They do **not** publish host ports — connections
come from inside the same network namespace.

| Logical port | Service | Access from |
|------|---------|-------------|
| 5432 | PostgreSQL (`aistack-infra-postgres`) | `localhost:5432` (host net) / `host.containers.internal:5432` (bridge pods) |
| 6379 | Redis (`aistack-infra-redis`) | `localhost:6379` / `host.containers.internal:6379` |

---

## Security Notes

- **Firewall**: Public exposure is through Cloudflare Tunnel + Access policies. Current public hostnames include Dify on `24261` and Hermes Bridge on `24270`.
- **No low ports**: Nothing below 1024. No root needed.
- **Unpredictable**: `2426X` won't be hit by scanners probing 3000, 5000, 8000, 8080, etc.
- **WAHA API key**: Set `WAHA_API_KEY` in production to prevent unauthorized WhatsApp access on 24263.
- **Hermes Dashboard on 24265**: bound to `0.0.0.0` (all interfaces, post Jul-2026 rework). Auth gate is the bundled `self-hosted` OIDC provider talking to a Cloudflare Zero Trust SaaS/OIDC app — the same GitHub identity policy the rest of the platform uses. `HERMES_DASHBOARD_PUBLIC_URL` locks the OAuth callback to `https://oc.thepkb.in`. No CF Access self-hosted app and no HTTP Host header override on the tunnel — both were remnants of the loopback-bind era.

---

## Quick Reference

```bash
# Check what's listening on AIStack ports right now
sudo ss -tlnp | grep -E ':(2426[0-9]|242[0-9][0-9])'

# Cross-check against systemd state
systemctl --user is-active aistack-*.service

# Individual health checks (only for services currently running)
curl http://localhost:24265/             # Open WebUI
curl http://localhost:24269/v1/models    # Bifrost Gateway
curl -sS --max-time 5 -i \
	-H "Accept: application/json, text/event-stream" \
	-H "Content-Type: application/json" \
	-X POST http://localhost:24270/mcp \
	-d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"health","version":"1.0"}}}'
```

---

## Adding a New Service

1. **Pick the next free number** from the live map above (24268, 24270, or 24272+).
2. **Add it to this file** in the same edit as the deploy.
3. **Configure the service** to bind only that port.
4. **Document the unit** in [Systemd-Services](Systemd-Services.md) if it auto-starts.

---

*Last updated: 2026-06-29 — llama.cpp default model swapped to `Devstral-Small-2505-Q5_K_M`; `llama-ctl switch` now auto-propagates the alias to LiteLLM (see [commit 7804627](https://github.com/carponoid/aistack/commit/7804627)).*
