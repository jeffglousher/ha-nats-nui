# Contributing

Discuss substantial changes in an issue first. Keep app behavior independent of
any particular installation, workload or consumer. Never commit credentials,
backups, local options.json files or private deployment details.

Run `python tools/check_release.py` (requires PyYAML 6.0.3), `sh -n nats_nui/run.sh`,
and `docker build --build-arg BUILD_VERSION=test --build-arg BUILD_ARCH=amd64 -t addon-test ./nats_nui`.
The image build runs isolated runtime tests against disposable data; a failure
stops the build. CI also builds and tests natively on amd64 and arm64 runners.

For runtime changes, test in a disposable HA installation as well: configuration,
startup, shutdown, upgrade with existing data, backup/restore and reconnection.
Do not test destructive operations on a live broker. Document limits honestly.

Bump the app version for shipped changes, update its changelog and tests, and
preserve existing app identity and data paths. Pin updated upstream inputs and
review licenses. Contributions to wrapper code are accepted under LICENSE.

Before submitting, run `python tools/check_privacy.py` and Gitleaks on both the
working tree and Git history. Reports must redact matched credentials.

## Updating dependency overlays

The Dockerfile checks out a pinned NUI revision and then copies the Go and npm
manifests from `nats_nui/dependencies` over that source. These are build inputs,
not an independent Go project. Never run `go mod tidy` in the overlay directory:
without source files it removes every requirement and checksum.

For a Go update, create a disposable checkout of the exact revision in the
Dockerfile, copy both overlay files (`go.mod` and `go.sum`) into its root, and
apply the add-on patches. Use the Dockerfile's Go toolchain. Run
`go get <module>@<version>` in that checkout, inspect any other version changes,
then run `go mod tidy`, `go mod verify`, and the relevant upstream tests there.
Copy the resulting `go.mod` and `go.sum` back together. Review the complete diff
for unexpected removals or downgrades and run the release checks and both native
image builds; these compile the actual application and run vulnerability checks.
The early overlay guard rejects missing required modules or archive checksums.

## Released upstream policy

Follow released NUI versions, pinned by source revision and image digest. Update
NATS server through its released image versions in the separate server app.
Avoid independent library migrations merely to follow newer dependency versions.
Ordinary Go and npm overlay version PRs are disabled. Docker and GitHub Actions
version updates, vulnerability alerts, security updates, weekly image scans and
binary `govulncheck` remain enabled.

Known vulnerabilities remain real findings: do not dismiss them just because
they originate upstream. Prefer a fixed upstream release when available; retain
necessary security patches until it incorporates them. Any security overlay
change must build against the pinned upstream source and pass the existing
checks. A generated security PR is not automatically safe to merge, particularly
when Go's isolated tidy step removes the source-dependent requirement graph.
