# Development container 0.5.4

The app builds NUI fork commit `46bca9281a3254a3ce66deb56c44faffc205991a`
with SUBJECTS/watch and CBOR/CDDL support. It bundles the schema version 1 board
contract and preserves custom schemas and saved connections in the data volume.

The image build runs frontend tests, schema containment checks, connection
recovery tests, ingress authorization tests and restart persistence checks.
Release checks build and scan both amd64 and aarch64 images. Check the results
on the pull request for the exact revision being installed.

Production verification uses the deployed app through authenticated HA ingress:
open the saved connection, list streams and subjects, decode a retained board
event as CBOR and validate it with the bundled CDDL. An image build or readiness
log alone does not establish this behavior.

This is a development deployment. Fresh installation and cold backup/restore on
a disposable HA system remain separate community-release checks in
[RELEASING.md](RELEASING.md).
