import re

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
            # FIXME: Multiple ports defined. Currently only one supported
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
                print("* Warning line skipped in lag: %s" % l.strip("\n"))

    def __repr__(self):
        return "lag %s (primary %s) ports: %s"  % (self.lagid, self.primary, self.ports)

    def generate_junos(self)
        commands = []

        # FIXME: It will be repeated multiple times per each lag
        commands.append("set chassis aggregated-devices ethernet device-count 400")

        iface = "eth %s" % self.primary
        # FIXME: Catch error in case interface is not defined in the map
        iface = iface_map[iface]
        commands.append("set interfaces ge-2/0/1 ether-options 802.3ad ae%d" % (iface,self.lagid))

        commands.append("set interfaces ae%d aggregated-ether-options lacp active" % self.lagid)
        commands.append("set interfaces ae%d unit 0 family ethernet-switching" % self.lagid)
        return (commands)
