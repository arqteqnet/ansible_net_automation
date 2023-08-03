#!/usr/bin/env python3
from rpc_calls import rpc_call
from data_sanitisation import sanitise_data
from parsers import data_parser
from vpn_nodes import vpn_data
from utils import program_flow
from outputcolours import bcolours
from deepdiff import DeepDiff
import sys
import json
import yaml
import requests


################################################################################
##REQUEST CLASS TO INSTANTIATE FOR MULTIPLE REQUEST USAGE#######################
class api_request():

    def __init__(self, vpn_data, cli_args, secret):
########ARGS PARSER#############
        self.cli_args = cli_args
########VAULT SECRET############
        self.secret = secret
########VPN YAML DATA###########
        self.vpn_data = vpn_data


################################################################################
####METHOD TO RETRIEVE PAYLOAD DYNAMICALLY BASED ON ARGS INPUT##################
    def payload(self, command, custom=None):
        payload_function = getattr(rpc_call(self.cli_args), command)
        post_data = payload_function()

        return post_data

################################################################################
####REQUEST FOR GLOBAL ADMIN REQUEST############################################
####OPTION VARS TO ALLOW FOR CUSTOM PAYLOADS FOR COMPLEX REQUESTS###############
    def global_admin(self, node, command=None, array_payload=None, custom=None):

################################################################################
########DFAULT TO ARGS PARSER INPUT IF NONE SUPPLIED############################
        if array_payload == None and command == None and custom == None:
            post_payload = self.payload(self.cli_args.command)
########USE CUSTOM COMMAND INPUT################################################
        elif array_payload == None and command != None:
            post_payload = self.payload(command)
############UPDATING TO GLOBAL VPN FOR PERFORMING VPN USER LOGIN CHECKS#########
            if command == "ls_sessions" and custom != None:
                post_payload['params']['HubName_str'] = custom
########USE PREASSEMBLED PAYLOAD################################################
        elif array_payload != None:
            post_payload = array_payload

########VPN NODE FROM VPN YAML FILE#############################################
        vpn_node = self.vpn_data[node]['address']
        try:
            payload = json.dumps(post_payload)
            r = requests.post(
                url=f"https://{vpn_node}:{self.cli_args.port}/api",
                data=payload,
                headers={
                    'Content-type': 'application/json',
                    'X-VPNADMIN-PASSWORD' : self.secret
                    },
                verify=False,
                timeout=3,
            )
        except requests.exceptions.Timeout:
            print(f"\nConnection timeout for {vpn_node}. Skipping")
            r = None

        except Exception as err:
            print(f"ERR: {err}: Failed to connect to {vpn_node}.")
            r = None
        if r is not None:
            if len(r.text) == 0:
                print(f"ERR: returned no data. This is usually an issue with username or password (not API key)")
                sys.exit(1)
            elif r.status_code != 200:
                print(f"Connection Error, Reason: {r.reason}")
                sys.exit(1)
            results = json.loads(r.text.encode('utf-8'))
        else:
            results = None

        return results

################################################################################
####HUB MODE REQUESTS###########################################################

    def hub_admin(self, node, command=None, array_payload=None):

        if array_payload == None and command == None:
            post_payload = self.payload(self.cli_args.command)
        elif array_payload == None and command != None:
            post_payload = self.payload(command)
        elif array_payload != None:
            post_payload = array_payload

        vpn_node = self.vpn_data[node]['address']
        try:
            payload = json.dumps(post_payload)
            r = requests.post(
                url=f"https://{vpn_node}:{self.cli_args.port}/api",
                data=payload,
                headers={
                    'Content-type': 'application/json',
                    'X-VPNADMIN-HUBNAME' : self.cli_args.hub,
                    'X-VPNADMIN-PASSWORD' : self.secret
                    },
                verify=False,
                timeout=3,
            )
        except requests.exceptions.Timeout:
            print(f"\nConnection timeout for {vpn_node}. Skipping")
            r = None

        except Exception as err:
            print(f"ERR: {err}: Failed to connect to {vpn_node}.")
            r = None
        if r is not None:
            if len(r.text) == 0:
                print(f"ERR: returned no data. This is usually an issue with username or password (not API key)")
                sys.exit(1)
            elif r.status_code != 200:
                print(f"Connection Error, Reason: {r.reason}")
                sys.exit(1)
            results = json.loads(r.text.encode('utf-8'))
        else:
            results = None

        return results


class request_mode():

    def __init__(self, args, yaml_config, secret, vpn_admin, vpn_credentials):
########ARGS PARSER#############
        self.args = args
########VAULT SECRET############
        self.secret = secret
########VPN YAML DATA###########
        self.yaml_config = yaml_config
########ADMIN MODE#############
        self.vpn_admin = vpn_admin
########REQUEST CLASS INSTATIATE####
        self.vpn_request = api_request(vpn_data, args, secret)
########DATAPARSER INSTATIATE#######
        self.data_parse = data_parser(args, yaml_config, vpn_data, secret, self.vpn_request)
        self.payload_function = rpc_call(args)
        self.program_logic = program_flow(args)
        self.vpn_credentials = vpn_credentials

    def vpn_login_check(self):
                vpn_fault_check = {}
                print(f"\n{bcolours.BOLD}VPN Login Failsafe check. This may take a few moments..{bcolours.ENDC}")
                for node in ['se0-dc1', 'se1-dc1', 'se0-dc2', 'se1-dc2', 'se0-dc3', 'se1-dc3']:
                    sevpn_data = self.vpn_request.global_admin(node, command="ls_sessions", custom="IT-VPN")
                    if sevpn_data != None:
                        vpn_fault_check.update({ node: sevpn_data })
                check = self.data_parse.vpn_login_check(vpn_fault_check)

    def single_vpn_check(self):
        if len(self.args.vpn) > 1:
                print("Only One VPN can be configured at a time. Exiting")
                sys.exit(1)

    def multiple_vpn_check(self):
        if len(self.args.vpn) <= 1:
                print("More than One VPN needs selecting for Diff to occur. Exiting")
                sys.exit(1)


    def simple_request(self):
        print(self.args.command)
        if self.vpn_admin is None:
            for node in self.args.vpn:
                request_data = self.vpn_request.hub_admin(node)
                if self.args.command == "add_user" or self.args.command == "del_user":
                    sevpn_data = sanitise_data(self.args, request_data, vpn_data[node]['address'])
                elif 'error' not in request_data.keys():
                    sevpn_data = sanitise_data(self.args, request_data, vpn_data[node]['address'])
                else:
                    print(request_data)
                    sys.exit(1)
        else:
            for node in self.args.vpn:
                request_data = self.vpn_request.global_admin(node)
                if self.args.command == "add_user" or self.args.command == "del_user":
                    sevpn_data = sanitise_data(self.args, request_data, vpn_data[node]['address'])
                elif 'error' not in request_data.keys():
                    sevpn_data = sanitise_data(self.args, request_data, vpn_data[node]['address'])
                else:
                    print(request_data)
                    sys.exit(1)

    def add_routes(self):
        self.single_vpn_check()
        self.vpn_login_check()
        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_routes")
        return_compare = self.data_parse.Routes(cache_1)
        payload = [ self.payload_function.stop_switch() ]


        if return_compare != None:
            for change in return_compare:
                payload.append (self.payload_function.add_route(change))
            payload.append(self.payload_function.start_switch() )


            self.data_parse.ProposedChanges(payload, router=True)
            self.program_logic.dry_run(payload)
            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload, router=True)
        else:
            print("No changes required. Exiting")
            sys.exit(1)




    def del_routes(self):
        self.single_vpn_check()
        self.vpn_login_check()
        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_routes")
        return_compare = self.data_parse.Routes(cache_1)

        payload = [ self.payload_function.stop_switch() ]


        if return_compare != None:
            for route, change in return_compare.items():
                payload.append (self.payload_function.del_route(change))
            payload.append(self.payload_function.start_switch())


            self.data_parse.ProposedChanges(payload, router=True)
            self.program_logic.dry_run(payload)
            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload, router=True)
        else:
            print("No changes required. Exiting")
            sys.exit(1)

    def add_hub(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload = []

        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_hub")
        return_compare = self.data_parse.Hubs(cache_1)

        if return_compare != None:

            for hub in return_compare:
                payload.append (self.payload_function.add_hub(hub))

            self.data_parse.ProposedChanges(payload)

            self.program_logic.dry_run(payload)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload)

        else:
            print("No changes required. Exiting")
            sys.exit(1)

    def del_hub(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload = []

        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_hub")
        cache_2 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_interfaces")
        hub_list = self.data_parse.Hubs(cache_1)

        if hub_list != None:
            data = self.data_parse.HubInUse(hub_list, cache_2)

            if data != []:
                for hub in data:
                    payload.append (self.payload_function.del_hub(hub))

                self.data_parse.ProposedChanges(payload)

                self.program_logic.dry_run(payload)

                self.program_logic.continue_flow()

                post_execute = self.data_parse.ComplexChange(payload)

        else:
            print("No changes required. Exiting")
            sys.exit(1)



    def add_interfaces(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload = []

        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_interfaces")
        cache_2 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_hub")
        return_compare = self.data_parse.Interfaces(cache_1, cache_2)

        payload = [ self.payload_function.stop_switch() ]

        if return_compare != None:

            for interface in return_compare:
                payload.append (self.payload_function.add_interface(interface))
            payload.append(self.payload_function.start_switch())

            self.data_parse.ProposedChanges(payload, router=True)

            self.program_logic.dry_run(payload)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload, router=True)

        else:
            print("No changes required. Exiting")
            sys.exit(1)


    def del_interfaces(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload = []
        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_interfaces")
        cache_2 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_hub")
        return_compare = self.data_parse.Interfaces(cache_1, cache_2)

        payload = [ self.payload_function.stop_switch() ]

        if return_compare != None:

            for hub, ip in return_compare.items():
                payload.append (self.payload_function.del_interface(hub))
            payload.append(self.payload_function.start_switch())

            self.data_parse.ProposedChanges(payload, router=True)

            self.program_logic.dry_run(payload)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload, router=True)

        else:
            print("No changes required. Exiting")
            sys.exit(1)


    def add_bridge(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload = []

        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_bridges")
        return_compare = self.data_parse.Bridges(cache_1)


        if return_compare['vpn_missing'] != []:
            for bridge in return_compare['vpn_missing']:
                payload.append (self.payload_function.add_bridge(bridge))

            self.data_parse.ProposedChanges(payload, router=False)

            self.program_logic.dry_run(payload)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload, router=False)

        else:
            print("No changes required. Exiting")
            sys.exit(1)


    def update_groups(self):
        self.single_vpn_check()
        self.vpn_login_check()
        payload1 = []
        payload2 = []
        payload3 = []

        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_groups")
        return_compare = self.data_parse.Groups(cache_1, self.args.hub)


        if return_compare != None:

            if 'vpn_missing' in return_compare.keys():
                for group in return_compare['vpn_missing']:
                    payload1.append (self.payload_function.create_group(group))


            if 'existing' in return_compare.keys():
                for group in return_compare['existing']:
                    payload2.append (self.payload_function.set_group(group))

            if 'vpn_redundant' in return_compare.keys():
                for group in return_compare['vpn_redundant']:
                    print(group)
                    payload3.append (self.payload_function.del_group(group))
                    print(payload3)

            self.data_parse.ProposedChanges(payload1, custom='New')

            self.data_parse.ProposedChanges(payload2, custom='Existing')

            self.data_parse.ProposedChanges(payload3, custom='Redundant')

            self.program_logic.dry_run(payload1+payload2+payload3)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload1, custom='New')
            post_execute = self.data_parse.ComplexChange(payload2, custom='Existing')
            post_execute = self.data_parse.ComplexChange(payload3, custom='Redundant')

        else:
            print("No changes required. Exiting")
            sys.exit(1)


    def update_acls(self):
        self.single_vpn_check()
        self.vpn_login_check()
        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="ls_acl")
        yaml_data = self.data_parse.AccessLists(cache_1)
        payload = self.payload_function.add_acl(yaml_data)

        self.data_parse.ProposedChanges(payload, cache_1)

        self.program_logic.dry_run(payload)

        self.program_logic.continue_flow()

        post_execute = self.data_parse.ComplexChange(payload, cache_1)

    def update_radius(self):
        self.single_vpn_check()
        self.vpn_login_check()
        radius_secret = self.vpn_credentials['data']['data']['radius_secret']
        cache_1 = self.vpn_request.global_admin(self.args.vpn[0], command="get_hub_radius")
        cache_1['result']['HubName_str'] = self.args.hub
        yaml_data = self.data_parse.RadiusAuth(radius_secret)
        payload = self.payload_function.set_hub_radius(yaml_data)
        return_compare = self.data_parse.RadiusDiff(payload, cache_1)

        if return_compare != None:
            self.data_parse.ProposedChanges(payload)

            self.program_logic.dry_run(payload)

            self.program_logic.continue_flow()

            post_execute = self.data_parse.ComplexChange(payload)

    def user_diff(self):
        user_data = {}
        mismatching_groups = {}
        self.multiple_vpn_check()
        for vpn in self.args.vpn:
            if vpn not in user_data.keys():
                users = self.vpn_request.hub_admin(vpn, command="ls_users")
                vpn_users, vpn_user_groups = self.data_parse.UserGathering(users)
                user_data.update({ vpn : vpn_users })
                mismatching_groups.update({ vpn : vpn_user_groups })

        diff = set(user_data[self.args.vpn[0]]) - set(user_data[self.args.vpn[1]])
        if diff != set():
            print(f"\nUsers Missing: {self.args.vpn[1]} VS {self.args.vpn[0]}")
            for user in diff:
               print(f"Name: {user}")



        diff1 = set(user_data[self.args.vpn[1]]) - set(user_data[self.args.vpn[0]])
        if diff1 != set():
            print(f"\nUsers Missing: {self.args.vpn[0]} VS {self.args.vpn[1]}")
            for user in diff1:
               print(f"Name: {user}")

        if diff == set() and diff1 == set():
            print("\nVPN Users Identical.")
            print("\nChecking VPN Users vs LDAP Users")
            for vpn_user in user_data[self.args.vpn[0]]:
                if vpn_user not in self.args.ldap_users.keys():
                    print(f"{bcolours.BOLD}{vpn_user}{bcolours.ENDC}: {bcolours.FAIL}NO LDAP MATCH{bcolours.ENDC}")


        group_diff = DeepDiff(mismatching_groups[self.args.vpn[0]], mismatching_groups[self.args.vpn[1]])
        if group_diff != {}:
            print(f"{bcolours.BOLD}\nUser Group Diff{bcolours.ENDC}")
            for key, values in group_diff['values_changed'].items():
                print(f"{bcolours.BOLD}User: {key[6:-2]}{bcolours.ENDC}")
                print(f"{bcolours.OKGREEN}+{values['old_value']}{bcolours.ENDC}")
                print(f"{bcolours.FAIL}-{values['new_value']}{bcolours.ENDC}")

        else:
            print("\nNo Group Mismatch found")
