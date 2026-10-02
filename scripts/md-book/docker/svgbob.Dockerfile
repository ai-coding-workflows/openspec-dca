ARG RUST_IMAGE=rust:1.94-bookworm
FROM ${RUST_IMAGE}
RUN apt-get update && apt-get install -y --no-install-recommends musl-tools gcc-mingw-w64-x86-64 \
    && rm -rf /var/lib/apt/lists/*
ENV CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER=x86_64-w64-mingw32-gcc
WORKDIR /source
CMD ["sh", "-ec", "git init .; git remote add origin https://github.com/boozook/mdbook-svgbob.git; git fetch --depth 1 origin \"$SVGBOB_REVISION\"; git checkout --detach FETCH_HEAD; rustup target add \"$SVGBOB_TARGET\"; cargo build --locked --release --target \"$SVGBOB_TARGET\"; mkdir /output; cp target/\"$SVGBOB_TARGET\"/release/mdbook-svgbob* /output/"]
