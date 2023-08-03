#!/usr/bin/env python3
################################################################################
#COLOUR CLASS FOR STDOUT#
class bcolours:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

################################################################################
##PAUSE PROGRAM FOR USER STDOUT EVALATION#######################################
class program_flow():
    def __init__(self, args):
        self.args = args

####CONTINUE WITH FUNCTION######################################################
    def continue_flow(self):
        while True:
            last_confirmation = input(f"\nContinue with {self.args.command} Y/N ")
            if last_confirmation == "Y":
                print("\nProceeding\n")
                break
            elif last_confirmation == "y":
                print("\nProceeding\n")
                break
            else:
                print("\nExiting Program, Goodbye")
                exit(1)

    def dry_run(self, data):
        count = len(data)
        if self.args.test == 'true':
            print(f'\n{count} changes above would have been performed. Zero changes have been implemented.\n******DryRun Completed******')
            exit(1)


class Error(Exception):
    """Base class for other exceptions"""
    pass


class NotPresent(Error):
    """Raised when no onlined service present"""
    pass
