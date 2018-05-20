import re

class LAG(object):

    def __init__(self, lines, iface_map):
        self.lagid = 0
        self.iface_map   = iface_map
        self.primary = ""
        self.ports = []
        self.names = []
        self.deployed = 0
        for l in lines:
            r1 = re.match("lag \"(\S*)\" dynamic id (\S+)",l)
            r2 = re.match("\s+primary-port (\S*)",l)
            # FIXME: Multiple ports defined. Currently only one supported
            r3 = re.match("\s+ports ethernet (\S*)",l)
            r4 = re.match("\s+deploy",l)
            r5 = re.match("\s+port-name \"(.*)\" ethernet (\S+)", l)
            if r1:
                self.lagid = r1.group(1)
            elif r2:
                self.primary = r2.group(1)
            elif r3:
                self.ports.append(r3.group(1))
            elif r4:
                self.deployed = 1
            elif r5:
                self.names.append(r5.group(1))
            else:
                print("* Warning line skipped in lag: %s" % l.strip("\n"))

    def __repr__(self):
        return "lag %s (primary %s) ports: %s"  % (self.lagid, self.primary, self.ports)

    def generate_junos(self):
        commands = []

        # FIXME: It will be repeated multiple times per each lag
        commands.append("set chassis aggregated-devices ethernet device-count 400")

        iface = "eth %s" % self.primary
        # FIXME: Catch error in case interface is not defined in the map
        iface = self.iface_map[iface]
        commands.append("set interfaces %s ether-options 802.3ad ae%s" % (iface,self.lagid))

        commands.append("set interfaces ae%s aggregated-ether-options lacp active" % self.lagid)
        commands.append("set interfaces ae%s unit 0 family ethernet-switching" % self.lagid)
        return (commands)
