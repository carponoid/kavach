# Kavach

Open-source family safety and MDM stack for shambala.

This is the Layer-1 workspace for ADR-019. The pod is intentionally designed as
one rootless Podman pod named `kavach` so the services share a network namespace
and can talk over `localhost`.

## Current build status

- Kavach Dashboard, AdGuard Home, Traccar, FMD Server, Headwind MDM, and approver share the same pod
- Headwind follows the official PostgreSQL-backed container path
- Default rollout is **managed Android only**: no host `:53`, DoH origin on `:24283`
- Public admin access will go through Cloudflare Tunnel + Access

## Layout

```text
kavach/
├── README.md
├── ANDROID-DNS.md
├── dashboard/
│   ├── index.html
│   └── default.conf
├── approver/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── config/
│   ├── approver.env.example
│   └── traccar.xml
├── kavach                # management CLI
└── containers/
    └── pod.yaml          # Podman Kube YAML for the kavach pod
```

## Commands

```bash
./kavach build
./kavach start
./kavach stop
./kavach restart
./kavach status
./kavach health
./kavach deploy
```

## Host volumes

The control script creates these under `/ai/kavach/`:

- `adguard/conf`
- `adguard/work`
- `traccar/conf`
- `traccar/data`
- `traccar/logs`
- `fmd/conf`
- `fmd/db`
- `mdm/postgres`
- `mdm/work`
- `approver/data`
- `dashboard`
- `logs`

## Notes

- Host ports in use are tracked in [docs/Port-Registry-from-aistack.md](docs/Port-Registry-from-aistack.md)
- Design decisions are tracked in [docs/ADR-019.md](docs/ADR-019.md)
- Native Android **Private DNS** means **DoT on `:853`**, not DoH. The default pod intentionally avoids privileged DNS ports so it can start rootless on shambala.
- The Kavach portal is served on `http://localhost:24284` and is intended to be published as `https://kavach.thepkb.in` through the shambala tunnel.
- Layer-1 apps are proxied under the dashboard host as `/apps/{adguard,traccar,fmd,mdm,approver}` so one Cloudflare Access session on `kavach.thepkb.in` is reused across the whole portal.
- The default DNS path is a managed Android DNS/VPN app pinned to `https://dns-kavach.thepkb.in/dns-query`.
- Current tunnel routing uses AdGuard DoH on the TLS listener (`https://127.0.0.1:24283/dns-query`) with a local certificate and Cloudflare origin `noTLSVerify`.
- Runtime DoH hardening is enabled (`http.doh.insecure_enabled: false`, `tls.enabled: true`) in `/ai/kavach/adguard/conf/AdGuardHome.yaml`.
- The approver is intentionally minimal on first pass: it serves the block page,
  records access requests, and exposes approval endpoints. Telegram and AdGuard
  writeback are wired by env vars and can be enabled without changing the pod shape.
