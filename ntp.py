import re

class NTP(object):
	
    def __init__(self,lines):
        self.iface = ""
        self.servers = []
        for l in lines:
            r2 = re.match("\s+source-interface (\S+) (\d+)", l)
            r3 = re.match("\s+server (\S+)", l)
            if r2:
            	# Note we statically assign source interface as lo0
                self.iface = "lo0"
            elif r3:
                self.servers.append(r3.group(1))
            else:
                print("* Warning line skipped in ntp: %s" % l.strip("\n"))

    def generate_junos(self):

        commands = []
        if self.iface != "":
            commands.append("set system ntp source-address %s" % self.iface)
        for server in self.servers():
            commands.append("set system ntp server %s" % server)

        return (commands)
