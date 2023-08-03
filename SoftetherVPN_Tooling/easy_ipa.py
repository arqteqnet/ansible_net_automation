#!/usr/bin/env python3
import requests
import json
from getpass import getpass
import logging
import SimpleEncryption
import sys
import os

################################################################################
#IPA CLASS MODULE FOR SIMPLE LDAP SERVICES
################################################################################

class ipa():

    def __init__(self, server='ipa.internal.example.com', sslverify=False, args=None):
        self.server = server
        self.sslverify = sslverify
        self.log = logging.getLogger(__name__)
        self.session = requests.Session()
        self.args = args
        self.encrypted_cookie_file = ".encrypted-cookie"
        self.cookie = None

################################################################################
#login User/Password and create Cookie
################################################################################
    def login(self):
        ret = False

        user = input("IPA Login Username: ")
        password = getpass('Enter User Password: ')
        ipaurl = f'https://{self.server}/ipa/session/login_password'
        header = {'referer': ipaurl,'Content-Type':
                  'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        login = {'user': user, 'password': password}
        auth = self.session.post(ipaurl, headers=header, data=login,
                               verify=self.sslverify)

        if auth.status_code != 200:
            self.log.warning(f'Failed to log {user} in to {self.server}'
            )
            exit(1)
        else:
            self.log.info(f'Successfully logged in as {user}')


        return auth.cookies['ipa_session']
################################################################################
#RE-USABLE REQUEST FOR ALL FUNCTOINS
################################################################################

    def IpaRequest(self, payload):
        try:
            results = None
            ipaurl = f'https://{self.server}/ipa'
            session_url = f'https://{self.server}/ipa/session/json'
            headers = {'referer': ipaurl,'Content-Type': 'application/json',
                      'Accept': 'application/json'}
            data = {'id': 0, 'method': payload['method'], 'params':
                    [payload['item'], payload['params']]}
            self.log.debug(f'Making {payload["method"]} request to {session_url}')

            if self.cookie == None:
                request = self.session.post(
                        session_url, headers=headers,
                        data=json.dumps(data),
                        verify=self.sslverify,
                        timeout=6,
                )
            else:
                request = self.session.post(
                        session_url, headers=headers,
                        cookies=self.cookie, data=json.dumps(data),
                        verify=self.sslverify,
                        timeout=6,
                )
        except requests.exceptions.Timeout:
            print(f"\nConnection timeout for {self.server}.")
            request = None

        except Exception as err:
            print(f"ERR: {err}: Failed to connect to {self.server}.")
            request = None
        if request is not None:
            if len(request.text) == 0:
                print(f"ERR: returned no data. This is usually incorrect credentials or cookie")
                sys.exit(1)
            elif request.status_code != 200:
                print(f"Conenction Error, Reason: {request.reason}")
                #sys.exit(1)
            elif request.status_code == 200:
                results = json.loads(request.text.encode('utf-8'))
        else:
            results = None


        return results, request

################################################################################
#TEST COOKIE SESSION AUTH
################################################################################
    def ping(self):
        m = {'item': [], 'method': 'ping', 'params':
             {}}

        results, code = self.IpaRequest(m)

        return results, code
################################################################################
#HOSTS AKA SYSTEM
################################################################################
    def host_show(self, hostname):
        m = {'item': [hostname], 'method': 'host_show', 'params':
             {'all': True}}
        results, code = self.IpaRequest(m)

        return results

################################################################################
#USER FIND, LEAVE user=None for all users
################################################################################

    def user_find(self, user=None, attrs={}, sizelimit=40000):
        params = {'all': True,
                  'no_members': False,
                  'sizelimit': sizelimit,
                  'whoami': False}
        params.update(attrs)
        m = {'item': [user], 'method': 'user_find', 'params': params}
        results, code = self.IpaRequest(m)

        return results

################################################################################
#USER SHOW
################################################################################
    def user_show(self, user):
        m = {'item': [user], 'method': 'user_show', 'params':
             {'all': True, 'raw': False}}
        results, code = self.IpaRequest(m)

        return results

    def cookie_assert(self):
        ret = False
        test_cookie = True
        crypt = SimpleEncryption

        while test_cookie is True:
            if os.path.exists(f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}"):

                with open(f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}", "r") as f:
                    encrypted_data=json.load(f)
                    f.close

                decrypt_cookie = crypt.decrypt(encrypted_data, self.args.encryption_key, f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}")
                decrypt_cookie = bytes.decode(decrypt_cookie)

                self.cookie = {'ipa_session': decrypt_cookie}
                results, request_code = self.ping()

                if request_code.status_code != 200:
                    print("\nIPA Cookie Session Invalid. Redirecting to LDAP Login")
                    os.remove(f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}")
                    cookie = self.login()
                    self.cookie = {'ipa_session': cookie}

                    encrypted_dict = crypt.encrypt(cookie, self.args.encryption_key)
                    with open(f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}", 'w') as f:
                        f.write(json.dumps(encrypted_dict))
                        f.close

                    self.cookie_assert

                elif request_code.status_code == 200:
                    print("\nIPA Cookie Session Valid")
                    test_cookie = False
                    ret = True

            else:
                print("\nNo IPA Cookie Found, redirecting to LDAP login")
                cookie = self.login()
                encrypted_dict = crypt.encrypt(cookie, self.args.encryption_key)
                with open(f"{os.environ.get('HOME')}/{self.encrypted_cookie_file}", 'w') as f:
                    f.write(json.dumps(encrypted_dict))
                    f.close
                self.cookie_assert

        return ret
