#!/usr/bin/env python

####################
# monitoring_control.py
# Disable and enable monitoring notifications for a particular host or VIP

import argparse
import socket
import requests
import sys
import ConfigParser
import os
import ntplib
from urllib import urlencode
from datetime import datetime
from datetime import timedelta
import logging

####################
# CONFIGURATION
####################
config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'monitoring_control_config.ini')
config.read(config_path)

MON_HOST = config.get("configuration", "mon_host")
MON_USERNAME = config.get("configuration", "username")
MON_PASS = config.get("configuration", "password")

NTP_SERVER = config.get("configuration", "ntp_server")
NTP_VERSION = int(config.get("configuration", "ntp_version"))

OPERATION_CODES = {"enable": 28, "disable": 29, "downtime_services": 86, "downtime_host": 55}

LOG_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
####################


def initialize_console_logger(log_level):
    """
    Add console handler to the logger
    """
    log_formatter = logging.Formatter(LOG_FORMAT)
    mc_logger = logging.getLogger("monitoring-control")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    console_handler.setLevel(log_level)
    mc_logger.setLevel(logging.DEBUG)

    mc_logger.addHandler(console_handler)


def process_command_line():
    """
    returns parsed arguments from the command line
    """
    # parse for command line arguments...
    parser = argparse.ArgumentParser()

    # you can optionally specify a hostname or default to using a local one
    parser.add_argument("--target", help="a target hostname to enable/disable notifications;" +
                                         "defaults to the run host",
                        dest="t",
                        default=socket.getfqdn().lower(),
                        required=False)

    # take in the an enable or disable notification operation
    parser.add_argument("--operation", help="a notification operation to execute on a host",
                        dest="o",
                        required=True)

    # take in the an enable or disable notification operation
    parser.add_argument("--duration", help="a downtime window duration, in minutes; default is 10",
                        dest="d",
                        type=int,
                        default=10,
                        required=False)

    # take in the an enable or disable notification operation
    parser.add_argument("--downtime_type", help="a type of downtime, either 'services' or 'host'; default is host",
                        dest="dt",
                        default="services",
                        required=False)

    args = parser.parse_args()

    if args.o not in ["enable", "disable", "downtime"]:
        parser.error("--operation " + args.o + " is not one of 'enable', 'disable', 'downtime'")
    if (args.o == "downtime") and args.dt not in ["services", "host"]:
        parser.error("--downtime_type " + args.dt + " is not one of 'services' or 'host'")

    return args


def get_utc_date(ntp_server, ntp_version):
    """
    if possible, obtain date via query to time server local to the monitoring server to formulate exact downtime calls

    this is necessary for making calls remotely with servers in other timezones as monitoring server, as monitoring requires
    dates in downtime calls to be exact

    in a general case, monitoring server has utc server time
    """
    mc_logger = logging.getLogger("monitoring-control")

    try:
        # make remote call to ntp server
        ntp_client = ntplib.NTPClient()
        ntp_response = ntp_client.request(ntp_server, version=ntp_version)
    except socket.error as e:
        # use local date if remote call fails
        mc_logger.warning("Could not fetch time from %s due to socket error: %s" % (ntp_server, e))
        mc_logger.info("Using local time instead of remote...")
        dt = datetime.utcnow()
    else:
        # convert response in seconds to standard linux date format in utc
        dt = datetime.utcfromtimestamp(ntp_response.tx_time)

    return dt


def send_command(options):
    """
    returns a status of a given notification operation request to the monitoring server
    """
    call_url = "http://" + MON_USERNAME + ":" + MON_PASS + "@" + MON_HOST \
               + "/nagios/cgi-bin//cmd.cgi?"
    try:
        r = requests.get(call_url, params=options)
        # anything 400 or 500 is an exception
        r.raise_for_status()
        # get the content from the response to parse
        text = r.text

        if "successfully submitted" not in text:
            raise RuntimeError("Response from remote monitoring server denotes critical error")

    except requests.exceptions.Timeout:
        raise RuntimeError("Request to %s timed out" % call_url)


def main():
    args = process_command_line()
    initialize_console_logger(logging.DEBUG)

    mc_logger = logging.getLogger("monitoring-control")

    # get the operation code of the given operation string
    if args.o == 'downtime':
        args.o += "_" + args.dt

    operation = args.o
    target = args.t
    window_in_min = args.d

    options = dict()

    options['cmd_mod'] = 2
    options['ahas'] = 'on'
    options['host'] = target
    options['cmd_typ'] = OPERATION_CODES[operation]

    # get optional duration params if actually set
    if operation == 'downtime_services' or operation == 'downtime_host':
        curr_time = get_utc_date(NTP_SERVER, NTP_VERSION)
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

    try:
        send_command(options)
        mc_logger.info('OK')
        return 0
    except Exception as err:
        mc_logger.exception("Error from send_command(): %s", err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
