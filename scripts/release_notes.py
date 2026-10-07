#!/usr/bin/env python3
"""Generate release notes and the Docker Hub overview for the current inputs.

  release_notes.py notes    [REPORT]  -> markdown release notes (stdout), for GitHub Releases
  release_notes.py overview [REPORT]  -> full Docker Hub overview (stdout)
  release_notes.py push     [REPORT]  -> update the Docker Hub overview + short description
                                         (needs DOCKERHUB_USERNAME / DOCKERHUB_TOKEN)

REPORT is the image's /etc/ansible_aio_ee/python-deps-report.txt (optional).
"""
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "tomoliveri/ansible_aio_ee"
IMAGE = f"docker.io/{REPO}"
GITHUB = f"https://github.com/{REPO}"


def inputs():
    ee = (ROOT / "execution-environment.yml").read_text()
    version = re.search(r"org\.ansible\.version=([\w.]+)", ee).group(1)
    core = re.search(r"org\.ansible\.core-version=([\w.]+)", ee).group(1)
    sections, current = {"bundled": [], "extra": [], "dependency": []}, None
    for line in (ROOT / "requirements.yml").read_text().splitlines():
        if line.strip().startswith("#"):
            current = ("bundled" if "community package" in line else "extra" if "Extras" in line
                       else "dependency" if "Dependencies" in line else current)
        match = re.search(r"name:\s*([\w.]+),\s*version:\s*([\w.\-]+)", line)
        if match and current:
            sections[current].append(match.groups())
    return version, core, sections


def dropped(report):
    if not report or not pathlib.Path(report).is_file():
        return []
    return [l[2:].strip() for l in pathlib.Path(report).read_text().splitlines() if l.startswith("- ")]


def release_section(version, core, sections, drops):
    total = sum(len(v) for v in sections.values())
    built = datetime.date.today().isoformat()
    lines = [
        f"## Release `{version}`",
        "",
        "| | |",
        "|---|---|",
        f"| **Image** | `{IMAGE}:{version}` (also `:latest`) |",
        f"| **ansible** | {version} (community package) |",
        f"| **ansible-core** | {core} |",
        f"| **Collections** | {total}: {len(sections['bundled'])} from the ansible package, "
        f"{len(sections['extra'])} extras, {len(sections['dependency'])} "
        f"{'dependency' if len(sections['dependency']) == 1 else 'dependencies'} |",
        "| **Base** | Red Hat UBI 10, Python 3.12 |",
        "| **Platforms** | linux/amd64, linux/arm64 |",
        f"| **Built** | {built} |",
        "",
    ]
    if drops:
        lines += [
            "**Python requirements left out** (they conflict with the rest of the image; the collections "
            "are installed, but modules needing these libraries won't work):",
            "",
            *[f"- `{d.replace('optional:', '')}`" for d in drops],
            "",
        ]
    lines += [
        "**Extra collections** (beyond the ansible package): "
        + ", ".join(f"`{n}` {v}" for n, v in sections["extra"]),
        "",
    ]
    return lines


def overview(version, core, sections, drops):
    lines = [
        "# 🔋 ansible_aio_ee",
        "",
        "**The all-in-one Ansible execution environment for AWX and Automation Controller.** "
        "Every collection from the `ansible` community package, plus Red Hat upstream and vendor "
        "collections (F5, Juniper, Palo Alto, Cisco, Arista, Fortinet, Dell, HPE, CrowdStrike, ...), "
        "with the Python and system libraries they need.",
        "",
        "## 🚀 Quick start",
        "",
        "In AWX / Automation Controller: **Administration → Execution Environments → Add**, image "
        f"`{IMAGE}:latest`, or pin a release such as `{IMAGE}:{version}`.",
        "",
        "```sh",
        f"ansible-navigator run site.yml --eei {IMAGE}:latest",
        f'docker run --rm -it -v "$PWD:/runner/project" -w /runner/project {IMAGE}:latest ansible-playbook site.yml',
        "```",
        "",
        "## 🏷️ Tags",
        "",
        "| Tag | Meaning |",
        "|---|---|",
        "| `latest` | Newest release, rebuilt monthly with OS security fixes |",
        "| `<ansible version>` e.g. `14.5.0` | Matches the `ansible` community package release it's built from |",
        "",
        *release_section(version, core, sections, drops),
        "## 🔄 How it's maintained",
        "",
        "Rebuilt monthly by CI. New `ansible` releases are picked up automatically, checked with a "
        "dependency preflight, built for amd64 and arm64, smoke-tested, and only then published. "
        "A failed update never replaces a working image.",
        "",
        "## 📚 More",
        "",
        f"- Source, full collection list and build-your-own guide: {GITHUB}",
        f"- Release history: {GITHUB}/releases",
        f"- Issues: {GITHUB}/issues",
        "",
        "Build definitions are MIT licensed; the image bundles third-party software under its own "
        f"licenses (mostly GPL-3.0). See {GITHUB}/blob/main/NOTICE.md",
        "",
    ]
    return "\n".join(lines)


def notes(version, core, sections, drops):
    lines = release_section(version, core, sections, drops)[2:]  # skip the heading
    lines += [
        "```sh",
        f"docker pull {IMAGE}:{version}",
        "```",
        "",
        f"Full collection list with versions: [README]({GITHUB}/blob/{version}/README.md#-whats-inside).",
    ]
    return "\n".join(lines) + "\n"


def push(version, core, sections, drops):
    user, token = os.environ["DOCKERHUB_USERNAME"], os.environ["DOCKERHUB_TOKEN"]
    login = urllib.request.Request(
        "https://hub.docker.com/v2/users/login", method="POST",
        data=json.dumps({"username": user, "password": token}).encode(),
        headers={"Content-Type": "application/json"},
    )
    jwt = json.load(urllib.request.urlopen(login, timeout=60))["token"]
    total = sum(len(v) for v in sections.values())
    body = {
        "description": f"All-in-one Ansible EE for AWX/Controller: ansible {version}, {total} collections, amd64+arm64"[:100],
        "full_description": overview(version, core, sections, drops),
    }
    update = urllib.request.Request(
        f"https://hub.docker.com/v2/repositories/{REPO}/", method="PATCH",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"},
    )
    urllib.request.urlopen(update, timeout=60).read()
    print(f"Docker Hub overview updated for {version}")


def main():
    action = sys.argv[1]
    data = (*inputs(), dropped(sys.argv[2] if len(sys.argv) > 2 else None))
    if action == "push":
        push(*data)
    else:
        print({"notes": notes, "overview": overview}[action](*data))


if __name__ == "__main__":
    main()
