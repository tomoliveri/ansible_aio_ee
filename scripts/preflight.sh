#!/bin/bash
# Fast pre-build check (~2 min): would the current inputs build, and which collections'
# Python requirements would be dropped? Runs in the same UBI 10 base as the image.
set -euo pipefail
cd "$(dirname "$0")/.."
core=$(grep -oE 'ansible-core==[0-9.]+' execution-environment.yml)
docker run --rm -v "$PWD:/repo:ro" -w /repo -e PYTHONDONTWRITEBYTECODE=1 \
  registry.access.redhat.com/ubi10/ubi:latest bash -c "
    set -e
    dnf install -y -q python3 python3-pip https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm >/dev/null
    python3 -m pip install -q --root-user-action=ignore --disable-pip-version-check \
      ansible-builder==3.1.1 uv==0.12.23 $core ansible-runner
    python3 scripts/preflight.py --install-system"
