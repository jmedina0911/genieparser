# Global Imports
import json
from collections import defaultdict

# Metaparser
from genie.metaparser import MetaParser

# =============================================
# Collection for '/mgmt/tm/net/dns-resolver' resources
# =============================================


class NetDnsresolverSchema(MetaParser):

    schema = {}


class NetDnsresolver(NetDnsresolverSchema):
    """ To F5 resource for /mgmt/tm/net/dns-resolver
    """

    cli_command = "/mgmt/tm/net/dns-resolver"

    def rest(self):

        response = self.device.get(self.cli_command)

        response_json = response.json()

        if not response_json:
            return {}

        return response_json
