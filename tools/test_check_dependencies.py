"""Regression cases for destructive detached-manifest updates."""
from pathlib import Path
import shutil
import tempfile
import unittest
from check_dependencies import check_go_overlay

SOURCE = Path(__file__).resolve().parents[1] / "nats_nui/dependencies"


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        for name in ("go.mod", "go.sum"):
            shutil.copyfile(SOURCE / name, self.directory / name)

    def test_current_overlay(self):
        check_go_overlay(self.directory)

    def test_tidy_without_sources(self):
        (self.directory / "go.mod").write_text("module github.com/nats-nui/nui\n\ngo 1.26.0\n")
        (self.directory / "go.sum").write_text("")
        with self.assertRaisesRegex(ValueError, "lost required modules"):
            check_go_overlay(self.directory)

    def test_module_requirement_removed(self):
        path = self.directory / "go.mod"
        path.write_text("\n".join(line for line in path.read_text().splitlines()
                                  if "github.com/nats-io/nats.go " not in line))
        with self.assertRaisesRegex(ValueError, "lost required modules"):
            check_go_overlay(self.directory)

    def test_archive_checksum_removed_but_mod_checksum_retained(self):
        path = self.directory / "go.sum"
        path.write_text("\n".join(line for line in path.read_text().splitlines()
                                  if not (line.startswith("github.com/nats-io/nats.go ")
                                          and "/go.mod " not in line)))
        with self.assertRaisesRegex(ValueError, "Missing archive checksum"):
            check_go_overlay(self.directory)


if __name__ == "__main__":
    unittest.main()
