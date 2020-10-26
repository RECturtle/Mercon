#!/usr/bin/env python3
import argparse
import re
import subprocess


# Create arguments for ip and target
parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--target",
    help="Enter one word name for target to be used for out files"
)
parser.add_argument(
    "-i", "--ip",
    help="ip address of target"
)
args = parser.parse_args()


# Run nmap on ip with outfile of nmap+target
def run_nmap(ip, target):
    a = subprocess.run(
        ["nmap", "-sC", "-sV", ip, "-o", "nmap" + target],
        capture_output=True,
        shell=False,
    )
    # return output from nmap
    return a.stdout


# Check for args, if missing print help message
def check_args(args):

    # If args - return nmap scan. Else - print help
    if args.target and args.ip:
        target = args.target.title()
        ip = args.ip
        ret = run_nmap(ip, target)
        return ret
    else:
        parser.print_help()
        return False


# Search for ports in output
def grab_ports(output):
    if (checked_args):
        re1 = b'[\n]80[/]'
        re2 = b'[\n]443[/]'
        re3 = b'[\n]139[/]'
        re4 = b'[\n]445[/]'

        # Ports into list
        ports = [re1, re2, re3, re4]

        # Compile each regex and search checked_args for ports
        p = [re.compile(x).search(checked_args) for x in ports]

        # If port found, grab port, convert to string, replace symbols,
        # and add to port_list to be returned.
        port_list = [x
                     .group()
                     .decode('utf-8')
                     .replace("\n", "")
                     .replace("/", "")
                     for x in p
                     if x is not None
                     ]
        return port_list


# Check ports to determine gobuster and/or smbmap
# 0 = none, 1 = web only, 2 = smb only, 3 = both
def check_ports(ports):
    web = 0
    smb = 0

    # Determine if we ports open
    if (('80' in ports) or ('443' in ports)):
        web = 1

    # Determine if SMB ports open
    if (('139' in ports) or ('445' in ports)):
        smb = 2
    return web + smb


#TODO Add in gobuster and smbshare functions
#TODO Requirements and dependencies

checked_args = check_args(args)
found_ports = grab_ports(checked_args)
nmap_results = check_ports(found_ports)
print(nmap_results)
