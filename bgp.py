import re

class BGP(object):
    def __init__(self, lines, debug=0):
    	# Local AS number
        self.las = 0
        self.cluster = ""
        self.neighbors = dict()
        for l in lines:
            if debug == 1: print("* bgp debug: %s" % l.strip("\n"))
            r1 = re.match("\s*local-as (\S+)",l)
            r2 = re.match("\s*neighbor (\S+) remote-as (\S+)",l)
            r3 = re.match("\s*neighbor (\S+) description (.*)",l)
            r4 = re.match("\s*neighbor (\S+) next-hop-self",l)
            r5 = re.match("\s*neighbor (\S+) timers\s+keep-alive (\S+)\s+hold-time (\S+)",l)
            r6 = re.match("\s*neighbor (\S+) update-source (.*)",l)
            r7 = re.match("\s*neighbor (\S+) soft-reconfiguration inbound",l)
            r8 = re.match("\s*cluster-id (\S+)",l)
            r9 = re.match("\s*neighbor (\S+) weight (\S+)",l)
            if r1:
                self.las = int(r1.group(1))
            elif r2:
            	self.neighbors[r2.group(1)]=dict()
            	self.neighbors[r2.group(1)]['remote_as']=int(r2.group(2))
            	self.neighbors[r2.group(1)]['nhs']=0
            	self.neighbors[r2.group(1)]['soft_reconfig']=0
            elif r3:
            	self.neighbors[r3.group(1)]['description']=r3.group(2)
            elif r4:
            	self.neighbors[r4.group(1)]['nhs']=1
            elif r5:
            	self.neighbors[r5.group(1)]['keep_alive']=r5.group(2)
            	self.neighbors[r5.group(1)]['hold_time']=r5.group(3)
            elif r6:
            	self.neighbors[r6.group(1)]['interface']=r6.group(2)
            elif r7:
            	self.neighbors[r7.group(1)]['soft_reconfig']=1
            elif r8:
            	self.cluster = r8.group(1)
            elif r9:
            	# Weight not supported in junos
            	pass
            else:
                print("* Warning line skipped in bgp: %s" % l.strip("\n"))

    def generate_junos(self):
        commands = []

        if self.cluster != "":
        	commands.append("set protocols bgp group internal cluster %s" % self.cluster)

        for neig in self.neighbors.keys():
        	if self.neighbors[neig]['remote_as'] == self.las:
        		# Internal BGP
        		commands.append("set protocols bgp group internal type internal")
        		commands.append("set protocols bgp group internal local-as %d" % self.las)
        		prefix = "set protocols bgp group internal"
        	else:
        		# External BGP
        		remote_as = self.neighbors[neig]['remote_as']
        		commands.append("set protocols bgp group external type external")
        		commands.append("set protocols bgp group external local-as %d" % self.las)
        		commands.append("set protocols bgp group external peer-as %d" % remote_as)
        		prefix = "set protocols bgp group external"

        	description = self.neighbors[neig]['description']
        	commands.append("%s neighbor %s description \"%s\"" % (prefix,neig,description))
        	hold_time = self.neighbors[neig]['hold_time']
        	commands.append("%s neighbor %s hold-time %s" % (prefix,neig,hold_time))

        # FIXME: remove duplicates via sets
        return (commands)
