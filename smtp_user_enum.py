#!/usr/bin/python3

import socket 
import optparse
import sys


G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
W = '\033[0m'   # White
B = '\033[94m'  # Blue

def print_banner(target, mode):
    banner = f"""
{B}  _______________________________________________________________
 {B} /                                                               \\
{B} |   {Y}███████╗███╗   ███╗████████╗██████╗     ███████╗███╗   ██╗██╗   ██╗{B} |
{B} |   {Y}██╔════╝████╗ ████║╚══██╔══╝██╔══██╗    ██╔════╝████╗  ██║██║   ██║{B} |
{B} |   {Y}███████╗██╔████╔██║   ██║   ██████╔╝    █████╗  ██╔██╗ ██║██║   ██║{B} |
{B} |   {Y}╚════██║██║╚██╔╝██║   ██║   ██╔═══╝     ██╔══╝  ██║╚██╗██║██║   ██║{B} |
{B} |   {Y}███████║██║ ╚═╝ ██║   ██║   ██║         ███████╗██║ ╚████║╚██████╔╝{B} |
{B} |   {Y}╚══════╝╚═╝     ╚═╝   ╚═╝   ╚═╝         ╚══════╝╚═╝  ╚═══╝ ╚═════╝ {B} |
 {B} \\_______________________________________________________________/
                                              {W}By: {Y}@logic0x01{W}
    
    {B}[*]{W} Target : {G}{target}{W}
    {B}[*]{W} Mode   : {G}{mode}{W}
    {B}[*]{W} Port   : {G}25 (SMTP){W}
    """
    print(banner)


usage = "usage: %prog -t <target_ip> [-w <wordlist> | -u <username>]"
parser = optparse.OptionParser(usage=usage, description="SMTP Username Enumeration Tool")

parser.add_option('-w', '--wordlist', dest='usernames_list', help='Path to usernames wordlist')
parser.add_option('-t', '--target', dest='target', help='Target IP or hostname')
parser.add_option('-u', '--username', dest='username', help="Single username to check")

opts, args = parser.parse_args()

if not opts.target or (not opts.usernames_list and not opts.username):
    parser.print_help()
    sys.exit(1)

mode = "Single User" if opts.username and not opts.usernames_list else "Wordlist"
if opts.username and opts.usernames_list: mode = "Hybrid (User + Wordlist)"

print_banner(opts.target, mode)

usernames_to_check = []
if opts.username: usernames_to_check.append(opts.username)
if opts.usernames_list:
    try:
        with open(opts.usernames_list, 'r') as file:
            usernames_to_check.extend([u.strip() for u in file.readlines()])
    except FileNotFoundError:
        print(f"{R}[!] Error: Wordlist '{opts.usernames_list}' not found.{W}")
        sys.exit(1)

try:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    print(f"{B}[*]{W} Attempting connection...")
    soc.connect((opts.target, 25))
    banner_raw = soc.recv(1024)

    print(f"{B}[*]{W} Starting scan on {G}{len(usernames_to_check)}{W} entries...\n")

    for username in usernames_to_check:
        soc.send(b"VRFY " + username.encode() + b'\r\n')
        result = soc.recv(1024).decode(errors='ignore')

        if "250" in result or "252" in result:
            print(f"{G}[+]{W} VALID USER: {Y}{username}{W}")

except Exception as e:
    print(f"{R}[!] Connection error: {e}{W}")
finally:
    soc.close()
