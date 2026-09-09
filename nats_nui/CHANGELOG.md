# 0.4.3

- Rebuild closed cached connections and return bucket errors without crashing NUI.
- Check watcher creation before reading bucket updates.

- Fix key/value bucket size, maximum value size and replica settings being
  silently ignored because frontend field names differed from nats.go JSON.
- Populate those settings correctly when reopening a bucket for editing.
- Add frontend API contract regression tests for bucket creation and updates.

# Changelog

## 0.4.2

Require an explicit list of Home Assistant user IDs for console access. The list
starts empty and denies access until configured; sidebar visibility alone is
insufficient authorization. Watchdog retains a restricted health endpoint.

Prevent concurrent connection deletion and requests from racing in the connection
pool. Retry after a failed connection refresh instead of reusing the closed
connection. Synchronize status notifications with subscription cancellation and
close notification channels when a connection closes. Run the full connection
package and regression tests with Go's race detector during each image build.

## 0.4.1

Apply Alpine security updates during builds, including patched OpenSSL libraries.
Correct exit-trap quoting for shell analysis; shutdown cleanup behavior is preserved.

## 0.4.0

Rebuild patched Go/frontend dependencies with Go 1.27.1; run 81 frontend tests and a Linux binary vulnerability gate. Harden schema file containment and ingress request isolation. Add traversal, symlink, spoofed-header, and cross-site request regression checks.

## 0.3.0

- Community release candidate with pinned inputs and isolated image-build tests.
- Release, contributor, security and licensing guidance.
- Runtime privilege/readiness hardening and stronger release checks.


## 0.2.1

- New Info page, configuration help and general-purpose documentation.
- Configurable service log detail; routine HTTP access logs disabled.
- Clear startup, readiness, shutdown and service-failure messages.
- Existing connections and ingress-only access are preserved.

## 0.2.0

- Require HA ingress; remove standalone port access.
- Proxy HTTP and WebSockets only from Supervisor.
- Bind NUI backend to container loopback; preserve connections and schemas.
