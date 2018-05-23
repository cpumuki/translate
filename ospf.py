import re

def netmask2cidr(mask):
    return sum([bin(int(x)).count('1') for x in mask.split('.')])

class OSPF(object):
    def __init__(self, lines, debug=0):
        self.version = 2 # default version 2
        self.graceful = 0
        self.area = []
        self.summary = dict()
        self.log = 0
        for l in lines:
            if debug == 1: print("* ospf debug: %s" % l.strip("\n"))
            r0 = re.match("(router ospf|\s+log-status-change)$", l)
            r1 = re.match("\s+area (\S+)$", l)
            r2 = re.match("\s+graceful-restart", l)
            r3 = re.match("\s+log adjacency", l)
            r4 = re.match("\s+area (\S+) range (\S+) (\S+) (advertise cost (\d+))", l)
            r5 = re.match("\s+area (\S+) range (\S+)\/(\d+) advertise cost (\d+)", l)
            if "ipv6 router ospf" in l:
                self.version = 3
            elif r1:
                self.area.append(r1.group(1))
                self.summary[r1.group(1)] = []
            elif r2:
                self.graceful = 1
            elif r3:
                self.log = 1
            elif r4:
                a,b,c = r4.group(4).split(" ")
                data = "%s,%s,%s" % (r4.group(2), r4.group(3), c)
                self.summary[r4.group(1)].append(data)
            elif r5:
                cost = r5.group(4)
                data = "%s,%s,%s" % (r5.group(2), r5.group(3), cost)
                self.summary[r5.group(1)].append(data)
            elif r0:
                pass
            else: 
                print("* Warning line skipped in ospf: %s" % l.strip("\n"))

    def __repr__(self):
        return "ospf version %s areas: %s"  % (self.version, self.area)

    def generate_junos(self):
        commands = []
        if self.version == 2:
            protocol = "set protocols ospf"
            # Add some specific commands to OSPFv2
            commands.append("set protocols ospf no-rfc-1583")
        else:
            protocol = "set protocols ospf3"

        if self.graceful:
            commands.append("set routing-options graceful-restart")

        # area-range commands
        for area in self.summary.keys():
            for item in self.summary[area]:
                prefix,mask,cost = item.split(",")
                if self.version == 2:
                    # IPv6 netmask is already in CIDR notation
                    mask = netmask2cidr(mask)
                commands.append("%s area %s area-range %s/%s override-metric %s exact" %   
                        (protocol, area, prefix, mask, cost))
        return (commands)
