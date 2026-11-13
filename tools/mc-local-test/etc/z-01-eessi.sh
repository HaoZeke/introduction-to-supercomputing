# Login initialisation for EESSI 2025.06, same role as Magic Castle's
# /etc/profile.d/z-01-site.sh. Guest uids start at 60001.
# ssh sets USER; a non-login exec as this uid may not, and the exercises use it.
if [ "$(id -u)" -ge 60001 ]; then
    if [ -z "${USER:-}" ]; then
        USER=$(id -un)
        export USER
    fi
    if [ -z "${LOGNAME:-}" ]; then
        LOGNAME=$USER
        export LOGNAME
    fi
    if [ -r /cvmfs/software.eessi.io/versions/2025.06/init/Magic_Castle/bash ]; then
        # shellcheck disable=SC1091
        . /cvmfs/software.eessi.io/versions/2025.06/init/Magic_Castle/bash
    elif [ -r /cvmfs/software.eessi.io/versions/2025.06/init/bash ]; then
        EESSI_SILENT=1
        # shellcheck disable=SC1091
        . /cvmfs/software.eessi.io/versions/2025.06/init/bash
    fi
fi
