ARG DOCS_WITH_D2=false
FROM rust:1.94-bookworm@sha256:6ae102bdbf528294bc79ad6e1fae682f6f7c2a6e6621506ba959f9685b308a55 AS d2-preprocessor
RUN cargo install mdbook-d2 --version 0.3.9 --locked --root /opt/d2-tools

FROM golang:1.24-bookworm@sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac AS d2-compiler
RUN GOBIN=/opt/d2-tools/bin go install oss.terrastruct.com/d2@v0.7.1

FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS d2-false

FROM d2-false AS d2-true
COPY --from=d2-preprocessor /opt/d2-tools/bin/mdbook-d2 /usr/local/bin/
COPY --from=d2-compiler /opt/d2-tools/bin/d2 /usr/local/bin/

FROM d2-${DOCS_WITH_D2}
ARG TARGETARCH
ARG DOCS_WITH_MERMAID=false
COPY toolchain.json install-mdbook.py /opt/docs-toolchain/
RUN python3 /opt/docs-toolchain/install-mdbook.py "$TARGETARCH" \
    && mdbook --version \
    && if [ "$DOCS_WITH_MERMAID" = true ]; then mdbook-mermaid --version; fi
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /book
ENTRYPOINT ["mdbook"]
CMD ["build"]
