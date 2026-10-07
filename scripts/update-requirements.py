#!/usr/bin/env python3
"""Regenerate requirements.yml, the README collection table and the ansible-core pin from an Ansible community release.

The collection set is the one shipped in the `ansible` community package (curated
and maintained upstream), plus the extras in extra-collections.txt. Each extra and its
whole dependency tree is resolved here and pinned, so the image build installs with
--no-deps (fast, deterministic). Collections in excluded-collections.txt are dropped.

Without an argument it picks the newest ansible release whose Python requirement is met
by the base image's Python (BASE_PYTHON), so a future major that needs a newer Python
doesn't break the unattended monthly update; it keeps tracking the newest compatible line.

Usage: scripts/update-requirements.py [ANSIBLE_VERSION]
"""
import concurrent.futures
import functools
import json
import pathlib
import re
import ssl
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_PYTHON = (3, 12)  # python3 in the UBI 10 base image
BUILD_DATA = "https://raw.githubusercontent.com/ansible-community/ansible-build-data/main/{major}/ansible-{version}.deps"
GALAXY = "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/{ns}/{name}/versions/?limit=100"
GALAXY_VERSION = "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/{ns}/{name}/versions/{version}/"


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


CTX = ssl_context()


def fetch(url):
    with urllib.request.urlopen(url, timeout=60, context=CTX) as r:
        return r.read().decode()


def vkey(v):
    """Numeric sort key for X.Y.Z (pre-release suffixes ignored)."""
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def spec_ok(version, spec):
    """True if version satisfies a spec like '*', '>=2.15.0,<2.19.0' or '==1.2.3'."""
    ops = {
        ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b, ">": lambda a, b: a > b, "<": lambda a, b: a < b,
    }
    for part in filter(None, (p.strip() for p in (spec or "*").split(","))):
        op = next((o for o in (">=", "<=", "==", "!=", ">", "<") if part.startswith(o)), None)
        if op and not ops[op](vkey(version), vkey(part[len(op):])):
            return False
    return True


@functools.lru_cache(maxsize=None)
def galaxy_versions(name):
    """Stable versions of a Galaxy collection, newest first ([] if it isn't on Galaxy)."""
    ns, coll = name.split(".")
    try:
        data = json.loads(fetch(GALAXY.format(ns=ns, name=coll)))["data"]
    except Exception:  # noqa: BLE001 - missing/unreachable means "not installable"
        return []
    stable = (v["version"] for v in data if re.fullmatch(r"\d+\.\d+\.\d+", v["version"]))
    return sorted(stable, key=vkey, reverse=True)[:15]


@functools.lru_cache(maxsize=None)
def galaxy_meta(name, version):
    """(requires_ansible, dependencies) for one collection version."""
    ns, coll = name.split(".")
    detail = json.loads(fetch(GALAXY_VERSION.format(ns=ns, name=coll, version=version)))
    deps = detail.get("metadata", {}).get("dependencies") or {}
    return detail.get("requires_ansible"), tuple(sorted(deps.items()))


def _safe_meta(name, version):
    try:
        galaxy_meta(name, version)
    except Exception:  # noqa: BLE001 - resolve() retries and handles it
        pass


def resolve(name, spec, chosen, core, depth=0):
    """Add the newest workable version of `name` and its whole dependency tree to `chosen`.

    A version is workable if it matches `spec`, supports this ansible-core, and every
    dependency (recursively) is on Galaxy and agrees with what's already pinned.
    `chosen` is only modified on success.
    """
    if name in chosen:
        return spec_ok(chosen[name], spec)
    if depth > 10:
        return False
    for version in galaxy_versions(name):
        if not spec_ok(version, spec):
            continue
        try:
            requires, deps = galaxy_meta(name, version)
        except Exception:  # noqa: BLE001 - unreadable metadata: try an older version
            continue
        if not spec_ok(core, requires):
            continue
        trial = dict(chosen, **{name: version})
        if all(resolve(dep, dep_spec, trial, core, depth + 1) for dep, dep_spec in deps):
            chosen.update(trial)
            return True
    return False


def resolve_extras(wanted, bundled, core):
    """Pin each wanted extra plus its dependencies; skip (with a warning) any that can't be
    satisfied from Galaxy, so one broken extra never blocks an unattended update."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:  # warm the caches in parallel
        pairs = [(n, v) for n, vs in zip(wanted, pool.map(galaxy_versions, wanted)) for v in vs]
        list(pool.map(lambda nv: _safe_meta(*nv), pairs))
    pinned = dict(bundled)
    for name in wanted:
        trial = dict(pinned)
        try:
            ok = resolve(name, "*", trial, core)
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"WARNING: {name}: {exc}", file=sys.stderr)
        if ok:
            pinned = trial
        else:
            print(f"WARNING: skipping {name}: no recent release supports ansible-core {core} "
                  "with all dependencies available on Galaxy", file=sys.stderr)
    return {n: v for n, v in pinned.items() if n not in bundled}


def python_ok(spec):
    """True if BASE_PYTHON satisfies a simple spec like '>=3.12' or '>=3.12,<3.15'."""
    ops = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, "<": lambda a, b: a < b}
    for part in filter(None, (p.strip() for p in spec.split(","))):
        op = next((o for o in (">=", "<=", ">", "<") if part.startswith(o)), None)
        if op and not ops[op](BASE_PYTHON, vkey(part[len(op):])[:2]):
            return False
    return True


def load_deps(version):
    deps = {}
    for line in fetch(BUILD_DATA.format(major=version.split(".")[0], version=version)).splitlines():
        key, _, value = line.partition(":")
        deps[key.strip()] = value.strip()
    return deps


def newest_compatible():
    """Newest stable ansible release on PyPI whose build data says it runs on BASE_PYTHON."""
    releases = json.loads(fetch("https://pypi.org/pypi/ansible/json"))["releases"]
    stable = sorted((v for v in releases if re.fullmatch(r"\d+\.\d+\.\d+", v)), key=vkey, reverse=True)
    for version in stable[:60]:
        try:
            deps = load_deps(version)
        except Exception:  # noqa: BLE001 - no build data for this release; try the next
            continue
        if python_ok(deps.get("_python", "")):
            return version, deps
        print(f"skipping ansible {version}: needs Python {deps.get('_python')}", file=sys.stderr)
    sys.exit("no compatible ansible release found")


def read_list(name):
    path = ROOT / name
    if not path.exists():
        return []
    return [l.split("#")[0].strip() for l in path.read_text().splitlines() if l.split("#")[0].strip()]


def main():
    if len(sys.argv) > 1:
        version, deps = sys.argv[1], load_deps(sys.argv[1])
    else:
        version, deps = newest_compatible()
    core = deps.pop("_ansible_core_version")
    collections = {k: v for k, v in deps.items() if not k.startswith("_")}

    for name in read_list("excluded-collections.txt"):
        collections.pop(name, None)
    wanted = [n for n in read_list("extra-collections.txt") if n not in collections]
    added = resolve_extras(wanted, collections, core)
    extras = {n: v for n, v in added.items() if n in wanted}
    dependencies = {n: v for n, v in added.items() if n not in wanted}

    out = [
        "---",
        f"# Generated by scripts/update-requirements.py from ansible {version} (ansible-core {core}).",
        "# Edit extra-collections.txt / excluded-collections.txt and re-run instead of editing by hand.",
        "collections:",
        f"  # Collections shipped in the ansible {version} community package",
    ]
    out += [f"  - {{name: {n}, version: {v}}}" for n, v in sorted(collections.items())]
    if extras:
        out.append("  # Extras from extra-collections.txt (newest release compatible with this ansible-core)")
        out += [f"  - {{name: {n}, version: {v}}}" for n, v in sorted(extras.items())]
    if dependencies:
        out.append("  # Dependencies of the extras")
        out += [f"  - {{name: {n}, version: {v}}}" for n, v in sorted(dependencies.items())]
    (ROOT / "requirements.yml").write_text("\n".join(out) + "\n")

    rows = [f"| `{n}` | {v} | bundled |" for n, v in sorted(collections.items())]
    rows += [f"| `{n}` | {v} | extra |" for n, v in sorted(extras.items())]
    rows += [f"| `{n}` | {v} | dependency |" for n, v in sorted(dependencies.items())]
    table = "\n".join([
        f"**ansible {version}** · **ansible-core {core}** · {len(collections) + len(added)} collections",
        "",
        "<details>",
        "<summary>Show all collections</summary>",
        "",
        "| Collection | Version | Source |",
        "|---|---|---|",
        *rows,
        "",
        "</details>",
    ])
    readme = ROOT / "README.md"
    readme.write_text(re.sub(
        r"(<!-- BEGIN collections -->\n).*?(<!-- END collections -->)",
        lambda m: f"{m.group(1)}{table}\n{m.group(2)}",
        readme.read_text(),
        flags=re.S,
    ))

    ee = ROOT / "execution-environment.yml"
    text = re.sub(r"ansible-core==[\w.]+", f"ansible-core=={core}", ee.read_text())
    text = re.sub(r"(org\.ansible\.version=)[\w.]+", rf"\g<1>{version}", text)
    text = re.sub(r"(org\.ansible\.core-version=)[\w.]+", rf"\g<1>{core}", text)
    ee.write_text(text)
    print(f"ansible {version} / ansible-core {core}: {len(collections)} bundled + {len(extras)} extra"
          f" + {len(dependencies)} dependency collections")


if __name__ == "__main__":
    main()
