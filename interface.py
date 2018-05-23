import re

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