#/usr/bin/python

import re
import sys
import json

from ospf import OSPF
from bgp import BGP
from lag import LAG
from vlan import VLAN
from ve import VE
from interface import INTERFACE
from ntp import NTP

class VRF(object):
    def __init__(self,lines):
        self.name = ""
        for l in lines:
            r1 = re.match("vrf (\S+)",l)
            if r1:
                self.name = r1.group(1)
            else:
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

def process_line_config(line):
    commands = []
    r1 = re.match("ip route (\S+)\/(\S+) null0", line)
    r2 = re.match("ip route (\S+)\/(\S+) (\S+) distance (\d+)", line)
    r3 = re.match("lldp enable.*", line)
    r4 = re.match("snmp-server contact (.*)", line)
    r5 = re.match("snmp-server location (.*)", line)
    r6 = re.match("snmp-server host (\S+) version v2c 2 (\S+)", line)
    r7 = re.match("snmp-server community 2 (\S+) ro \"(\S+)\"", line)
    r8 = re.match("snmp-server trap-source (\S+) (\d+)", line)
    r10 = re.match("snmp-server", line)
    r11 = re.match("snmp-server max-ifindex-per-module 64", line)
    r12 = re.match("snmp-server preserve-statistics", line)   
    if r1:
        commands.append("set routing-options static route %s/%s discard" % (r1.group(1), r1.group(2)))
    elif r2:
        commands.append("set routing-options static route %s/%s next-hop %s preference %s" % (r2.group(1), r2.group(2), r2.group(3),r2.group(4)))
    elif r3:
        # NOTE: lldp enabled all ports
        commands.append("set protocols lldp interface all")
    elif r4:
        commands.append("set snmp contact %s" % r4.group(1))
    elif r5:
        commands.append("set snmp location %s" % r5.group(1))
    elif r6:
        commands.append("set snmp trap-group HOSTS targets %s" % r6.group(1))
        commands.append("set snmp trap-group HOSTS version v2")
    elif r7:
        # FIXME: Need to configure TrustedLineNets
        print("* FIXME: You need to configure TrustedLineNets (client list or prefix list)")
        print("* FIXME: You need to change the SNMP community (ie: public)")
        commands.append("set snmp community public client-list-name TrustedLineNets")
        print
    elif r8:
        # Ignore the interface configured and set lo0
        commands.append("set snmp trap-options source-address lo0")
    elif r10:
        pass
    elif r11:
        pass
    elif r12:
        pass
    return commands

def process_chunk(chunk):
    line = chunk[0]
    commands = []
    if "vlan" in line:
        vlan = VLAN(chunk, iface_map)
        commands = vlan.generate_junos()
    elif "interface ve" in line:
        ve = VE(chunk)
    elif "interface ethernet" in line:
        iface = INTERFACE(chunk)
        # print(iface)
    elif "lag" in line:
        lag = LAG(chunk, iface_map)
        commands = lag.generate_junos()
        for c in commands:
            print(c)
    elif "snmp-server" in line:
        snmp = SNMP(chunk)
    elif "router ospf" in line:
        ospf = OSPF(chunk, debug=0)
        commands = ospf.generate_junos()
    elif "router bgp" in line:
        bgp = BGP(chunk)
        commands = bgp.generate_junos()
    return commands

def is_ignored_command(line):
    for ic in ignored_commands:
        # Ignore commands should be partial or full commands                
        if ic in line:
            return True
    return False

def is_one_to_one(line):
    commands = []
    r1 = re.match("hostname (\S+)", line)
    r2 = re.match("ip arp-age (\d+)", line)
    r4 = re.match("ip dns domain-name (\S+)", line)
    r5 = re.match("username (\S+)( privilege (\d+)){0,1} password 8 .*", line)
    r6 = re.match("logging host (\S+)", line)
    r7 = re.match("ip dns server-address (\S+)+", line)
    r8 = re.match("telnet server", line)
    r9 = re.match("no ip icmp redirects", line)
    r10 = re.match("telnet timeout (\d+)", line)
    if r1:
        commands.append("set system host-name %s" % r1.group(1))
    elif r2:
        commands.append("set system arp aging-timer %s" % r2.group(1))
    elif r4:
        commands.append("set system domain-name %s" % r4.group(1))
    elif r5:
        commands.append("set system login user %s full-name %s" % (r5.group(1),r5.group(1)))
        if r5.group(2) == "":
            commands.append("set system login user %s class super-user" % r5.group(1))        
        else:
            commands.append("set system login user %s class operator" % r5.group(1))        
    elif r6:
        commands.append("set system syslog host %s" % r6.group(1))
    elif r7:
        commands.append("set system name-server %s" % r7.group(1))
    elif r8:
        commands.append("set system services telnet")
    elif r9:
        commands.append("set system no-redirects")
    elif r10:
        # FIXME: telnet logout needs to be configured in the login class (idle-timeout)
        pass
    return commands

#
# ---------------------------------------------------
# Main
# ---------------------------------------------------
# 
# FIXME: No multicast support
# FIXME: No VRF support

if __name__ == "__main__":
    commands = []
    input_file     = "example.conf"
    ignore_file    = "ignore.json"
    interface_file = "interfaces.json"

    # Read interface mapping from vendor to vendor
    with open(interface_file) as f:
        iface_map = json.load(f)

    # Read commands to be ignored from JSON file
    with open(ignore_file) as f:
        ignored_commands = json.load(f)

    in_block = 0
    commands = []
    with open(input_file) as f:

        # Parse the router configuration
        for line in f:
            if is_ignored_command(line):
                continue
            if is_one_to_one(line):
                continue
            if in_block == 0:
                if "!" in line:
                    continue
                chunk = []
                # Different type of parsing:
                #   0) Commands to be ignored (is_ignored_command) above
                #   1) Group of commands indented ended by '!' (r1)
                #   2) Group of commands non-indented (multiple lines) (ie: lldp, snmp) (r2)
                #   3) Group of commands to be ignored by printing a warning message (r3)
                #   4) Commands to be translated one by one (above)
                r1 = re.match("^(vlan|interface|router ospf|ipv6 router ospf|lag|router bgp|vrf|ntp).*", line)
                r2 = re.match("(lldp|snmp|ip route|ipv6 route|ip prefix-list|ipv6 prefix-list).*", line)
                r3 = re.match("(ip access-list|ipv6 access-list|route-map|aaa authentication|aaa authorization|radius-server|clock) .*", line)
                if r1:
                    in_block = 1
                    chunk.append(line)
                elif r3:
                    in_block = 2
                    chunk.append(line)
                elif r2:
                    # Configuration given by a set of lines (no indentation)
                    commands = commands + process_line_config(line)
                else:
                    # One to One mapping for the following commands
                    print("* Warning global line skipped: %s" % line.strip("\n"))
            else:
                if "!" in line:
                    if in_block == 1:
                        # Create the objects based on the type of group
                        commands = commands + process_chunk(chunk)
                    elif in_block == 2:
                        # These are commands not translated, just print a warning
                        print("* FIXME: Convert the commands for: %s" % chunk[0].strip("\n"))
                    in_block=0
                # Keep appending lines in the current group
                chunk.append(line)

    for c in commands:
        print(c)
