<div align="center">

# 🔋 ansible_aio_ee

**The all-in-one Ansible execution environment for AWX and Automation Controller.**<br>
Every collection from the `ansible` community package, the libraries they need, ready to run.

[![build](https://github.com/tomoliveri/ansible_aio_ee/actions/workflows/build.yml/badge.svg)](https://github.com/tomoliveri/ansible_aio_ee/actions/workflows/build.yml)
[![Docker pulls](https://img.shields.io/docker/pulls/tomoliveri/ansible_aio_ee?logo=docker&logoColor=white)](https://hub.docker.com/r/tomoliveri/ansible_aio_ee)
[![Image size](https://img.shields.io/docker/image-size/tomoliveri/ansible_aio_ee/latest?logo=docker&logoColor=white&label=size)](https://hub.docker.com/r/tomoliveri/ansible_aio_ee/tags)
[![Platforms](https://img.shields.io/badge/platform-amd64%20%7C%20arm64-blue)](#-quick-start)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## 📖 Why?

Once upon a time Ansible was *batteries included*: install it, write a playbook, and almost every module you wanted was right there. Great for new users, less great for the maintainers spread thin across thousands of modules, so the batteries came out and moved into collections.

**This image puts the batteries back in.** Point AWX or Automation Controller at it and modules for AWS, Azure, VMware, Cisco, Windows, Kubernetes, NetBox, Vault and much more just work, with no custom image builds and no missing Python libraries.

## 🚀 Quick start

In AWX / Automation Controller, go to **Administration → Execution Environments → Add**:

| Field | Value |
|---|---|
| Image | `docker.io/tomoliveri/ansible_aio_ee:latest` |
| Pull | *Only pull the image if not present before running* (or *Always* to follow `latest`) |

Then select it on your job templates. Prefer reproducible runs? Pin a release tag such as `:14.5.0`. Tags follow the `ansible` community package version.

Run it locally with [ansible-navigator](https://ansible.readthedocs.io/projects/navigator/):

```sh
ansible-navigator run site.yml --eei docker.io/tomoliveri/ansible_aio_ee:latest
```

or plain Docker:

```sh
docker run --rm -it -v "$PWD:/runner/project" -w /runner/project \
  docker.io/tomoliveri/ansible_aio_ee:latest ansible-playbook site.yml
```

## 📦 What's inside

| Layer | Contents |
|---|---|
| **Base** | CentOS Stream 10 · Python 3.12 · ansible-core · ansible-runner |
| **Collections** | Everything in the [`ansible`](https://pypi.org/project/ansible/) community package, plus [extras](extra-collections.txt): `awx.awx`, `cisco.asa`, `junipernetworks.junos`, `openvswitch.openvswitch`, `recordsansible.ara`, `servicenow.itsm` |
| **Python libraries** | Everything the collections declare, plus [extras](requirements.txt) for plugins that don't: WinRM / PSRP with Kerberos + CredSSP, `python-ldap`, `jmespath`, `netaddr`, `hvac`, `pynetbox`, `python-gitlab`, `ara` and more |
| **System packages** | [`bindep.txt`](bindep.txt): git, ssh + sshpass, rsync, subversion, nmap, krb5, openldap |

<!-- BEGIN collections -->
**ansible 14.5.0** · **ansible-core 2.21.5** · 98 collections

<details>
<summary>Show all collections</summary>

| Collection | Version | Source |
|---|---|---|
| `amazon.aws` | 11.4.0 | bundled |
| `ansible.mariadb` | 6.0.2 | bundled |
| `ansible.mysql` | 5.2.0 | bundled |
| `ansible.netcommon` | 8.7.1 | bundled |
| `ansible.posix` | 2.2.2 | bundled |
| `ansible.utils` | 6.1.1 | bundled |
| `ansible.windows` | 3.8.0 | bundled |
| `arista.eos` | 12.3.0 | bundled |
| `azure.azcollection` | 3.21.0 | bundled |
| `check_point.mgmt` | 6.9.0 | bundled |
| `chocolatey.chocolatey` | 1.6.0 | bundled |
| `cisco.aci` | 2.13.0 | bundled |
| `cisco.intersight` | 2.21.0 | bundled |
| `cisco.ios` | 11.6.0 | bundled |
| `cisco.iosxr` | 12.5.0 | bundled |
| `cisco.meraki` | 2.25.1 | bundled |
| `cisco.mso` | 2.13.0 | bundled |
| `cisco.nxos` | 11.2.0 | bundled |
| `cisco.ucs` | 1.16.0 | bundled |
| `cloudscale_ch.cloud` | 2.8.0 | bundled |
| `community.aws` | 11.2.0 | bundled |
| `community.ciscosmb` | 1.0.12 | bundled |
| `community.clickhouse` | 2.4.0 | bundled |
| `community.crypto` | 3.5.0 | bundled |
| `community.dns` | 4.2.0 | bundled |
| `community.docker` | 5.4.0 | bundled |
| `community.general` | 13.5.0 | bundled |
| `community.grafana` | 2.3.0 | bundled |
| `community.hashi_vault` | 7.1.0 | bundled |
| `community.hrobot` | 2.8.0 | bundled |
| `community.library_inventory_filtering_v1` | 1.1.5 | bundled |
| `community.libvirt` | 2.3.0 | bundled |
| `community.mongodb` | 1.8.0 | bundled |
| `community.mysql` | 5.0.2 | bundled |
| `community.okd` | 5.0.0 | bundled |
| `community.postgresql` | 4.2.0 | bundled |
| `community.proxmox` | 2.0.0 | bundled |
| `community.proxysql` | 1.8.0 | bundled |
| `community.rabbitmq` | 1.7.0 | bundled |
| `community.routeros` | 3.22.0 | bundled |
| `community.sap_libs` | 1.7.1 | bundled |
| `community.sops` | 2.5.0 | bundled |
| `community.vmware` | 6.5.0 | bundled |
| `community.windows` | 3.3.0 | bundled |
| `community.zabbix` | 4.2.0 | bundled |
| `containers.podman` | 1.21.0 | bundled |
| `cyberark.conjur` | 1.3.14 | bundled |
| `cyberark.pas` | 1.0.40 | bundled |
| `dellemc.enterprise_sonic` | 4.1.0 | bundled |
| `dellemc.openmanage` | 10.0.3 | bundled |
| `dellemc.powerflex` | 3.2.0 | bundled |
| `dellemc.unity` | 2.1.0 | bundled |
| `f5networks.f5_modules` | 1.44.0 | bundled |
| `fortinet.fortimanager` | 2.15.0 | bundled |
| `fortinet.fortios` | 2.6.0 | bundled |
| `google.cloud` | 1.15.0 | bundled |
| `grafana.grafana` | 6.1.0 | bundled |
| `graphiant.naas` | 26.9.0 | bundled |
| `hetzner.hcloud` | 6.12.0 | bundled |
| `hitachivantara.vspone_block` | 4.8.3 | bundled |
| `hitachivantara.vspone_object` | 1.2.0 | bundled |
| `ibm.storage_virtualize` | 3.4.0 | bundled |
| `ieisystem.inmanage` | 4.0.0 | bundled |
| `infinidat.infinibox` | 1.8.6 | bundled |
| `infoblox.nios_modules` | 1.9.0 | bundled |
| `inspur.ispim` | 2.2.4 | bundled |
| `kaytus.ksmanage` | 4.0.0 | bundled |
| `kubernetes.core` | 6.6.0 | bundled |
| `kubevirt.core` | 2.3.0 | bundled |
| `lowlydba.sqlserver` | 2.8.1 | bundled |
| `microsoft.ad` | 1.12.1 | bundled |
| `microsoft.iis` | 1.3.0 | bundled |
| `netapp.cloudmanager` | 21.24.0 | bundled |
| `netapp.ontap` | 23.6.0 | bundled |
| `netapp.storagegrid` | 21.17.0 | bundled |
| `netapp_eseries.santricity` | 2.0.3 | bundled |
| `netbox.netbox` | 3.23.0 | bundled |
| `ngine_io.cloudstack` | 3.3.0 | bundled |
| `openstack.cloud` | 2.6.0 | bundled |
| `ovirt.ovirt` | 3.2.2 | bundled |
| `pcg.alpaca_operator` | 2.2.0 | bundled |
| `purestorage.flasharray` | 1.43.0 | bundled |
| `purestorage.flashblade` | 1.26.0 | bundled |
| `ravendb.ravendb` | 1.0.4 | bundled |
| `splunk.es` | 6.0.1 | bundled |
| `telekom_mms.icinga_director` | 2.6.1 | bundled |
| `theforeman.foreman` | 5.13.0 | bundled |
| `vmware.vmware` | 2.11.0 | bundled |
| `vmware.vmware_rest` | 4.11.0 | bundled |
| `vultr.cloud` | 1.14.1 | bundled |
| `vyos.vyos` | 6.0.0 | bundled |
| `wti.remote` | 1.0.11 | bundled |
| `awx.awx` | 24.6.1 | extra |
| `cisco.asa` | 7.0.0 | extra |
| `junipernetworks.junos` | 11.1.1 | extra |
| `openvswitch.openvswitch` | 2.2.2 | extra |
| `recordsansible.ara` | 0.1.0 | extra |
| `servicenow.itsm` | 2.16.0 | extra |

</details>
<!-- END collections -->

## 🔄 Always current

The image keeps itself up to date. Every week CI checks for a new `ansible` release. When there is one, it regenerates the pinned collection list, rebuilds for amd64 and arm64, smoke-tests the image and publishes it. Nothing changed? The check finishes in seconds without building.

| Trigger | What happens |
|---|---|
| ⏰ Weekly (Monday) | Update check → build + publish only if something changed |
| 🔀 Push to `main` | Build + publish, only when EE inputs change |
| 🧪 Pull request | Lint + amd64 build and smoke test, never published |
| ▶️ Manual dispatch | Update check → build + publish |

## 🛠️ Build your own

Need something leaner? Trim the inputs and build with [ansible-builder](https://ansible.readthedocs.io/projects/builder/) 3.x:

```sh
pip install ansible-builder
ansible-builder build --tag my_ee -v 3
```

| File | Purpose |
|---|---|
| [`execution-environment.yml`](execution-environment.yml) | ansible-builder v3 definition (base image, core/runner pins, build steps) |
| [`requirements.yml`](requirements.yml) | Pinned collections. **Generated:** don't edit by hand |
| [`extra-collections.txt`](extra-collections.txt) | Collections to add on top of the `ansible` package |
| [`excluded-collections.txt`](excluded-collections.txt) | Collections from the `ansible` package to leave out |
| [`requirements.txt`](requirements.txt) | Python libraries collections don't declare themselves |
| [`bindep.txt`](bindep.txt) | System packages (`[compile]` = build stage only) |

Move to a new Ansible release (CI does this weekly):

```sh
scripts/update-requirements.py          # latest release on PyPI
scripts/update-requirements.py 14.5.0   # or a specific one
```

## 🩺 Troubleshooting

If a module fails inside this EE, the cause is almost always a missing Python library or system package on the controller side.

1. Check the module's docs for its `requirements:`.
2. Add the library to [`requirements.txt`](requirements.txt) (or the package to [`bindep.txt`](bindep.txt)) and open a pull request, or [open an issue](https://github.com/tomoliveri/ansible_aio_ee/issues) with the module name and error.

<details>
<summary><b>Collections removed since the 2022 image</b> (deprecated, renamed or unmaintained upstream)</summary>

| Removed | Use instead |
|---|---|
| `community.kubernetes` | `kubernetes.core` |
| `community.kubevirt` | `kubevirt.core` |
| `servicenow.servicenow` | `servicenow.itsm` |
| `t_systems_mms.icinga_director` | `telekom_mms.icinga_director` |
| `ngine_io.vultr` | `vultr.cloud` |
| `community.google` | `google.cloud` |
| `community.fortios` | `fortinet.fortios` |
| `community.azure` | `azure.azcollection` |
| `community.network`, `community.digitalocean`, `community.skydive`, `ngine_io.exoscale`, `dellemc.os6/os9/os10`, `cisco.nso`, `frr.frr`, `gluster.gluster`, `hpe.nimble`, `ibm.qradar`, `inspur.sm`, `mellanox.onyx`, `netapp.aws/azure/elementsw/um_info`, `sensu.sensu_go` | No longer maintained. Add to [`extra-collections.txt`](extra-collections.txt) in your own build if you still need one |

</details>

## 🤝 Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the Ansible coding standards this repo follows and how to test changes.

## 📜 License

The build definitions and scripts in this repository are [MIT licensed](LICENSE).
The published image bundles third-party software (ansible-core, collections, Python and OS packages) under its own licenses, mostly GPL-3.0. See [NOTICE.md](NOTICE.md).
