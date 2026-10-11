# NUI for Home Assistant

Explore and manage your NATS servers from Home Assistant.

- Save connections to existing NATS servers.
- Browse JetStream streams, consumers and key/value buckets.
- Inspect messages and publish messages to NATS subjects.
- Open securely through Home Assistant ingress with your existing HA sign-in.

Add your Home Assistant user ID to **Configuration → Console administrators**,
save and restart the app, then select **Open Web UI**. The companion NATS app
is connected automatically on first setup when using shared-token authentication
without TLS. Manage that connection and add other servers in NUI. Enable
**Show in sidebar** for quick access.
See [Documentation](nats_nui/DOCS.md) for connection setup and troubleshooting.

This app provides the NUI interface. A running NATS server is required.

## Installation

On Home Assistant OS, open Settings → Apps → App store → Repositories and add
`https://github.com/jeffglousher/ha-nats-nui`. Then install the app from this
repository and follow its documentation.

Standalone Home Assistant Container installations do not include Supervisor apps.
These are independent community wrappers, not official upstream distributions.

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md),
[License](LICENSE), and [release readiness](RELEASE_STATUS.md).

## Development payload inspection

This container pins the development fork integration 46bca9281a3254a3ce66deb56c44faffc205991a
(current CBOR/CDDL plus latest SUBJECTS explorer/watch), rather than the upstream
release source. The server reports 0.9.3-ha-cbor-subjects.2+46bca928. Existing ingress,
connection recovery and dependency overlays are retained.

Pick CBOR when inspecting agent-board messages. The bundled agent-board.cddl is a
verbatim deployment copy of the authoritative contract in agent-message-board;
refresh it from that source when shipping a new board contract. Payload versions
live in the contract/type, not stream or bucket identifiers. Native notices and
metadata are CBOR with explicit schema version 1; pre-versioning formats are retired.

Image-owned contracts are refreshed under /db/cddlschemas/bundled on startup.
Place custom CDDL under /db/cddlschemas/default; container upgrades preserve it.
The CDDL schema loader is restricted to this directory tree. No host port or new
Supervisor privilege is required. SUBJECTS discovers existing names and replaces
MESSAGES with the selected subject; browsing alone does not publish messages.