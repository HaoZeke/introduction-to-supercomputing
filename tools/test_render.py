"""Round-trip and sanity tests for tools/render_profile.py.

Run: python3 tools/test_render.py
"""
import contextlib
import copy
import io
import math
import re
import sys
import tempfile
import unittest
import unittest.mock
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

    def test_tag_after_an_opening_brace(self):
        self.assertEqual(self.r(r"\texttt{{{a}}}", a="x"), r"\texttt{x}")
        self.assertEqual(self.r(r"\textbf{\texttt{{{a}} to}}", a="x"), r"\textbf{\texttt{x to}}")

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

    def test_slide_jobs_follow_the_profile(self):
        rel = "course-module-fundamentals-of-hpc/slides/fundamentals-of-hpc.org"
        for name, prof in self.profiles.items():
            with self.subTest(name):
                text = rp.render_all(name)[rel]
                jobs = prof["jobs"]["fundamentals"]
                want = [jobs[j]["ntasks"] for j in ("first", "mpi", "firsttest", "r")]
                got = [int(v) for k, v in SBATCH.findall(text) if k == "ntasks"]
                self.assertEqual(got, want)
                key = "nodes" if jobs["mpi_compare"]["nodes"] != jobs["mpi"]["nodes"] else "ntasks"
                self.assertIn(f"\\texttt{{{key}={jobs['mpi_compare'][key]}}}", text)

    def test_slide_jobs_take_the_cpu_partition(self):
        rel = "course-module-fundamentals-of-hpc/slides/fundamentals-of-hpc.org"
        profiles = copy.deepcopy(self.profiles)
        profiles["src"]["partitions"]["cpu"] = "cpu_test"
        with unittest.mock.patch.object(rp, "load_profiles", return_value=profiles):
            text = rp.render_all("src")[rel]
        self.assertEqual(re.findall(r"^#SBATCH --partition=(\S+)", text, re.M), ["cpu_test"] * 6)

    def test_fs_commands_use_the_profiles_scratch(self):
        rel = "course-module-snellius-fs/README.md"
        snel, src = rp.render_all("snellius")[rel], rp.render_all("src")[rel]
        for line in ("#SBATCH --constraint=scratch-node\n", "mkdir /scratch-shared/"):
            self.assertIn(line, snel)
            self.assertNotIn(line, src)
        self.assertIn(f"ls {self.profiles['src']['paths']['scratch_user']}/\n", src)

    def test_src_prose_points_at_the_profiles_scratch(self):
        user = self.profiles["src"]["paths"]["scratch_user"]
        readme = "course-module-snellius-fs/README.md"
        deck = "course-module-fundamentals-of-hpc/slides/fundamentals-of-hpc.org"
        snel, src = rp.render_all("snellius"), rp.render_all("src")
        for line in ("You can create your own directory", "denoted as `/scratch-shared`"):
            self.assertIn(line, snel[readme])
            self.assertNotIn(line, src[readme])
        self.assertIn(f"your directory `{user}` already exists", src[readme])
        self.assertIn("tasks; use =/scratch-shared= \\\\", snel[deck])
        self.assertIn(f"tasks; use ={user}= \\\\", src[deck])

    def test_src_example_outputs_name_their_source(self):
        rel = "course-module-snellius-hybrid-jobs/README.md"
        note = "(the job ID and the time are from a Snellius run)"
        self.assertEqual(rp.render_all("src")[rel].count(note), 2)
        self.assertNotIn(note, rp.render_all("snellius")[rel])

    def test_mail_options_only_where_slurm_sends_mail(self):
        rel = "course-module-fundamentals-of-hpc/slides/fundamentals-of-hpc.org"
        for name, prof in self.profiles.items():
            with self.subTest(name):
                text = rp.render_all(name)[rel]
                self.assertEqual("--mail-type=BEGIN,END" in text, prof["slurm"]["mail"])

    def test_validate_rejects_more_tasks_than_nodes_hold(self):
        prof = {"jobs": {"m": {"j": {"nodes": 3, "ntasks": 7, "ntasks_per_node": 2}}}}
        self.assertTrue(any("7 tasks on 3 nodes" in p for p in rp.validate("x", prof)))
        prof["jobs"]["m"]["j"]["ntasks"] = 6
        self.assertEqual(rp.validate("x", prof), [])

    def test_rendered_job_scripts_fit_each_profile(self):
        for name, prof in self.profiles.items():
            with self.subTest(name):
                self.assertEqual(rp.check_scripts(name, prof, rp.render_all(name)), [])

    def test_check_scripts_reads_every_sbatch_block(self):
        prof = self.profiles["src"]
        text = ("#!/bin/bash\n#SBATCH --nodes=1\n#SBATCH --ntasks=10\n#SBATCH --time=00:01:00\n"
                "echo\n#SBATCH -N 3\n#SBATCH -n 6\n"
                "\n#SBATCH --nodes 2  # comment\n#SBATCH --ntasks=2\n#SBATCH --constraint=scratch-node\n"
                "\n#SBATCH --nodes=#\n#SBATCH --ntasks=#\n")
        self.assertEqual(rp.sbatch_blocks(text), [
            (2, {"nodes": 1, "ntasks": 10}),
            (6, {"nodes": 3, "ntasks": 6}),
            (9, {"nodes": 2, "ntasks": 2, "constraint": "scratch-node"}),
            (13, {}),
        ])
        self.assertEqual(rp.check_scripts("src", prof, {"j.sh": text}), [
            "src: j.sh:2 asks 10 CPUs per node, limit 2",
            "src: j.sh:6 spreads 6 tasks over 3 nodes without --ntasks-per-node",
            "src: j.sh:9 asks for constraint scratch-node, which src lacks",
        ])
        self.assertEqual(rp.check_scripts("snellius", self.profiles["snellius"], {"j.sh": text}),
                         ["snellius: j.sh:6 spreads 6 tasks over 3 nodes without --ntasks-per-node"])

    def test_check_scripts_reads_every_option_on_a_line(self):
        prof = self.profiles["src"]
        text = ("#!/bin/bash\n#SBATCH --nodes=1 --ntasks=10\n\n"
                "#SBATCH -N 3 -n 6 --exclusive\n\n"
                "#SBATCH --exclusive --nodes 2 --ntasks=4 -C scratch-node  # comment\n")
        self.assertEqual(rp.sbatch_blocks(text), [
            (2, {"nodes": 1, "ntasks": 10}),
            (4, {"nodes": 3, "ntasks": 6}),
            (6, {"nodes": 2, "ntasks": 4, "constraint": "scratch-node"}),
        ])
        self.assertEqual(rp.check_scripts("src", prof, {"j.sh": text}), [
            "src: j.sh:2 asks 10 CPUs per node, limit 2",
            "src: j.sh:4 spreads 6 tasks over 3 nodes without --ntasks-per-node",
            "src: j.sh:6 spreads 4 tasks over 2 nodes without --ntasks-per-node",
            "src: j.sh:6 asks for constraint scratch-node, which src lacks",
        ])

    def test_check_scripts_reads_joined_short_options(self):
        self.assertEqual(rp.sbatch_options("-n4 -N2 -c8"), [("-n", "4"), ("-N", "2"), ("-c", "8")])
        self.assertEqual(rp.sbatch_options("-N 2 -n=4 -Cgpu"), [("-N", "2"), ("-n", "4"), ("-C", "gpu")])
        text = "#!/bin/bash\n#SBATCH -N1 -n4\n#SBATCH -c2\n"
        self.assertEqual(rp.sbatch_blocks(text), [(2, {"nodes": 1, "ntasks": 4, "cpus_per_task": 2})])
        self.assertEqual(rp.check_scripts("src", self.profiles["src"], {"j.sh": text}),
                         ["src: j.sh:2 asks 8 CPUs per node, limit 2"])

    def test_override_cannot_unset_a_base_option(self):
        base = {"nodes": 2, "ntasks": 8, "ntasks_per_node": 4}
        self.assertEqual(rp.override({"nodes": 1, "ntasks": 2, "ntasks_per_node": 2}, base),
                         "--nodes=1 --ntasks=2 --ntasks-per-node=2")
        with self.assertRaisesRegex(ValueError, "--ntasks-per-node"):
            rp.override({"nodes": 1, "ntasks": 2}, base)

    def test_validate_rejects_unpinned_multi_node_jobs(self):
        prof = {"jobs": {"m": {"j": {"nodes": 3, "ntasks": 6}}}}
        self.assertTrue(any("without --ntasks-per-node" in p for p in rp.validate("x", prof)))
        prof["jobs"]["m"]["j"]["ntasks"] = 3
        self.assertEqual(rp.validate("x", prof), [])
        src = copy.deepcopy(self.profiles["src"])
        del src["jobs"]["hybrid"]["ex4"]["ntasks_per_node"]
        self.assertEqual(rp.validate("src", src),
                         ["src: jobs.hybrid.ex4 spreads 6 tasks over 3 nodes without --ntasks-per-node"])

    def test_lint_catches_one_line_stack_load(self):
        prof = self.profiles["src"]
        self.assertTrue(rp.lint(prof, {"x.sh": "module load 2025 foss/2025a\n"}))
        self.assertFalse(rp.lint(prof, {"x.sh": "module load 2025   # stack\n"}))
        for line in ("[learner@int6 ~]$ module load 2025 foss/2025a", "$ module load 2025 foss/2025a",
                     "module   load 2025 GCC/14.2.0"):
            self.assertTrue(rp.lint(prof, {"x.sh": line + "\n"}), line)
        for line in ("module load 2025 && module load foss/2025a", "module load 2025; module load foss/2025a"):
            self.assertFalse(rp.lint(prof, {"x.sh": line + "\n"}), line)

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
            (root / "course-module-x" / "hands-on" / "build").write_text("#!/bin/bash\nmodule load 2025\n")
            (root / "course-module-x" / "hands-on" / "notes").write_text("module load 2025 x\n")
            files = rp.course_files(root)
            self.assertEqual(sorted(files), ["course-module-x/README.md", "course-module-x/hands-on/build",
                                             "course-module-x/hands-on/run.sh"])
            self.assertEqual(rp.lint(prof, files), ["course-module-x/hands-on/run.sh:1: module load 2025 foss/2025a"])
            self.assertEqual(rp.course_files(root, skip={"course-module-x/hands-on/run.sh"}).keys(),
                             {"course-module-x/README.md", "course-module-x/hands-on/build"})

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
