#/usr/bin/python

import re
import sys

class VLAN(object):
    """ Creates a VLAN object """
    def __init__(self, lines):
        self.id = 0
        self.name = ""
        self.l3iface = ""
        self.modes = []
        self.ports = []
        for l in lines:
            r1 = re.match("^vlan (\d+) name (\S+)", l)
            r2 = re.match("\s+(untagged|tagged) ethe (\S+)", l)
            r3 = re.match("\s+router-interface ve (\S+)", l)
            if r1:
                self.id = r1.group(1)
                self.name = r1.group(2)
            elif r2:
                # TODO: is the order kept ?
                self.modes.append(r2.group(1))
                self.ports.append(r2.group(2))
            elif r3:
                self.l3iface = r3.group(1)
            else:
                print("* Warning line skipped: %s" % l.strip("\n"))

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
                print("* Warning line skipped: %s" % l.strip("\n"))

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
                    print("* Warning line skipped: %s" % l.strip("\n"))

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
                print("* Warning line skipped: %s" % l.strip("\n"))

    def __repr__(self):
        return "lag %s (primary %s) ports: %s"  % (self.lagid, self.primary, self.ports)

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

if __name__ == "__main__":
    in_block = 0
    file = "example2.conf"
    commands = []
    with open(file) as f:
        for line in f:
            if in_block == 0:
                chunk = []
                # Create object for the following groups
                r1 = re.match("^(vlan|interface|snmp|router ospf|ipv6 router ospf|lag).*", line)
                r2 = re.match("(ip access-list|ipv6 access-list|route-map statics|aaa authentication|aaa authorization|radius-server|clock|route-map statics6) .*", line)
                if r1:
                    # Create an object and process further
                    in_block = 1
                    chunk.append(line)
                elif r2:
                    # Print a warning for this statements
                    in_block = 2
                    chunk.append(line)
                else:
                    # One to One mapping for the following commands
                    o1 = re.match("ip router-id (\S+)", line)
                    o2 = re.match("ip dns domain-name (\S+)", line)
                    o3 = re.match("ip dns server-address (.*)", line)
                    o4 = re.match("no ip icmp redirects", line)
                    o5 = re.match("ip arp-age (\S+)", line)
                    o6 = re.match("no ip source-route", line)
                    # This commands will be simply ignored
                    r3 = re.match("(ip ssh|acl-policy|ver|module|no route-only|cpu-usage|qos queue-type|ip tcp burst-normal|ipv6 enable-acl-cam-sharing|no spanning-tree| no dual-mode-default-vlan|system-max|banner).*", line)

                    if o1:
                        commands.append("set system router-id %s" % o1.group(1))
                    elif o2:
                        commands.append("set system dns %s" % o2.group(1))
                    elif o3:
                        commands.append("set system dns %s" % o3.group(1))
                    elif o4:
                        commands.append("set system no-icmp-redirects")
                        commands.append("set system no-ipv6-icmp-redirects")
                    elif o5:
                        commands.append("set system arp-age")
                    elif o6:
                        commands.append("set system no-source-route")
                    elif r3:
                        pass
                    else:
                        print("* Warning global line skipped: %s" % line.strip("\n"))
            else:
                if "!" in line:
                    if in_block == 1:
                        process_chunk(chunk)
                    elif in_block == 2:
                        # These are commands we will not translate, just print a warning
                        print("* Convert the commands for: %s" % chunk[0].strip("\n"))
                    in_block=0
                chunk.append(line)

