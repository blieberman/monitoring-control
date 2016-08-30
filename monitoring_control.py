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
from urllib import urlencode
from datetime import datetime
from datetime import timedelta

####################
# CONFIGURATION
####################
config = ConfigParser.ConfigParser()
config.read("/etc/monitoring_control/monitoring_control_config.ini")

MON_HOST = config.get("configuration", "mon_host")
MON_USERNAME = config.get("configuration", "username")
MON_PASS = config.get("configuration", "password")

OPERATION_CODES = {"enable": 28, "disable": 29, "downtime": 86}
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

    # take in the an enable or disable notification operation
    parser.add_argument("--duration", help="a downtime window duration, in minutes",
                        dest="d",
                        type=int,
                        required=False)

    args = parser.parse_args()
    if args.o == "downtime" and args.d is None:
        parser.error("--operation downtime requires --duration")

    return args


def send_command(options):
    # returns a status of a given notification operation request to the monitoring server
    call_url = "http://" + MON_USERNAME + ":" + MON_PASS + "@" + MON_HOST \
                   + "/nagios/cgi-bin//cmd.cgi?"
    try:
        r = requests.get(call_url, params=options)
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


def main():
    args = process_command_line()

    target = args.t
    # get the operation code of the given operation string
    operation = OPERATION_CODES[args.o]
    window_in_min = args.d

    options = dict()

    options['cmd_typ'] = operation
    options['cmd_mod'] = 2
    options['ahas'] = 'on'
    options['host'] = target

    # get optional duration params if actually set
    if operation == 86:
        curr_time = datetime.now()
        end_time = curr_time + timedelta(minutes=window_in_min)

        options['com_data'] = 'set_by_monitoring_control'
        options['trigger'] = 0
        options['start_time'] = datetime.strftime(curr_time, '%m-%d-%Y %H:%M:%S')
        options['end_time'] = datetime.strftime(end_time, '%m-%d-%Y %H:%M:%S')
        options['fixed'] = 1
        options['hours'] = 2
        options['minutes'] = 0
        options['com_author'] = 'monitoring_control'
        options['btnSubmit'] = 'Commit'

    options = urlencode(options)
    # call the set_notifications method given the command line arguments
    status = send_command(options)

    sys.exit(status)

if __name__ == "__main__":
    main()
