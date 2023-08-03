# Softether VPN Tooling for performing administration tasks
Click here for link to [Softether Repo](https://github.com/SoftEtherVPN/SoftEtherVPN)


# How To Use

This repo contains a tool called vpnadmin.
- ![vpnadmin](vpnadmin)

# Prereqs
* VPN Connection and privilegs to access VPN's
* Vault Environment variable exported on your system. See [HashiCopr Vault](https://www.vaultproject.io/)
* python3
* installed python requirements

# Environment Variables
* Local Secrets Override file can be used instead of Vault. Export Variable is ```VPN_SECRETS="/fqdn_path/vpn_secrets.yaml"```
* Vault Path can be overriden by Envrionment Variable VAULT_PATH="path/to/vault/secrets"
* Defaults to: ```PATH```

# VPN NameSpaces
* The argumment **--hub** identifies a VPN NameSpace
* Each VPN namespace has its own Vault Secret credentials
* Each VPN namespace is its Own Unique VPn with differently defined services

# Usage

Help
```
vpnadmin -h
usage: vpnadmin [-h]
                {vault,test,ls_users,ls_ip,ls_groups,ls_switch,ls_interfaces,ls_routes,ls_acl,ls_sessions,add_user,edit_user,search_user,del_user,add_routes,del_routes,add_hub,del_hub,add_interfaces,del_interfaces,add_groups,update_groups,del_groups,update_acls,update_radius}
                ...

Softether RPC Json Tool

positional arguments:
  {vault,test,ls_users,ls_ip,ls_groups,ls_switch,ls_interfaces,ls_routes,ls_acl,ls_sessions,add_user,edit_user,search_user,del_user,add_routes,del_routes,add_hub,del_hub,add_interfaces,del_interfaces,add_groups,update_groups,del_groups,update_acls,update_radius}
                        Provides VPN Admin functions
    vault               Vault plugins
    test                VPN Connection and Authentication Tester
    ls_users            List Users, formatted into Groups
    ls_ip               List Users and the IP's
    ls_groups           List Groups
    ls_switch           List Switches and Switch Status
    ls_interfaces       List Interfaces defined in Switch
    ls_routes           List Switches and Switch Status
    ls_acl              List ACL's for VPN Namespace
    ls_sessions         List Sessions on VPN namespace
    add_user            Add Users to VPN's
    edit_user           Edit User on VPN's
    search_user         Searching Users on VPN's by realname (filtered) or username (exact)
    del_user            Delete Users from VPN's
    add_routes          Add Routes to VPN Switch
    del_routes          Delete Routes from VPN Switch
    add_hub             Add missing Hub to VPN
    del_hub             Del Redundant Hubs from VPN
    add_interfaces      Add interfaces to VPN
    del_interfaces      Delete interfaces from VPN
    add_groups          Add Groups to VPN
    update_groups       Add Groups to VPN
    del_groups          Delete Groups from VPN
    update_acls         Update ACL's on VPN
    update_radius       Update Radius Auth per VPN Name
    user_diff           Diff Users between Multiple VPNs

options:
  -h, --help            show this help message and exit

```


# Breakdown of Tool Arguments:

The tooling has been architectured with layered ArgumentParsers. This allows multiple operations to be formed into a single tooling.

## Built in Failsafes

Since you need to be connected to the VPN to remotely manage them, there is risk of locking yourself and everyone from the VPN.
Certain functions all **Not Safe** to perform whilst connected inband to the VPN cluster.

# Manage Single VPN

Certain tasks are not safe to add on multiple VPN's simultaneously. There is failsafe to ensure only a single VPN is managed at a time.
```
vpnadmin add_routes --vpn se0-dc1 se0-dc2
Only One VPN can be configured at a time. Exiting
```

# Unable to configure VPN Inband

A VPN Cluster consists of the VPN's providing the overlay. eg [se0-dc1, se0-dc2] is a cluster, so you can not manage this whilst connected in band.

```
vpnadmin add_routes --vpn se1-dc3

VPN Login Failsafe check. This may take a few moments..

Enter LDAP/VPN Login Username to verify VPN Login: jdoe
User: jdoe
VPN Connected: se1-dc2

Unable to manage SE1 VPN Cluster client is connected
Change VPN Server Cluster to configure.

```

# FreeIPA API User Verifications

To ensure that users being added are defined in the backend LDAP Directory, there are two modules which provide the following:

* ![easy_ipa](easy_ipa): Simple API request module to perform simple queries to IPA API
* ![SimpleEncryption](SimpleEncryption): Encrypts and Decrypts IPA Session Cookie using Master key from Vault, for Sessions with IPA.

## Functions

Its current High Level Functions are:
- **vault**\
  Authentication Tests and Lookups

- **test**\
  Checks connectivity and authentication to VPN API.

- **ls_users**\
  List **all Users** in grouped together by Groups. Usable with **--group** to list Users in Group.

- **ls_sessions**\
  List **list sessions** on given VPN namespace

- **ls_groups**\
  List **list groups** on given VPN namespace with the number of members in the groups

- **ls_acl**\
  List **list Access Lists** on VPN. usable with **--group** to identify Group ACL

- **ls_ip**\
  List **list Sessions and IP addresses** on VPN. Usable with **--ip** or **--username**.

- **search_user**\
  Search a user by **--username** or **--realname**. Realname search performs a best match.

- **add_user**\
  Add a user to the VPN. Some parameters will have defaults if not specifically given. For example:
  * Authentication defaults to **radius**. Password can be set and prompts for a password.
  * Requires a group to be selected, if unsure use **IT**
  * HUB (aka VPN namespace) mostly used is **VPN**
  * VPN Node must be selected. **--vpn all** iterates over all VPN Nodes.

- **edit_user**\
  edit a user on VPNs. Some parameters will have defaults if not specifically given. For example:
  * Authentication defaults to **radius**. Password can be set and prompts for a password.
  * Requires a group to be selected, if unsure use **--group IT**
  * HUB (aka VPN namespace) mostly used is **VPN**
  * VPN Node must be selected. **all** iterates over all VPN Nodes.
  * Most notable reasons for editing is to change **auth** or **group** parameters

- **del_user**\
  Delete user from VPN using **--username** as selector

- **add_hub**\
  Add Hubs which is equivalent of a bind for a L2 Bridge, L3 Interface and VPN connections

- **del_hub**\
  Delete Hubs. Unable to delete a Hub if it has a Interface bound to it.

- **user_diff**\
  Performs a Diff Function between Two VPN Servers. If the VPN users are Identical, it will check Group Mismatches.
  Only if both VPN Servers users are identical, will it proceed to perform a Diff against Users defined in IPA LDAP directory

# Vault Intergration

## Vault Authentication Tests

**Successful**
```
Successful:
vpnadmin vault --test auth
Vault Authentication Successful
```

**Unsuccessful due to expired or invalid token. Results in New login**
```
vpnadmin vault --test auth

Warning: Vault Envronment Variable exists, but doesnt match [ https://vault:8200 ]


Not authenticated, Vault token invalid or expired. Redirecting to Vault Login!


Vault LDAP login to create new Token!
Enter LDAP Username: jdoe
Enter Password (HIDDEN):
```


## Environment Variable not Set

```
 vpnadmin vault --test auth

Vault environment variable NOT set

```

## Vault Path returns no secrets
```
vpnadmin add_user --vpn all --hub IT-VPN --username jsmith --realname "test mike" --group IT

Not authenticated, Vault token invalid or expired. Redirecting to Vault Login!


Vault LDAP login to create new Token!
Enter LDAP Username: jdoe
Enter Password (HIDDEN):

No secrets found. check following are correct:

VAULT_ADDR: https://vault:8200
Vault Path: networking/data/sevpn/hub_credential
```

# Function examples

## Test
Performs a simple Authentication test to the HUB. If HUB is not defined, it defaults to VPN.

```
./vpnadmin test --vpn se1-dc1 se1-dc2 se1-dc3

VPN Node: se0-dc1.internal.example.com
Test Successful

VPN Node: se0-dc2.internal.example.com
Test Successful

VPN Node: se0-dc3.internal.example.com
```

## List Users

```
./vpnadmin ls_users --vpn se1-dc1 --hub IT-VPN

VPN Node: se0-dc1.internal.example.com
Group: IT
User: jdoe | Real Name: john doe | Last Login: 2020-07-20T10:41:05.650Z

```

## List sessions
```
vpnadmin ls_sessions --vpn se0-dc1 --hub SC-VPN

VPN Node: se0-dc1.internal.example.com
Username: Local Bridge | IP: 0.0.0.0 | Connection Name: SID-LOCALBRIDGE-1 | Created: 2021-12-21T06:07:14.451Z | Last Activity: 2021-12-21T06:07:14.451Z
Username: L3SW_MASTER | IP: 0.0.0.0 | Connection Name: SID-L3-MASTER-3 | Created: 2021-12-21T06:07:14.511Z | Last Activity: 2021-12-21T06:07:14.532Z
Username: jdoe | IP: 1.1.1.1 | Connection Name: SID-JDOE-[OPENVPN_L3]-6536 | Created: 2022-01-13T03:34:40.324Z | Last Activity: 2022-01-14T16:57:17.978Z
```

## List Access Lists
```
vpnadmin ls_acl --vpn se0-dc2 --hub IT-VPN --group IT

VPN Vault Path Environment variable NOT set.
Default = networking/data/sevpn/hub_credentials


VPN Node: se0-dc2.internal.example.com

Rule No: 33
Rule Name: ALLOW ALL IT
State: Enabled
Src IP: 0.0.0.0 Mask: 0.0.0.0
Src User: IT
Dst IP: 0.0.0.0 Mask: 0.0.0.0
Dst User:
Protocol: 0
Src Port: 0
Dst Port: 0


```

## List Groups

```
vpnadmin ls_groups --vpn se0-dc2 --hub IT-VPN

VPN Vault Path Environment variable NOT set.
Default = networking/data/sevpn/hub_credentials


VPN Node: se0-dc2.internal.example.com
Group: IT | Real Name: IT Engineering Team | Number Users: 4

```

## List IP Addresses

```
vpnadmin ls_ip --vpn se0-dc2 --hub IT-VPN --username jdoe

VPN Vault Path Environment variable NOT set.
Default = networking/data/sevpn/hub_credentials


VPN Node: se0-dc2.internal.example.com
Session Name: jdoe
```

```
vpnadmin ls_ip --vpn se0-dc2 --hub IT-VPN --ip 10.10.10.207

VPN Vault Path Environment variable NOT set.
Default = networking/data/sevpn/hub_credentials


VPN Node: se0-dc2.internal.example.com
Session Name: jdoe
IP: 10.10.10.207
Connections Type: l2tp
DHCP: True
Created: 2022-01-27T09:01:57.485Z
Last Comms: 2022-01-27T09:02:27.837Z
```


## Add Users                

Users being added **Should** conform to LDAP names, unless its a User/Password Combination locally defined on VPN.


```
./vpnadmin add_user --vpn all --hub IT-VPN --username jsmith --group IT

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added

VPN Node: se0-dc3.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added

VPN Node: se0-dc3.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added

VPN Node: se0-dc1.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added

VPN Node: se0-dc1.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account added
```


## Search Users by Username

```
./vpnadmin search_user --vpn all --hub IT-VPN --username jdoe

VPN Node: se0-dc1.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2022-01-13T08:47:39.467Z

VPN Node: se0-dc2.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2021-11-17T08:53:11.897Z

VPN Node: se0-dc3.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2022-01-13T10:22:14.365Z

```

## Search Users by Real Name

```
./vpnadmin search_user --vpn all --hub IT-VPN --realname "doe"

VPN Node: se0-dc1.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2022-01-13T08:47:39.467Z

VPN Node: se0-dc2.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2021-11-17T08:53:11.897Z

VPN Node: se0-dc3.internal.example.com
User: jdoe | Real Name: John Doe | Group: IT | Last Login: 2022-01-13T10:22:14.365Z

```

## Delete User

```
./vpnadmin del_user --vpn all --hub IT-VPN --username jsmith

VPN Node: se0-dc1.internal.example.com
Username: jsmith | HUB: IT-VPN | State: removed

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | State: removed

VPN Node: se0-dc3.internal.example.com
Username: jsmith | HUB: IT-VPN | State: removed

```

## Edit User

```vpnadmin edit_user --vpn all --hub IT-VPN --username jsmith --group STANDARD

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: STANDARD| State: Account updated

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: STANDARD| State: Account updated
```

## Edit User with Password auth
```
vpnadmin edit_user --vpn all --hub IT-VPN --username jsmith --realname "tests" --group IT --auth password
Enter User Password:

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account updated

VPN Node: se0-dc2.internal.example.com
Username: jsmith | HUB: IT-VPN | Group: IT| State: Account updated
```

# Configuration Managed with YAML
All commands below are managed with ![vpn_config.yaml](vpn_config.yaml)

## Add HUBs
```
vpnadmin add_hub --vpn se0-dc2

VPN Login Failsafe check. This may take a few moments..

Enter LDAP/VPN Login Username to verify VPN Login: jdoe
User: jdoe
VPN Connected: se0-dc2
Safe to Manage VPN Cluster: se0
Proceeding with function: add_hub


VPN Node: se0-dc2.internal.example.com

VPN Missing Hubs:
Hub Name: TEST
------------------------------------------------------------------------------

Proposed Changes for se0-dc2.internal.example.com
Hub to be Added
HUB:TEST

1 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******

```

## Delete HUBs
You will not be able to delete a Hub if it has an Interface Bound.
Delete the Interface and remove first before trying to delete a Hub.

```
vpnadmin del_hub --vpn se0-dc2

VPN Login Failsafe check. This may take a few moments..

Enter LDAP/VPN Login Username to verify VPN Login: jdoe
User: jdoe
VPN Connected: se0-dc2
Safe to Manage VPN Cluster: se0
Proceeding with function: del_hub


VPN Node: se0-dc2.internal.example.com
VPN Redundant Hubs:
Hub: AWS-USA

HUB: AWS-USA Skipped Deletion
Bound to Interface in VSwitch. IP: 192.168.250.1
Delete interface to proceed

```

## Add INTERFACES
Adds Interfaces to VSwitch. The tooling defaults to VSwitch Named **MASTER**. This is how we have defined it in our setup.

If a HUB is not defined, the tooling will exit. A Interface must be bound to a HUB. The example is below.
```
vpnadmin add_interfaces --vpn se0-dc2

VPN Login Failsafe check. This may take a few moments..

Enter LDAP/VPN Login Username to verify VPN Login: jdoe
User: jdoe
VPN Connected: se0-dc2
Safe to Manage VPN Cluster: se0
Proceeding with function: add_interfaces

HUB: AWS-ASIA Not Defined, Skipping: 192.168.254.200
No changes required. Exiting
```

A proposed change with a defined HUB.
```
VPN Node: se0-dc2.internal.example.com

Missing Interfaces:
HUB: AZURE-EMEA
IP: 192.168.255.221
MASK: 255.255.255.252
------------------------------------------------------------------------------

Proposed Changes for se0-dc2.internal.example.com
MASTER Switch Stoppped
Interfaces to Add to Switch
HUB:AZURE-EMEA
IP:192.168.255.221
MASK:255.255.255.252
MASTER Switch Started

3 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******
```

## Delete Interfaces
Deleting Interfaces from VSwitch. If the HUB and Interface Pairing in the Config doesnt exist in the VPN, the Interface is skipped.
A Interface can not exist without a HUB.
```
HUB: AWS-UK Not Defined, Skipping: 192.168.250.20

VPN Node: se0-dc2.internal.example.com
VPN Redundant Interfaces:
HUB:AWS-IRL
IP:192.168.250.25
------------------------------------------------------------------------------

Proposed Changes for se0-dc2.internal.example.com
MASTER Switch Stoppped
Interfaces to Delete from Switch
HUB:AWS-IRL
MASTER Switch Started

3 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******
```

## Add Groups
Groups are the building blocks of RBAC services. It allows for Granular control of Users with ACL's.
Group Policies allows for setting paramters such as:
- Private LAN (no interclient communication)
- No IPv6
- Force DHCP ONLY
- Prevent DHCP offers from Clients
- Upload/Download Limits
- Activated Security Policy
- Client Connection Timeout
- Number of parralel connections (set to two incase of connection Dropping)
- Drop BUM (Uknown Unicast, Multicast, Broadcast, exceptions of ARP and DHCP)
- QoS for VOIP and Video Traffic

There Groups Config Adds or Updates the Group with the Parameters Provided.
```
Proposed Changes for se0-dc2.internal.example.com
New Group to be Added/Updated
HUB: DMZ-VPN
Group: QA
RealName: QA & DEV USER
Policy Enabled: True
VPN Access Enabled: True
No DHCP Client Server: True
Force DHCP: True
No BUM: True
Private Client Lan: True
Max Connections: 0
Client Timeout: 3600
Max Upload: 0
Max Download: 0
Multiple Login Connections: 2
QoS: True
Filter All IPv6: True
------------------------------------------------------------------------------


1 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******
```

## Update ACL's
ACL's are updated in a single API call. It replaces ACL's for the Entire VPN Namespace in a single iteration.
They are updated to Users at Run Time, so a User does not need to reconnect to see the changes.
This is why you are not able to manage a VPN cluster and update ACL's, to prvent breaking your own access.

Each VPN Namepsace has its own ACL's. The ACL's are defined per VPN location, eg dc1, dc2, dc3.

A diff Library called **Deepdiff** is used to verify any changes to an existing ACL.
```
Proposed Changes for se0-dc2.internal.example.com
ACL Diff
HTTPS
DestPortStart_u32
+443
-80
ACL Diff
IT ACCESS ALL
SrcUsername_str
+IT
-

ACL's to Update

Rule Number/Priority: 5
Name:: HTTPS
Active: True
Discarding: False
Source IP: 10.0.0.0
Src Mask: 255.0.0.0
Src Port: any
Src User/Group: any
Dst IP: 0.0.0.0
Dst Mask 0.0.0.0
Dst User/Group: any
Dst Port: 443

Rule Number/Priority: 8
Name:: IT ALL ACCESS
Active: True
Discarding: False
Source IP: 10.0.0.0
Src Mask: 255.0.0.0
Src Port: any
Src User/Group: IT
Dst IP: 0.0.0.0
Dst Mask 0.0.0.0
Dst User/Group: any
Dst Port: 443

2 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******

```

## Add/Update Radius Authentication
Authentication is set on a Per HUB basis. Since a HUB can be a termination point for different VPN Namespaces eg [VPN, QA-VPN, SC-VPN, SPICE-VPN].

This allows the flexibility of defining different Backend Authentication Radius Services.

QA-VPN for example uses LDAP only, where as the other VPN Namespaces all use our inbouse MFA service.

The Configuration paramters are Globally Defined Configuration which are applied per VPN Namespace.

If no changes are required, the output is like below:
```
vpnadmin update_radius --vpn se1-dc2 --hub IT-VPN

VPN Login Failsafe check. This may take a few moments..

Enter LDAP/VPN Login Username to verify VPN Login: jdoe
User: jdoe
VPN Connected: se0-dc2
Safe to Manage VPN Cluster: se1
Proceeding with function: update_radius

VPN State Correct. Exiting
```

If changes are to be made:
```
DMZ-VPN Auth Diff Changes
RadiusPort_u32
+2001
-2000
------------------------------------------------------------------------------

Proposed Changes for se0-dc2.internal.example.com
Radius Auth Config to be updated
HUB:DMZ-VPN
Server:127.0.0.1
Port:2001
Retry Interval:500
Secret: **redacted**

4 changes above would have been performed. Zero changes have been implemented.
******DryRun Completed******
```

# Data Doesnt Exist Flows

## Delete User

```
./vpnadmin del_user --vpn all --hub IT-VPN --username jsmith

VPN Node: se0-dc2.internal.example.com
Username: jsmith | State: No account found

VPN Node: se0-dc2.internal.example.com
Username: jsmith | State: No account found

VPN Node: se0-dc3.internal.example.com
Username: jsmith | State: No account found
```

## Search User

```
./vpnadmin search_user --vpn all --hub IT-VPN --username jsmith

VPN Node: se0-dc2.internal.example.com
No matching users found!

VPN Node: se0-dc2.internal.example.com
No matching users found!

VPN Node: se0-dc3.internal.example.com
No matching users found!

```

## Edit User

```
vpnadmin edit_user --vpn all --hub IT-VPN --username jsmith --realname "tests" --group IT --auth password
Enter User Password:

VPN Node: se0-dc2.internal.example.com
Username: jsmith | State: No account found

VPN Node: se0-dc2.internal.example.com
Username: jsmith | State: No account found

VPN Node: se0-dc3.internal.example.com
Username: jsmith | State: No account found
```

## User Diff
```
vpnadmin user_diff --vpn se1-dc2 se1-dc3

VPN Vault Path Environment variable NOT set.
Default = PATH


No IPA Cookie Found, redirecting to LDAP login
IPA Login Username: jdoe
Enter User Password:

IPA Cookie Session Valid

VPN Users Identical.

Checking VPN Users vs LDAP Users
jsmith: NO LDAP MATCH


No Group Mismatch found
```
