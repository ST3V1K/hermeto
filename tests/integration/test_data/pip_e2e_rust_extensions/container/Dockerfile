FROM registry.access.redhat.com/ubi10/ubi@sha256:eb7b37c778c77760191b979f666258250fee158d5b0ae70b0f1de5d00b9cf698

# Test disabled network access
RUN if getent hosts www.google.com; then echo "Has network access!"; exit 1; fi

# These packages must be prefetched during the previous phase.
# Refer to the test for further details.
RUN dnf -y install \
    cargo \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-devel \
    libffi-devel \
    openssl-devel \
    perl-interpreter \
    perl-FindBin \
    perl-lib \
    perl-IPC-Cmd \
    perl-File-Compare \
    perl-File-Copy

WORKDIR /src

ARG CARGO_BUILD_JOBS
RUN . /tmp/hermeto.env \
    && python3 -m pip install -r requirements.txt

# See pip/e2e for the resasoning behind switching WORKDIR
RUN cp -r /src /app
WORKDIR /app
