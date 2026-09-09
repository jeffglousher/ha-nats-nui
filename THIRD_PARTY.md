# Third-party components

Wrapper files use the MIT license in LICENSE. NUI 0.9.3 is distributed under
the Unlicense (licenses/NUI.txt). Its Go/frontend dependencies, Alpine packages,
nginx and container tooling retain their upstream licenses. The upstream source
commit and image digests are pinned in the Dockerfile. Local patches restrict
the listener to loopback and adjust service logging; upstream authors do not
endorse these changes. Artwork is separately attributed in ARTWORK.md.

The wrapper also patches schema containment and rebuilds Go/frontend dependencies
from the manifests and lockfiles in nats_nui/dependencies. Go 1.27.1 and
govulncheck 1.8.0 are selected explicitly for the backend build.
