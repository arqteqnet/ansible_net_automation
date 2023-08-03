#!/usr/bin/env python3

################################################################################
##RPC PAYLOAD CLASS TO DYNAMICALLY CREATE PAYLOAD FOR REQUESTS##################
class rpc_call():

    def __init__(self, cli_args):
        self.cli_args = cli_args

        try:
            self.cli_args.hub = cli_args.hub
        except AttributeError:
            self.cli_args.hub = 'VPN'


    def test(self):
        #if function == 'test':
        payload = {
                  "jsonrpc": "2.0",
                  "id": "rpc_call_id",
                  "method": "Test",
                  "params": {
                  "IntValue_u32": 0,
                  "HubName_str": self.cli_args.hub
                      }
                  }
        return payload
    def ls_users(self):
        payload = {
               "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "EnumUser",
                "params": {
                "HubName_str": self.cli_args.hub
                   }
               }
        return payload

    def search_user(self):
        payload = {
               "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "EnumUser",
                "params": {
                "HubName_str": self.cli_args.hub
                   }
               }
        return payload

    def listeners(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumListener",
               "params": {}
                  }
        return payload

    def ls_bridge(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumEthernet",
               "params": {}
                  }
        return payload

    def add_bridge(self, bridge):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "AddLocalBridge",
              "params": {
                "DeviceName_str": bridge['name'],
                "HubNameLB_str": bridge['hub'],
                "Online_bool": bridge['online'],
                "Active_bool": bridge['active'],
                "TapMode_bool": bridge['tap_mode']
              }
            }

        return payload

    def delete_bridge(self, bridge):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "DeleteLocalBridge",
              "params": {
                "DeviceName_str": bridge['name'],
                "HubNameLB_str": bridge['hub']
              }
            }

        return payload

    def ls_hub(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumHub",
               "params": {}
                  }
        return payload

    def add_user(self):
        if self.cli_args.auth == 4:
            payload = {
                   "jsonrpc": "2.0",
                   "id": "rpc_call_id",
                   "method": "CreateUser",
                   "params": {
                   "HubName_str": self.cli_args.hub,
                   "Name_str": self.cli_args.username,
                   "Realname_utf": self.cli_args.realname,
                   "GroupName_str": self.cli_args.group,
                   "AuthType_u32": self.cli_args.auth
                       }
                   }
        elif self.cli_args.auth == 1:
            payload =  {
                    "jsonrpc": "2.0",
                    "id": "rpc_call_id",
                    "method": "CreateUser",
                    "params": {
                    "HubName_str": self.cli_args.hub,
                    "Name_str": self.cli_args.username,
                    "GroupName_str": self.cli_args.group,
                    "Realname_utf": self.cli_args.realname,
                    "AuthType_u32": self.cli_args.auth,
                    "Auth_Password_str": self.cli_args.password
                    }
                }

        return payload

    def del_user(self):
        payload = {
                "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "DeleteUser",
                "params": {
                "HubName_str": self.cli_args.hub,
                "Name_str": self.cli_args.username
                    }
                }
        return payload

    def edit_user(self):
        if self.cli_args.auth == 1:
            payload =  {
                    "jsonrpc": "2.0",
                    "id": "rpc_call_id",
                    "method": "SetUser",
                    "params": {
                    "HubName_str": self.cli_args.hub,
                    "Name_str": self.cli_args.username,
                    "GroupName_str": self.cli_args.group,
                    "Realname_utf": self.cli_args.realname,
                    "AuthType_u32": self.cli_args.auth,
                    "Auth_Password_str": self.cli_args.password
                    }
                }

        elif self.cli_args.auth == 4:
            payload =  {
                    "jsonrpc": "2.0",
                    "id": "rpc_call_id",
                    "method": "SetUser",
                    "params": {
                    "HubName_str": self.cli_args.hub,
                    "Name_str": self.cli_args.username,
                    "GroupName_str": self.cli_args.group,
                    "Realname_utf": self.cli_args.realname,
                    "AuthType_u32": self.cli_args.auth
                    }
                }
        return payload

    def ls_sessions(self, hub=None):
        if hub == None:
            hub = self.cli_args.hub

        payload =  {
                "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "EnumSession",
                "params": {
                "HubName_str": hub
                }
            }
        return payload

    def ls_ip(self):
        payload =  {
                "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "EnumIpTable",
                "params": {
                "HubName_str": self.cli_args.hub
                }
            }
        return payload

    def ls_groups(self):
        payload = {
                "jsonrpc": "2.0",
                "id": "rpc_call_id",
                "method": "EnumGroup",
                "params": {
                "HubName_str": self.cli_args.hub
                }
            }
        return payload

    def create_group(self, group):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "CreateGroup",
              "params": {
                "HubName_str": group['hub'],
                "Name_str": group['GroupName'],
                "Realname_utf": group['realname'],
                "Note_utf": "note",
                "UsePolicy_bool": group['PolicyActivated'],
                "policy:Access_bool": group['AllowVPNConnections'],
                "policy:DHCPFilter_bool": False,
                "policy:DHCPNoServer_bool": group['NoDHCPServerClient'],
                "policy:DHCPForce_bool": group['ForceDhcp'],
                "policy:NoBridge_bool": False,
                "policy:NoRouting_bool": False,
                "policy:CheckMac_bool": False,
                "policy:CheckIP_bool": False,
                "policy:ArpDhcpOnly_bool": group['DropBUM'],
                "policy:PrivacyFilter_bool": group['PrivateLan'],
                "policy:NoServer_bool": False,
                "policy:NoBroadcastLimiter_bool": False,
                "policy:MonitorPort_bool": False,
                "policy:MaxConnection_u32": 0,
                "policy:TimeOut_u32": group['ClientTimeOut'],
                "policy:MaxMac_u32": 0,
                "policy:MaxIP_u32": 0,
                "policy:MaxUpload_u32": group['MaxUpload'],
                "policy:MaxDownload_u32": group['MaxDownload'],
                "policy:FixPassword_bool": False,
                "policy:MultiLogins_u32": group['MultiLoginNumber'],
                "policy:NoQoS_bool": group['QoS'],
                "policy:RSandRAFilter_bool": False,
                "policy:RAFilter_bool": False,
                "policy:DHCPv6Filter_bool": False,
                "policy:DHCPv6NoServer_bool": False,
                "policy:NoRoutingV6_bool": False,
                "policy:CheckIPv6_bool": False,
                "policy:NoServerV6_bool": False,
                "policy:MaxIPv6_u32": 0,
                "policy:NoSavePassword_bool": False,
                "policy:AutoDisconnect_u32": 0,
                "policy:FilterIPv4_bool": False,
                "policy:FilterIPv6_bool": group['FilterIPv6'],
                "policy:FilterNonIP_bool": False,
                "policy:NoIPv6DefaultRouterInRA_bool": False,
                "policy:NoIPv6DefaultRouterInRAWhenIPv6_bool": False,
                "policy:VLanId_u32": 0,
                "policy:Ver3_bool": False
              }
            }

        return payload

    def set_group(self, group):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "SetGroup",
              "params": {
                "HubName_str": group['hub'],
                "Name_str": group['GroupName'],
                "Realname_utf": group['realname'],
                "Note_utf": "note",
                "UsePolicy_bool": group['PolicyActivated'],
                "policy:Access_bool": group['AllowVPNConnections'],
                "policy:DHCPFilter_bool": False,
                "policy:DHCPNoServer_bool": group['NoDHCPServerClient'],
                "policy:DHCPForce_bool": group['ForceDhcp'],
                "policy:NoBridge_bool": False,
                "policy:NoRouting_bool": False,
                "policy:CheckMac_bool": False,
                "policy:CheckIP_bool": False,
                "policy:ArpDhcpOnly_bool": group['DropBUM'],
                "policy:PrivacyFilter_bool": group['PrivateLan'],
                "policy:NoServer_bool": False,
                "policy:NoBroadcastLimiter_bool": False,
                "policy:MonitorPort_bool": False,
                "policy:MaxConnection_u32": 0,
                "policy:TimeOut_u32": group['ClientTimeOut'],
                "policy:MaxMac_u32": 0,
                "policy:MaxIP_u32": 0,
                "policy:MaxUpload_u32": group['MaxUpload'],
                "policy:MaxDownload_u32": group['MaxDownload'],
                "policy:FixPassword_bool": False,
                "policy:MultiLogins_u32": group['MultiLoginNumber'],
                "policy:NoQoS_bool": group['QoS'],
                "policy:RSandRAFilter_bool": False,
                "policy:RAFilter_bool": False,
                "policy:DHCPv6Filter_bool": False,
                "policy:DHCPv6NoServer_bool": False,
                "policy:NoRoutingV6_bool": False,
                "policy:CheckIPv6_bool": False,
                "policy:NoServerV6_bool": False,
                "policy:MaxIPv6_u32": 0,
                "policy:NoSavePassword_bool": False,
                "policy:AutoDisconnect_u32": 0,
                "policy:FilterIPv4_bool": False,
                "policy:FilterIPv6_bool": group['FilterIPv6'],
                "policy:FilterNonIP_bool": False,
                "policy:NoIPv6DefaultRouterInRA_bool": False,
                "policy:NoIPv6DefaultRouterInRAWhenIPv6_bool": False,
                "policy:VLanId_u32": 0,
                "policy:Ver3_bool": False
              }
            }

        return payload

    def del_group(self, data):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "DeleteGroup",
              "params": {
                "HubName_str": data['hub'],
                "Name_str": data['GroupName']
              }
            }

        return payload

    def ls_acl(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumAccess",
               "params": {
               "HubName_str": self.cli_args.hub
               }
            }
        return payload

    def ls_overlays(self):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "EnumLink",
              "params": {
                "HubName_str": self.cli_args.hub
              }
            }
        return payload

    def add_acl(self, acls):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "SetAccessList",
              "params": {
                "HubName_str": self.cli_args.hub,
                "AccessList": []
                }
              }
        try:
############Since Mac address of clients are dynamic we are nt using this paramter
            acl_id = 0
            for acl in acls:
                acl_id += 1
                if acl['ip version'] == "ipv4":
                    ipv6_bool = False
                    ipv6_src_ip_binary = 'AAAAAAAAAAAAAAAAAAAAAA=='
                    ipv6_src_mask_binary = 'AAAAAAAAAAAAAAAAAAAAAA=='
                    ipv6_dst_ip_binary = 'AAAAAAAAAAAAAAAAAAAAAA=='
                    ipv6_dst_mask_binary = 'AAAAAAAAAAAAAAAAAAAAAA=='
                    mac_binary = 'AAAAAAAA'

                if 'src ip' in acl.keys():
                    src_ip = acl['src ip']
                    src_mask = acl['src mask']
                elif 'src ip' not in acl.keys():
                    src_ip = '0.0.0.0'
                    src_mask = '0.0.0.0'

                if 'dst ip' in acl.keys():
                    dst_ip = acl['dst ip']
                    dst_mask = acl['dst mask']
                elif 'dst ip' not in acl.keys():
                    dst_ip = '0.0.0.0'
                    dst_mask = '0.0.0.0'

                if 'src group' in acl.keys():
                    src_user = acl['src group']
                elif 'src group' not in acl.keys():
                    src_user = ''

                if 'dst group' in acl.keys():
                    dst_user = acl['dst group']
                elif 'dst group' not in acl.keys():
                    dst_user = ''

                if 'protocol' in acl.keys():
                    if acl['protocol'] == 'tcp':
                        protocol = 6
                    elif acl['protocol'] == 'udp':
                        protocol = 17
                elif 'protocol' not in acl.keys():
                    protocol = 0

                if 'src port' in acl.keys():
                    if isinstance(acl['src port'], int):
                        src_port_start = acl['src port']
                        src_port_end = acl['src port']
                    if isinstance(acl['src port'], str):
                        src_port_start = int(acl['src port'].split('-')[0])
                        src_port_end = int(acl['src port'].split('-')[1])
                elif 'src port' not in acl.keys():
                        src_port_start = 0
                        src_port_end = 0

                if 'dst port' in acl.keys():
                    if isinstance(acl['dst port'], int):
                        dst_port_start = acl['dst port']
                        dst_port_end = acl['dst port']
                    if isinstance(acl['dst port'], str):
                        dst_port_start = int(acl['dst port'].split('-')[0])
                        dst_port_end = int(acl['dst port'].split('-')[1])
                elif 'dst port' not in acl.keys():
                        dst_port_start = 0
                        dst_port_end = 0


                payload['params']['AccessList'].append({
                        "Id_u32": acl_id,
                        "Note_utf": acl['name'],
                        "Active_bool": acl['active'],
                        "Priority_u32": acl_id,
                        "Discard_bool": acl['discard'],
                        "IsIPv6_bool": ipv6_bool,
                        "SrcIpAddress_ip": src_ip,
                        "SrcSubnetMask_ip": src_mask,
                        "DestIpAddress_ip": dst_ip,
                        "DestSubnetMask_ip": dst_mask,
                        "SrcIpAddress6_bin": ipv6_src_ip_binary,
                        "SrcSubnetMask6_bin": ipv6_src_mask_binary,
                        "DestIpAddress6_bin": ipv6_dst_ip_binary,
                        "DestSubnetMask6_bin": ipv6_dst_mask_binary,
                        "Protocol_u32": protocol,
                        "SrcPortStart_u32": src_port_start,
                        "SrcPortEnd_u32": src_port_end,
                        "DestPortStart_u32": dst_port_start,
                        "DestPortEnd_u32": dst_port_end,
                        "SrcUsername_str": src_user,
                        "DestUsername_str": dst_user,
                        "CheckSrcMac_bool": False,
                        "SrcMacAddress_bin": mac_binary,
                        "SrcMacMask_bin": mac_binary,
                        "CheckDstMac_bool": False,
                        "DstMacAddress_bin": mac_binary,
                        "DstMacMask_bin": mac_binary,
                        "CheckTcpState_bool": False,
                        "Established_bool": False,
                        "Delay_u32": 0,
                        "Jitter_u32": 0,
                        "Loss_u32": 0,
                        "RedirectUrl_str": ""
                      }
                    )

        except KeyError as err:
            print(f"Key Error: {err}, Exiting")
            exit(1)

        return payload

    def ls_routes(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumL3Table",
               "params": {
               "Name_str": self.cli_args.l3_switch
               }
            }
        return payload

    def ls_interfaces(self, ):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumL3If",
               "params": {
               "Name_str": self.cli_args.l3_switch
               }
            }
        return payload

    def ls_switch(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumL3Switch",
               "params": {}
            }
        return payload

    def ls_bridges(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "EnumLocalBridge",
               "params": {}
            }
        return payload


    def start_switch(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "StartL3Switch",
               "params": {
               "Name_str": self.cli_args.l3_switch
               }
            }
        return payload

    def stop_switch(self):
        payload = {
               "jsonrpc": "2.0",
               "id": "rpc_call_id",
               "method": "StopL3Switch",
               "params": {
               "Name_str": self.cli_args.l3_switch
               }
            }
        return payload

    def add_interface(self, interface):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "AddL3If",
              "params": {
              "Name_str": self.cli_args.l3_switch,
              "HubName_str": interface['hub'],
              "IpAddress_ip": interface['ip'],
              "SubnetMask_ip": interface['mask']
              }
            }
        return payload

    def del_interface(self, hub):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "DelL3If",
              "params": {
              "Name_str": self.cli_args.l3_switch,
              "HubName_str": hub
              }
            }
        return payload

    def add_route(self, route):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "AddL3Table",
              "params": {
              "Name_str": self.cli_args.l3_switch,
              "NetworkAddress_ip": route['network'],
              "SubnetMask_ip": route['mask'],
              "GatewayAddress_ip": route['gw'],
              "Metric_u32": route['metric']
              }
            }


        return payload

    def del_route(self, route):
        print(route)
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "DelL3Table",
              "params": {
              "Name_str": self.cli_args.l3_switch,
              "NetworkAddress_ip": route['network'],
              "SubnetMask_ip": route['mask'],
              "GatewayAddress_ip": route['gw'],
              "Metric_u32": route['metric']
              }
            }
        return payload

    def add_hub(self, hub, secret=""):
        payload = {
            "jsonrpc": "2.0",
            "id": "rpc_call_id",
            "method": "CreateHub",
            "params": {
            "HubName_str": hub,
            "AdminPasswordPlainText_str": secret,
            "Online_bool": True,
            "MaxSession_u32": 0,
            "NoEnum_bool": False,
            "HubType_u32": 0
            }
          }

        return payload

    def del_hub(self, hub):
        payload = {
            "jsonrpc": "2.0",
            "id": "rpc_call_id",
            "method": "DeleteHub",
            "params": {
            "HubName_str": hub
            }
          }

        return payload

    def get_hub_radius(self):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "GetHubRadius",
              "params": {
                "HubName_str": self.cli_args.hub
              }
            }

        return payload

    def set_hub_radius(self, radius_config):
        payload = {
              "jsonrpc": "2.0",
              "id": "rpc_call_id",
              "method": "SetHubRadius",
              "params": {
                "HubName_str": self.cli_args.hub,
                "RadiusServerName_str": radius_config['IP'],
                "RadiusPort_u32": radius_config['Port'],
                "RadiusSecret_str": radius_config['secret'],
                "RadiusRetryInterval_u32": radius_config['RetryInterval']
              }
            }


        return payload
