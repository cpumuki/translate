
import unittest
from vlan import VLAN

class VLANTest(unittest.TestCase):
    """ Test case for VLAN objects """

    def test_generate_junos(self):
        """ Test the function generate_junos in the VLAN class """

        # Define a static map of interfaces
        iface_map = {"eth 1/1": "et-1/0/1"}
        chunk = ["vlan 2 name TEST", "untagged ethe 1/1", "router-interface ve 2"]
        result = ["set vlans TEST", "set vlans TEST vlan-id 2"]

        vlan = VLAN(chunk, iface_map)
        commands = vlan.generate_junos()
       
        self.assertEqual(commands, result)

if __name__ == '__main__':
    unittest.main()