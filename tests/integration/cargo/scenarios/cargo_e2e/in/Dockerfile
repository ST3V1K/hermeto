FROM docker.io/rust:1.75 as builder

COPY . /source

WORKDIR /source

RUN cargo build --release

FROM registry.fedoraproject.org/fedora-minimal:45

COPY --from=builder /source/target/release/rustic /bin/rustic

ENTRYPOINT ["rustic"]
