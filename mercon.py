#!/usr/bin/env python3
import argparse
import re
import subprocess


# Create arguments for ip, target, and wordlist
parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--target",
    help="Enter one word name for target to be used for out files"
)
parser.add_argument(
    "-i", "--ip",
    help="ip address of target"
)
parser.add_argument(
    "-w", "--wordlist",
    help="Enter full path to wordlist. This will be used for gobuster scan"
)

args = parser.parse_args()


def check_args(args):
    """
    Check to ensure args were provided.
    If args, run nmap scan and return results
    If no no args, print help message.
    """
    if args.target and args.ip and args.wordlist:
        target = args.target.title()
        ip = args.ip
        print("===== Running Nmap Scan =====")
        ret = run_nmap(ip, target)
        return ret
    else:
        parser.print_help()
        return False


def run_nmap(ip, target):
    """Run nmap on ip with outfile of nmap+target."""
    a = subprocess.run(
        ["nmap", "-sC", "-sV", ip, "-o", "nmap" + target],
        capture_output=True,
        shell=False,
    )
    # return output from nmap
    return a.stdout


def grab_ports(output):
    """Search for ports in output."""
    if (output):
        re1 = b'[\n]80[/]'
        re2 = b'[\n]443[/]'
        re3 = b'[\n]139[/]'
        re4 = b'[\n]445[/]'

        # Ports into list
        ports = [re1, re2, re3, re4]

        # Compile each regex and search output for ports
        p = [re.compile(x).search(output) for x in ports]

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


def check_ports(ports):
    """
    Check ports to determine running gobuster and/or smbmap.
    0 = none
    1 = gobuster
    2 = smbmap
    3 = both
    """
    web = 0
    smb = 0

    # Determine if we ports open
    if (('80' in ports) or ('443' in ports)):
        web = 1

    # Determine if SMB ports open
    if (('139' in ports) or ('445' in ports)):
        smb = 2
    return web + smb


def go_run(args):
    """Run gobuster and return output"""
    print("[+] Gobuster Running")
    go_complete = subprocess.run(
        ["gobuster", "dir", "-u", "http://" + args.ip + "/",
        "-w", args.wordlist,
        "-x", "txt",
        "-o", "gobuster" + args.target],
        capture_output=True,
        shell=False
    )
    return go_complete


def smb_run(args):
    """Run smbmap and return output"""
    print("[+] Smbmap Running")
    smb_complete = subprocess.run(
        ["smbmap", "-H", args.ip],
        capture_output=True,
        shell=False
    )
    return smb_complete


def next_run(results, args):
    """Based of results of check_ports, run Smbmap, Gobuster, or both"""
    if results == 0:
        print(
            "Nmap did not find standard web or smb ports open.\n"
            "Check the Nmap outfile to ensure the host was up "
            "and the correct ip was used.\n"
        )
    else:
        if results == 3:
            # Run gobuster and smbmap in separate processes
            print("===== Gobuster and Smbmap Running =====")
            smb_out = smb_run(args)
            print_results(smb_out.stdout)

            go_out = go_run(args)
            print_results(go_out.stdout)

        elif results == 2:
            # Run smbmap
            smb_out = smb_run(args)
            print_results(smb_out.stdout)

        elif results == 1:
            # Ping index.php and run gobuster with -x updated accordingly
            go_out = go_run(args)
            print_results(go_out.stdout)


def print_results(arg):
    """Convert from b'' to string and print"""
    string_arg = arg.decode("utf-8")
    print(string_arg)


# TODO Add gobuster curl of index.php to change gobuster command
# TODO Refactor next_run - currently has repeat code
# TODO Requirements and dependencies
# TODO Tests


if __name__ == '__main__':
    nmap_out = check_args(args)
    if (nmap_out):
        print_results(nmap_out)
        found_ports = grab_ports(nmap_out)
        nmap_results = check_ports(found_ports)
        next_run(nmap_results, args)
