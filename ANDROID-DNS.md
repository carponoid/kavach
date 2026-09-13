# Android DNS Rollout

Kavach is initially optimised for **managed Android devices only**. It is **not**
trying to be a LAN-wide DNS appliance in phase 1.

## Default path: managed DoH app

This is the primary rollout path for the 2 supervised kids.

- **Transport:** DNS-over-HTTPS
- **Public endpoint:** `https://dns-kavach.thepkb.in/dns-query`
- **Local origin:** `127.0.0.1:24283` → AdGuard internal `:443`
- **Why first:** works over ordinary HTTPS, survives Cloudflare Tunnel, avoids
  host `:53` and host `:853`, and keeps the pod rootless

### Enforcement model

- Push a DNS/VPN client app from Headwind MDM
- Set the app to use the Kavach DoH endpoint
- On Device Owner devices, require the app to stay installed and active
- Combine with app whitelist / kiosk controls so the child cannot casually swap
  to another DNS path

### App choice

Recommended first-pass option:

- **RethinkDNS** or another F-Droid-available DNS/VPN client that supports a
  custom DoH endpoint

Kavach does not depend on one specific client implementation, but the client
must support:

- custom DoH URL
- policy persistence under MDM
- local VPN-based DNS enforcement

## Optional path: native Android Private DNS

This is the app-less path, but it is **not** the phase-1 default.

- **Transport:** DNS-over-TLS
- **Android setting:** Private DNS hostname only
- **Port:** `:853`

Important correction:

- Android's native **Private DNS** uses **DoT**, not DoH
- `https://dns-kavach.thepkb.in/dns-query` is **not** valid in the native
  Private DNS field

### Why deferred

- raw TCP `:853` is not carried by HTTP-only tunnel paths
- rootless Podman cannot bind `:853` on shambala with the current kernel policy
- exposing `:853` needs a host-level privileged-port helper or another direct
  TCP-capable edge design

## Not used initially: classic DNS on `:53`

Classic port-53 DNS is intentionally out of scope for phase 1 because:

- routers and general LAN devices are not the target yet
- rootless Podman cannot bind host `:53` with the current host policy
- managed-device DoH achieves the family-safety goal with less host complexity

## Practical recommendation

1. Start with **managed DoH app** for supervised kids.
2. Keep **native Private DNS / DoT 853** as a later option if you want the
   app-less Android path.
3. Add classic `:53` only if Kavach later becomes a LAN DNS service for routers
   or unmanaged devices.