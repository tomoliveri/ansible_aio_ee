# Third-party notices

The MIT [LICENSE](LICENSE) covers only the files in this repository: the
ansible-builder definition, requirement lists, scripts, tests and CI configuration.

The container image built from them (`docker.io/tomoliveri/ansible_aio_ee`) is an
aggregate of third-party software, each part distributed under its own license.
None of it is relicensed by this project.

| Component | License |
|---|---|
| [ansible-core](https://github.com/ansible/ansible) | GPL-3.0-or-later |
| [ansible-runner](https://github.com/ansible/ansible-runner) | Apache-2.0 |
| Ansible collections ([`requirements.yml`](requirements.yml)) | Per collection: mostly GPL-3.0-or-later, some GPL-2.0-or-later, Apache-2.0, BSD-2-Clause, MIT or MPL-2.0 |
| Python libraries ([`requirements.txt`](requirements.txt) and collection dependencies) | Per package (Apache-2.0, BSD, MIT, LGPL, ...) |
| [CentOS Stream 10](https://www.centos.org/) base image and RPM packages | Per package |

Each collection's license is in its `MANIFEST.json` and `LICENSE`/`COPYING` file
inside the image. To list them:

```sh
docker run --rm docker.io/tomoliveri/ansible_aio_ee:latest sh -c \
  'cd /usr/share/ansible/collections/ansible_collections && for m in */*/MANIFEST.json; do
     python3 -c "import json,sys; c=json.load(open(sys.argv[1]))[\"collection_info\"]; print(c[\"namespace\"]+\".\"+c[\"name\"], c.get(\"license\") or c.get(\"license_file\"))" "$m"; done'
```

Python package licenses: `pip-licenses` or `pip show <package>` inside the image.
RPM licenses: `rpm -qa --qf '%{NAME} %{LICENSE}\n'`.

Source code for the GPL components is available from their upstream projects
linked above, from [Ansible Galaxy](https://galaxy.ansible.com/) for collections,
and from the [CentOS Stream sources](https://gitlab.com/redhat/centos-stream/rpms)
for OS packages.
