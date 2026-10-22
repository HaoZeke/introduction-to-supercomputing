# Teach the first successful job

`lesson.tex` gives instructors a short path from the shell through a verified
job to parallelism, files and workflows. Its main path ends with learner
questions. Full runnable scripts, numerical checks and resource examples
follow the backup divider. The longer module decks remain the extended
reference for architecture, accounting, profiler details and site policy.

Build on the remote build host with `bash teaching/build.sh`. The output is
`teaching/lesson.pdf`. Listings use `inputminted` to read the runnable files
at build time; edits to those files appear in the PDF without copying code.
The fundamentals deck also includes its OpenMP job directly from `pi.sh`.

Before teaching, use the controller's `pixi run rehearse --course PATH`
command inside a two-task Slurm allocation. It checks independent numerical
answers and workflow task failures in a separate copy of this checkout.
The command needs the course software modules and HyperQueue executable;
its guide is `surf-controller-mc/docs/teaching.md`. The controller's live
rehearsal checks the specific deployment as a learner. Read the SRC resource
overrides rather than submitting Snellius-sized allocations to small VMs.
