# ansible_aio_ee
All-in-one execution environment for Ansible Controller / AWX 

## What does this do?

Once upon a time...

Ansible was 'batteries included', meaning that you could install Ansible, write a playbook and get up and running quickly, most of the modules you'd want to use would come bundled in. This was great for new users, but not so great for the developers who found themselves spread thin, supporting a growing list of modules. 
The Ansible team decided to take the batteries out. 

*This makes it easy to put the batteries back in.*

This provides a large number of community collections, allowing you to use modules on AWX or Automation Controller with little fuss. It includes All collections but not all python libraries.

## Basic Installation

In your AWX / Ansible Automation controller UI, https://awx/#/execution_environments/add

Add:
```docker.io/tomoliveri/ansible_aoi_ee:latest```

## Advanced Instalation

Requirements for this method:
  - Docker / Podman
  - ansible-builder 

You can modify the requirements.yml file to support *only* the modules you require. 
You may need to add additional python libraries in your requirements.txt, some of them are captured under collection_requirements. 
In Development: the custom_build_playbook will generate a new requirements.txt, with only the python libraries associated to the enabled collections.

Then, generate a new image with:
```ansible-builder build --tag ansible_custom_ee -v 3```

Verbose output is strongly reccomended.

## Caveats & Likely issues

Almost certainly if you're using this execution environment and your required module fails, it will be due to a missing python library. 
Feel free to reach out to me, or raise an issue here if you're having trouble and I'll help out when I can. 
Building a new (and stripped down) execution environment will be the fastest way to get you up and going. 
See Ansible Builder for instructions - https://github.com/ansible/ansible-builder 

## Included Collections
  - amazon.aws
  - arista.eos
  - awx.awx
  - check_point.mgmt
  - cisco.aci
  - cisco.asa
  - cisco.intersight
  - cisco.ios
  - cisco.iosxr
  - cisco.meraki
  - cisco.mso
  - cisco.nso
  - cisco.nxos
  - cisco.ucs
  - cloudscale_ch.cloud
  - community.aws
  - community.crypto
  - community.digitalocean
  - community.docker
  - community.fortios
  - community.general
  - community.google
  - community.grafana
  - community.hashi_vault
  - community.hrobot 
  - community.kubevirt
  - community.kubernetes
  - community.libvirt
  - community.mongodb
  - community.mysql
  - community.network
  - community.okd
  - community.postgresql
  - community.proxysql
  - community.rabbitmq
  - community.routeros 
  - community.skydive 
  - community.sops
  - community.vmware
  - community.windows
  - community.zabbix
  - containers.podman
  - cyberark.conjur
  - cyberark.pas
  - dellemc.enterprise_sonic
  - dellemc.openmanage
  - dellemc.os10
  - dellemc.os6
  - dellemc.os9
  - f5networks.f5_modules
  - fortinet.fortimanager
  - fortinet.fortios
  - frr.frr
  - gluster.gluster
  - google.cloud
  - hetzner.hcloud
  - hpe.nimble
  - ibm.qradar
  - inspur.sm
  - junipernetworks.junos
  - kubernetes.core
  - mellanox.onyx
  - netapp.aws
  - netapp.cloudmanager
  - netapp.elementsw
  - netapp.ontap
  - netapp_eseries.santricity
  - netbox.netbox
  - ngine_io.cloudstack
  - ngine_io.exoscale
  - ngine_io.vultr
  - openstack.cloud
  - openvswitch.openvswitch
  - ovirt.ovirt
  - purestorage.flasharray
  - purestorage.flashblade
  - sensu.sensu_go
  - servicenow.servicenow
  - splunk.es
  - t_systems_mms.icinga_director
  - theforeman.foreman
  - vyos.vyos
  - wti.remote

## Excluded Collections
### Disabled due to issue with azure_compute #
 - community.azure 
 - chocolatey.chocolatey 
 - azure.azcollection 
 - netapp.um_info
 - netapp.azure

### Seems to break things in spectacular fashion 
 - infinidat.infinibox 