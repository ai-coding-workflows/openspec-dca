"""Install checksum-verified upstream mdBook toolchain binaries."""
import hashlib
import io
import json
import os
import sys
import tarfile
import urllib.request
from pathlib import Path

config = json.loads(Path(__file__).with_name("toolchain.json").read_text())
asset = config["linux"][sys.argv[1]]

tools = (
    ("mdbook", "rust-lang/mdBook", config["mdbook_version"], asset["mdbook_sha256"]),
    (
        "mdbook-mermaid",
        "badboy/mdbook-mermaid",
        config["mdbook_mermaid_version"],
        asset["mdbook_mermaid_sha256"],
    ),
)

if os.environ.get("DOCS_WITH_MERMAID", "true") != "true":
    tools = tools[:1]

for name, repository, version, expected_digest in tools:
    url = (
        f"https://github.com/{repository}/releases/download/v{version}/"
        f"{name}-v{version}-{asset['target']}.tar.gz"
    )
    with urllib.request.urlopen(url, timeout=120) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != expected_digest:
        raise SystemExit(f"{name} release checksum mismatch")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = next((item for item in tar.getmembers() if Path(item.name).name == name), None)
        if member is None or not member.isfile():
            raise SystemExit(f"Expected a regular {name} executable")
        executable = tar.extractfile(member)
        if executable is None:
            raise SystemExit(f"Could not read {name} executable")
        destination = Path("/usr/local/bin") / name
        destination.write_bytes(executable.read())
    os.chmod(destination, 0o755)
