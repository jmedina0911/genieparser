""" show_firewall.py

JunOs parsers for the following show commands:
    * show firewall
    * show firewall counter filter v6_local-access-control v6_last_policer
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from pyats.utils.exceptions import SchemaError
from genie.metaparser.util.schemaengine import (Any, 
        Optional, Use, Schema, Or)

class ShowFirewallSchema(MetaParser):

    """ Schema for:
            * show firewall
    """

    """schema = {
    Optional("@xmlns:junos"): str,
    "firewall-information": {
        Optional("@xmlns"): str,
        "filter-information": [
            {
                Optional("counter"): {
                    "byte-count": str,
                    "counter-name": str,
                    "packet-count": str
                },
                "filter-name": str,
                Optional("policer"): {
                    "byte-count": str,
                    "packet-count": str,
                    "policer-name": str
                }
            }
        ]
    }
}"""

    def validate_counter_list(value):
        # Pass firmware list as value
        if not isinstance(value, list):
            raise SchemaError('counter is not a list')
        counter_inner_schema = Schema(
                        {
                            "byte-count": str,
                            "counter-name": str,
                            "packet-count": str
                        
                        }
                    
        )
        # Validate each dictionary in list
        for item in value:
            counter_inner_schema.validate(item)
        return value

    
    def validate_filter_information_list(value):
        if not isinstance(value, list):
            raise SchemaError('filter-information is not a list')
        filter_schema = Schema({
                Optional("counter"): Use(ShowFirewall.validate_counter_list),
                "filter-name": str,
                Optional("policer"): {
                    "byte-count": str,
                    "packet-count": str,
                    "policer-name": str
                }
        })
        for item in value:
            filter_schema.validate(item)
        return value
    schema = {
        Optional("@xmlns:junos"): str,
        "firewall-information": {
            Optional("@xmlns"): str,
            "filter-information": Use(validate_filter_information_list)
        }
    }



class ShowFirewall(ShowFirewallSchema):
    """ Parser for:
            * show firewall
    """

    cli_command = 'show firewall'

    def cli(self, output=None):
        if not output:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Filter: catch_all
        p1 = re.compile(r'^Filter: +(?P<filter_name>\S+)$')

        # cflow_counter_v4                              28553344730            151730215
        p2 = re.compile(r'^(?P<counter_name>\S+) +(?P<byte_count>\d+) +(?P<packet_count>\d+)$')

        # Policers:
        p3 = re.compile(r'^Policers:$')

        # Counters:
        p4 = re.compile(r'^Counters:$')
        
        ret_dict = {}
        pol_coun = None

        for line in out.splitlines():
            line = line.strip()

            # Filter: catch_all
            m = p1.match(line)
            if m:
                group = m.groupdict()
                filter_list = ret_dict.setdefault("firewall-information", {}) \
                    .setdefault("filter-information", [])
                filter_dict = {"filter-name": group['filter_name']}
                filter_list.append(filter_dict)

            # cflow_counter_v4                              28553344730            151730215
            m = p2.match(line)
            if m:
                group = m.groupdict()
                if pol_coun == 'counter':
                    counter_list = filter_dict.setdefault('counter', [])
                    counter_dict = {k.replace('_', '-'):v for k, v in group.items() if v is not None}
                    counter_list.append(counter_dict)
                elif pol_coun == 'policer':
                    policer_dict = filter_dict.setdefault('policer', {})
                    policer_dict.update({"policer-name": group.pop("counter_name")})
                    policer_dict.update({k.replace('_', '-'):v for k, v in group.items() if v is not None})

            # Policers:
            m = p3.match(line)
            if m:
                pol_coun = 'policer'

            # Counters:
            m = p4.match(line)
            if m:
                pol_coun = 'counter'

        return ret_dict

class ShowFirewallCounterFilterSchema(MetaParser):

    """ Schema for:
            * show firewall counter filter v6_local-access-control v6_last_policer
    """

    schema = {
    Optional("@xmlns:junos"): str,
    "firewall-information": {
        Optional("@xmlns"): str,
        "filter-information": {
            "counter": {
                "byte-count": str,
                "counter-name": str,
                "packet-count": str
            },
            "filter-name": str
            }
        }
    }


class ShowFirewallCounterFilter(ShowFirewallCounterFilterSchema):
    """ Parser for:
            * show firewall counter filter v6_local-access-control v6_last_policer
            * show firewall counter filter ICMP_ACL_filter block
    """

    cli_command = [
        'show firewall counter filter v6_local-access-control v6_last_policer',
        'show firewall counter filter {filter} block'
        ]

    def cli(self, filter=None, output=None):
        if not output:
            if filter:
                out = self.device.execute(self.cli_command[1].format(
                    filter=filter
                ))
            else:
                out = self.device.execute(self.cli_command[0])
        else:
            out = output

        #Filter: catch_all
        p1 = re.compile(r'^Filter: +(?P<filter_name>\S+)$')

        #cflow_counter_v4                              28553344730            151730215
        p2 = re.compile(r'^(?P<counter_name>\S+) +(?P<byte_count>\d+) +(?P<packet_count>\d+)$')

        #Policers:
        p3 = re.compile(r'^(?P<filter_name>\APolicers:)$')
        
        ret_dict = {}

        for line in out.splitlines():
            line = line.strip()

            #Filter: catch_all
            m = p1.match(line)
            if m:
                group = m.groupdict()
                filter_information_list = ret_dict.setdefault("firewall-information", {})\
                    .setdefault("filter-information", {})

                filter_information_list["filter-name"] = group["filter_name"]
                continue

            #v6_last_policer                                1061737740              7860915
            m = p2.match(line)
            if m:
                group = m.groupdict()
                inner_filter_dict = {}
                inner_filter_dict["counter-name"] = group["counter_name"]
                inner_filter_dict["byte-count"] = group["byte_count"]
                inner_filter_dict["packet-count"] = group["packet_count"]

                filter_information_list["counter"] = inner_filter_dict
                
                continue

        return ret_dict