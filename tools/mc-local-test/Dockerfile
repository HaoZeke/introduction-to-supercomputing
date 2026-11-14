FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d && chmod 755 /usr/sbin/policy-rc.d

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        bsdutils \
        ca-certificates \
        curl \
        fuse3 \
        gcc \
        gpg \
        iproute2 \
        libslurm-dev \
        make \
        munge \
        nfs-common \
        nfs-ganesha \
        procps \
        python3 \
        rpcbind \
        slurm-wlm \
        slurm-wlm-basic-plugins \
        wget \
        nfs-ganesha-vfs \
    && rm -rf /var/lib/apt/lists/*

# CernVM-FS 2.14.1, mounted by hand in entrypoint.sh (no systemd here).
# cvmfs-config-eessi 0.6.0 is the config package the EESSI client expects.
RUN wget -O /tmp/cvmfs-release.deb https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb \
    && dpkg -i /tmp/cvmfs-release.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        cvmfs=2.14.1+ubuntu24.04 \
        cvmfs-fuse3=2.14.1+ubuntu24.04 \
        cvmfs-libs=2.14.1+ubuntu24.04 \
    && wget -O /tmp/cvmfs-config-eessi.deb https://github.com/EESSI/filesystem-layer/releases/download/v0.6.0/cvmfs-config-eessi_0.6.0_all.deb \
    && dpkg -i /tmp/cvmfs-config-eessi.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/*.deb

COPY etc/cvmfs-default.local /etc/cvmfs/default.local

# Compute Canada spank-cc-tmpfs, built against this image's Slurm.
COPY spank /opt/spank-cc-tmpfs
RUN make -C /opt/spank-cc-tmpfs \
    && cp /opt/spank-cc-tmpfs/cc-tmpfs_mounts.so /usr/lib/x86_64-linux-gnu/slurm-wlm/cc-tmpfs_mounts.so

COPY etc /opt/mc/etc
COPY entrypoint.sh /opt/mc/entrypoint.sh

RUN chmod 755 /opt/mc/entrypoint.sh \
    && groupadd -g 60001 def-sponsor00 \
    && useradd -u 60001 -g 60001 -d /home/user01 -M -s /bin/bash user01 \
    && mkdir -p /var/log/slurm /var/spool/slurm /var/spool/slurmd /var/run/slurmctld /var/log/ganesha /var/lib/nfs/ganesha /localscratch \
    && chown slurm:slurm /var/log/slurm /var/spool/slurm /var/spool/slurmd /var/run/slurmctld \
    && chmod 1777 /localscratch

ENTRYPOINT ["/opt/mc/entrypoint.sh"]
