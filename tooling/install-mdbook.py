"""Install a checksum-verified upstream release binary during image construction."""
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
version = config["mdbook_version"]
url = f"https://github.com/rust-lang/mdBook/releases/download/v{version}/mdbook-v{version}-{asset['target']}.tar.gz"
with urllib.request.urlopen(url, timeout=120) as response:
    archive = response.read()
if hashlib.sha256(archive).hexdigest() != asset["sha256"]:
    raise SystemExit("mdBook release checksum mismatch")
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
    member = next(item for item in tar.getmembers() if item.name in ("mdbook", "./mdbook"))
    if not member.isfile():
        raise SystemExit("Expected a regular mdbook executable")
    executable = tar.extractfile(member)
    Path('/usr/local/bin/mdbook').write_bytes(executable.read())
os.chmod('/usr/local/bin/mdbook', 0o755)
