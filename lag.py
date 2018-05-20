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
