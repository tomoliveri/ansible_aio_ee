# ansible_aio_ee
All-in-one execution environment for AWX / Ansible Automation Controller.

## What does this do?

Once upon a time...

Ansible was 'batteries included', meaning that you could install Ansible, write a playbook and get up and running quickly, most of the modules you'd want to use would come bundled in. This was great for new users, but not so great for the developers who found themselves spread thin, supporting a growing list of modules.
The Ansible team decided to take the batteries out.

*This makes it easy to put the batteries back in.*

The image contains every collection shipped in the `ansible` community package (currently **ansible 14.5.0 / ansible-core 2.21.5**), a few maintained extras, and the Python and system libraries those collections need, so modules work in AWX / Automation Controller with little fuss.

## Basic Installation

In your AWX / Automation Controller UI, go to **Execution Environments → Add** and use:

```
docker.io/tomoliveri/ansible_aio_ee:latest
```

or pin a release, e.g. `docker.io/tomoliveri/ansible_aio_ee:14.5.0` (tags follow the `ansible` community package version). Images are built for `amd64` and `arm64`.

You can then select it in job templates as required.

## What's inside

- **Base:** CentOS Stream 10, Python 3.12, ansible-core 2.21, ansible-runner 2.4.
- **Collections:** see [`requirements.yml`](requirements.yml) (generated, pinned) — the full `ansible` package set plus [`extra-collections.txt`](extra-collections.txt) (`awx.awx`, `cisco.asa`, `junipernetworks.junos`, `openvswitch.openvswitch`, `recordsansible.ara`, `servicenow.itsm`).
- **Python libraries:** whatever each collection declares (added automatically by ansible-builder) plus [`requirements.txt`](requirements.txt) for plugins that don't declare theirs: WinRM/PSRP (with Kerberos and CredSSP), `python-ldap`, `jmespath`, `netaddr`, `hvac`, `pynetbox`, `python-gitlab`, `ara`, and more.
- **System packages:** [`bindep.txt`](bindep.txt): git, ssh/sshpass, rsync, subversion, nmap, krb5, openldap.

## Building your own

Requirements: Docker or Podman, and `pip install ansible-builder` (3.x).

Trim `requirements.yml` / `requirements.txt` to what you need, then:

```
ansible-builder build --tag ansible_custom_ee -v 3
```

### Updating to a new Ansible release

```
scripts/update-requirements.py            # latest ansible on PyPI
scripts/update-requirements.py 14.5.0     # or a specific release
```

This regenerates `requirements.yml` from that release's collection list (from [ansible-build-data](https://github.com/ansible-community/ansible-build-data)) and updates the ansible-core pin in `execution-environment.yml`. Add or remove collections with `extra-collections.txt` and `excluded-collections.txt`, not by editing `requirements.yml`.

## CI

`.github/workflows/build.yml` builds and smoke-tests the image for amd64 and arm64 on every push and pull request, and monthly. On `main`, if the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets are set, it publishes `:latest` and `:<ansible version>` to Docker Hub.

## Caveats & likely issues

If a module fails in this EE, it is almost certainly a missing Python library or system package on the controller side. Open an issue with the module name and error, or add the library to `requirements.txt` and build your own.

Removed since the 2022 image (deprecated, renamed or unmaintained upstream): `community.kubernetes` (use `kubernetes.core`), `community.kubevirt` (use `kubevirt.core`), `community.google`, `community.fortios`, `community.skydive`, `community.azure`, `community.network`, `community.digitalocean`, `servicenow.servicenow` (use `servicenow.itsm`), `t_systems_mms.icinga_director` (use `telekom_mms.icinga_director`), `ngine_io.vultr` (use `vultr.cloud`), `ngine_io.exoscale`, `dellemc.os6/os9/os10`, `cisco.nso`, `frr.frr`, `gluster.gluster`, `hpe.nimble`, `ibm.qradar`, `inspur.sm`, `mellanox.onyx`, `netapp.aws/azure/elementsw/um_info`, `sensu.sensu_go`.
