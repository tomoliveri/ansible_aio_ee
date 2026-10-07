#!/usr/bin/env python3
"""Download every pinned collection in parallel and install them offline in one go.

ansible-galaxy downloads ~170 collections one at a time (~40 minutes). This runs in
the ansible-builder "galaxy" stage before its own install step, which then finds the
collections already installed. Anything that fails here is left for that step to
fetch, so this can only make the build faster, never break it.

Usage: prefetch_collections.py REQUIREMENTS_YML COLLECTIONS_PATH
"""
import concurrent.futures
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

ARTIFACT = "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/{ns}-{name}-{version}.tar.gz"


def download(item, dest):
    name, version = item
    ns, coll = name.split(".")
    target = dest / f"{ns}-{coll}-{version}.tar.gz"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(ARTIFACT.format(ns=ns, name=coll, version=version), timeout=120) as resp:
                target.write_bytes(resp.read())
            return target
        except Exception as exc:  # noqa: BLE001 - retry, then leave it to ansible-galaxy
            if attempt == 3:
                print(f"prefetch: giving up on {name}:{version}: {exc}", flush=True)
            time.sleep(2 ** attempt)
    return None


def main():
    requirements, collections_path = pathlib.Path(sys.argv[1]), sys.argv[2]
    pins = re.findall(r"name:\s*([\w]+\.[\w]+),\s*version:\s*([\w.\-]+)", requirements.read_text())
    dest = pathlib.Path(tempfile.mkdtemp())
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        files = [f for f in pool.map(lambda p: download(p, dest), pins) if f]
    print(f"prefetch: downloaded {len(files)}/{len(pins)} collections in {time.time() - start:.0f}s", flush=True)
    if files:
        result = subprocess.run(
            ["ansible-galaxy", "collection", "install", "--offline", "--no-deps",
             "-p", collections_path, *map(str, files)],
            capture_output=True, text=True, check=False,
        )
        print(f"prefetch: offline install rc={result.returncode} in {time.time() - start:.0f}s total", flush=True)
        if result.returncode:
            print(result.stdout[-2000:], result.stderr[-2000:], flush=True)


if __name__ == "__main__":
    main()
