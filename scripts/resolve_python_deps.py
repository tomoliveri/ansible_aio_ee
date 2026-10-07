#!/usr/bin/env python3
"""Drop the Python requirements of collections that can't co-exist with the rest.

Runs inside the ansible-builder "builder" stage, just before pip installs the
combined requirements file that ansible-builder generated (each line is annotated
"# from collection <name>"). An all-in-one image will sooner or later contain two
vendor SDKs that pin incompatible versions of a shared library; rather than failing
the whole build, this keeps the image consistent and drops the requirements of the
fewest collections, in priority order:

  1. our own requirements.txt ("user") and non-annotated lines: must resolve
  2. collections shipped in the ansible community package
  3. extra collections, then each line of optional-requirements.txt on its own

Resolution uses `uv pip compile` (seconds, where pip's backtracking resolver can run
for hours on ~400 loose requirements). Groups are added one at a time; when a group
doesn't resolve it is bisected to find the offending collection(s). Dropped collections
stay installed (their other modules still work) and are listed in the report. The
requirements file is then rewritten as a fully pinned list, so pip has nothing left
to resolve.

Usage: resolve_python_deps.py REQUIREMENTS_TXT GALAXY_REQUIREMENTS_YML REPORT [OPTIONAL_REQUIREMENTS_TXT]
"""
import importlib.metadata
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ANNOTATION = re.compile(r"#\s*from collection\s+(\S+)\s*$")


def parse(path):
    """Return ordered (line, collection) pairs; collection None for core lines."""
    pairs = []
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = ANNOTATION.search(raw)
        owner = match.group(1) if match else None
        pairs.append((raw, None if owner == "user" else owner))
    return pairs


def bundled_collections(galaxy_reqs):
    """Collections listed in the 'shipped in the ansible community package' section."""
    names, section = set(), None
    for line in galaxy_reqs.read_text().splitlines():
        if line.strip().startswith("#"):
            section = "bundled" if "community package" in line else "other"
        match = re.search(r"name:\s*([\w.]+)", line)
        if match and section == "bundled":
            names.add(match.group(1))
    return names


CONSTRAINTS = pathlib.Path(tempfile.gettempdir()) / "aio-constraints.txt"


def write_constraints():
    """Keep the ansible-core/runner already installed in the image, plus the pip lock."""
    pins = [f"{p}=={importlib.metadata.version(p)}" for p in ("ansible-core", "ansible-runner")]
    lock = pathlib.Path(os.environ.get("PIP_CONSTRAINT") or "/nonexistent")
    if lock.is_file():
        pins += [line for line in lock.read_text().splitlines()
                 if line.strip() and not line.lower().startswith(("ansible-core==", "ansible-runner=="))]
    CONSTRAINTS.write_text("\n".join(pins) + "\n")


def resolves(lines):
    """Compile `lines` with uv. Returns (ok, pinned requirements or error text)."""
    with tempfile.NamedTemporaryFile("w", suffix=".in", delete=False) as tmp:
        tmp.write("\n".join(lines) + "\n")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "uv", "pip", "compile", tmp.name, "--python", sys.executable,
             "--constraint", str(CONSTRAINTS), "--no-header", "--no-annotate", "--quiet"],
            capture_output=True, text=True, check=False, timeout=900,
            env=dict(os.environ, UV_NO_PROGRESS="1"),
        )
        ok, out = result.returncode == 0, (result.stdout if result.returncode == 0 else result.stderr[-3000:])
    except subprocess.TimeoutExpired:
        ok, out = False, "uv pip compile timed out"
    pathlib.Path(tmp.name).unlink()
    return ok, out


def add_groups(accepted, names, reqs, dropped):
    """Add as many of `names` as resolve together with `accepted` (bisecting on failure)."""
    if not names:
        return accepted
    candidate = accepted + [line for n in names for line in reqs[n]]
    ok, err = resolves(candidate)
    if ok:
        print(f"  ok: {len(names)} collection(s)", flush=True)
        return candidate
    if len(names) == 1:
        print(f"  DROPPING Python requirements of {names[0]}:\n{err}", flush=True)
        dropped.append(names[0])
        return accepted
    mid = len(names) // 2
    accepted = add_groups(accepted, names[:mid], reqs, dropped)
    return add_groups(accepted, names[mid:], reqs, dropped)


def main():
    req_path, galaxy_reqs, report = (pathlib.Path(a) for a in sys.argv[1:4])
    pairs = parse(req_path)
    reqs = {}
    for line, owner in pairs:
        if owner:
            reqs.setdefault(owner, []).append(line)
    core = [line for line, owner in pairs if owner is None]
    bundled = bundled_collections(galaxy_reqs)
    tier2 = sorted(n for n in reqs if n in bundled)
    tier3 = sorted(n for n in reqs if n not in bundled)
    if len(sys.argv) > 4 and pathlib.Path(sys.argv[4]).is_file():
        for raw in pathlib.Path(sys.argv[4]).read_text().splitlines():
            line = raw.split("#")[0].strip()
            if line:
                name = f"optional:{line}"
                reqs[name] = [line]
                pairs.append((line, name))
                tier3.append(name)

    print(f"Resolving Python deps: core + {len(tier2)} bundled + {len(tier3)} extra collections", flush=True)
    write_constraints()
    ok, err = resolves(core)
    if not ok:
        sys.exit(f"Core requirements (requirements.txt) don't resolve on their own:\n{err}")
    dropped = []
    accepted = add_groups(core, tier2, reqs, dropped)
    accepted = add_groups(accepted, tier3, reqs, dropped)

    ok, pinned = resolves(accepted)
    if not ok:
        sys.exit(f"Final resolve failed unexpectedly:\n{pinned}")
    req_path.write_text("# Fully pinned by resolve_python_deps.py (uv pip compile)\n" + pinned)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "Collections whose Python requirements were dropped because they conflict with the rest\n"
        "of the image (the collections are installed; modules needing those libraries won't work):\n"
        + "".join(f"- {n}\n" for n in dropped) if dropped else "No collections were dropped.\n"
    )
    print(report.read_text(), flush=True)


if __name__ == "__main__":
    main()
