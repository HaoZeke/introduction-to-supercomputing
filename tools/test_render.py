"""Round-trip and sanity tests for tools/render_profile.py.

Run: python3 tools/test_render.py
"""
import math
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_profile as rp  # noqa: E402

SBATCH = re.compile(r"^#SBATCH --([a-z-]+)=(\d+)", re.M)


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


class Profiles(unittest.TestCase):
    profiles = rp.load_profiles()

    def test_snellius_reproduces_published_files(self):
        for rel, text in rp.render_all("snellius").items():
            with self.subTest(rel):
                self.assertEqual(text, (rp.ROOT / rel).read_text())

    def test_profiles_pass_their_own_limits(self):
        for name, prof in self.profiles.items():
            self.assertEqual(rp.validate(name, prof), [])

    def test_src_scripts_match_profile_and_keep_stack_on_own_line(self):
        prof = self.profiles["src"]
        rendered = rp.render_all("src")
        self.assertEqual(rp.lint(prof, rendered), [])
        limit = prof["limits"]["max_cpus_per_node"]
        scripts = {job["script"]: job for job in prof["jobs"]["hybrid"].values() if "script" in job}
        seen = 0
        for rel, text in rendered.items():
            job = scripts.get(Path(rel).name)
            if not job:
                continue
            seen += 1
            got = {k.replace("-", "_"): int(v) for k, v in SBATCH.findall(text)}
            with self.subTest(rel):
                for key, _ in rp.SBATCH_KEYS:
                    self.assertEqual(got.get(key), job.get(key))
                per_node = got.get("ntasks_per_node") or math.ceil(got["ntasks"] / got["nodes"])
                self.assertLessEqual(per_node * got["cpus_per_task"], limit)
                stack = re.escape(prof["modules"]["stack"])
                self.assertRegex(text, rf"(?m)^module load {stack}\s*(#.*)?$")
        self.assertEqual(seen, len(scripts))

    def test_lint_catches_one_line_stack_load(self):
        prof = self.profiles["src"]
        self.assertTrue(rp.lint(prof, {"x.sh": "module load 2025 foss/2025a\n"}))
        self.assertFalse(rp.lint(prof, {"x.sh": "module load 2025   # stack\n"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
