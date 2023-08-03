# Cumulus Network Automation PlayBooks
Click here for link to [Cumulus Documentation](https://docs.nvidia.com/networking-ethernet-software/)

Click here for link to [Ansible Documentation](https://docs.ansible.com/)


## Introduction to Cumulus and Automation

Cumulus has created some CLI tooling for versions 3-4, which were scripts operating various aspects of:
* Linux systemd files and Services
* FreeRange Routing files
* Standard Debian Linux

Cumulus does not recommend using the net-clu ansible library, which will be decommissioned in future.
it is recommended to use the Linux files to manage the system.


## Prereqs
* Ansible installed
* Network Access via SSH to devices being managed

## Ansible Tags
Ansible playbooks have been designed with Tags to ensure failsafe measures.

Tags can be applied to Roles, Tasks ect. See below [Port Interfaces Role](roles/ports_interfaces/tasks/main.yml)
```
---

- name: backup configuration files
  include: backups.yml
  tags:
    - backups
    - never  <--- Built in Tag, if no else defined,it will not Run
    - diff_set
    - set

- name: check only single host for configuring network devices
  include: single_host.yml
  tags:
    - always <--- built in tag, will always run.

- name: configure switch port breakouts and speeds
  include: ports.yml
  tags:
    - ports
    - breakouts
    - never
    - diff_set
    - set
  notify: reload networking

```

## Highstate Playbooks

 **Highstate Playbooks** is a play that runs everything within the state.
Since we are using **tags**, we need to define common tags that apply to all tasks.

We are currently using **highstate** as the highstate trigger.

# Check

When running a Playbook, in order to check eg **test=true** we need to use the command **--check**.
This is a ansible built in command.

# Verbose Diff Output

To view verbose changes being made, be sure to pass command **--diff**.
Another Ansible builtin command.

# Inventory

Inventory Files can be different on individual endpoints running ansible. We define a [Inventory file](inventory)


# Sudo

If logging in as your own user, you will need to provide a sudo escalation Password, to allow the Sudo escalation.
This is passed to the command via *-K* (capital K)

## Host Files

We shall provide a breakdown of a hostfile example:

```
## Iface

  - name: swp1 # Iface name
    auto: true # Active in config
    vlans: 2-10 #Trunk Vlans
    alias: server0 #Iface description
    mtu: 9216 # MTU
    storm_control_runtime: false # Runtime Stormcontrol to be run for this iface
    storm_control: # storm control paramters
        broadcast: 400
        unknown_unicast: 500
        multicast: 3000

## Bond

  - name: server2-bond
    lacp_bypass: 1 # Allow port to come up without lacp
    lacp_rate: 1 # lacp periodics
    miimon: 100 # time to wait for bond churn
    min_links: 1 #links minimum
    bond_mode: 802.3ad # bond mode
    slave: swp39 # slave of bonds
    loadbalance_hash: layer3+4 #loadbalance mode
    access_vlan: 18 # access port vlan
    clag_id: 39 # MCLAG ID for ICCP
    bpduguard: mstpctl-bpduguard yes # BPUD Guard
    stp_edge: true # Edge port
    mtu: 9216 # MTU of Bond

## Bridge Port (switch function in Linux)

  - name: bridge # name should always be bridge
    bridge_ports: <> # Ports bound to bridge (any L2 port should be bound)
    bridge_stp: on # STP On or Off
    vlans: 2-1000 2000-2500 #VLANS Bound
    vlan_aware: bridge-vlan-aware # Newer Age Vlan aware for flooding
    stp_priority: 16384 # STP priority

## ports

ports:
  - comment: # Comments in file
    - SFP+ ports
    - <port label>    = <10G>
  - name: 1 # Port Name. 1 = swp1
    type: 1x # 1x equals no breakout
  - name: 2
    type: 1x

  - name: 48
    type: 1x
    comment:
      - QSFP28 ports
      - ""
      - <port label>    = [40G|50G|100G]
      - or when split = [2x50G|4x10G|4x25G|disabled]
  - name: 49
    type: 4x10G #40G split into 4x10G Ports
```

## Runtime Usage

```
ansible-playbook -i inventory --limit=switch0.internal.example.com --check cumulus_highstate.yml -K -t runtime
```

Example:
```
ansible-playbook -i inventory --limit=switch0.internal.example.com --check cumulus_highstate.yml -K -t runtime
BECOME password:
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks instead. This feature will be removed in version 2.16. Deprecation
warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
Enter your Cumulus username ?: ansible

PLAY [cumulus] ****************************************************************************************************************************************

TASK [Gathering Facts] ********************************************************************************************************************************
ok: [switch0.internal.example.com]

TASK [ports_interfaces : Check for single host] *******************************************************************************************************
[WARNING]: conditional statements should not include jinja2 templating delimiters such as {{ }} or {% %}. Found: {{ play_hosts|length }} != 1
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : debug] ***********************************************************************************************************************
ok: [switch0.internal.example.com] => {
    "msg": "Checking for Single Host to run Playbook against"
}

TASK [runtime_updates : Broadcast Runtime update Test] ************************************************************************************************
skipping: [switch0.internal.example.com] => (item={'name': 'eth0', 'auto': True, 'address': '10.10.10.2/24', 'gateway': '10.10.10.1', 'vrf': 'mgmt'})
skipping: [switch0.internal.example.com] => (item={'name': 'eth1', 'auto': True})
skipping: [switch0.internal.example.com] => (item={'name': 'swp1', 'auto': True, 'vlans': '2-10', 'alias': 'server1', 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
skipping: [switch0.internal.example.com] => (item={'name': 'swp2', 'auto': True, 'no_autonegatiation': True, 'link_speed': 10000, 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
skipping: [switch0.internal.example.com] => (item={'name': 'swp3', 'auto': True, 'no_autonegatiation': True, 'link_speed': 10000, 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
skipping: [switch0.internal.example.com] => (item={'name': 'swp4', 'auto': True, 'no_autonegatiation': True, 'link_speed': 10000, 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})

```

## Interfaces Usage

```
ansible-playbook -i inventory --limit=switch0.internal.example.com --check cumulus_highstate.yml -K -t interfaces
BECOME password:
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks instead. This feature will be removed in version 2.16. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
Enter your Cumulus username ?: ansible

PLAY [cumulus] **********************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************************************************************
ok: [switch0.internal.example.com]

TASK [ports_interfaces : Check for single host] *************************************************************************************************************************************************************************************
[WARNING]: conditional statements should not include jinja2 templating delimiters such as {{ }} or {% %}. Found: {{ play_hosts|length }} != 1
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : debug] *****************************************************************************************************************************************************************************************************
ok: [switch0.internal.example.com] => {
    "msg": "Checking for Single Host to run Playbook against"
}

TASK [ports_interfaces : Load Interface configuration] ******************************************************************************************************************************************************************************
changed: [switch0.internal.example.com]

TASK [ports_interfaces : Load switchd configuration STG] ****************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Load switchd configuration PROD] ****************************************************************************************************************************************************************************
ok: [switch0.internal.example.com]

RUNNING HANDLER [ports_interfaces : reload networking] ******************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

PLAY RECAP **************************************************************************************************************************************************************************************************************************
switch0.internal.example.com              : ok=4    changed=1    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0
```

## Highstate Usage

```
ansible-playbook -i inventory --limit=switch0.internal.example.com --check cumulus_highstate.yml -K -t highstate
BECOME password:
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks instead. This feature will be removed in version 2.16. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
Enter your Cumulus username ?: ansible

PLAY [cumulus] **********************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************************************************************
ok: [switch0.internal.example.com]

TASK [ports_interfaces : Backup interface Configuration] ****************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Backup FRRouting daemon configuration] *********************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Backup FRRouting configuration] ****************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Backup Ports configuration] ********************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : run show config commands] **********************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : fetch the file and store it locally] ***********************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : run show config files] *************************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : fetch the file and store it locally] ***********************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : run show license file] *************************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : fetch license file] ****************************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Check for single host] *************************************************************************************************************************************************************************************
[WARNING]: conditional statements should not include jinja2 templating delimiters such as {{ }} or {% %}. Found: {{ play_hosts|length }} != 1
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : debug] *****************************************************************************************************************************************************************************************************
ok: [switch0.internal.example.com] => {
    "msg": "Checking for Single Host to run Playbook against"
}

TASK [ports_interfaces : Load Ports configuration] **********************************************************************************************************************************************************************************
ok: [switch0.internal.example.com]

TASK [ports_interfaces : Load Interface configuration] ******************************************************************************************************************************************************************************
changed: [switch0.internal.example.com]

TASK [ports_interfaces : Load switchd configuration STG] ****************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

TASK [ports_interfaces : Load switchd configuration PROD] ****************************************************************************************************************************************************************************
ok: [switch0.internal.example.com]

TASK [runtime_updates : Broadcast Runtime update] ***********************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com] => (item={'name': 'eth0', 'auto': True, 'address': '10.10.105/24', 'gateway': '10.10.101', 'vrf': 'mgmt'})
skipping: [switch0.internal.example.com] => (item={'name': 'eth1', 'auto': True})
...

TASK [runtime_updates : Multicast Runtime update] ***********************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com] => (item={'name': 'eth0', 'auto': True, 'address': '10.10.105/24', 'gateway': '10.10.101', 'vrf': 'mgmt'})
skipping: [switch0.internal.example.com] => (item={'name': 'eth1', 'auto': True})
skipping: [switch0.internal.example.com] => (item={'name': 'swp1', 'auto': True, 'vlans': '2-10', 'alias': 'server0', 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
skipping: [switch0.internal.example.com] => (item={'name': 'swp2', 'auto': True, 'no_autonegatiation': True, 'link_speed': 10000, 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
...

TASK [runtime_updates : unknown_unicast Runtime update] *****************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com] => (item={'name': 'eth0', 'auto': True, 'address': '10.10.105/24', 'gateway': '10.10.101', 'vrf': 'mgmt'})
skipping: [switch0.internal.example.com] => (item={'name': 'eth1', 'auto': True})
skipping: [switch0.internal.example.com] => (item={'name': 'swp1', 'auto': True, 'vlans': '2-10', 'alias': 'server0', 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})
skipping: [switch0.internal.example.com] => (item={'name': 'swp2', 'auto': True, 'no_autonegatiation': True, 'link_speed': 10000, 'mtu': 9216, 'storm_control_runtime': False, 'storm_control': {'broadcast': 400, 'unknown_unicast': 500, 'multicast': 3000}})

RUNNING HANDLER [ports_interfaces : reload networking] ******************************************************************************************************************************************************************************
skipping: [switch0.internal.example.com]

PLAY RECAP **************************************************************************************************************************************************************************************************************************
switch0.internal.example.com              : ok=5    changed=1    unreachable=0    failed=0    skipped=16   rescued=0    ignored=0

```
