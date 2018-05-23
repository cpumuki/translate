import re

class VLAN(object):
    """ Creates a VLAN object """
    def __init__(self, lines, iface_map):
        self.id = 0
        self.iface_map   = iface_map
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
                print("* Warning line skipped in vlan: %s" % l.strip("\n"))
                pass

    def __repr__(self):
        return "vlan %s (%s) l3interface: %s" % (self.id, self.name, self.l3iface)

    def generate_junos(self):
        commands = []

        commands.append("set vlans %s" % self.name)
        commands.append("set vlans %s vlan-id %s" % (self.name, self.id))
        for p in self.ports:
            # FIXME interface-type trunk|access
            iface = self.iface_map["eth " + p]
            commands.append("set interfaces %s unit 0 family ethernet-switching vlan members %s" % 
                (iface, self.name))

        # FIXME: remove duplicates
        return (commands)
