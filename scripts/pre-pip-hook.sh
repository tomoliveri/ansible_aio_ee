#!/bin/bash
# Called by ansible-builder's assemble script (builder stage) right before it pip-installs
# the combined collection requirements. See execution-environment.yml.
set -euo pipefail
reqs=/tmp/src/requirements.txt

# Collections sometimes ship lines like '-c constraints.txt' that point at files which
# never reach the build; pip would abort on them.
sed -i -E '/^[[:space:]]*-(c|r|-constraint|-requirement)([[:space:]]|=)/d' "$reqs"

# Resolve with uv (fast), dropping the Python deps of collections that conflict with the
# rest of the image, and rewrite the file as a fully pinned list for pip.
"${PYCMD:-/usr/bin/python3}" -m pip install --quiet --disable-pip-version-check uv==0.12.23
"${PYCMD:-/usr/bin/python3}" /output/aio/resolve_python_deps.py "$reqs" /output/aio/requirements.yml /output/aio/python-deps-report.txt /output/aio/optional-requirements.txt
