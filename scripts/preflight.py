#!/usr/bin/env python3
"""Fast pre-build check (~1-2 min, no image build): will these inputs resolve?

Downloads the pinned collections in parallel, extracts them, runs ansible-builder's own
introspection on them (so the combined requirements are exactly what the image build
produces), then runs the same uv-based conflict resolver the build uses
(scripts/resolve_python_deps.py). Prints which collections'
Python requirements would be dropped, and exits non-zero only if the core
requirements (requirements.txt) can't resolve, i.e. the build would fail.

Run it with scripts/preflight.sh (UBI 10 container, same as the build), or inside a
Python 3.12 environment: pip install ansible-builder==3.1.1 uv ansible-core==<pin>
ansible-runner && python3 scripts/preflight.py [--install-system]
"""
import concurrent.futures
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile

import ansible_builder

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prefetch_collections import download  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def extract(tarball, collections_root):
    ns, name = tarball.name.split("-")[:2]
    target = collections_root / "ansible_collections" / ns / name
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball) as tar:
        tar.extractall(target, filter="data")


def install_system_packages(bindep):
    """Install the RPMs the build stage would (so sdists that compile can be resolved)."""
    packages = []
    for line in bindep.read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name, _, profile = line.partition("[")
        platforms = re.findall(r"platform:(\S+?)(?=[\s\]])", profile)
        if not platforms or any(p in ("rpm", "redhat", "rhel", "centos") for p in platforms):
            packages.append(name.split()[0])
    subprocess.run(["dnf", "install", "-y", "-q", "--setopt=strict=0", "--setopt=install_weak_deps=0", *sorted(set(packages))],
                   check=False, stdout=subprocess.DEVNULL)


def main():
    requirements_yml = ROOT / "requirements.yml"
    pins = re.findall(r"name:\s*([\w]+\.[\w]+),\s*version:\s*([\w.\-]+)", requirements_yml.read_text())
    dest = pathlib.Path(tempfile.mkdtemp())
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        tarballs = dict(zip((n for n, _ in pins), pool.map(lambda p: download(p, dest), pins)))
    missing = [n for n, t in tarballs.items() if t is None]
    if missing:
        print(f"preflight: couldn't download {missing}; the build will retry them")

    collections_root = dest / "collections"
    for tarball in filter(None, tarballs.values()):
        extract(tarball, collections_root)

    # ansible-builder's own introspection: same discovery and default exclusions as the build.
    introspect = pathlib.Path(ansible_builder.__file__).parent / "_target_scripts" / "introspect.py"
    combined, bindep = dest / "requirements.txt", dest / "bindep.txt"
    subprocess.run(
        [sys.executable, str(introspect), "introspect", str(collections_root),
         f"--user-pip={ROOT / 'requirements.txt'}", f"--user-bindep={ROOT / 'bindep.txt'}",
         f"--write-pip={combined}", f"--write-bindep={bindep}"],
        check=True, stdout=subprocess.DEVNULL,
    )
    if "--install-system" in sys.argv:
        install_system_packages(bindep)
    # Same sanitising as scripts/pre-pip-hook.sh: drop references to files that never ship.
    kept = [l for l in combined.read_text().splitlines() if not re.match(r"\s*-(c|r|-constraint|-requirement)[\s=]", l)]
    combined.write_text("\n".join(kept) + "\n")

    report = dest / "report.txt"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/resolve_python_deps.py"), str(combined), str(requirements_yml),
         str(report), str(ROOT / "optional-requirements.txt")],
        check=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
