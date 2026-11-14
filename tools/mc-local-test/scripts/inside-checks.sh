#!/bin/bash
# Exercises from course-module-src-eessi-fs, run on the login node as user01.
# MC_SCOPE=all runs every exercise. MC_SCOPE=ci skips the 1000-file transfer.
set -u

scope=${MC_SCOPE:-all}
fail=0
results=()

record() {
    local name=$1 status=$2 secs=$3
    results+=("${name}|${status}|${secs}")
    printf 'RESULT %-36s %s %ss\n' "$name" "$status" "$secs"
    if [ "$status" != PASS ]; then
        fail=1
    fi
}

time_run() {
    local name=$1
    shift
    local start status
    start=$SECONDS
    if "$@"; then
        status=PASS
    else
        status=FAIL
        echo "exercise failed: $name" >&2
    fi
    record "$name" "$status" "$((SECONDS - start))"
}

wait_job() {
    local j=$1 want=$2 i state
    for i in $(seq 1 90); do
        if ! squeue -h -j "$j" | grep -q .; then
            break
        fi
        sleep 2
    done
    if squeue -h -j "$j" | grep -q .; then
        echo "job $j still queued" >&2
        scontrol show job "$j" >&2 || true
        return 1
    fi
    state=$(scontrol show job "$j" 2>/dev/null | sed -n 's/.*JobState=\([^ ]*\).*/\1/p' | head -n 1)
    echo "job $j JobState=${state:-unknown}"
    [ "$state" = "$want" ]
}

cvmfs_pin() {
    cvmfs2 --version | grep -q '2.14.1'
}

home_identity() {
    cd "$HOME" || return 1
    [ "$(pwd)" = "$HOME" ] || return 1
    df -hT /home /scratch /project >/dev/null || return 1
    du -sh "$HOME" >/dev/null || return 1
}

scratch_links() {
    ls -ld "$HOME/scratch" "$HOME/projects/def-sponsor00" /scratch/"$USER" /project/def-sponsor00 >/dev/null || return 1
    [ -d /scratch/"$USER" ] || return 1
    [ -d /project/def-sponsor00 ] || return 1
}

scratch_file() {
    touch /scratch/"$USER"/testfile-scratch.foo || return 1
    [ -f /scratch/"$USER"/testfile-scratch.foo ]
}

login_tmp_vs_compute() {
    echo "a file on login1" > /tmp/testfile-login1.foo || return 1
    grep -q 'a file on login1' /tmp/testfile-login1.foo || return 1
    srun -t 5 bash -c 'ls -l /scratch/$USER/ /tmp/; test -f /scratch/$USER/testfile-scratch.foo; test ! -e /tmp/testfile-login1.foo'
}

slides_nav() {
    cd "$HOME" || return 1
    [ "$(pwd)" = "$HOME" ] || return 1
    cd "$HOME/scratch" || return 1
    [ "$(pwd)" = "$HOME/scratch" ] || return 1
    ls >/dev/null || return 1
    cd "$HOME" || return 1
    [ "$(pwd)" = "$HOME" ]
}

slides_files() {
    cd "$HOME" || return 1
    touch "$HOME/slide-file.txt" || return 1
    printf 'edited\n' > "$HOME/slide-file.txt" || return 1
    grep -q edited "$HOME/slide-file.txt" || return 1
    cp "$HOME/slide-file.txt" "$HOME/scratch/" || return 1
    mv "$HOME/scratch/slide-file.txt" "$HOME/scratch/slide-file-renamed.txt" || return 1
    [ -f "$HOME/scratch/slide-file-renamed.txt" ]
}

slides_dirs() {
    cd "$HOME" || return 1
    mkdir "$HOME/slide-dir" || return 1
    cd "$HOME/slide-dir" || return 1
    ls >/dev/null || return 1
    cd "$HOME" || return 1
    rmdir "$HOME/slide-dir"
}

slides_perm() {
    chmod 644 "$HOME/slide-file.txt" || return 1
    [ "$(stat -c %a "$HOME/slide-file.txt")" = 644 ] || return 1
    printf 'shared\n' > "$HOME/projects/def-sponsor00/slide-shared.txt" || return 1
    chmod 644 "$HOME/projects/def-sponsor00/slide-shared.txt" || return 1
    [ "$(stat -c %a "$HOME/projects/def-sponsor00/slide-shared.txt")" = 644 ]
}

slides_disk() {
    df -h /home /scratch /project >/dev/null || return 1
    du -sh "$HOME" >/dev/null
}

project_dir() {
    ls -ld "$HOME/projects/def-sponsor00" >/dev/null || return 1
    df -h /project >/dev/null
}

extract_jobs() {
    python3 "$HOME/extract-sbatch.py" /opt/course/README.md --out "$HOME/sbatch-scripts" --expect 2
}

one_script() {
    local pattern=$1
    local found
    found=$(find "$HOME/sbatch-scripts" -name "$pattern" -print | head -n 1)
    [ -n "$found" ] || return 1
    printf '%s\n' "$found"
}

job_files() {
    local script j1 j2
    script=$(one_script '*-files.slurm') || return 1
    j1=$(sbatch --parsable "$script") || return 1
    j2=$(sbatch --parsable "$script") || return 1
    wait_job "$j1" COMPLETED || return 1
    wait_job "$j2" COMPLETED || return 1
    grep -q "/localscratch/$USER.$j1.0" "$HOME/slurm-$j1.out" || return 1
    grep -q "/localscratch/$USER.$j2.0" "$HOME/slurm-$j2.out" || return 1
    grep -q testfile.foo "$HOME/slurm-$j1.out" || return 1
    grep -q 'total 0' "$HOME/slurm-$j1.out" || return 1
    [ "$j1" != "$j2" ]
}

job_localscratch() {
    local script j
    script=$(one_script '*-localscratch-test.slurm') || return 1
    j=$(sbatch --parsable "$script") || return 1
    wait_job "$j" COMPLETED || return 1
    grep -q "/localscratch/$USER.$j.0/testfile-local.foo" "$HOME/slurm-$j.out" || return 1
    grep -q "/scratch/$USER/testfile-local.foo" "$HOME/slurm-$j.out" || return 1
    [ -s "/scratch/$USER/testfile-local.foo" ]
}

eessi_2025() {
    [ "${EESSI_VERSION:-}" = "2025.06" ] || return 1
    module load GCC/14.3.0 || return 1
    gcc --version | head -n 1 | grep -q '14.3.0' || return 1
    module load pigz/2.8-GCCcore-14.3.0 || return 1
    pigz --version | grep -q 'pigz 2.8' || return 1
    module load zstd/1.5.7-GCCcore-14.3.0 || return 1
    zstd --version | grep -q 'v1.5.7'
}

eessi_2023() {
    local out
    out=$(bash -lc 'set -e
module use /cvmfs/software.eessi.io/init/modules
module load EESSI/2023.06
module load GCC/13.2.0
module load pigz/2.8-GCCcore-13.2.0
module load zstd/1.5.5-GCCcore-13.2.0
gcc --version
pigz --version
zstd --version') || return 1
    printf '%s\n' "$out" | grep -q '(GCC) 13.2.0' || return 1
    printf '%s\n' "$out" | grep -q 'pigz 2.8' || return 1
    printf '%s\n' "$out" | grep -q 'v1.5.5'
}

job_ex1() {
    local j
    rm -rf "$HOME/course-module-src-eessi-fs"
    cp -a /opt/course "$HOME/course-module-src-eessi-fs"
    cd "$HOME/course-module-src-eessi-fs/ex1" || return 1
    j=$(sbatch --parsable run.sh) || return 1
    echo "ex1 job $j"
    wait_job "$j" COMPLETED || return 1
    grep -q 'Printing 1000000 elements' "slurm-$j.out" || return 1
    grep -q 'Printing 10000000 elements' "slurm-$j.out" || return 1
    grep -q 'Printing 100000000 elements' "slurm-$j.out" || return 1
    grep -q 'Buffer size \[MB\]: 800.000' "slurm-$j.out" || return 1
    [ -s "$HOME/ex1.dat" ]
}

file_count() {
    local n
    n=$(find "$1" -type f | wc -l)
    [ "$((n))" = "$2" ]
}

transfer_setup() {
    rm -rf "$HOME/file_transfer_test" "$HOME/file_transfer_test.tar.gz" "$HOME/file_transfer_test.tar.zst"
    rm -rf /scratch/"$USER"/file_transfer_test /scratch/"$USER"/file_transfer_test.tar.gz
    mkdir "$HOME/file_transfer_test" || return 1
    local i
    for i in $(seq 1 1000); do
        head -c 1M </dev/urandom > "$HOME/file_transfer_test/file_$i.bin" || return 1
    done
    du -sh "$HOME/file_transfer_test"
    file_count "$HOME/file_transfer_test" 1000
}

transfer_individual() {
    local copied
    TIMEFORMAT='individual_copy %R sec'
    { time cp -r "$HOME/file_transfer_test" /scratch/"$USER"/; } 2>&1 || return 1
    copied=$(find /scratch/"$USER"/file_transfer_test -type f | wc -l)
    [ "$((copied))" = 1000 ]
}

transfer_gzip() {
    cd "$HOME" || return 1
    TIMEFORMAT='tar_gzip %R sec'
    { time tar -czf file_transfer_test.tar.gz file_transfer_test; } 2>&1 || return 1
    du -sh file_transfer_test.tar.gz
    [ "$(stat -c %s file_transfer_test.tar.gz)" -gt 900000000 ]
}

transfer_pigz() {
    cd "$HOME" || return 1
    module load pigz/2.8-GCCcore-14.3.0 || return 1
    TIMEFORMAT='tar_pigz %R sec'
    { time tar -I pigz -cf file_transfer_test.tar.gz file_transfer_test; } 2>&1 || return 1
    du -sh file_transfer_test.tar.gz
    [ "$(stat -c %s file_transfer_test.tar.gz)" -gt 900000000 ]
}

transfer_zstd() {
    cd "$HOME" || return 1
    module load zstd/1.5.7-GCCcore-14.3.0 || return 1
    TIMEFORMAT='tar_zstd %R sec'
    { time tar -I zstd -cf file_transfer_test.tar.zst file_transfer_test; } 2>&1 || return 1
    du -sh file_transfer_test.tar.zst
    [ "$(stat -c %s file_transfer_test.tar.zst)" -gt 900000000 ]
}

transfer_archive_copy() {
    cp "$HOME/file_transfer_test.tar.gz" /scratch/"$USER"/ || return 1
    tar -xzf /scratch/"$USER"/file_transfer_test.tar.gz -C /scratch/"$USER" || return 1
    file_count /scratch/"$USER"/file_transfer_test 1000
}

pty_course() {
    cd "$HOME" || return 1
    script -q -e -c "srun -t 15 --pty bash" /tmp/pty-session.log <<EOF
echo PTY_OK
echo TMPDIR=\${TMPDIR-<unset>}
echo SLURM_TMPDIR=\${SLURM_TMPDIR-<unset>}
LOCAL=\${SLURM_TMPDIR:-/localscratch/\$USER.\$SLURM_JOB_ID.0}
time cp /scratch/\$USER/file_transfer_test.tar.gz \$LOCAL/
time tar -xzf \$LOCAL/file_transfer_test.tar.gz -C \$LOCAL
echo PTY_DONE
exit
EOF
    [ "$?" -eq 0 ] || return 1
    grep -q PTY_DONE /tmp/pty-session.log || return 1
    grep -q 'TMPDIR=/tmp' /tmp/pty-session.log || return 1
    grep -q 'SLURM_TMPDIR=/localscratch/' /tmp/pty-session.log
}

pty_short() {
    script -q -e -c "srun -t 2 --pty bash" /tmp/pty-short.log <<EOF
echo PTY_OK
echo TMPDIR=\${TMPDIR-<unset>}
echo SLURM_TMPDIR=\${SLURM_TMPDIR-<unset>}
exit
EOF
    [ "$?" -eq 0 ] || return 1
    grep -q PTY_OK /tmp/pty-short.log || return 1
    grep -q 'TMPDIR=/tmp' /tmp/pty-short.log || return 1
    grep -q 'SLURM_TMPDIR=/localscratch/' /tmp/pty-short.log
}

prepare_alloc() {
    cat > "$HOME/alloc.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    size_t mb = (argc > 1) ? strtoul(argv[1], NULL, 10) : 0;
    size_t n = mb * 1024UL * 1024UL;
    unsigned char *p = malloc(n);
    size_t i;
    if (!p) { perror("malloc"); return 2; }
    for (i = 0; i < n; i += 4096) p[i] = 1;
    printf("touched %zu MB\n", mb);
    return 0;
}
EOF
    gcc -O2 -o "$HOME/alloc" "$HOME/alloc.c"
}

cgroup_under() {
    local j
    j=$(sbatch --parsable -J under -t 2 --mem=512M --wrap "$HOME/alloc 100") || return 1
    wait_job "$j" COMPLETED || return 1
    grep -q 'touched 100 MB' "$HOME/slurm-$j.out"
}

cgroup_over() {
    local j
    j=$(sbatch --parsable -J over -t 2 --mem=128M --wrap "$HOME/alloc 400") || return 1
    wait_job "$j" OUT_OF_MEMORY
}

cgroup_default() {
    local j
    j=$(sbatch --parsable -J default_over -t 2 --wrap "$HOME/alloc 400") || return 1
    wait_job "$j" OUT_OF_MEMORY
}

cleanup_transfer() {
    rm -rf "$HOME/file_transfer_test" "$HOME/file_transfer_test.tar.gz" "$HOME/file_transfer_test.tar.zst"
    rm -rf /scratch/"$USER"/file_transfer_test /scratch/"$USER"/file_transfer_test.tar.gz
    rm -f "$HOME/slide-file.txt" "$HOME/scratch/slide-file-renamed.txt"
    rm -f "$HOME/projects/def-sponsor00/slide-shared.txt"
}

cd "$HOME" || exit 1
echo "scope=$scope EESSI_VERSION=${EESSI_VERSION:-unset} USER=$USER"

time_run cvmfs-2.14.1 cvmfs_pin
time_run home-identity home_identity
time_run scratch-links scratch_links
time_run scratch-shared-file scratch_file
time_run login-tmp-vs-compute login_tmp_vs_compute
time_run slides-navigate slides_nav
time_run slides-file-management slides_files
time_run slides-directories slides_dirs
time_run slides-permissions slides_perm
time_run slides-disk slides_disk
time_run project-dir project_dir
time_run extract-job-scripts extract_jobs
time_run job-files job_files
time_run job-localscratch job_localscratch
time_run eessi-2025.06-modules eessi_2025
time_run eessi-2023.06-gcc eessi_2023
time_run ex1-run job_ex1

if [ "$scope" = all ]; then
    time_run transfer-generate transfer_setup
    time_run transfer-individual-copy transfer_individual
    time_run transfer-tar-gzip transfer_gzip
    time_run transfer-tar-pigz transfer_pigz
    time_run transfer-tar-zstd transfer_zstd
    time_run transfer-archive-copy transfer_archive_copy
    time_run srun-pty-localscratch pty_course
else
    time_run srun-pty pty_short
fi

time_run cgroup-prepare prepare_alloc
time_run cgroup-under-512M cgroup_under
time_run cgroup-over-128M cgroup_over
time_run cgroup-default-256M cgroup_default
cleanup_transfer

echo "===== exercise table ====="
printf '%-36s %-6s %s\n' EXERCISE RESULT SECONDS
for row in "${results[@]}"; do
    IFS='|' read -r name status secs <<<"$row"
    printf '%-36s %-6s %s\n' "$name" "$status" "$secs"
done

if [ "$fail" -ne 0 ]; then
    echo "checks failed"
    exit 1
fi
echo "checks passed"
