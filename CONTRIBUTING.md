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

Ordinary automated Go version PRs are disabled because their isolated tidy step
cannot see upstream source. Dependency alerts, security updates, the weekly image
scan and binary `govulncheck` remain enabled. Any generated Go security PR still
needs the source-aware process above; do not merge a destructive manifest diff.

React, React DOM and their type packages update as one group. Major React, MSW
and TypeScript version PRs are deferred until the upstream source is migrated;
this version-update policy does not disable vulnerability alerts. A compiler
upgrade must run `tsc` against the pinned frontend configuration as well as Vite:
the production Vite build alone does not type-check the application. MSW upgrades
must migrate the mock handlers and browser worker API and run the frontend tests.
