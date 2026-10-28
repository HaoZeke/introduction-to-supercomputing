"""Round-trip and sanity tests for tools/render_profile.py.

Run: python3 tools/test_render.py
"""
import contextlib
import io
import math
import re
import sys
import tempfile
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
        self.assertEqual(self.r("{{#missing?}}x{{/missing?}}"), "")
        self.assertEqual(self.r("{{^missing?}}x{{/missing?}}"), "x")

    def test_standalone_tag_lines_vanish(self):
        self.assertEqual(self.r("a\n{{#t}}\nb\n{{/t}}\nc\n", t=True), "a\nb\nc\n")

    def test_nested_value_renders_in_context(self):
        self.assertEqual(self.r("{{#j}}{{../note}}{{/j}}", note="run {{script}}", j={"script": "x.sh"}), "run x.sh")

    def test_missing_value_is_an_error(self):
        with self.assertRaises(KeyError):
            self.r("{{nope}}")
        with self.assertRaises(KeyError):
            self.r("{{#nope}}x{{/nope}}")

    def test_names_do_not_fall_back_to_outer_contexts(self):
        with self.assertRaises(KeyError):
            self.r("{{#j}}{{top}}{{/j}}", top="t", j={"k": 1})
        with self.assertRaises(KeyError):
            self.r("{{#j}}{{#top}}x{{/top}}{{/j}}", top=True, j={"k": 1})
        self.assertEqual(self.r("{{#j}}{{../top}}{{k}}{{/j}}", top="t", j={"k": 1}), "t1")
        with self.assertRaises(KeyError):
            self.r("{{../../top}}", top="t")


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

    def test_src_fundamentals_jobs_fit_one_node(self):
        prof = self.profiles["src"]
        rendered = rp.render_all("src")
        limit = prof["limits"]["max_cpus_per_node"]
        files = {
            "hello": "course-module-fundamentals-of-hpc/hands-on.md",
            "pi": "course-module-fundamentals-of-hpc/hands-on/pi.sh",
        }
        for job, rel in files.items():
            with self.subTest(job):
                want = prof["jobs"]["fundamentals"][job]["cpus_per_task"]
                got = [int(v) for k, v in SBATCH.findall(rendered[rel]) if k == "cpus-per-task"]
                self.assertEqual(got, [want])
                self.assertLessEqual(want, limit)
                self.assertIn(f"--partition={prof['partitions']['cpu']}\n", rendered[rel])

    def test_gpu_job_uses_each_profiles_gpu_partition(self):
        rel = "course-module-fundamentals-of-hpc/hands-on.md"
        for name, prof in self.profiles.items():
            with self.subTest(name):
                text = rp.render_all(name)[rel]
                parts = re.findall(r"(?m)^#SBATCH --partition=(\S+)", text)
                self.assertEqual(parts[-1], prof["partitions"]["gpu"])
        self.assertNotIn("gpu_a100", rp.render_all("src")[rel])

    def test_validate_rejects_more_tasks_than_nodes_hold(self):
        prof = {"jobs": {"m": {"j": {"nodes": 3, "ntasks": 7, "ntasks_per_node": 2}}}}
        self.assertTrue(any("7 tasks on 3 nodes" in p for p in rp.validate("x", prof)))
        prof["jobs"]["m"]["j"]["ntasks"] = 6
        self.assertEqual(rp.validate("x", prof), [])

    def test_lint_catches_one_line_stack_load(self):
        prof = self.profiles["src"]
        self.assertTrue(rp.lint(prof, {"x.sh": "module load 2025 foss/2025a\n"}))
        self.assertFalse(rp.lint(prof, {"x.sh": "module load 2025   # stack\n"}))

    def test_lint_catches_one_line_stack_load_in_prose(self):
        prof = self.profiles["src"]
        self.assertTrue(rp.lint(prof, {"s.org": "- Load =2025 foss/2025a= before =mpirun=.\n"}))
        self.assertTrue(rp.lint(prof, {"r.md": "First load `2025 GCC/14.2.0`.\n"}))
        self.assertFalse(rp.lint(prof, {"s.org": "- Load =2025=, then =foss/2025a=.\n"}))
        self.assertFalse(rp.lint(prof, {"s.org": "@@beamer:\\$@@ module load 2025 \\\\\n"}))


class LintCourseFiles(unittest.TestCase):
    def test_lint_reads_files_without_a_template(self):
        prof = rp.load_profiles()["src"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "course-module-x" / "hands-on").mkdir(parents=True)
            (root / "course-module-x" / "hands-on" / "run.sh").write_text("module load 2025 foss/2025a\n")
            (root / "course-module-x" / "README.md").write_text("module load 2025\n")
            (root / "course-module-x" / "data.csv").write_text("module load 2025 x\n")
            files = rp.course_files(root)
            self.assertEqual(sorted(files), ["course-module-x/README.md", "course-module-x/hands-on/run.sh"])
            self.assertEqual(rp.lint(prof, files), ["course-module-x/hands-on/run.sh:1: module load 2025 foss/2025a"])
            self.assertEqual(rp.course_files(root, skip={"course-module-x/hands-on/run.sh"}).keys(),
                             {"course-module-x/README.md"})

    def test_published_course_files_pass_every_profile(self):
        for name, prof in rp.load_profiles().items():
            with self.subTest(name):
                rendered = rp.render_all(name)
                files = rp.course_files(rp.ROOT, skip=rendered)
                # Every templated file leaves this set, so count both.
                self.assertGreater(len(files) + len(rendered), 50)
                self.assertEqual(rp.lint(prof, files), [])


class Check(unittest.TestCase):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rp.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def test_check_flags_extra_missing_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_main("src", "--out", tmp)[0], 0)
            code, text = self.run_main("src", "--check", "--against", tmp)
            self.assertEqual(code, 0, text)
            n = len(rp.render_all("src"))
            self.assertIn(f"src: {n}/{n} files identical", text)

            script = Path(tmp, "course-module-snellius-hybrid-jobs/hands-on/ex1/submit-axpy.sh")
            script.chmod(0o755)
            code, text = self.run_main("src", "--check", "--against", tmp)
            self.assertEqual(code, 1)
            self.assertIn("mode: course-module-snellius-hybrid-jobs/hands-on/ex1/submit-axpy.sh", text)
            script.chmod(0o644)

            Path(tmp, "stale.md").write_text("old render\n")
            code, text = self.run_main("src", "--check", "--against", tmp)
            self.assertEqual(code, 1)
            self.assertIn("extra: stale.md", text)
            self.assertIn("1 extra", text)
            Path(tmp, "stale.md").unlink()

            script.unlink()
            code, text = self.run_main("src", "--check", "--against", tmp)
            self.assertEqual(code, 1)
            self.assertIn("missing: course-module-snellius-hybrid-jobs/hands-on/ex1/submit-axpy.sh", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
