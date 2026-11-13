#!/bin/bash
# Bring up one role of the local Magic Castle-like cluster.
set -eu

role="${1:-}"

log() {
    printf 'mc-local: %s\n' "$*"
}

# Addresses are pinned in compose.yaml so every node can resolve the others
# before Docker's DNS replies. Slurm records "NO NETWORK ADDRESS FOUND" if
# the controller cannot resolve a node name at registration.
seed_hosts() {
    local ip h
    while read -r ip h; do
        if grep -qE "[[:space:]]${h}([[:space:]]|$)" /etc/hosts; then
            continue
        fi
        echo "${ip} ${h}" >> /etc/hosts
    done <<'EOF'
172.30.13.2 mgmt1
172.30.13.3 login1
172.30.13.4 node1
172.30.13.5 node2
EOF
}

require_hosts() {
    seed_hosts
    local h
    for h in "$@"; do
        if ! grep -qE "[[:space:]]${h}([[:space:]]|$)" /etc/hosts; then
            log "missing host ${h}"
            cat /etc/hosts
            return 1
        fi
    done
}

setup_munge() {
    if [ ! -s /run/munge.key ]; then
        log "missing /run/munge.key"
        exit 1
    fi
    install -o munge -g munge -m 0400 /run/munge.key /etc/munge/munge.key
    mkdir -p /run/munge
    chown munge:munge /run/munge
    if ! pgrep -x munged >/dev/null 2>&1; then
        runuser -u munge -- munged
    fi
}

mount_one() {
    local share="$1" dest="$2" i
    mkdir -p "${dest}"
    if mountpoint -q "${dest}"; then
        return 0
    fi
    for i in $(seq 1 40); do
        if mount -t nfs4 \
            -o proto=tcp,nosuid,nolock,noatime,actimeo=3,nfsvers=4.2,soft,timeo=20,retrans=2 \
            "mgmt1:/${share}" "${dest}"; then
            log "mounted ${share} on ${dest}"
            return 0
        fi
        sleep 2
    done
    log "failed to mount ${share}"
    return 1
}

mount_cvmfs() {
    mkdir -p /cvmfs/software.eessi.io /var/lib/cvmfs
    if mountpoint -q /cvmfs/software.eessi.io; then
        log "cvmfs already mounted"
        return 0
    fi
    log "mounting software.eessi.io"
    mount -t cvmfs software.eessi.io /cvmfs/software.eessi.io
    local i
    for i in $(seq 1 30); do
        if [ -r /cvmfs/software.eessi.io/versions/2025.06/init/bash ]; then
            log "EESSI 2025.06 is visible"
            return 0
        fi
        sleep 2
    done
    log "EESSI 2025.06 init script did not appear"
    ls -la /cvmfs/software.eessi.io || true
    return 1
}

install_slurm_conf() {
    mkdir -p /etc/slurm /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/run/slurmctld /localscratch
    cp /opt/mc/etc/slurm.conf /etc/slurm/slurm.conf
    cp /opt/mc/etc/cgroup.conf /etc/slurm/cgroup.conf
    cp /opt/mc/etc/plugstack.conf /etc/slurm/plugstack.conf
    cp /opt/mc/etc/epilog /etc/slurm/epilog
    chmod 755 /etc/slurm/epilog
    chown slurm:slurm /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/run/slurmctld
    chmod 1777 /localscratch
    install -m 0644 /opt/mc/etc/z-01-eessi.sh /etc/profile.d/z-01-eessi.sh
}

prepare_cgroup() {
    if [ ! -f /sys/fs/cgroup/cgroup.controllers ]; then
        log "cgroup v2 controllers file is missing"
        return 0
    fi
    mkdir -p /sys/fs/cgroup/init
    local p c
    for p in $(cat /sys/fs/cgroup/cgroup.procs); do
        echo "${p}" > /sys/fs/cgroup/init/cgroup.procs 2>/dev/null || true
    done
    for c in $(cat /sys/fs/cgroup/cgroup.controllers); do
        echo "+${c}" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null || true
    done
    # slurmd's cgroup/v2 plugin (IgnoreSystemd) creates its scope under system.slice.
    mkdir -p /sys/fs/cgroup/system.slice
    for c in $(cat /sys/fs/cgroup/cgroup.controllers); do
        echo "+${c}" > /sys/fs/cgroup/system.slice/cgroup.subtree_control 2>/dev/null || true
    done
    log "cgroup subtree: $(cat /sys/fs/cgroup/cgroup.subtree_control)"
    log "system.slice subtree: $(cat /sys/fs/cgroup/system.slice/cgroup.subtree_control 2>/dev/null || echo missing)"
}

prepare_export() {
    mkdir -p /export/home/user01/projects /export/scratch/user01 /export/project/60001 /var/log/ganesha /var/lib/nfs/ganesha/v4recov
    if [ ! -L /export/project/def-sponsor00 ]; then
        ln -s /project/60001 /export/project/def-sponsor00
    fi
    if [ ! -L /export/home/user01/scratch ]; then
        ln -s /scratch/user01 /export/home/user01/scratch
    fi
    if [ ! -L /export/home/user01/projects/def-sponsor00 ]; then
        ln -s /project/def-sponsor00 /export/home/user01/projects/def-sponsor00
    fi
    if [ ! -f /export/home/user01/.bashrc ]; then
        cp /etc/skel/.bashrc /export/home/user01/.bashrc
        cp /etc/skel/.profile /export/home/user01/.profile
    fi
    chown -R 60001:60001 /export/home/user01 /export/scratch/user01
    chown root:60001 /export/project/60001
    chmod 750 /export/home/user01 /export/scratch/user01
    chmod 755 /export/home/user01/projects
    chmod 2770 /export/project/60001
    touch /export/.ready
}

unset INVOCATION_ID || true

case "${role}" in
    nfs)
        prepare_export
        log "starting nfs-ganesha"
        exec ganesha.nfsd -F -L /var/log/ganesha/ganesha.log -f /opt/mc/etc/ganesha.conf -p /var/run/ganesha.nfsd.pid
        ;;
    login)
        # Nodes start only after this container is healthy, so do not wait for them.
        require_hosts mgmt1 login1 node1 node2
        setup_munge
        mount_one home /home
        mount_one project /project
        mount_one scratch /scratch
        mount_cvmfs
        install_slurm_conf
        log "starting slurmctld"
        exec slurmctld -D -f /etc/slurm/slurm.conf -vv
        ;;
    slurmd)
        require_hosts mgmt1 login1 node1 node2
        setup_munge
        mount_one home /home
        mount_one project /project
        mount_one scratch /scratch
        mount_cvmfs
        install_slurm_conf
        prepare_cgroup
        log "starting slurmd on $(hostname -s)"
        exec slurmd -D -f /etc/slurm/slurm.conf -vv
        ;;
    *)
        echo "usage: entrypoint.sh {nfs|login|slurmd}" >&2
        exit 1
        ;;
esac
