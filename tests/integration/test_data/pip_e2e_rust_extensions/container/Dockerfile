FROM registry.access.redhat.com/ubi10/ubi@sha256:864f6b94f9f64a059aed7dc8f95b0854f5eb06140f95aed32300da63a1f7877d

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
