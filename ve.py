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
        self.p2p = 0
        self.p2p6 = 0
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
            r9 = re.match("\s+ip ospf network point-to-point", l)
            r10 = re.match("\s+ip mtu (\d+)", l)
            r11 = re.match("\s+ipv6 enable", l)
            r12 = re.match("\s+ipv6 mtu (\d+)", l)
            r13 = re.match("\s+ipv6 ospf network point-to-point", l)
            r14 = re.match("\s+ipv6 nd suppress-ra", l)
            r15 = re.match("\s+bandwidth (\d+)", l)
            r16 = re.match("\s+vrf forwarding (\S+)", l)
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
            elif r9:
                self.p2p = 1
            elif r10:
                self.mtu = r10.group(1)
            elif r11:
                pass
            elif r12:
                self.mtu = r12.group(1)
            elif r13:
                self.p2p6 = 1
            elif r14:
                # FIXME: is there anyting to do ?
                pass
            elif r15:
                # Nothing to do with bandwidth
                pass
            elif r16:
                # FIXME: No support for VRF for the time being
                pass
            else: 
                print("* Warning line skipped in VE: %s" % l.strip("\n"))

    def __repr__(self):
        return "ve %s (%s) ipaddress: %s" % (self.id, self.name, self.ipaddress)
