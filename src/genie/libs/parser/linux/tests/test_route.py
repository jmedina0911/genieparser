import re
import unittest
from unittest.mock import Mock

from pyats.topology import Device

from genie.metaparser.util.exceptions import (SchemaMissingKeyError,
                                              SchemaEmptyParserError)

from genie.libs.parser.linux.route import Route,\
                                          ShowNetworkStatusRoute,\
                                          IpRouteShowTableAll


#############################################################################
# unitest for 'route'
#############################################################################

class TestRoute(unittest.TestCase):
    '''
    Unit test for
        * route
    '''
    
    device = Device(name='aDevice')
    maxDiff = None
    empty_output = {'execute.return_value': ''}

    golden_output = {'execute.return_value': '''
        Kernel IP routing table
        Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
        default         _gateway        0.0.0.0         UG    600    0        0 wlo1
        172.17.0.0      0.0.0.0         255.255.0.0     U     0      0        0 docker0
        192.168.1.0     0.0.0.0         255.255.255.0   U     600    0        0 wlo1
        192.168.122.0   0.0.0.0         255.255.255.0   U     0      0        0 virbr0
        10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 eth1-05
    '''}

    golden_parsed_output = {
        'routes': {
            '10.10.0.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'eth1-05',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '172.17.0.0': {
                'mask': {
                    '255.255.0.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'docker0',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '192.168.1.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'wlo1',
                                'metric': 600,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '192.168.122.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'virbr0',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            'default': {
                'mask': {
                    '0.0.0.0': {
                        'nexthop': {
                            1: {
                                'flags': 'UG',
                                'gateway': '_gateway',
                                'interface': 'wlo1',
                                'metric': 600,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
        },
    }

    def test_empty(self):
        self.device1 = Mock(**self.empty_output)
        obj = Route(device=self.device1)
        with self.assertRaises(SchemaEmptyParserError):
            parsed_output = obj.parse()

    def test_golden(self):
        self.device = Mock(**self.golden_output)
        obj = Route(device=self.device)
        parsed_output = obj.parse()
        self.assertEqual(parsed_output, self.golden_parsed_output)


#############################################################################
# unitest For netstat -rn
#############################################################################

class TestShowNetworkStatusRoute(unittest.TestCase):
    '''
    Unit test for
        * netstat -rn
    '''
    
    device = Device(name='aDevice')
    maxDiff = None
    empty_output = {'execute.return_value': ''}

    golden_output = {'execute.return_value': '''
        Kernel IP routing table
        Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
        0.0.0.0         192.168.1.1     0.0.0.0         UG        0 0          0 wlo1
        172.17.0.0      0.0.0.0         255.255.0.0     U         0 0          0 docker0
        192.168.1.0     0.0.0.0         255.255.255.0   U         0 0          0 wlo1
        192.168.122.0   0.0.0.0         255.255.255.0   U         0 0          0 virbr0
        10.10.0.0       0.0.0.0         255.255.255.0   U         0 0          0 eth1-05
    '''}

    golden_parsed_output = {
        'routes': {
            '0.0.0.0': {
                'mask': {
                    '0.0.0.0': {
                        'nexthop': {
                            1: {
                                'flags': 'UG',
                                'gateway': '192.168.1.1',
                                'interface': 'wlo1',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '10.10.0.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'eth1-05',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '172.17.0.0': {
                'mask': {
                    '255.255.0.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'docker0',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '192.168.1.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'wlo1',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
            '192.168.122.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'flags': 'U',
                                'gateway': '0.0.0.0',
                                'interface': 'virbr0',
                                'metric': 0,
                                'ref': 0,
                                'use': 0,
                            },
                        },
                    },
                },
            },
        },
    }

    def test_empty(self):
        self.device1 = Mock(**self.empty_output)
        obj = ShowNetworkStatusRoute(device=self.device1)
        with self.assertRaises(SchemaEmptyParserError):
            parsed_output = obj.parse()

    def test_golden(self):
        self.device = Mock(**self.golden_output)
        obj = ShowNetworkStatusRoute(device=self.device)
        parsed_output = obj.parse()
        self.assertEqual(parsed_output, self.golden_parsed_output)

class TestIpRouteShowTableAll(unittest.TestCase):
    '''
    Unit test for
        * netstat -rn
    '''
    
    device = Device(name='aDevice')
    maxDiff = None
    empty_output = {'execute.return_value': ''}

    golden_output = {'execute.return_value': '''
        default via 192.168.1.1 dev enp7s0 proto dhcp metric 100
        169.254.0.0/16 dev enp7s0 scope link metric 1000
        172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
        172.18.0.0/16 dev br-d19b23fac393 proto kernel scope link src 172.18.0.1 linkdown
        192.168.1.0/24 dev enp7s0 proto kernel scope link src 192.168.1.212 metric 100 
        broadcast 127.0.0.0 dev lo table local proto kernel scope link src 127.0.0.1 
        local 10.233.44.70 dev kube-ipvs0 table local proto kernel scope host src 10.233.44.70
        broadcast 192.168.1.255 dev enp7s0 table local proto kernel scope link src 192.168.1.212 
    '''}

    golden_parsed_output = {
        'routes': {
            '0.0.0.0': {
                'mask': {
                    '0.0.0.0': {
                        'nexthop': {
                            1: {
                                'gateway': '192.168.1.1',
                                'interface': 'enp7s0',
                                'metric': 100
                            },
                        },
                    },
                },
            },
            '169.254.0.0': {
                'mask': {
                    '255.255.0.0': {
                        'nexthop': {
                            1: {
                                'interface': 'enp7s0',
                                'scope': 'link',
                                'metric': 1000
                            },
                        },
                    },
                },
            },
            '172.17.0.0': {
                'mask': {
                    '255.255.0.0': {
                        'nexthop': {
                            1: {
                                'interface': 'docker0',
                                'scope': 'link',
                                'proto': 'kernel',
                                'src': '172.17.0.1'
                            },
                        },
                    },
                },
            },
            '172.18.0.0': {
                'mask': {
                    '255.255.0.0': {
                        'nexthop': {
                            1: {
                                'interface': 'br-d19b23fac393',
                                'scope': 'link',
                                'proto': 'kernel',
                                'src': '172.18.0.1'
                            },
                        },
                    },
                },
            },
            '192.168.1.0': {
                'mask': {
                    '255.255.255.0': {
                        'nexthop': {
                            1: {
                                'interface': 'enp7s0',
                                'scope': 'link',
                                'proto': 'kernel',
                                'src': '192.168.1.212'
                            },
                        },
                    },
                },
            },
            '127.0.0.0': {
                'mask': {
                    '255.255.255.255': {
                        'nexthop': {
                            1: {
                                'interface': 'lo',
                                'scope': 'link',
                                'proto': 'kernel',
                                'src': '127.0.0.1',
                                'broadcast': True,
                                'table': 'local'
                            },
                        },
                    },
                },
            },
            '10.233.44.70': {
                'mask': {
                    '255.255.255.255': {
                        'nexthop': {
                            1: {
                                'interface': 'kube-ipvs0',
                                'scope': 'host',
                                'proto': 'kernel',
                                'src': '10.233.44.70',
                                'local': True,
                                'table': 'local'
                            },
                        },
                    },
                },
            },
            '192.168.1.255': {
                'mask': {
                    '255.255.255.255': {
                        'nexthop': {
                            1: {
                                'interface': 'enp7s0',
                                'scope': 'link',
                                'proto': 'kernel',
                                'src': '192.168.1.212',
                                'broadcast': True,
                                'table': 'local'
                            },
                        },
                    },
                },
            },
        },
    }

    def test_empty(self):
        self.device1 = Mock(**self.empty_output)
        obj = IpRouteShowTableAll(device=self.device1)
        with self.assertRaises(SchemaEmptyParserError):
            parsed_output = obj.parse()

    def test_golden(self):
        self.device = Mock(**self.golden_output)
        obj = IpRouteShowTableAll(device=self.device)
        parsed_output = obj.parse()
        self.assertEqual(parsed_output, self.golden_parsed_output)



if __name__ == '__main__':
    unittest.main()
