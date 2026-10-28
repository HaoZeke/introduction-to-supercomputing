"""Round-trip and sanity tests for tools/render_profile.py.

Run: python3 tools/test_render.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_profile as rp  # noqa: E402

class Engine(unittest.TestCase):
    def r(self, text, **ctx):
        return rp.render(text, [ctx])

    def test_value_and_format_spec(self):
        self.assertEqual(self.r("[{{a.b:<4}}]", a={"b": 7}), "[7   ]")

    def test_sections(self):
        self.assertEqual(self.r("{{#xs}}<{{.}}>{{/xs}}", xs=[1, 2]), "<1><2>")
        self.assertEqual(self.r("{{#d}}{{k}}{{/d}}", d={"k": "v"}), "v")
        self.assertEqual(self.r("{{^xs}}none{{/xs}}", xs=[]), "none")
        self.assertEqual(self.r("{{#missing}}x{{/missing}}"), "")

    def test_standalone_tag_lines_vanish(self):
        self.assertEqual(self.r("a\n{{#t}}\nb\n{{/t}}\nc\n", t=True), "a\nb\nc\n")

    def test_nested_value_renders_in_context(self):
        self.assertEqual(self.r("{{#j}}{{note}}{{/j}}", note="run {{script}}", j={"script": "x.sh"}), "run x.sh")

    def test_missing_value_is_an_error(self):
        with self.assertRaises(KeyError):
            self.r("{{nope}}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
