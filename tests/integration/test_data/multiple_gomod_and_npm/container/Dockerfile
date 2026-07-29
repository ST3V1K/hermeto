FROM registry.access.redhat.com/ubi9/ubi@sha256:5bc32620d0cbdfd788723448efa1c0c04e9859c0e33f9d5545329a4550edc7ab

# Test disabled network access
RUN if getent hosts www.google.com; then echo "Has network access!"; exit 1; fi

# Install dependencies from RPM lockfile
RUN dnf -y install golang npm

WORKDIR /src/gomod-package
RUN . /tmp/hermeto.env && go build

WORKDIR /src/npm-package
RUN . /tmp/hermeto.env && npm install
