# Release readiness — 0.4.0 candidate

## Verified

- Release metadata, translations, pinned build inputs and minimal privileges.
- Native amd64 image build and isolated runtime regression tests.
- Authentication, persistence, restart recovery and secret-safe service logging.
- NUI ingress HTTP, assets, API and WebSockets; anonymous/direct access rejected.
- Schema traversal and symlink escape rejection; HA credentials stripped by proxy.
- All 81 upstream frontend tests and production frontend build.
- Patched dependency lockfiles and Go server vulnerability analysis. The remaining
  module-level GO-2026-5932 advisory affects the unused OpenPGP package; no
  vulnerable server calls were identified. Linux binary scanning is a build gate.

## Remaining release gates

- Native arm64 image builds and full container operating-system vulnerability scan.
- Fresh repository installation and cold backup/restore on a disposable HA system.
- Final license/attribution review and release evidence for supported platforms.

Source publication is separate from declaring a stable supported release. See
RELEASING.md for the complete release checklist.
