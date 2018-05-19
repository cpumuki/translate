#/usr/bin/python

import re
import sys
import json

class VLAN(object):
    """ Creates a VLAN object """
    def __init__(self, lines):
        self.id = 0
        self.name = ""
        self.l3iface = ""
        self.modes = []
        self.ports = []
        self.loop = 0
        for l in lines:
            r1 = re.match("^vlan (\d+) name (\S+)", l)
            r2 = re.match("\s+(untagged|tagged) ethe (\S+)", l)
            r3 = re.match("\s+router-interface ve (\S+)", l)
            r4 = re.match("\s+loop-detection", l)
            if r1:
                self.id = r1.group(1)
                self.name = r1.group(2)
            elif r2:
                # TODO: is the order kept ?
                self.modes.append(r2.group(1))
                self.ports.append(r2.group(2))
            elif r3:
                self.l3iface = r3.group(1)
            elif r4:
                self.loop = 1
            else:
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

    def __repr__(self):
        return "vlan %s (%s) l3interface: %s" % (self.id, self.name, self.l3iface)

class VE(object):
    """ Create a VE object """
    def __init__(self, lines):
        self.id = 0
        self.name = ""
        self.ospf = dict()
        self.ipaddress = []
        self.helper = []
        self.pim = 0
        self.mtu = 0
        self.ip6address = []
        self.mtu6 = 0
        self.ospf3 = dict()
        for l in lines:
            r1 = re.match("^interface ve (\d+)", l)
            r2 = re.match("\s+port-name (.*)", l)
            r3 = re.match("\s+ip ospf (area|cost|dead-interval|hello-interval) (\S+)", l)
            r4 = re.match("\s+ipv6 ospf (area|cost|dead-interval|hello-interval) (\S+)", l)
            r5 = re.match("\s+ip address (\S+)", l)
            r6 = re.match("\s+ipv6 address (\S+)", l)
            r7 = re.match("\s+ip helper-address (\S+)", l)
            r8 = re.match("\s+ip pim-sparse", l)
            if r1:
                self.id = r1.group(1)
            elif r2:
                self.name = r2.group(1)
            elif r3:
                self.ospf[r3.group(1)] = r3.group(2)
            elif r4:
                self.ospf[r4.group(1)] = r4.group(2)
            elif r5:
                self.ipaddress.append(r5.group(1))
            elif r6:
                self.ip6address.append(r6.group(1))
            elif r7:
                self.helper.append(r7.group(1))
            elif r8:
                self.pim = 1
            else: 
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

    def __repr__(self):
        return "ve %s (%s) ipaddress: %s" % (self.id, self.name, self.ipaddress)

class INTERFACE(object):
    """ Creates a physical INTERFACE object """
    def __init__(self, lines):
        self.port = ""
        self.name = ""
        self.enabled = 0
        self.interval = 30
        self.flow_control = 0
        self.link_fault = 0
        for l in lines:
            r1 = re.match("interface ethernet (\S+)", l)
            r2 = re.match("\s+port-name (.*)", l)
            r3 = re.match("\s+load-interval (.*)", l)
            if r1:
                self.port = r1.group(1)
            elif r2:
                self.name = r2.group(1)
            elif r3:
                self.interval = r3.group(1)
            else:
                if "link-fault-signaling" in l:
                    self.link_fault = 1
                elif "no flow-control" in l:
                    self.flow_control = 0
                elif "enable" in l:
                    self.enabled = 1
                else: 
                    # print("* Warning line skipped: %s" % l.strip("\n"))
                    pass

    def __repr__(self):
        return "interface %s (%s)"  % (self.port, self.name)

class SNMP(object):
    def __init__(self,lines):
        self.comunity = "public"
        self.location = "MYLOCATION"
        self.hosts = []

    def __repr__(self):
        return "snmp community %s, location %s" % (self.community, self.location)

class LAG(object):
    def __init__(self,lines):
        self.lagid = 0
        self.primary = ""
        self.ports = []
        self.names = []
        self.deployed = 0
        for l in lines:
            r1 = re.match("lag \"(\S*)\" dynamic id (\S+)",l)
            r2 = re.match("\s*primary-port (\S*)",l)
            # FIXME: Multiple ports defined
            r3 = re.match("\s*ports ethernet (\S*)",l)
            r4 = re.match("\s*deploy",l)
            if r1:
                self.lagid = r1.group(1)
            elif r2:
                self.primary = r2.group(1)
            elif r3:
                self.ports.append(r3.group(1))
            elif r4:
                self.deployed = 1
            else:
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

    def __repr__(self):
        return "lag %s (primary %s) ports: %s"  % (self.lagid, self.primary, self.ports)

class BGP(object):
    def __init__(self,lines):
        self.las = 0
        for l in lines:
            r1 = re.match("\s*local-as (\S+)",l)
            if r1:
                self.las = r1.group(1)
            else:
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

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

class NTP(object):
    def __init__(self,lines):
        self.name = ""
        for l in lines:
            r1 = re.match("ntp",l)
            if r1:
                self.name = ""
            else:
                # print("* Warning line skipped: %s" % l.strip("\n"))
                pass

class OSPF(object):
    def __init__(self,lines):
        self.version = 2 # default version 2
        self.graceful = 0
        self.area = []
        self.log = 0
        for l in lines:
            r1 = re.match("area (\S+)", l)
            r2 = re.match("\s+graceful-restart", l)
            r3 = re.match("\s+log adjacency", l)
            if "ipv6 router ospf" in l:
                self.version = 3
            elif r1:
                self.area.append(r1.group(1))
            elif r2:
                self.graceful = 1
            elif r3:
                self.log = 1
            else: 
                print("* Warning line skipped: %s" % l.strip("\n"))

def process_line_config(line):
    return True

def process_chunk(chunk):
    line = chunk[0]
    if "vlan" in line:
        vlan = VLAN(chunk)
        # print(vlan)
    elif "interface ve" in line:
        ve = VE(chunk)
        # print(ve)
    elif "interface ethernet" in line:
        iface = INTERFACE(chunk)
        # print(iface)
    elif "snmp-server" in line:
        snmp = SNMP(chunk)

def is_ignored_command(line):   
    for ic in ignored_commands:
        # Ignore commands should be partial or full commands                
        if ic in line:
            return True
    return False

def is_one_to_one(line):

    r1 = re.match("hostname (\S+)", line)
    r2 = re.match("ip arp-age (\d+)", line)
    r4 = re.match("ip dns domain-name (\S+)", line)
    r5 = re.match("username (\S+)( privilege (\d+)){0,1} password 8 .*", line)
    r6 = re.match("logging host (\S+)", line)
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
    else:
        return False
    return True

#
# ---------------------------------------------------
# main
# ---------------------------------------------------
# 
if __name__ == "__main__":

    commands = []
    input_file = "example2.conf"
    ignore_file = "ignore.json"
    interface_file = "interfaces.json"

    # Read interface mapping from vendor to vendor
    with open(ignore_file) as f:
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
                #   1) Group of commands indented ended by '!'
                #   2) Group of commands non-indented (multiple lines)
                #   3) Group of commands to be ignored by printing a warning message
                #   4) Commands to be translated one by one (above)
                r1 = re.match("^(vlan|interface|snmp|router ospf|ipv6 router ospf|lag|router bgp|vrf|ntp).*", line)
                r2 = re.match("(lldp|ip route|ipv6 route|ip prefix-list|ipv6 prefix-list).*", line)
                r3 = re.match("(ip access-list|ipv6 access-list|route-map|aaa authentication|aaa authorization|radius-server|clock) .*", line)
                if r1:
                    in_block = 1
                    chunk.append(line)
                elif r3:
                    in_block = 2
                    chunk.append(line)
                elif r2:
                    # Configuration given by a set of lines (no indentation)
                    process_line_config(line)
                else:
                    # One to One mapping for the following commands
                    print("* Warning global line skipped: %s" % line.strip("\n"))
            else:
                if "!" in line:
                    if in_block == 1:
                        # Create the objects based on the type of group
                        process_chunk(chunk)
                    elif in_block == 2:
                        # These are commands will not be translated, just print a warning
                        print("* Convert the commands for: %s" % chunk[0].strip("\n"))
                    in_block=0
                # Keep appending lines in the current group
                chunk.append(line)

