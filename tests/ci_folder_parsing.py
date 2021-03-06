"""Testing strategy for dynamic testing via folder structure."""

import importlib
import inspect
import os
import glob
import json
import argparse
from unittest.mock import Mock
from pyats import aetest
from pyats.aetest.steps import Steps

from genie.libs import parser as _parser
from genie.metaparser.util.exceptions import SchemaEmptyParserError

from pyats.topology import Device

# Create the parser
my_parser = argparse.ArgumentParser(description="Optional arguments for 'nose'-like tests")
my_parser.add_argument('-o', "--operating_system",
                       type=str,
                       help='The OS you wish to filter on',
                       default=None)
my_parser.add_argument('-c', "--class_name",
                       type=str,
                       help="The Class you wish to filter on, (not the Test File)",
                       default=None)
args = my_parser.parse_args()

_os = args.operating_system
_class = args.class_name

# This is the list of Classes that currently have no testing. It was found during the process
# of converting to folder based testing strategy
CLASS_SKIP = {
    "asa": {"ShowVpnSessiondbSuper": True},
    "iosxe": {
        "ShowPimNeighbor": True,
        "ShowIpInterfaceBrief": True,
        "ShowIpInterfaceBriefPipeVlan": True,
        "ShowBfdSessions": True,
        "ShowBfdSessions_viptela": True,
        "ShowBfdSummary": True,
        "ShowDot1x": True,
        "ShowEnvironmentAll": True,
        "ShowControlConnections_viptela": True,
        "ShowControlConnections": True,
        "ShowEigrpNeighborsSuperParser": True,
        "ShowIpEigrpNeighborsDetailSuperParser": True,
        "ShowIpOspfInterface": True,
        "ShowIpOspfNeighborDetail": True,
        "ShowIpOspfShamLinks": True,
        "ShowIpOspfVirtualLinks": True,
        "ShowIpOspfMplsTrafficEngLink": True,
        "ShowIpOspfDatabaseOpaqueAreaTypeExtLink": True,
        "ShowIpOspfDatabaseOpaqueAreaTypeExtLinkAdvRouter": True,
        "ShowIpOspfDatabaseOpaqueAreaTypeExtLinkSelfOriginate": True,
        "ShowIpOspfDatabaseTypeParser": True,
        "ShowIpOspfLinksParser": True,
        "ShowIpRouteDistributor": True,
        "ShowIpv6RouteDistributor": True,
        "ShowControlLocalProperties_viptela": True,
        "ShowControlLocalProperties": True,
        "ShowVrfDetailSuperParser": True,
        "ShowBgp": True,
        "ShowBgpAllNeighborsRoutesSuperParser": True,
        "ShowBgpDetailSuperParser": True,
        "ShowBgpNeighborSuperParser": True,
        "ShowBgpNeighborsAdvertisedRoutesSuperParser": True,
        "ShowBgpNeighborsReceivedRoutes": True,
        "ShowBgpNeighborsReceivedRoutesSuperParser": True,
        "ShowBgpNeighborsRoutes": True,
        "ShowBgpSummarySuperParser": True,
        "ShowBgpSuperParser": True,
        "ShowIpBgpAllNeighborsAdvertisedRoutes": True,
        "ShowIpBgpAllNeighborsReceivedRoutes": True,
        "ShowIpBgpNeighborsReceivedRoutes": True,
        "ShowIpBgpNeighborsRoutes": True,
        "ShowIpBgpRouteDistributer": True,
        "ShowPolicyMapTypeSuperParser": True,
        "ShowIpLocalPool": True,
        "ShowInterfaceDetail": True,
        "ShowInterfaceIpBrief": True,
        "ShowInterfaceSummary": True,
        "ShowAuthenticationSessionsInterface": True,
        "ShowVersion_viptela": True,
        "ShowBfdSummary_viptela": True,
        "ShowSoftwaretab_viptela": True, # PR submitted
        "ShowRebootHistory_viptela": True,
        "ShowOmpSummary_viptela": True,
        "ShowSystemStatus_viptela": True,
        "ShowTcpProxyStatistics": True, # PR submitted
        "ShowTcpproxyStatus": True, # PR submitted
        "ShowPlatformTcamUtilization": True, # PR submitted
        "ShowLicense": True, # PR submitted
        "Show_Stackwise_Virtual_Dual_Active_Detection": True, # PR submitted
        "Show_Cts_Sxp_Connections_Brief": True, # PR submitted
        "ShowSoftwaretab": True, # PR submitted
    },
    "ios": {
        "ShowPimNeighbor": True,
        "ShowInterfacesTrunk": True,
        "ShowIpInterfaceBrief": True,
        "ShowIpInterfaceBriefPipeVlan": True,
        "ShowDot1x": True,
        "ShowBoot": True,
        "ShowPagpNeighbor": True,
        "ShowIpProtocols": True,
        "ShowIpv6Rpf": True,
        "ShowIpOspfDatabaseRouter": True,
        "ShowIpOspfInterface": True,
        "ShowIpOspfMplsTrafficEngLink": True,
        "ShowIpOspfNeighborDetail": True,
        "ShowIpOspfShamLinks": True,
        "ShowIpOspfVirtualLinks": True,
        "ShowIpv6Route": True,
        "ShowIpBgp": True,
        "ShowMplsLdpNeighbor": True,
        "ShowInterfaceDetail": True,
        "ShowInterfaceIpBrief": True,
        "ShowInterfaceSummary": True,
        "ShowInterfaceTransceiverDetail": True,
        "ShowSdwanSystemStatus": True,
        "ShowSdwanSoftware": True,
    },
}

EMPTY_SKIP = {
    "iosxe": {"ShowVersion": True},
    "ios": {
        "ShowVersion": True,
        "ShowIpv6EigrpNeighbors": True,
        "ShowIpv6EigrpNeighborsDetail": True,
    },
}


def read_from_file(file_path):
    """Helper function to read from a file."""
    f = open(file_path, "r")
    return f.read()


def read_json_file(file_path):
    """Helper function to read in json."""
    with open(file_path) as f:
        data = json.load(f)
    return data


def read_python_file(file_path):
    """Helper function to read in a Python file, and look for expected_output."""
    _module = importlib.machinery.SourceFileLoader("expected", file_path).load_module()
    return getattr(_module, "expected_output")


def get_operating_systems():
    """Helper Script to get operating systems."""
    # Update and fix as more OS's converted to folder baed tests
    if _os:
        return [_os]
    return ["asa", "ios", "iosxe"]
    # operating_system = []
    # for folder in os.listdir("./"):
    #    if os.path.islink("./" + folder):
    #        operating_system.append(folder)
    # return operating_system


class FileBasedTest(aetest.Testcase):
    """Standard pyats testcase class."""

    OPERATING_SYSTEMS = get_operating_systems()
    @aetest.test
    @aetest.test.loop(operating_system=OPERATING_SYSTEMS)
    def check_os_folder(self, steps, operating_system):
        """Loop through OS's and run appropriate tests."""
        parse_files = []
        # Get all of the root level files
        for parse_file in glob.glob(
            f"../src/genie/libs/parser/{operating_system}/*.py"
        ):
            if parse_file.endswith("__init__.py"):
                continue
            # Load all of the classes in each of those files, and search for classes
            # that have a `cli` method
            _module = importlib.machinery.SourceFileLoader(
                os.path.basename(parse_file[: -len(".py")]), parse_file
            ).load_module()
            start = 0
            for name, local_class in inspect.getmembers(_module):
                if CLASS_SKIP.get(operating_system) and CLASS_SKIP[operating_system].get(name):
                    continue
                if _class and _class != name:
                    continue
                if hasattr(local_class, "cli") and not name.endswith("_iosxe"):
                    # if name != 'ShowAuthenticationSessionsInterface':
                    #    start = 1
                    # if not start:
                    #    continue
                    with steps.start(f"{operating_system} -> {name}") as class_step:
                        with class_step.start(
                            f"Test Golden -> {operating_system} -> {name}",
                            continue_=True,
                        ) as golden_steps:
                            self.test_golden(
                                golden_steps, local_class, operating_system, None
                            )
                        with class_step.start(
                            f"Test Empty -> {operating_system} -> {name}",
                            continue_=True,
                        ) as empty_steps:
                            self.test_empty(empty_steps, local_class, operating_system, None)

    def test_golden(self, steps, local_class, operating_system, token=None):
        """Test step that finds any output named with _output.txt, and compares to similar named .py file."""
        folder_root = f"{operating_system}/{local_class.__name__}/cli/equal"
        output_glob = glob.glob(f"{folder_root}/*_output.txt")
        if len(output_glob) == 0:
            self.failed(f"No files found in appropriate directory for {local_class}")
        # Look for any files ending with _output.txt, presume the user defined name from that (based
        # on truncating that _output.txt suffix) and obtaining expected results and potentially an arguments file
        for user_defined in output_glob:
            user_test = os.path.basename(user_defined[: -len("_output.txt")])
            with steps.start(
                f"Gold -> {operating_system} -> {local_class.__name__} -> {user_test}",
                continue_=True,
            ):
                golden_output_str = read_from_file(
                    f"{folder_root}/{user_test}_output.txt"
                )
                golden_output = {"execute.return_value": golden_output_str}

                golden_parsed_output = read_python_file(
                    f"{folder_root}/{user_test}_expected.py"
                )
                arguments = {}
                if os.path.exists(f"{folder_root}/{user_test}_arguments.json"):
                    arguments = read_json_file(
                        f"{folder_root}/{user_test}_arguments.json"
                    )

                device = Mock(**golden_output)
                obj = local_class(device=device)
                parsed_output = obj.parse(**arguments)
                assert parsed_output == golden_parsed_output, "{parsed_output} \n!=\n{golden_parsed_output}".format(parsed_output=parsed_output, golden_parsed_output=golden_parsed_output)

    def test_empty(self, steps, local_class, operating_system, token=None):
        """Test step that looks for empty output."""

        folder_root = f"{operating_system}/{local_class.__name__}/cli/empty"
        output_glob = glob.glob(f"{folder_root}/*_output.txt")
        if (
            len(output_glob) == 0
            and not EMPTY_SKIP.get(operating_system, {}).get(local_class.__name__)
        ):
            self.failed(
                f"No files found in appropriate directory for {local_class} empty file"
            )
        for user_defined in output_glob:
            user_test = os.path.basename(user_defined[: -len("_output.txt")])
            with steps.start(
                f"Empty -> {operating_system} -> {local_class.__name__} -> {user_test}",
                continue_=True,
            ):
                empty_output_str = read_from_file(
                    f"{folder_root}/{user_test}_output.txt"
                )
                empty_output = {"execute.return_value": empty_output_str}
                arguments = {}
                if os.path.exists(f"{folder_root}/{user_test}_arguments.json"):
                    arguments = read_json_file(
                        f"{folder_root}/{user_test}_arguments.json"
                    )

                device = Mock(**empty_output)
                obj = local_class(device=device)
                try:
                    obj.parse(**arguments)
                    self.failed(f"File parsed, when expected not to for {local_class}")
                except SchemaEmptyParserError:
                    return True


if __name__ == "__main__":
    aetest.main()
