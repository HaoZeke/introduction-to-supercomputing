# Adding a cluster profile

Cluster profiles keep scheduler, software, storage, access and course-sizing
facts out of the course material. The renderer applies one TOML profile to
the shell scripts, hands-on Markdown and Org slide sources in every module.

## Render and check

Python 3.11 or newer is the only requirement.

```console
# Render every profile under build/<profile>/
python3 tools/render_profile.py --all

# Render both profiles in temporary directories, validate their jobs and
# module setup, and prove that Snellius still matches the published files.
python3 tools/render_profile.py --all --check

# Render just one profile to a chosen directory.
python3 tools/render_profile.py src --out /tmp/course-src
```

The Snellius files in the repository are the canonical published copy.
Templates live under `profiles/templates/` at the same relative paths.
Changing a template therefore requires updating its published Snellius file:

```console
python3 tools/render_profile.py snellius --out .
python3 tools/render_profile.py --all --check
python3 tools/test_render.py
```

The all-profile check compares file content and executable bits. It also
rejects jobs that exceed a profile's node limits, unsupported Slurm
constraints, missing template values, and software-stack modules loaded on
the wrong line.

## Add a cluster

1. Copy the closest profile, usually `src.toml`, to
   `profiles/<short-name>.toml`. Use a lower-case file name; that name is the
   renderer's command-line profile name.
2. Replace every fact. In particular, verify:
   - login and web-portal hosts in `[system]`;
   - CPU, graphics processing unit and staging partitions in `[partitions]`;
   - scheduler constraints, mail support and array limits in `[slurm]`;
   - course job sizes in every `[jobs.*]` table;
   - the European Environment for Scientific Software Installations
     initialization path, module path and module names in `[modules]`;
   - home, shared scratch, node-local scratch, project and archive paths in
     `[paths]`;
   - accounting and site tools in `[tools]`, `[commands]` and `[accounting]`;
   - the course node limit in `[limits]`.
3. Set `render.course_cluster` to the profile whose small teaching cluster is
   described on the course-cluster slide. For a new teaching deployment this
   is normally the new profile itself. `render.asides` lists profiles whose
   compatibility notes should appear in another profile's published copy.
4. Render and inspect the result:

   ```console
   python3 tools/render_profile.py <short-name> --out /tmp/course-<short-name>
   python3 tools/render_profile.py --all --check
   python3 tools/test_render.py
   ```

5. Check every generated job against the real scheduler before teaching:
   `sinfo`, `scontrol show config`, `module spider`, a short `sbatch` job, and
   storage commands should agree with the TOML file. Record the verification
   date in `profile.verified`.

## Template rules

The supported Mustache-style syntax and derived fields are documented in
[`DESIGN.md`](../DESIGN.md). Prefer capability flags such as `tools.ear` or
`data_movement.archive_available` over tests for a cluster name. A missing
required value is an error; use an optional section ending in `?` only when
absence is intentional.

Never edit a generated non-Snellius tree and copy it back. Edit the template
and profile, regenerate the Snellius published copy, and let the parity check
detect content drift.
