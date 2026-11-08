"""Tests for eclipse-problems: python3 -m unittest discover -s emf/tools"""
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("eclipse-problems")
BEGIN = bytes.fromhex("40b18b8123bc00141a2596e7a393be1e")
END = bytes.fromhex("c058fbf323bc00141a51f38c7bbb77c6")

# A real .markers.snap from the Oomph workspace, captured 2026-11-08.
REAL_SNAP = BEGIN + bytes.fromhex(
    "00000002001f2f70742e75702e666575702e6578616d7363686564756c652e64"
    "736c2e756900000001000000000000000202002d6f72672e65636c697073652e"
    "636f72652e7265736f75726365732e6e6f4578706c69636974456e636f64696e"
    "6700030008736576657269747902000000010008"
    "6c6f636174696f6e03001f2f70742e75702e666575702e6578616d7363686564"
    "756c652e64736c2e756900076d657373616765030045"
    "50726f6a6563742027"
    "70742e75702e666575702e6578616d7363686564756c652e64736c2e75692720"
    "686173206e6f206578706c6963697420656e636f64696e6720736574"
    "000001a1ab8b7e22"
) + END + BEGIN + BEGIN


def utf(s):
    b = s.encode()
    return struct.pack(">H", len(b)) + b


def marker(type_, attrs, created, id_=1):
    """One marker as MarkerWriter.write lays it out (type always by name)."""
    out = struct.pack(">qb", id_, 2) + utf(type_) + struct.pack(">h", len(attrs))
    for k, v in attrs.items():
        out += utf(k)
        if isinstance(v, bool):
            out += struct.pack(">b?", 1, v)
        elif isinstance(v, int):
            out += struct.pack(">bi", 2, v)
        else:
            out += struct.pack(">b", 3) + utf(v)
    return out + struct.pack(">q", created)


def snap_entry(path, markers):
    return struct.pack(">i", 2) + utf(path) + struct.pack(">i", len(markers)) + b"".join(markers)


JAVA = "org.eclipse.jdt.core.problem"


class EclipseProblemsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        self.state = self.ws / ".metadata/.plugins/org.eclipse.core.resources/.projects"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, project, name, data):
        d = self.state / project
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_bytes(data)

    def run_tool(self):
        r = subprocess.run([sys.executable, TOOL, self.ws], capture_output=True, text=True, check=True)
        lines = r.stdout.splitlines()
        self.assertRegex(lines[0], r"^snapshot: \d+s old")
        return lines[1:]

    def test_decodes_a_real_snapshot(self):
        self.write("pt.up.feup.examschedule.dsl.ui", ".markers.snap", REAL_SNAP)
        self.assertEqual(self.run_tool(), [
            "WARNING pt.up.feup.examschedule.dsl.ui / "
            "Project 'pt.up.feup.examschedule.dsl.ui' has no explicit encoding set",
        ])

    def test_later_snapshots_replace_earlier_markers(self):
        old = marker(JAVA, {"severity": 2, "message": "old", "lineNumber": 3}, 1000)
        base = struct.pack(">i", 3) + utf("/p/A.java") + struct.pack(">i", 1) + old
        warn = marker(JAVA, {"severity": 1, "message": "unused", "lineNumber": 9}, 2000)
        err = marker(JAVA, {"severity": 2, "message": "boom", "lineNumber": 4}, 3000)
        task = marker("org.eclipse.core.resources.taskmarker", {"message": "TODO"}, 3000)
        self.write("p", ".markers", base)
        self.write("p", ".markers.snap",
                   BEGIN + snap_entry("/p/A.java", [warn]) + END
                   + BEGIN + snap_entry("/p/A.java", [warn, err]) + snap_entry("/p/B.java", [task]) + END
                   + BEGIN + snap_entry("/p/A.java", [old]))  # unfinished chunk: ignored
        self.assertEqual(self.run_tool(), [
            "ERROR p A.java:4 boom",
            "WARNING p A.java:9 unused",
        ])

    def test_marks_problems_older_than_their_file(self):
        (self.ws / "p").mkdir()
        java = self.ws / "p/A.java"
        java.write_text("class A {}")
        os.utime(java, (2, 2))  # edited at 2 s, after the problem was created (1000 ms)
        self.write("p", ".markers.snap",
                   BEGIN + snap_entry("/p/A.java", [marker(JAVA, {"severity": 2, "message": "boom"}, 1000)]) + END)
        self.assertEqual(self.run_tool(), ["ERROR p A.java boom (file edited since)"])


if __name__ == "__main__":
    unittest.main()
