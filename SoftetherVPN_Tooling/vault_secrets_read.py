#!/usr/bin/env python3
import json
import requests
import os
import sys
from getpass import getpass
import hvac
from outputcolours import bcolours

################################################################################
##VAULT CLASS MODULE FOR LOGIN AND SECRETS RETRIEVAL############################
class vault_services:
####DEFAULT URL. EXPORT VARS TO BE USED IN FUTURE###############################
    def __init__(self, vault_url="https://vault.internal.example.com:8200", token_filename=".vault-token"):
        self.vault_url = vault_url
        self.token_filename = token_filename

####CHECK IF VAULT ENV VARIABLE IS SET AND IF IT MATHES DEFAULT URL#############
    def vault_export(self, first_run=True):
        ret = False
        if first_run is True:
            if os.environ.get('VAULT_ADDR') is not None and os.environ.get('VAULT_ADDR') != self.vault_url:
                print(f"\n{bcolours.WARNING}Warning: Vault Envronment Variable exists, but doesnt match [ {self.vault_url} ]{bcolours.ENDC}\n")
                ret = True
            elif os.environ.get('VAULT_ADDR') is not None and os.environ.get('VAULT_ADDR') == self.vault_url:
                ret = True
            else:
                print(f"\n{bcolours.FAIL}Vault environment variable NOT set{bcolours.ENDC}\n")
                sys.exit(1)
        elif first_run is False:
            ret = True

        return ret


################################################################################
####ASSERT VAULT AUTHENTICATION###########
    def token_assert(self, first_run=True):
        ret = False
########PREVENT CONTINOUS LOOP###################
        if first_run is True:
            test_env = self.vault_export(first_run)
        elif first_run is False:
            test_env = self.vault_export(first_run)

        if test_env is True:
            if os.path.exists(f"{os.environ.get('HOME')}/{self.token_filename}"):
                with open(f"{os.environ.get('HOME')}/{self.token_filename}", "r") as f:
                    data=f.readlines()
                    f.close
################RETRIEVE VAULT AUTH TOKEN#######################################
                auth_test = hvac.Client(url=os.environ.get('VAULT_ADDR'), token=data[0])
################IF VAULT AUTHENTICATION SUCCEEDS################################
                if auth_test.is_authenticated() is True:
                    ret = True
################IF AUTH FAILS. REDIRECT TO LOGIN#################################
                elif auth_test.is_authenticated() is not True:
                    print(f"\n{bcolours.FAIL}Not authenticated, Vault token invalid or expired. Redirecting to Vault Login!\n{bcolours.ENDC}")
                    #remove token
                    os.remove(f"{os.environ.get('HOME')}/{self.token_filename}")
                    retest = self.token_assert(False)

            else:
################IF VAULT TOKEN DOES NOT EXIST, FORCE NEW LOGIN###################
                print(F"\n{bcolours.HEADER}Vault LDAP login to create new Token!{bcolours.ENDC}")
                user= input(f"{bcolours.BOLD}Enter LDAP Username: {bcolours.ENDC}")
                passwd = getpass(prompt=f"{bcolours.BOLD}Enter Password (HIDDEN): {bcolours.ENDC}")
                client = hvac.Client(url=f"{os.environ.get('VAULT_ADDR')}")
                login_response = client.auth.ldap.login(username=user,password=passwd,)
                token=login_response['auth']['client_token']
                with open(f"{os.environ.get('HOME')}/{self.token_filename}", 'w') as f:
                    f.write(token)
                    f.close
                ret = self.token_assert(False)

        return ret

####READ VAULT SECRETS, WITH PROVIDED VAULT PATH. VERIFY VAULT AUTH#############
    def read_secrets(self, secrets_path) -> dict:
        read_response = None
        #test Export varaible is correctly set
        token_auth = self.token_assert()
        if token_auth is True:
            # Assert Token exists, if not Login using LDAP
            # Open and import token value for Auth
            with open(f"{os.environ.get('HOME')}/{self.token_filename}", "r") as f:
                data=f.readlines()
                f.close
            # Auth uing token
            read_secrets = hvac.Client(url=os.environ.get('VAULT_ADDR'), token=data[0])
            read_response =  read_secrets.read(path=secrets_path)
            if read_response is None:
                print(f"""\n{bcolours.FAIL}No secrets found. check following are correct:{bcolours.ENDC}\n
VAULT_ADDR: {bcolours.FAIL}{os.environ.get('VAULT_ADDR')}{bcolours.ENDC}
Vault Path: {bcolours.FAIL}{secrets_path}{bcolours.ENDC}\n""")
                sys.exit(1)
        else:
            re_run_read_secrets = self.read_secrets(secrets_path)


        return read_response
