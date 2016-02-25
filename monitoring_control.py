#!/usr/bin/python

####################
# Ben Lieberman
# monitoring_control.py
# Disable and enable monitoring notifications for a particular Nagios host

import argparse
import socket
import requests
import sys
import ConfigParser

####################
# CONFIGURATION
####################
config = ConfigParser.ConfigParser()
config.read("./monitoring_control_config.ini")
MON_HOST = config.get("configuration", "mon_host")
MON_USERNAME = config.get("configuration", "username")
MON_PASS = config.get("configuration", "password")

OPERATION_CODES = {"enable": "28", "disable": "29"}
####################


def process_command_line():
    # returns parsed arguments from the command line

    # parse for command line arguments...
    parser = argparse.ArgumentParser()

    # you can optionally specify a hostname or default to using a local one
    parser.add_argument("--target", help="a target hostname to enable/disable notifications;" +
                                         "defaults to the run host",
                        dest="t",
                        default=socket.gethostname())

    # take in the an enable or disable notification operation
    parser.add_argument("--operation", help="a notification operation to execute on a host",
                        dest="o",
                        required=True)

    args = parser.parse_args()
    return args


def set_notifications(target, operation):
    # returns a status of a given notification operation request to the monitoring server
    call_url = "http://" + MON_USERNAME + ":" + MON_PASS + "@" + MON_HOST \
                   + "/nagios/cgi-bin//cmd.cgi?cmd_typ=" + operation + "&cmd_mod=2&ahas=on&host=" + target

    try:
        r = requests.get(call_url)
        # get the content from the response to parse
        content = r.content

        if "successfully submitted" in content:
            print "OK"
            return 0
        else:
            print content
            return 1

    except requests.exceptions.Timeout:
        print "Error: Request timed out..."
        return 1


####################
def main():
    args = process_command_line()
    target = args.t
    # get the operation code of the given operation string
    operation = OPERATION_CODES[args.o]

    # call the set_notifications method given the command line arguments
    status = set_notifications(target, operation)

    sys.exit(status)

if __name__ == "__main__":
    main()
