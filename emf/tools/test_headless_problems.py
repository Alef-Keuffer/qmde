"""Tests for headless-problems: python3 -m unittest discover -s emf/tools"""
import runpy
import struct
import tempfile
import unittest
from pathlib import Path

relocate = runpy.run_path(str(Path(__file__).with_name("headless-problems")))["relocate"]
BEGIN = bytes.fromhex("40b18b8123bc00141a2596e7a393be1e")
END = bytes.fromhex("c058fbf323bc00141a51f38c7bbb77c6")


def location(uri):
    b = uri.encode()
    return BEGIN + struct.pack(">H", len(b)) + b + bytes(16) + END


class RelocateTest(unittest.TestCase):
    def test_rewrites_matching_prefix_and_leaves_others(self):
        with tempfile.TemporaryDirectory() as ws:
            projects = Path(ws, ".metadata/.plugins/org.eclipse.core.resources/.projects")
            (projects / "a").mkdir(parents=True)
            (projects / "b").mkdir()
            (projects / "a/.location").write_bytes(location("URI//file:/old/My%20Drive/emf/bundles/a"))
            (projects / "b/.location").write_bytes(location("URI//file:/elsewhere/b"))

            relocate(Path(ws), "file:/old/My%20Drive/emf", "file:/new/emf")

            self.assertEqual((projects / "a/.location").read_bytes(), location("URI//file:/new/emf/bundles/a"))
            self.assertEqual((projects / "b/.location").read_bytes(), location("URI//file:/elsewhere/b"))


if __name__ == "__main__":
    unittest.main()
