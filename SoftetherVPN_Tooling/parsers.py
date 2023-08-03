#!/usr/bin/env python3
from outputcolours import bcolours
from deepdiff import DeepDiff
import itertools
import sys
################################################################################
##CLASS TO LOGICAL PARSER RESPONSE DATA INTO FORMAT TO ITERATE AND SEARCH#######
class vpndata_parsers:
    def __init__(self, unsanity_data):
#########VPN RESPONSE DATA################
        self.unsanity_data = unsanity_data

################################################################################
####ITERATES OF USERS INTO ARRAY AND THEN SPLIT INTO GROUP MEMBERSHIP###########
    def UserList(self):
        Users = []
        vpn_dict = {}
        groups = []
        try:
            for data in self.unsanity_data['result']['UserList']:
                if isinstance(data, dict):
                    if data['Name_str']:
                        Users.append({ data['Name_str'] : { 'Group' : data['GroupName_str'],
                                                            'Real Name' : data['Realname_utf'],
                                                            'LastLogin': data['LastLoginTime_dt'] } })
            for dict_data in Users:
                for key, value in dict_data.items():
                    if value['Group'] not in groups:
                        groups.append(value['Group'])
                        vpn_dict[value['Group']] = []
                        vpn_dict[value['Group']].append({ key : { 'Real Name' : value['Real Name'].lower(),
                                                                  'LastLogin': value['LastLogin'] } } )
                    else:
                        vpn_dict[value['Group']].append({ key : { 'Real Name' : value['Real Name'].lower(),
                                                                  'LastLogin': value['LastLogin'] } } )
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict

####PARSES SESSION DATA INTO FORMAT TO EASILY OUTPUT TO STDOUT#######
    def SessionList(self):
        Users = []
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']['SessionList']:
                if isinstance(data, dict):
                    if data['Name_str']:
                        Users.append({ data['Name_str'] : { 'IP' : data['ClientIP_ip'],
                                                            'Username' : data['Username_str'],
                                                            'Created': data['CreatedTime_dt'],
                                                            'Last Comms': data['LastCommTime_dt']  } })
            vpn_dict.update({"Session List" : Users})

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict


####PARSES GROUP DATA INTO DICTIONARY###########
    def GroupList(self):
        groups = []
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']['GroupList']:
                if isinstance(data, dict):
                    if data['Name_str']:
                        groups.append({ data['Name_str'] : { 'Real Group Name' : data['Realname_utf'],
                                                             'Number Users' : data['NumUsers_u32']  } })
            vpn_dict.update({"Groups" : groups})

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict

####PARSES ACL DATA AND LOGICALLY ARRANGES FOR EASY OUTPUT TO STDOUT############
    def AccessList(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']['AccessList']:
                if isinstance(data, dict):
    ################UPDATES PROTOCOL NUMBER TO USER READABLE PROTOCOL###############
                    if data['Protocol_u32'] == 6:
                        data['Protocol_u32'] = 'TCP'
                    elif data['Protocol_u32'] == 17:
                        data['Protocol_u32'] = 'UDP'
                    elif data['Protocol_u32'] == 0:
                        data['Protocol_u32'] = 'ALL'
                    vpn_dict.update({ data['Id_u32'] : { 'Rule Name': data['Note_utf'],
                                      'State' :data['Active_bool'], 'Discard': data['Discard_bool'],
                                      'Source IP': [ data['SrcIpAddress_ip'], data['SrcSubnetMask_ip'] ],
                                      'Destination IP':[data['DestIpAddress_ip'],data['DestSubnetMask_ip']],
                                      'Protocol': data['Protocol_u32'],
                                      'Source Port': [data['SrcPortStart_u32'],data['SrcPortEnd_u32']],
                                      'Destination Port': [data['DestPortStart_u32'],data['DestPortEnd_u32']],
                                      'Source User': data['SrcUsername_str'],
                                      'Destination User': data['DestUsername_str'] }} )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict


    def ListIPs(self):
        vpn_dict = {}
        users = []
        try:
            for data in self.unsanity_data['result']['IpTable']:
                if isinstance(data, dict):
                    if data['SessionName_str']:
                        users.append({ data['SessionName_str'].lower() : {
                                       'IP' : data['IpAddress_ip'],
                                       'DHCP': data['DhcpAllocated_bool'],
                                        'Created': data['CreatedTime_dt'],
                                        'Last Comms': data['UpdatedTime_dt']
                                             }
                                        }
                                    )
                vpn_dict.update({"IP Table" : users})

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict


    def ListSwitch(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']["L3SWList"]:
                vpn_dict.update( { data['Name_str'] : {
                                  'Active': data['Active_bool'],
                                  'Online': data['Online_bool']
                                        }
                                    }
                                )
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None


        return vpn_dict


    def ListInterfaces(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']['L3IFList']:
                vpn_dict.update( { data['HubName_str'] : {
                                   'Network': data['IpAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip']
                                        }
                                    }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict


    def ListRoutes(self):
        routes = []
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']['L3Table']:
                routes.append( { 'Network': data['NetworkAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip'],
                                   'Gateway': data['GatewayAddress_ip'],
                                   'Metric': data['Metric_u32'],
                                    }
                                )

            vpn_dict.update( {'Routes': routes } )
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            vpn_dict = None

        return vpn_dict


    def AddInterface(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']:
                vpn_dict.update( { data['Name_str'] : {
                                   'Hub': data['HubName_str'],
                                   'Network': data['IpAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip']
                                        }
                                    }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        return vpn_dict


    def DelInterface(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']:
                vpn_dict.update( { data['Name_str'] : {
                                   'Hub': data['HubName_str'],
                                   'Network': data['IpAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip']
                                        }
                                    }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        return vpn_dict


    def AddRoute(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']:
                vpn_dict.update( { data['Name_str'] : {
                                   'Network': data['NetworkAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip'],
                                   'Gateway': data['GatewayAddress_ip'],
                                   'Metric': data['Metric_u32'],
                                        }
                                    }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        return vpn_dict


    def DelRoute(self):
        vpn_dict = {}
        try:
            for data in self.unsanity_data['result']:
                vpn_dict.update( { data['Name_str'] : {
                                   'Network': data['NetworkAddress_ip'],
                                   'Subnet Mask': data['SubnetMask_ip'],
                                   'Gateway': data['GatewayAddress_ip'],
                                   'Metric': data['Metric_u32'],
                                        }
                                    }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        return vpn_dict

################################################################################
#####CLASS CALLED TO OUTPUT DATA IN POST PARSED FORMAT OR ORIGINAL FORMAT#######

class vpndata_output():
    def __init__(self, args, data, error_data, vpn_node):
        self.args = args
        self.data = data
        self.error_data = error_data
        self.vpn_node = vpn_node
########ARRAY OF POTENTIAL VPN CLIENTS##############################
        self.vpn_client_types = ['l2tp', 'openvpn_l3', 'openvpn_l2']

########ENURE USERNAME VALUE##################
        try:
            self.username = self.args.username
        except AttributeError:
            self.username = None

########ENSURE REALNAME VALUE#################
        try:
            self.realname = self.args.realname
        except AttributeError:
            self.realname = None

########ENSURE GROUP NAME VALUE###############
        try:
            self.group = self.args.group
        except AttributeError:
            self.group = None

########ENSURE IP VALUE#######################
        try:
            self.ip = self.args.ip
        except AttributeError:
            self.ip = None

########REMOVE CASE SENSITIVITY##################
        if self.username is not None:
            self.username = self.username.lower()
        if self.realname is not None:
            self.realname = self.realname.lower()


################################################################################
####STDOUT SESSIONS######
    def ls_sessions(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        for key, values in self.data.items():
            for session in values:
                for user, details in session.items():
                    print(f"""Username: {details['Username']} | IP: {details['IP']} | Connection Name: {user} |
Created: {details['Created']} | Last Activity: {details['Last Comms']}""" )



####STDOUT USERS POST PARSED FORMAT######
    def ls_users(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        for group_name, users in self.data.items():
            if self.group is None:
                print(f"Group: {group_name}")
                for user in users:
                    for user, details in user.items():
                        print(f"User: {user} | Real Name: {details['Real Name']} | Last Login: {details['LastLogin']}")
            else:
                if self.group == group_name:
                    print(f"Group: {group_name}")
                    for user in users:
                        for user, details in user.items():
                            print(f"User: {user} | Real Name: {details['Real Name']} | Last Login: {details['LastLogin']}")


####STDOUT GROUPS######
    def ls_groups(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            for group_data in self.data['Groups']:
                for group, group_info in group_data.items():
                    print(f"Group: {group} | Real Name: {group_info['Real Group Name']} | Number Users: {group_info['Number Users']}")
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass

####STDOUT ACL#######
    def ls_acl(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        for acl_no, acl_data in self.data.items():
############IF NO GROUP IS SPECIFIED FOR SPECIFIC ACL######
            if self.group is None:
                print(f"\nRule No: {acl_no}\nRule Name: {acl_data['Rule Name']}")
                if acl_data['State'] == True:
                    print("State: Enabled")
                else:
                    print("State: Disabled")
                print(f"Discard: {acl_data['Discard']}")
                print(f"Src IP: {acl_data['Source IP'][0]} Mask: {acl_data['Source IP'][1]}")
                if {acl_data['Source User']} != '':
                    print(f"Src User: {acl_data['Source User']}")
                print(f"Dst IP: {acl_data['Destination IP'][0]} Mask: {acl_data['Destination IP'][1]}")
                if {acl_data['Destination User']} != '':
                    print(f"Dst User: {acl_data['Destination User']}")
                print(f"Protocol: {acl_data['Protocol']}")
                if acl_data['Source Port'][0] == 0 and acl_data['Source Port'][1] == 0:
                    print("Src Port: 0")
                else:
                    print(f"Src port: {acl_data['Source Port'][0]} : {acl_data['Source Port'][1]}")
                if acl_data['Destination Port'][0] == 0 and acl_data['Destination Port'][1] == 0:
                    print("Dst Port: 0")
                else:
                    print(f"Dst Port: {acl_data['Destination Port'][0]} : {acl_data['Destination Port'][1]}")
            else:
#################ALLOW ACL BASED ON GROUP#################
                if self.group == acl_data['Destination User'] or self.group == acl_data['Source User']:
                    print(f"\nRule No: {acl_no}\nRule Name: {acl_data['Rule Name']}")
                    if acl_data['State'] == True:
                        print("State: Enabled")
                    else:
                        print("State: Disabled")
                    print(f"Src IP: {acl_data['Source IP'][0]} Mask: {acl_data['Source IP'][1]}")
                    if {acl_data['Source User']} != '':
                        print(f"Src User: {acl_data['Source User']}")
                    print(f"Dst IP: {acl_data['Destination IP'][0]} Mask: {acl_data['Destination IP'][1]}")
                    if {acl_data['Destination User']} != '':
                        print(f"Dst User: {acl_data['Destination User']}")
                    print(f"Protocol: {acl_data['Protocol']}")
                    if acl_data['Source Port'][0] == 0 and acl_data['Source Port'][1] == 0:
                        print("Src Port: 0")
                    else:
                        print(f"Src port: {acl_data['Source Port'][0]} : {acl_data['Source Port'][1]}")
                    if acl_data['Destination Port'][0] == 0 and acl_data['Destination Port'][1] == 0:
                        print("Dst Port: 0")
                    else:
                        print(f"Dst Port: {acl_data['Destination Port'][0]} : {acl_data['Destination Port'][1]}")

    def ls_overlays(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            if self.data != {}:
                if self.data['LinkList'] != []:
                    print(f"{bcolours.BOLD}Hub: {self.data['HubName_str']}{bcolours.ENDC}")
                    for connection in self.data['LinkList']:
                        print(f"\nOverlay Name: {connection['AccountName_utf']}")
                        print(f"Remote Hub: {connection['ConnectedHubName_str']}")
                        print(f"Connected: {connection['Connected_bool']}")
                        print(f"Connected Time: {connection['ConnectedTime_dt']}")
                        print(f"IP/Hostname: {connection['Hostname_str']}")
                        print(f"Last Error: {connection['LastError_u32']}")
                        print(f"Online: {connection['Online_bool']}")
                else:
                    print(f"{bcolours.BOLD}No Overlays Configured{bcolours.ENDC}")
            else:
                print(f"{bcolours.BOLD}HUB not found.{bcolours.ENDC}")
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass


####SEARCH USER WITH USERNAME OR REALNAME##########
    def search_user(self):
        user_present = 0
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        if self.username is None and self.realname is None:
            print("Userame or RealName not supplied")
            exit(0)
        if self.data != {}:
            for group, users in self.data.items():
                for user in users:
#####################USERNAME SEARCH. EXACT MATCH NEEDED###################
                    if self.username is not None and self.realname is None:
                        for user_key, user_values in user.items():
                            if self.username == user_key:
                                user_present += 1
                                print(f"User: {user_key}\nReal Name: {user_values['Real Name']}")
                                print(f"Group: {group}\nLast Login: {user_values['LastLogin']}")
####################REALNAME SEARCH. FILTER MATCH############################
                    elif self.realname is not None and self.username is None:
                        for user_key, user_values in user.items():
                            if self.realname in user_values['Real Name']:
                                user_present += 1
                                print(f"User: {user_key}\nReal Name: {user_values['Real Name']}")
                                print(f"Group: {group}\nLast Login: {user_values['LastLogin']}")
#############NO USER MATCHES######
            if user_present == 0:
                print(f"{bcolours.FAIL}No matching users found!{bcolours.ENDC}")


####ADD USER STDOUT#####
    def add_user(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        if self.data != {}:
            print(f"Username: { self.data['Name_str'] }")
            print(f"HUB: { self.data['HubName_str'] }")
            print(f"Group: { self.data['GroupName_str'] }")
            print(f"{bcolours.OKGREEN}State: Account added{bcolours.ENDC}")
        elif self.error_data != {}:
            if self.error_data['error']['code'] == 66:
                print(f"Username: { self.username } | {bcolours.FAIL}State: Account already exists{bcolours.ENDC}")

####DELETE USER STDOUT
    def del_user(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        if self.data != {}:
            print(f"Username: { self.data['Name_str'] }")
            print(f"HUB: { self.data['HubName_str'] }")
            print(f"{bcolours.OKGREEN}State: Account Deleted{bcolours.ENDC}")
        elif self.error_data != {}:
            if self.error_data['error']['code'] == 29:
                print(f"Username: { self.username } | {bcolours.FAIL}State: No account found{bcolours.ENDC}")


####TEST STDOUT####
    def test(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        if self.data['StrValue_str']:
            print(f"{bcolours.OKGREEN}Test Successful{bcolours.ENDC}")


####EDIT USER STDOUT####
    def edit_user(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        if self.data != {}:
            print(f"Username: { self.data['Name_str'] }")
            print(f"HUB: { self.data['HubName_str'] }")
            print(f"Group: { self.data['GroupName_str'] }")
            print(f"{bcolours.OKGREEN}State: Account Updated{bcolours.ENDC}")
        elif self.error_data != {}:
            if self.error_data['error']['code'] == 29:
                print(f"Username: { self.username } | {bcolours.FAIL}State: No account found{bcolours.ENDC}")


####LIST ROUTES STDOUT####
    def ls_routes(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            for routes in self.data['Routes']:
                for data in routes:
                    print(f"Network: {data['Network']}\nSubnet: {data['Subnet Mask']}\nGateway: {data['Gateway']}\nMetric: {data['Metric']}")
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass

####ROUTES TO BE ADDED STDOUT#####
    def routes(self):
        try:
            for routes in self.data['Routes']:
                for data in routes:
                    print(f"Network: {data['Network']}\nSubnet: {data['Subnet Mask']}\nGateway: {data['Gateway']}\nMetric: {data['Metric']}")

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass

####LIST IP STDOUT###
    def ls_ip(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        for key, values in self.data.items():
            for session in values:
                for user, details in session.items():
                    try:
########################SPLITTING SESSION NAME INTO USERNAME########
                        sid, uname, type, number = user.split('-')
                        type = type[1:-1]
######################################################################################################################################
########################ENSURING ONLY SESSIONS WITH VPN CONNECTION, NOT CASCADE SESSIONS##############################################
                        if type in self.vpn_client_types:
                            if self.username is None and self.ip is None:
                                print(f"""Session Name: {uname}\nIP: {details['IP']}\nConnections Type: {type}\nDHCP: {details['DHCP']}
Created: {details['Created']}\nLast Comms: {details['Last Comms']}\n""" )

                            elif self.username is not None and self.username in uname:
                                print(f"""Session Name: {uname}\nIP: {details['IP']}\nConnections Type: {type}\nDHCP: {details['DHCP']}
Created: {details['Created']}\nLast Comms: {details['Last Comms']}\n""" )

                            elif self.ip is not None and self.ip == details['IP']:
                                print(f"""Session Name: {uname}\nIP: {details['IP']}\nConnections Type: {type}\nDHCP: {details['DHCP']}
Created: {details['Created']}\nLast Comms: {details['Last Comms']}\n""" )

                    except ValueError:
                        pass


####LIST VIRTUAL SWITCHES#####
    def ls_switch(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            for values in self.data['L3SWList']:
                print(f"{bcolours.OKGREEN}Switch: {values['Name_str']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Active: {values['Active_bool']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Online: {values['Online_bool']}{bcolours.ENDC}")
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass

####LIST INTERFACES ON SELECTED VSWITCH######
    def ls_interfaces(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            for values in self.data['L3IFList']:
                print(f"{bcolours.OKGREEN}\nHub Interface: {values['HubName_str']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Ip Address: {values['IpAddress_ip']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Subnet Mask: {values['SubnetMask_ip']}{bcolours.ENDC}")
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass

####LIST ROUTES ON SELECTED VSWITCH
    def ls_routes(self):
        print(f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
        try:
            for values in self.data['L3Table']:
                print(f"{bcolours.OKGREEN}\nNetwork: {values['NetworkAddress_ip']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Subnet Mask: {values['SubnetMask_ip']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Gateway: {values['GatewayAddress_ip']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Route Metric: {values['Metric_u32']}{bcolours.ENDC}")
        except KeyError as err:
            print(f"{bcolours.BOLD}KeyError: No Data. Skipping{bcolours.ENDC}")
            pass
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            pass
################################################################################
################PARSER FOR COMPLEX/CUSTOM PLAYLOADS#############################
class data_parser:
    def __init__(self, args, yaml_data, vpn_data, secret, vpn_request):
        self.yaml_data = yaml_data
        self.vpn_node = vpn_data[args.vpn[0]]['address']
        self.args = args
        self.vpn_data = vpn_data
        self.secret = secret
        self.vpn_request = vpn_request

####COMPARES DATASETS FOR MISSING OR REDUNDANT ROUTES##########
    def Routes(self, vpn_data):
        ret = None
        missing_routes = {'vpn_missing': [], 'vpn_redundant': {} }
        preprocess = {}
        processed_routes = []
        try:
            for routes in vpn_data['result']['L3Table']:
                if isinstance(routes, dict):
    ################PARSING VPN DATA INTO DATASET TO COMPARE AGAINST################
                    preprocess.update( { routes['NetworkAddress_ip'] : {
                                     'network': routes['NetworkAddress_ip'],
                                     'gw': routes['GatewayAddress_ip'],
                                     'metric': routes['Metric_u32'],
                                     'mask': routes['SubnetMask_ip']
                                        }
                                    }
                                )
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)
        try:
############OBTAINING DATA FROM YAML CONFIG##############
            for route_name, route_details in self.yaml_data[self.vpn_node][self.args.l3_switch.lower()]['routes'].items():
                processed_routes.append(route_details['network'])
################CHECK IF YAML ROUTE EXISTS IN PROCESSED VPN DATA################
                if route_details['network'] not in preprocess.keys():
                    missing_routes['vpn_missing'].append(route_details)
        except KeyError:
            print(f"No config found for {self.vpn_node}, Exiting")
            sys.exit(1)
########CHECKING FOR VPN REDUNDANT ROUTES#######################################
        for route, data in preprocess.items():
            if route not in processed_routes:
                missing_routes['vpn_redundant'].update({ route : data })

########STDOUT MISSING ROUTES FROM YAML#########################################
        if self.args.command == "add_routes":
            if missing_routes['vpn_missing'] != []:
                ret = missing_routes['vpn_missing']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"\n{bcolours.BOLD}Missing Routes:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for route in missing_routes['vpn_missing']:
                    print(f"{bcolours.OKGREEN}Network: {route['network']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Subnet Mask: {route['mask']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Gateway: {route['gw']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Route Metric: {route['metric']}{bcolours.ENDC}")
                    #print("#"*len(stdout))

########STDOUT REDUNDANT VPN ROUTES STAGED FOR DELETION#########################
        elif self.args.command == "del_routes":
            if missing_routes['vpn_redundant'] != {}:
                ret = missing_routes['vpn_redundant']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"{bcolours.BOLD}VPN Redundant Routes:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for route, data in missing_routes['vpn_redundant'].items():
                    print(f"{bcolours.OKGREEN}Network: {route}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Subnet Mask: {data['mask']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Gateway: {data['gw']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Route Metric: {data['metric']}{bcolours.ENDC}")
                    #print("#"*len(stdout))

        return ret

####ROUTER STOP RESPONSE JSON DATA######
    def RouterStop(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.OKGREEN}{vpn_data['params']['Name_str']} Switch Stoppped{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}{vpn_data['result']['Name_str']} Switch Stoppped{bcolours.ENDC}")
        else:
            print(vpn_data)

#####ROUTER START RESPONSE STDOUT#########
    def RouterStart(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.OKGREEN}{vpn_data['params']['Name_str']} Switch Started{bcolours.ENDC}")
            #print("#"*length)
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}{vpn_data['result']['Name_str']} Switch Started{bcolours.ENDC}")
        else:
            print(vpn_data)

####ADD ROUTE STDOUT#####################
    def AddedRoute(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Route add{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Net:{vpn_data['params']['NetworkAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Mask:{vpn_data['params']['SubnetMask_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Gateway:{vpn_data['params']['GatewayAddress_ip']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Route added\nNet:{vpn_data['result']['NetworkAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Mask:{vpn_data['result']['SubnetMask_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Gateway:{vpn_data['result']['GatewayAddress_ip']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####ADD ROUTE STDOUT#####################
    def DeletedRoute(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Route Delete{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Net:{vpn_data['params']['NetworkAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Mask:{vpn_data['params']['SubnetMask_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Gateway:{vpn_data['params']['GatewayAddress_ip']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Route added\nNet:{vpn_data['result']['NetworkAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Mask:{vpn_data['result']['SubnetMask_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Gateway:{vpn_data['result']['GatewayAddress_ip']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####ADD HUB STDOUT#####################
    def AddHub(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Hub to be Added{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['params']['HubName_str']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Hub added\nHUB:{vpn_data['result']['HubName_str']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####DEL HUB STDOUT#####################
    def DeleteHub(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Hub to be Deleted{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['params']['HubName_str']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Hub Deleted")
            print(f"HUB:{vpn_data['result']['HubName_str']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####SKIP DELETION OF HUB BOUND TO INTERFACES####################################
    def HubInUse(self, vpn_data: dict, interfaces):
        ret = None
        hub_interfaces = {}
        delete_hubs = []
        try:
            for interface in interfaces['result']['L3IFList']:
                if isinstance(interface, dict):
                    hub_interfaces.update({ interface['HubName_str']: {
                                            "IP Address":  interface['IpAddress_ip'],
                                            "Mask": interface['SubnetMask_ip']
                                            }
                                          }
                                        )
        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")

        for hub in vpn_data:
            if hub in hub_interfaces.keys():
                print(f"\n{bcolours.FAIL}HUB: {hub} Skipped Deletion{bcolours.ENDC}")
                print(f"{bcolours.BOLD}Bound to Interface in VSwitch. IP: {hub_interfaces[hub]['IP Address']}{bcolours.ENDC}")
                print(f"Delete interface to proceed")
            else:
                delete_hubs.append(hub)

        ret = delete_hubs
        return ret


    def Bridges(self, vpn_data: dict):

        bridges = {}
        processed_bridges = []
        missing_bridges = { 'vpn_missing' : [], 'vpn_redundant' : []}
        try:
            for bridge in vpn_data['result']['LocalBridgeList']:
                if isinstance(bridge, dict):
                    bridges.update({bridge['DeviceName_str']: bridge})

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")

        try:
            for bridge_key, bridge_v in self.yaml_data[self.vpn_node]['bridges'].items():
                if bridge_v['name'] not in bridges.keys():
                    missing_bridges['vpn_missing'].append(bridge_v)
                    processed_bridges.append(bridge_v['name'])


        except KeyError as err:
            print(f"KeyError: {err}")
            print(f"No config found for {self.vpn_node}, Exiting")
            sys.exit(1)

        for bridge_v, bridge_k in bridges.items():
            if bridge_v not in processed_bridges:
                missing_bridges['vpn_redundant']

        return missing_bridges

####ADD INTERFACE STDOUT#####################
    def AddInterface(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Interfaces to Add to Switch{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['params']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}IP:{vpn_data['params']['IpAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}MASK:{vpn_data['params']['SubnetMask_ip']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Interface Added{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['result']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}IP:{vpn_data['result']['IpAddress_ip']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}MASK:{vpn_data['result']['SubnetMask_ip']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####DELETE INTERFACE STDOUT#####################
    def DeleteInterface(self, vpn_data: dict, proposed=False, length=0):
        if proposed == True:
            #print("#"*length)
            print(f"{bcolours.BOLD}Interfaces to Delete from Switch{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['params']['HubName_str']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"\n{bcolours.OKGREEN}Interface Deleted{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['result']['HubName_str']}{bcolours.ENDC}")
        else:
            print(vpn_data)

####LIST VIRTUAL SWITCHES#####
    def AddGroup(self, vpn_data: dict, group_type=None, proposed=False):
        if group_type == None:
           group_type = 'VPN'
        if proposed == True:
            print(f"{bcolours.BOLD}{group_type} Group to be Added/Updated{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB: {vpn_data['params']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Group: {vpn_data['params']['Name_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}RealName: {vpn_data['params']['Realname_utf']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Policy Enabled: {vpn_data['params']['UsePolicy_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}VPN Access Enabled: {vpn_data['params']['policy:Access_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}No DHCP Client Server: {vpn_data['params']['policy:DHCPNoServer_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Force DHCP: {vpn_data['params']['policy:DHCPNoServer_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}No BUM: {vpn_data['params']['policy:ArpDhcpOnly_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Private Client Lan: {vpn_data['params']['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Connections: {vpn_data['params']['policy:MaxConnection_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Client Timeout: {vpn_data['params']['policy:TimeOut_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Upload: {vpn_data['params']['policy:MaxUpload_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Download: {vpn_data['params']['policy:MaxDownload_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Multiple Login Connections: {vpn_data['params']['policy:MultiLogins_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}QoS: {vpn_data['params']['policy:NoQoS_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Filter All IPv6: {vpn_data['params']['policy:FilterIPv6_bool']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"{bcolours.BOLD}{group_type} Group Added/Updated{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB: {vpn_data['result']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Group: {vpn_data['result']['Name_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}RealName: {vpn_data['result']['Realname_utf']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Policy Enabled: {vpn_data['result']['UsePolicy_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}VPN Access Enabled: {vpn_data['result']['policy:Access_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}No DHCP Client Server: {vpn_data['result']['policy:DHCPNoServer_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Force DHCP: {vpn_data['result']['policy:DHCPNoServer_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}No BUM: {vpn_data['result']['policy:ArpDhcpOnly_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Private Client Lan: {vpn_data['result']['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Connections: {vpn_data['result']['policy:MaxConnection_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Client Timeout: {vpn_data['result']['policy:TimeOut_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Upload: {vpn_data['result']['policy:MaxUpload_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Max Download: {vpn_data['result']['policy:MaxDownload_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Multiple Login Connections: {vpn_data['result']['policy:MultiLogins_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}QoS: {vpn_data['result']['policy:NoQoS_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Filter All IPv6: {vpn_data['result']['policy:FilterIPv6_bool']}{bcolours.ENDC}")

    def DeleteGroup(self, vpn_data: dict, proposed=False):
        if proposed == True:
            print(f"{bcolours.BOLD}Groups to be Deleted{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB: {vpn_data['params']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Group: {vpn_data['params']['Name_str']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"{bcolours.BOLD}Groups Deleted{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB: {vpn_data['result']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Group: {vpn_data['result']['Name_str']}{bcolours.ENDC}")

    def AddBridge(self, vpn_data: dict, proposed=False):
        if proposed == True:
            print(f"{bcolours.BOLD}Bridges to be Added{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Bridge: {vpn_data['params']['DeviceName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Hub: {vpn_data['params']['HubNameLB_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Online: {vpn_data['params']['Online_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Active: {vpn_data['params']['Active_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}TapMode: {vpn_data['params']['TapMode_bool']}{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"{bcolours.BOLD}Bridges Added{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Bridge: {vpn_data['params']['DeviceName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Hub: {vpn_data['params']['HubNameLB_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Online: {vpn_data['params']['Online_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Active: {vpn_data['params']['Active_bool']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}TapMode: {vpn_data['params']['TapMode_bool']}{bcolours.ENDC}")


    def AclDiff(self, yaml, live_list, proposed=False):
        vpn_existing = []
        yaml_config = []
        acl = {'new': [], 'updated': [], 'redundant': []}
        try:

            for payload_acl, enum in itertools.zip_longest(
                yaml['params']['AccessList'],
                live_list['result']['AccessList'],
                fillvalue={}
                ):
                vpn_existing.append(enum['Note_utf'])
                yaml_config.append(payload_acl['Note_utf'])
                if payload_acl['Note_utf'] == enum['Note_utf']:
                    diff = DeepDiff(payload_acl, enum)
                    if 'values_changed' in diff.keys():
                        acl['updated'].append(payload_acl)
                        if proposed == True:
                            print(f"{bcolours.BOLD}ACL Diff{bcolours.ENDC}")
                            for key, values in diff['values_changed'].items():
                                print(f"{bcolours.OKGREEN}{payload_acl['Note_utf']}{bcolours.ENDC}")
                                print(f"{bcolours.OKGREEN}{key[6:-2]}{bcolours.ENDC}")
                                print(f"{bcolours.OKGREEN}+{values['old_value']}{bcolours.ENDC}")
                                print(f"{bcolours.FAIL}-{values['new_value']}{bcolours.ENDC}")


        except KeyError as err:
            pass

        for acl_config in yaml['params']['AccessList']:
            if acl_config['Note_utf'] not in vpn_existing:
                acl['new'].append(acl_config)

        for live_acl in live_list['result']['AccessList']:
            if live_acl['Note_utf'] not in yaml_config:
                acl['redundant'].append(live_acl)

        return acl


    def UpdateAcl(self, vpn_data, new_acls, proposed=False):

        if proposed == True:
            if new_acls['new'] != []:
                print(f"{bcolours.BOLD}\nNew ACLs to be Added{bcolours.ENDC}")
                for acl in new_acls['new']:
                    print(f"{bcolours.OKGREEN}\nRule Number/Priority: {acl['Id_u32']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Name:: {acl['Note_utf']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Active: {acl['Active_bool']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Discarding: {acl['Discard_bool']}{bcolours.ENDC}")
                    if acl['SrcIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Source IP: {acl['SrcIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Src Mask: {acl['SrcSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Source IP: any{bcolours.ENDC}")
                    if acl['SrcPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Src Port: {acl['SrcPortStart_u32']}-{acl['SrcPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src Port: any{bcolours.ENDC}")
                    if acl['SrcUsername_str'] != '':
                        print(f"{bcolours.OKGREEN}Src User/Group: {acl['SrcUsername_str']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src User/Group: any{bcolours.ENDC}")
                    if acl['DestIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Dst IP: {acl['DestIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Dst Mask {acl['DestSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst IP: any{bcolours.ENDC}")
                    if acl['DestUsername_str'] != "":
                        print(f"{bcolours.OKGREEN}Dst User/Group: {acl['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst User/Group: any{bcolours.ENDC}")
                    if acl['DestPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Dst Port: {acl['DestPortStart_u32']}-{acl['DestPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst Port: any{bcolours.ENDC}")

            if new_acls['updated'] != []:
                print(f"{bcolours.BOLD}\nACL's to Update{bcolours.ENDC}")
                for acl in new_acls['updated']:
                    print(f"{bcolours.OKGREEN}\nRule Number/Priority: {acl['Id_u32']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Name:: {acl['Note_utf']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Active: {acl['Active_bool']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Discarding: {acl['Discard_bool']}{bcolours.ENDC}")
                    if acl['SrcIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Source IP: {acl['SrcIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Src Mask: {acl['SrcSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Source IP: any{bcolours.ENDC}")
                    if acl['SrcPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Src Port: {acl['SrcPortStart_u32']}-{acl['SrcPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src Port: any{bcolours.ENDC}")
                    if acl['SrcUsername_str'] != '':
                        print(f"{bcolours.OKGREEN}Src User/Group: {acl['SrcUsername_str']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src User/Group: any{bcolours.ENDC}")
                    if acl['DestIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Dst IP: {acl['DestIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Dst Mask {acl['DestSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst IP: any{bcolours.ENDC}")
                    if acl['DestUsername_str'] != "":
                        print(f"{bcolours.OKGREEN}Dst User/Group: {acl['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst User/Group: any{bcolours.ENDC}")
                    if acl['DestPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Dst Port: {acl['DestPortStart_u32']}-{acl['DestPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst Port: any{bcolours.ENDC}")

            if new_acls['redundant'] != []:
                print(f"{bcolours.BOLD}\nACL's to Delete{bcolours.ENDC}")
                for acl in new_acls['redundant']:
                    print(f"{bcolours.OKGREEN}\nRule Number/Priority: {acl['Id_u32']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Name:: {acl['Note_utf']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Active: {acl['Active_bool']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Discarding: {acl['Discard_bool']}{bcolours.ENDC}")
                    if acl['SrcIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Source IP: {acl['SrcIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Src Mask: {acl['SrcSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Source IP: any{bcolours.ENDC}")
                    if acl['SrcPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Src Port: {acl['SrcPortStart_u32']}-{acl['SrcPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src Port: any{bcolours.ENDC}")
                    if acl['SrcUsername_str'] != '':
                        print(f"{bcolours.OKGREEN}Src User/Group: {acl['SrcUsername_str']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Src User/Group: any{bcolours.ENDC}")
                    if acl['DestIpAddress_ip'] != "0.0.0.0":
                        print(f"{bcolours.OKGREEN}Dst IP: {acl['DestIpAddress_ip']}{bcolours.ENDC}")
                        print(f"{bcolours.OKGREEN}Dst Mask {acl['DestSubnetMask_ip']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst IP: any{bcolours.ENDC}")
                    if acl['DestUsername_str'] != "":
                        print(f"{bcolours.OKGREEN}Dst User/Group: {acl['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst User/Group: any{bcolours.ENDC}")
                    if acl['DestPortStart_u32'] != 0:
                        print(f"{bcolours.OKGREEN}Dst Port: {acl['DestPortStart_u32']}-{acl['DestPortEnd_u32']}{bcolours.ENDC}")
                    else:
                        print(f"{bcolours.OKGREEN}Dst Port: any{bcolours.ENDC}")



        elif 'result' in vpn_data.keys():
            print(f"{bcolours.BOLD}ACLs Added/Updated{bcolours.ENDC}")
            for acl in vpn_data['result']['AccessList']:
                print(f"{bcolours.OKGREEN}\nRule Number/Priority: {acl['Id_u32']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Name:: {acl['Note_utf']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Active: {acl['Active_bool']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Discarding: {acl['Discard_bool']}{bcolours.ENDC}")
                if acl['SrcIpAddress_ip'] != "0.0.0.0":
                    print(f"{bcolours.OKGREEN}Source IP: {acl['SrcIpAddress_ip']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Src Mask: {acl['SrcSubnetMask_ip']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Source IP: any{bcolours.ENDC}")
                if acl['SrcPortStart_u32'] != 0:
                    print(f"{bcolours.OKGREEN}Src Port: {acl['SrcPortStart_u32']}-{acl['SrcPortEnd_u32']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Src Port: any{bcolours.ENDC}")
                if acl['SrcUsername_str'] != '':
                    print(f"{bcolours.OKGREEN}Src User/Group: {acl['SrcUsername_str']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Src User/Group: any{bcolours.ENDC}")
                if acl['DestIpAddress_ip'] != "0.0.0.0":
                    print(f"{bcolours.OKGREEN}Dst IP: {acl['DestIpAddress_ip']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}Dst Mask {acl['DestSubnetMask_ip']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Dst IP: any{bcolours.ENDC}")
                if acl['DestUsername_str'] != "":
                    print(f"{bcolours.OKGREEN}Dst User/Group: {acl['policy:PrivacyFilter_bool']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Dst User/Group: any{bcolours.ENDC}")
                if acl['DestPortStart_u32'] != 0:
                    print(f"{bcolours.OKGREEN}Dst Port: {acl['DestPortStart_u32']}-{acl['DestPortEnd_u32']}{bcolours.ENDC}")
                else:
                    print(f"{bcolours.OKGREEN}Dst Port: any{bcolours.ENDC}")

        elif 'error' in vpn_data.keys():
            print(vpn_data)


    def Hubs(self, vpn_data: dict, interface_data=None, bridge_data=None):
        ret = None
        current_hubs = {'vpn_hubs' : [], 'yaml_hubs': []}
        missing_hubs = {'missing_hubs': [], 'redundant_hubs': []}
        try:
            for hubs in vpn_data['result']['HubList']:
                if isinstance(hubs, dict):
                    current_hubs['vpn_hubs'].append(hubs['HubName_str'])

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        try:
############OBTAINING DATA FROM YAML CONFIG##############
            for hub in self.yaml_data[self.vpn_node]['hubs']:
                current_hubs['yaml_hubs'].append(hub)
                if hub not in current_hubs['vpn_hubs']:
                    missing_hubs['missing_hubs'].append(hub)

            for hub in current_hubs['vpn_hubs']:
                if hub not in current_hubs['yaml_hubs']:
                    missing_hubs['redundant_hubs'].append(hub)
################CHECK IF YAML ROUTE EXISTS IN PROCESSED VPN DATA################
        except KeyError:
            print(f"No config found for {self.vpn_node}, Exiting")
            sys.exit(1)

########STDOUT ADD HUBS#########################################
        if self.args.command == "add_hub":
            if missing_hubs['missing_hubs'] != []:
                ret = missing_hubs['missing_hubs']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"\n{bcolours.BOLD}VPN Missing Hubs:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for hub in missing_hubs['missing_hubs']:
                    print(f"{bcolours.OKGREEN}Hub Name: {hub}{bcolours.ENDC}")
                    #print("#"*len(stdout))

########STDOUT REDUNDANT VPN HUBs FOR DELETION#########################
        elif self.args.command == "del_hub":
            if missing_hubs['redundant_hubs'] != []:
                ret = missing_hubs['redundant_hubs']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"{bcolours.BOLD}VPN Redundant Hubs:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for hub in missing_hubs['redundant_hubs']:
                    print(f"{bcolours.OKGREEN}Hub: {hub}{bcolours.ENDC}")
                    #print("#"*len(stdout))

        return ret

    def RadiusAuth(self, radius_secret: str):
        ret = None
############OBTAINING DATA FROM YAML CONFIG##############
        try:
            ret = self.yaml_data['GlobalOptions']['Radius'][self.args.hub]
            ret.update({"secret": radius_secret})


        except KeyError:
            print(f"No config found for {self.vpn_node}, Exiting")
            sys.exit(1)

        return ret

    def RadiusDiff(self, payload, live_config, proposed=False):
        ret = None
        diff = DeepDiff(payload['params'], live_config['result'])
        if 'values_changed' in diff.keys():
            ret = True
            print(f"{bcolours.BOLD}{self.args.hub} Auth Diff Changes{bcolours.ENDC}")
            for key, values in diff['values_changed'].items():
                print(f"{bcolours.OKGREEN}{key[6:-2]}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}+{values['old_value']}{bcolours.ENDC}")
                print(f"{bcolours.FAIL}-{values['new_value']}{bcolours.ENDC}")

        elif diff == {}:
            print(f"{bcolours.BOLD}{self.args.hub} State Correct. Exiting{bcolours.ENDC}")
            sys.exit(1)

        return ret

    def RadiusUpdate(self, vpn_data: dict, proposed=False):
        if proposed == True:
            print(f"{bcolours.BOLD}Radius Auth Config to be updated{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['params']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Server:{vpn_data['params']['RadiusServerName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Port:{vpn_data['params']['RadiusPort_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Retry Interval:{vpn_data['params']['RadiusRetryInterval_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Secret: **redacted**{bcolours.ENDC}")
        elif 'result' in vpn_data.keys():
            print(f"{bcolours.BOLD}Updated Radius Config{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}HUB:{vpn_data['result']['HubName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Server:{vpn_data['result']['RadiusServerName_str']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Port:{vpn_data['result']['RadiusPort_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Retry Interval:{vpn_data['result']['RadiusRetryInterval_u32']}{bcolours.ENDC}")
            print(f"{bcolours.OKGREEN}Secret: **redacted**{bcolours.ENDC}")
        else:
            print(vpn_data)

###COMPARES DATASETS FOR MISSING OR REDUNDANT INTERFACES##########
    def Interfaces(self, interfaces, hubs):
        ret = None
        hub_list = []
        network_list = []
        missing_interfaces = {'vpn_missing': [], 'vpn_redundant': {} }
        preprocess = {}
        processed_interfaces = {}
        unique_flow = []
        try:
            for hubs in hubs['result']['HubList']:
                if isinstance(hubs, dict):
                    hub_list.append(hubs['HubName_str'])


            for interface in interfaces['result']['L3IFList']:
                if isinstance(interface, dict):
    ################PARSING VPN DATA INTO DATASET TO COMPARE AGAINST################
                    network_list.append(interface['IpAddress_ip'])
                    preprocess.update( { interface['HubName_str'] : {
                                     'hub' : interface['HubName_str'],
                                     'network': interface['IpAddress_ip'],
                                     'mask': interface['SubnetMask_ip']
                                    }
                                  }
                                )

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)


        try:
############OBTAINING DATA FROM YAML CONFIG##############
            for interface_name, data in self.yaml_data[self.vpn_node][self.args.l3_switch.lower()]['interfaces'].items():
                processed_interfaces.update({ data['hub'] : data['ip'] })
################CHECK IF YAML INTERFACES EXISTS IN PROCESSED VPN DATA################
                if (data['hub'] in hub_list) and (data['ip'] not in network_list):
                    if data['hub'] not in unique_flow:
                        unique_flow.append(data['hub'])
                        missing_interfaces['vpn_missing'].append(data)
                elif (data['hub'] in hub_list) and (data['ip'] in network_list):
                    pass
                else:
                    print(f"HUB: {data['hub']} Not Defined, Skipping: {data['ip']}")

        except KeyError as err:
            print(f"Key Error: {err}, Exiting")
            sys.exit(1)

        try:
            for hub in hub_list:
################CHECK IF YAML INTERFACES EXISTS IN PROCESSED VPN DATA################
                if hub not in processed_interfaces.keys() and hub in preprocess.keys():
                    missing_interfaces['vpn_redundant'].update( {hub : preprocess[hub]['network'] })

        except KeyError:
            pass

########STDOUT MISSING ROUTES FROM YAML#########################################
        if self.args.command == "add_interfaces":
            if missing_interfaces['vpn_missing'] != []:
                ret = missing_interfaces['vpn_missing']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"\n{bcolours.BOLD}Missing Interfaces:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for iface in missing_interfaces['vpn_missing']:
                    print(f"{bcolours.OKGREEN}HUB: {iface['hub']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}IP: {iface['ip']}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}MASK: {iface['mask']}{bcolours.ENDC}")
                    #print("#"*len(stdout))

########STDOUT REDUNDANT VPN ROUTES STAGED FOR DELETION#########################
        elif self.args.command == "del_interfaces":
            if missing_interfaces['vpn_redundant'] != {}:
                ret = missing_interfaces['vpn_redundant']
                stdout = (f"\nVPN Node: {bcolours.OKGREEN}{self.vpn_node}{bcolours.ENDC}")
                print(stdout)
                print(f"{bcolours.BOLD}VPN Redundant Interfaces:{bcolours.ENDC}")
                #print("#"*len(stdout))
                for hub, ip in missing_interfaces['vpn_redundant'].items():
                    print(f"{bcolours.OKGREEN}HUB:{hub}{bcolours.ENDC}")
                    print(f"{bcolours.OKGREEN}IP:{ip}{bcolours.ENDC}")
                    #print("#"*len(stdout))

        return ret

    def GroupParse(self, data: dict, short=False):
        if short == False:
            for values in data:
                print(f"{bcolours.OKGREEN}HUB: {values['hub']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Group: {values['GroupName']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}RealName: {values['realname']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Policy Enabled: {values['PolicyActivated']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}VPN Access Enabled: {values['AllowVPNConnections']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}No DHCP Client Server: {values['NoDHCPServerClient']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Force DHCP: {values['ForceDhcp']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}No BUM: {values['DropBUM']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Private Client Lan: {values['PrivateLan']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Client Timeout: {values['ClientTimeOut']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Max Upload: {values['MaxUpload']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Max Download: {values['MaxDownload']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Multiple Login Connections: {values['MultiLoginNumber']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}QoS: {values['QoS']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Filter All IPv6: {values['FilterIPv6']}{bcolours.ENDC}")
        else:
            for values in data:
                print(f"{bcolours.OKGREEN}HUB: {values['hub']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}Group: {values['GroupName']}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}RealName: {values['realname']}{bcolours.ENDC}")


###COMPARES DATASETS FOR MISSING OR REDUNDANT INTERFACES##########
    def Groups(self, groups, hub):
        ret = None
        group_changes = {'vpn_missing': [], 'vpn_redundant': [], 'existing': [] }
        group_list = []
        processed_group = []
        try:
            for vpn_group in groups['result']['GroupList']:
                    group_list.append(vpn_group['Name_str'])

        except TypeError as err:
            print(f"{bcolours.BOLD}TypeError: No Data. Skipping{bcolours.ENDC}")
            sys.exit(1)

        try:
############OBTAINING DATA FROM YAML CONFIG##############
            for config_group, data in self.yaml_data['GlobalOptions'][hub]['groups'].items():
                processed_group.append(data['GroupName'])
################CHECK IF YAML INTERFACES EXISTS IN PROCESSED VPN DATA################
                if data['GroupName'] not in group_list:
                    group_changes['vpn_missing'].append(data)
                elif data['GroupName'] in group_list:
                    group_changes['existing'].append(data)

        except KeyError as err:
            print(f"Key Error: {err}, Exiting")
            sys.exit(1)

        try:
            for group in group_list:
################CHECK IF YAML INTERFACES EXISTS IN PROCESSED VPN DATA################
                if group not in processed_group:
                    group_changes['vpn_redundant'].append( { 'GroupName': group, 'hub': hub } )

        except KeyError:
            print(f"Key Error: {err}, Exiting")
            sys.exit(1)

        if group_changes['vpn_redundant'] != []:
            ret = group_changes
        elif group_changes['vpn_missing'] != []:
            ret = group_changes
        elif group_changes['existing'] != []:
            ret = group_changes

        return ret


    def vpn_login_check(self, vpn_fault_check):
        se0_cluster = ['se0-dc1', 'se0-dc2', 'se0-dc3']
        ret = None
        user_exist = False
        se1_cluster = ['se1-dc1', 'se1-dc2', 'se1-dc3']
        ldap_user = input(f"\n{bcolours.BOLD}Enter LDAP/VPN Login Username to verify VPN Login: {bcolours.ENDC}")
        for vpn_node, session_data in vpn_fault_check.items():
            for session in session_data['result']['SessionList']:
                try:
                    sid, uname, type, number = session['Name_str'].split('-')
                    uname = uname.lower()

                    if ldap_user == uname:
                        user_exist = True
                        print(f"{bcolours.BOLD}User: {ldap_user}{bcolours.ENDC}")
                        print(f"{bcolours.BOLD}VPN Connected: {vpn_node}{bcolours.ENDC}")
                        if vpn_node in se0_cluster and self.args.vpn[0] in se0_cluster:
                            print(f"\n{bcolours.BOLD}Unable to manage SE0 VPN Cluster client is connected.{bcolours.ENDC}")
                            print(f"{bcolours.BOLD}Change VPN Server Cluster to configure.{bcolours.ENDC}")
                            exit(1)
                        elif vpn_node in se1_cluster and self.args.vpn[0] in se1_cluster:
                            print(f"\n{bcolours.BOLD}Unable to manage SE1 VPN Cluster client is connected{bcolours.ENDC}")
                            print(f"{bcolours.BOLD}Change VPN Server Cluster to configure.{bcolours.ENDC}")
                            exit(1)
                        else:
                            print(f"{bcolours.OKGREEN}Safe to Manage VPN Cluster: {self.args.vpn[0].split('-')[0]}{bcolours.ENDC}")
                            print(f"{bcolours.OKGREEN}Proceeding with function: {self.args.command}\n{bcolours.ENDC}")
                            ret = True

                except ValueError:
                    pass

        if user_exist == False:
            print(f"{bcolours.BOLD}No VPN session with *{ldap_user}* found. Exiting{bcolours.ENDC}")
            sys.exit(1)

        return ret

    def UserGathering(self, users):
        user_list = []
        user_group = {}
        ret = None
        try:
            for vpn_node, user_data in users.items():
                for user in user_data['UserList']:
                    if isinstance(user['Name_str'], str):
                        if user['Name_str'] not in user_list:
                            user_list.append(user['Name_str'])
                        if user['Name_str'] not in user_group.keys():
                            try:
                                user_group.update({ user['Name_str'] : user['GroupName_str'] })
                            except KeyError:
                                user_group.update({ user['Name_str'] : "none" })
        except TypeError:
            pass
            #print(user)
                #if user['Realname_utf'] not in user_list:
                #    user_list.append(user['Realname_utf'])
#{'UserList': [{'AuthType_u32': 4, 'DenyAccess_bool': False, 'Ex.Recv.BroadcastBytes_u64': 38126090, 'Ex.Recv.BroadcastCount_u64': 275655, 'Ex.Recv.UnicastBytes_u64': 25445772936, 'Ex.Recv.UnicastCount_u64': 23155290, 'Ex.Send.BroadcastBytes_u64': 1328718, 'Ex.Send.BroadcastCount_u64': 6061, 'Ex.Send.UnicastBytes_u64': 4257702446, 'Ex.Send.UnicastCount_u64': 10909328, 'Expires_dt': '1970-01-01T09:00:00.000Z', 'GroupName_str': 'Office', 'IsExpiresFilled_bool': True, 'IsTrafficFilled_bool': True, #'LastLoginTime_dt': '2021-11-08T01:42:38.360Z', 'Name_str': 'abbottjo', 'Note_utf': '', 'NumLogin_u32': 26, 'Realname_utf': 'John Abbott'}

        return user_list, user_group

    def AccessLists(self, payload):
        ret = None
        acls = {'vpn_missing': [], 'vpn_redundant': [], 'existing': [] }
        acl_list = []
        processed_acl = []


        try:
############OBTAINING DATA FROM YAML CONFIG##############
            for acl in payload['result']['AccessList']:
                acl_list.append(acl["Note_utf"])

            yaml_data = self.yaml_data['AccessLists'][self.args.vpn[0].split('-')[1]][self.args.hub]
            for acl in yaml_data:
                processed_acl.append(acl['name'])
                if acl['name'] not in acl_list:
                    acls['vpn_missing'].append(acl['name'])
                elif acl['name'] in acl_list:
                    acls['existing'].append(acl)

            for acl in acl_list:
                if acl not in processed_acl:
                    acls['vpn_redundant'].append(acl)

        except KeyError as err:
            print(f"No Matching ACL config found. Exiting")
            sys.exit(1)

        if acls['vpn_missing'] != [] and acls['vpn_redundant'] != []:
            print((f"\n{bcolours.BOLD}ACL Changes for {self.vpn_node}{bcolours.ENDC}"))
            print("New Access Lists")
            for values in acls['vpn_missing']:
                print(f"{bcolours.OKGREEN}ACL: {values}{bcolours.ENDC}")
            print("\nRedundant Access Lists")
            for values in acls['vpn_redundant']:
                print(f"{bcolours.OKGREEN}ACL: {values}{bcolours.ENDC}")


        return yaml_data

    def ProposedChanges(self, payload, custom=None, router=False):
        stdout = (f"\n{bcolours.BOLD}Proposed Changes for {self.vpn_node}{bcolours.ENDC}")
        length = len(stdout)
        print("-"*length)
        print(stdout)
        n = 1
        iteration = len(payload)
        if self.args.command == "update_acls":
            acl_data = self.AclDiff(payload, custom, proposed=True)
            self.UpdateAcl(payload, acl_data, proposed=True)
        elif self.args.command == "update_radius":
            self.RadiusUpdate(payload, proposed=True)
        else:

            for changes in payload:
                if n == 1 and router == True:
                        n += 1
                        self.RouterStop(changes, proposed=True, length=length)
                elif n == iteration and router == True:
                        self.RouterStart(changes, proposed=True, length=length)
                else:
                    n += 1
                    if self.args.command == "add_routes":
                        self.AddedRoute(changes, proposed=True, length=length)
                    elif self.args.command == "del_routes":
                        self.DeletedRoute(changes, proposed=True, length=length)
                    elif self.args.command == "add_hub":
                        self.AddHub(changes, proposed=True, length=length)
                    elif self.args.command == "del_hub":
                        self.DeleteHub(changes, proposed=True, length=length)
                    elif self.args.command == "add_interfaces":
                        self.AddInterface(changes, proposed=True, length=length)
                    elif self.args.command == "del_interfaces":
                        self.DeleteInterface(changes, proposed=True, length=length)
                    elif self.args.command == "add_groups" or self.args.command == "update_groups":
                        if custom == 'New' or custom == "Existing":
                            self.AddGroup(changes, proposed=True, group_type=custom)
                        elif custom == "Redundant":
                            self.DeleteGroup(changes, proposed=True)
                    elif self.args.command == "add_bridge":
                        self.AddBridge(changes, proposed=True)


    def ComplexChange(self, payload, custom=None, router=False):
        n = 1
        iteration = len(payload)
        if self.args.command == "update_acls":
            acl_data = self.AclDiff(payload, custom)
            if acl_data['new'] != [] or acl_data['updated'] != [] or acl_data['redundant'] != []:
                changes = self.vpn_request.global_admin(self.args.vpn[0], array_payload=payload)
                self.UpdateAcl(changes, custom)
            else:
                print("No Changes Needed, Exiting")
                sys.exit(1)

        elif self.args.command == "update_radius":
            changes = self.vpn_request.global_admin(self.args.vpn[0], array_payload=payload)
            self.RadiusUpdate(changes)

        else:

            for posts in payload:
                changes = self.vpn_request.global_admin(self.args.vpn[0], array_payload=posts)
                if 'result' in changes.keys():
                    if n == 1 and router == True:
                         n += 1
                         self.RouterStop(changes)
                    elif n == iteration and router == True:
                         self.RouterStart(changes)
                    else:
                        n += 1
                        if self.args.command == "add_routes":
                            self.AddedRoute(changes)
                        if self.args.command == "del_routes":
                            self.DeletedRoute(changes)
                        elif self.args.command == "add_hub":
                            self.AddHub(changes)
                        elif self.args.command == "del_hub":
                            self.DeleteHub(changes)
                        elif self.args.command == "add_interfaces":
                            self.AddInterface(changes)
                        elif self.args.command == "del_interfaces":
                            self.DeleteInterface(changes)
                        elif self.args.command == "add_groups" or self.args.command == "update_groups":
                            if custom == 'New' or custom == "Existing":
                                self.AddGroup(changes, group_type=custom)
                            elif custom == "Redundant":
                                self.DeleteGroup(changes)
                        elif self.args.command == "del_groups":
                            self.DeleteGroup(changes)
                        elif self.args.command == "add_bridges":
                            self.AddBridge(changes)
                elif 'error' in changes.keys():
                    print(changes)
