import re

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
                print("* Warning line skipped in VE: %s" % l.strip("\n"))

    def __repr__(self):
        return "ve %s (%s) ipaddress: %s" % (self.id, self.name, self.ipaddress)
