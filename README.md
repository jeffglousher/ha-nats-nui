# NUI for Home Assistant

Explore and manage your NATS servers from Home Assistant.

- Save connections to existing NATS servers.
- Browse JetStream streams, consumers and key/value buckets.
- Inspect messages and publish messages to NATS subjects.
- Open securely through Home Assistant ingress with your existing HA sign-in.

Add your Home Assistant user ID to **Configuration → Console administrators**,
save and restart the app, then select **Open Web UI**. In NUI, select **ALL**, then **NEW**
to add a server connection. Enable **Show in sidebar** for quick access.
See [Documentation](nats_nui/DOCS.md) for connection setup and troubleshooting.

This app provides the NUI interface. A running NATS server is required.

## Installation

On Home Assistant OS, open Settings → Apps → App store → Repositories and add
`https://github.com/jeffglousher/ha-nats-nui`. Then install the app from this
repository and follow its documentation. Repository installation becomes
available when this repository is public; this candidate is not yet published.

Standalone Home Assistant Container installations do not include Supervisor apps.
These are independent community wrappers, not official upstream distributions.

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md),
[License](LICENSE), and [release readiness](RELEASE_STATUS.md).
