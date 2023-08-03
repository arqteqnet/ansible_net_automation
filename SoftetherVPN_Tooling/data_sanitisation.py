#!/usr/bin/env python3
from outputcolours import bcolours
from parsers import vpndata_parsers, vpndata_output

################################################################################
######CALL PARSERS FOR SPECIFIC DATASETS TO ORDER LOGICAL FOR FURTHER USAGE#####
def payload_sanitiser(unsanity_data: dict) -> dict:
    Users = []
    groups = []
    vpn_data = {}
    error_data = {}
####INSTANTIATE DATA PARSER CLASS##########
    parser = vpndata_parsers(unsanity_data)
    try:
########PASS DATA TO ERROR IF NOT SUCCESSFUL RESPONSE######
        if 'result' not in unsanity_data:
            error_data = unsanity_data
########USERLIST RESPONSE HEADER####################
        elif 'UserList' in unsanity_data['result']:
            vpn_data = parser.UserList()

########VPN SESSION LIST HEADER#######################
        elif 'SessionList' in unsanity_data['result']:
            vpn_data = parser.SessionList()

########GROUP LIST HEADER###########################
        elif 'GroupList' in unsanity_data['result']:
            vpn_data = parser.GroupList()

########ACCESS LIST HEADER###########################
        elif 'AccessList' in unsanity_data['result']:
            vpn_data = parser.AccessList()

########IP TABLE HEADER############################
        elif 'IpTable' in unsanity_data['result']:
            vpn_data = parser.ListIPs()

########DATA THAT DOES NOT NEED EXRTA PARSING######
        else:
            vpn_data = unsanity_data['result']

    except KeyError as err:
        print(f"Key Error: {err}")
        pass
    except TypeError as err:
        print(f"Type Error: {err}")
        pass

    return vpn_data, error_data


################################################################################
##METHOD TO SET ARGS BEFORE SANITISING AND STDOUT###############################
def sanitise_data(cli_args: str, vpn_data: dict, vpn_node: str) -> dict:
    function = cli_args.command
    vpn = cli_args.vpn

####IF USERNAME PARAMETER NOT SET####
    try:
        username = cli_args.username
    except AttributeError:
        username = None

####IF REALNAME SERACH PARAMETER NOT SET##
    try:
        realname = cli_args.realname
    except AttributeError:
        realname = None

####IF GROUP SEARCH PARAMETER NOT SET###
    try:
        group = cli_args.group
    except AttributeError:
        group = None

####IF IP NOT SEARCH FOR SEARCHING###
    try:
        ip = cli_args.ip
    except AttributeError:
        ip = None

##################################
####ENSURE NO CASE SENSITIVITY####
    if function is not None:
        function = function.lower()
    if username is not None:
        username = username.lower()
    if realname is not None:
        realname = realname.lower()

####CALLING SANITER OF RESPONSE DATA##################
    vpn_data, error_data = payload_sanitiser(vpn_data)
####INSTATIATE STDOUT CLASS FOR USER##################
    terminal_output = vpndata_output(cli_args, vpn_data, error_data, vpn_node)

####CALLING METHOD USING GETATTR() FROM ARGS INPUT######
    data = getattr(terminal_output, cli_args.command)
    data()
