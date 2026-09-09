"""Check the detached Go manifests before downloading or building upstream."""
from pathlib import Path
import re

# These modules are imported by the pinned application's server and tests.
# A deliberate source migration may update this set in the same review.
REQUIRED_MODULES = {
    "github.com/Masterminds/semver/v3",
    "github.com/adrg/xdg",
    "github.com/gofiber/fiber/v2",
    "github.com/nats-io/nats-server/v2",
    "github.com/nats-io/nats.go",
    "github.com/nats-io/nkeys",
    "github.com/ostafen/clover/v2",
    "github.com/samber/slog-fiber",
}


def check_go_overlay(directory: Path) -> None:
    manifest = (directory / "go.mod").read_text(encoding="utf-8")
    requirements = {}
    in_require = False
    for raw in manifest.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line == "require (":
            in_require = True
            continue
        if line == ")":
            in_require = False
            continue
        if line.startswith("require "):
            line = line.removeprefix("require ")
        elif not in_require:
            continue
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2 or not parts[1].startswith("v"):
            raise ValueError("Malformed Go requirement")
        module, version = parts
        if module in requirements:
            raise ValueError(f"Duplicate Go requirement: {module}")
        requirements[module] = version
    missing = REQUIRED_MODULES - requirements.keys()
    if missing:
        raise ValueError(f"Go overlay lost required modules: {sorted(missing)}")
    sums = set()
    for line in (directory / "go.sum").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 3 or not re.fullmatch(r"h1:[A-Za-z0-9+/]{43}=", parts[2]):
            raise ValueError("Malformed Go checksum")
        sums.add((parts[0], parts[1]))
    for module, version in requirements.items():
        if (module, version) not in sums:
            raise ValueError(f"Missing archive checksum: {module} {version}")


if __name__ == "__main__":
    check_go_overlay(Path(__file__).resolve().parents[1] / "nats_nui/dependencies")
    print("PASS: Go overlay requirements and checksums")
