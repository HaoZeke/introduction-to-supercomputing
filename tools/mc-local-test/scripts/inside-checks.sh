#!/bin/bash
# Exercises from course-module-src-eessi-fs, run on the login node as user01.
set -u
cd "$HOME"
echo "===== identity ====="
echo "USER=$USER HOME=$HOME"
pwd
df -hT /home /scratch /project
du -sh "$HOME"
echo "===== links ====="
ls -ld ~/scratch ~/projects/def-sponsor00 /scratch/$USER /project/def-sponsor00
echo "===== scratch file ====="
touch /scratch/$USER/testfile-scratch.foo
ls /scratch/$USER/
echo "===== login /tmp vs compute ====="
echo "a file on login1" > /tmp/testfile-login1.foo
cat /tmp/testfile-login1.foo
srun -t 5 ls -l /scratch/$USER/ /tmp/
echo "srun_ls_rc=$?"
echo "===== node-local script, twice ====="
cat > "$HOME/files.slurm" <<'EOF'
#!/bin/bash
#SBATCH -J files
#SBATCH -t 5

LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0
ls -l $LOCAL
hostname -s > "$LOCAL/testfile.foo"
ls -l $LOCAL
echo $LOCAL
ls -l /tmp
echo "TMPDIR=${TMPDIR-<unset>}"
echo "SLURM_TMPDIR=${SLURM_TMPDIR-<unset>}"
EOF
chmod +x "$HOME/files.slurm"
j1=$(sbatch --parsable "$HOME/files.slurm")
j2=$(sbatch --parsable "$HOME/files.slurm")
echo "jobs $j1 $j2"
for j in $j1 $j2; do
    for i in $(seq 1 60); do
        squeue -h -j "$j" | grep -q . || break
        sleep 2
    done
    echo "----- slurm-$j.out -----"
    cat "$HOME/slurm-$j.out" || true
    sacct -j "$j" --format=JobID,State,ExitCode,NodeList -P
done
echo "===== localscratch copy exercise ====="
cat > "$HOME/localscratch-test.slurm" <<'EOF'
#!/bin/bash
#SBATCH -J localscratch-test
#SBATCH -t 5

LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0
echo "This is a file on node-local scratch" > "$LOCAL/testfile-local.foo"
cp "$LOCAL/testfile-local.foo" /scratch/$USER/
realpath "$LOCAL/testfile-local.foo" /scratch/$USER/testfile-local.foo
EOF
j3=$(sbatch --parsable "$HOME/localscratch-test.slurm")
for i in $(seq 1 60); do
    squeue -h -j "$j3" | grep -q . || break
    sleep 2
done
echo "----- slurm-$j3.out -----"
cat "$HOME/slurm-$j3.out" || true
ls -l /scratch/$USER/testfile-local.foo
echo "===== project and EESSI ====="
df -h /project
echo "EESSI_VERSION=$EESSI_VERSION"
module avail GCC 2>&1 | grep -E 'GCC/14.3.0|GCC/13.2.0' || true
module avail pigz 2>&1 | grep pigz/2.8 || true
module avail zstd 2>&1 | grep zstd/1.5 || true
echo "===== switch to EESSI/2023.06 ====="
bash -lc 'module use /cvmfs/software.eessi.io/init/modules && module load EESSI/2023.06 && echo SWITCHED=$EESSI_VERSION && module avail GCC 2>&1 | grep -E "GCC/" | head'
echo "===== ex1/run.sh ====="
rm -rf "$HOME/course-module-src-eessi-fs"
cp -a /opt/course "$HOME/course-module-src-eessi-fs"
cd "$HOME/course-module-src-eessi-fs/ex1"
j4=$(sbatch --parsable run.sh)
echo "ex1 job $j4"
for i in $(seq 1 400); do
    squeue -h -j "$j4" | grep -q . || break
    sleep 3
done
echo "----- ex1 slurm-$j4.out -----"
cat "slurm-$j4.out" || true
sacct -j "$j4" --format=JobID,State,ExitCode,MaxRSS,Elapsed -P
ls -lh "$HOME/ex1.dat" || true
echo "===== file transfer ====="
cd "$HOME"
rm -rf "$HOME/file_transfer_test" "$HOME/file_transfer_test.tar.gz"
mkdir "$HOME/file_transfer_test"
cd "$HOME/file_transfer_test"
for i in {1..1000}; do
    head -c 1M </dev/urandom > "file_$i.bin"
done
du -sh "$HOME/file_transfer_test"
echo "----- individual copy -----"
TIMEFORMAT='individual_copy %R sec'
{ time cp -r "$HOME/file_transfer_test" /scratch/$USER/; } 2>&1
cd "$HOME"
echo "----- tar gzip -----"
TIMEFORMAT='tar_gzip %R sec'
{ time tar -czf file_transfer_test.tar.gz file_transfer_test; } 2>&1
du -sh file_transfer_test.tar.gz
module load pigz/2.8-GCCcore-14.3.0
echo "----- tar pigz -----"
TIMEFORMAT='tar_pigz %R sec'
{ time tar -I pigz -cf file_transfer_test.tar.gz file_transfer_test; } 2>&1
du -sh file_transfer_test.tar.gz
echo "----- archive copy -----"
TIMEFORMAT='archive_copy %R sec'
{ time cp file_transfer_test.tar.gz /scratch/$USER/; } 2>&1
cd /scratch/$USER/
tar -xzf file_transfer_test.tar.gz
echo "extracted $(find /scratch/$USER/file_transfer_test -type f | wc -l) files"
echo "===== srun --pty ====="
cd "$HOME"
script -q -e -c "srun -t 15 --pty bash" /tmp/pty-session.log <<EOF
echo PTY_START
tty
echo TMPDIR=\${TMPDIR-<unset>}
echo SLURM_TMPDIR=\${SLURM_TMPDIR-<unset>}
LOCAL=/localscratch/\$USER.\$SLURM_JOB_ID.0
echo LOCAL=\$LOCAL
time cp /scratch/\$USER/file_transfer_test.tar.gz \$LOCAL/
time tar -xzf \$LOCAL/file_transfer_test.tar.gz -C \$LOCAL
echo PTY_DONE
exit
EOF
echo "----- pty log -----"
cat /tmp/pty-session.log
echo "===== cgroup memory ====="
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
run_alloc() {
    local label="$1" mem="$2" mb="$3" jid
    if [ -n "$mem" ]; then
        jid=$(sbatch --parsable -J "$label" -t 2 --mem="$mem" --wrap "$HOME/alloc $mb")
    else
        jid=$(sbatch --parsable -J "$label" -t 2 --wrap "$HOME/alloc $mb")
    fi
    echo "cgroup job $label id=$jid mem=${mem:-default} touch=${mb}MB"
    for i in $(seq 1 40); do
        squeue -h -j "$jid" | grep -q . || break
        sleep 2
    done
    echo "----- $label slurm-$jid.out -----"
    cat "$HOME/slurm-$jid.out" || true
    sacct -j "$jid" --format=JobID,JobName,State,ExitCode,MaxRSS,ReqMem -P
}
run_alloc under 512M 100
run_alloc over 128M 400
run_alloc default_over "" 400
echo "===== cleanup transfer files ====="
rm -rf "$HOME/file_transfer_test" "$HOME/file_transfer_test.tar.gz"
rm -rf /scratch/$USER/file_transfer_test /scratch/$USER/file_transfer_test.tar.gz
echo "===== checks done ====="
