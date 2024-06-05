"""Filters for Jinja2 PostProcessing."""

from itertools import chain

from django_jinja import library
from netutils.vlan import vlanconfig_to_list

from nautobot_device_onboarding.constants import INTERFACE_TYPE_MAP_STATIC

# https://docs.nautobot.com/projects/core/en/stable/development/apps/api/platform-features/jinja2-filters/


@library.filter
def map_interface_type(interface_type):
    """Map interface type to a Nautobot type."""
    return INTERFACE_TYPE_MAP_STATIC.get(interface_type, "other")


@library.filter
def extract_prefix(network):
    """Extract the prefix length from the IP/Prefix. E.g 192.168.1.1/24."""
    return network.split("/")[-1]


@library.filter
def interface_status_to_bool(status):
    """Take links or admin status and change to boolean."""
    return "up" in status.lower()


@library.filter
def port_mode_to_nautobot(current_mode):
    """Take links or admin status and change to boolean."""
    mode_mapping = {
        "access": "access",
        "trunk": "tagged",
        "bridged": "tagged",
        "routed": "",
    }
    return mode_mapping.get(current_mode, "")


@library.filter
def key_exist_or_default(dict_obj, key):
    """Take a dict with a key and if its not truthy return a default."""
    if not dict_obj.get(key):
        return {}
    return dict_obj


@library.filter
def flatten_list_of_dict_from_value(list_of_dicts, value):
    """Takes a list of dictionaries with a value and flattens it."""
    flat_data = {list(item.keys())[0]: item[list(item.keys())[0]][value] for item in list_of_dicts}
    return flat_data


@library.filter
def flatten_dict_from_value(main_dict, wanted_value):
    """Takes a dictionary of dictionaries with a value and flattens it."""
    return {k: v[wanted_value] for k, v in main_dict.items()}


@library.filter
def get_entry_from_dict(dict_obj, key):
    """Take a dict with a key and return its object."""
    return dict_obj.get(key, "")


@library.filter
def interface_mode_logic(item):  # pylint: disable=too-many-return-statements
    """Logic to translate network modes to nautobot mode."""
    if isinstance(item, dict):
        if item.get("admin_mode"):
            if "access" in item["admin_mode"].lower():
                return "access"
            if item["admin_mode"] == "trunk" and item["trunking_vlans"] in ["ALL", "1-4094"]:
                return "tagged-all"
            if item["admin_mode"] == "trunk":
                return "tagged"
            if "dynamic" in item["admin_mode"]:
                if "access" in item["mode"]:
                    return "access"
                if item["mode"] == "trunk" and item["trunking_vlans"] in ["ALL", "1-4094"]:
                    return "tagged-all"
                if item["mode"] == "trunk":
                    return "tagged"
    else:
        if len(item) == 1:
            if item[0].get("admin_mode"):
                if "access" in item[0]["admin_mode"].lower():
                    return "access"
                if item[0]["admin_mode"] == "trunk" and item[0]["trunking_vlans"] in ["ALL", "1-4094"]:
                    return "tagged-all"
                if item[0]["admin_mode"] == "trunk":
                    return "tagged"
                if "dynamic" in item[0]["admin_mode"]:
                    if "access" in item[0]["mode"]:
                        return "access"
                    if item[0]["mode"] == "trunk" and item[0]["trunking_vlans"] in ["ALL", "1-4094"]:
                        return "tagged-all"
                    if item[0]["mode"] == "trunk":
                        return "tagged"
    return ""


@library.filter
def get_vlan_data(item, vlan_mapping):
    """Get vlan information from an item."""
    int_mode = interface_mode_logic(item)
    current_item = item
    if isinstance(item, list) and len(item) == 1:
        current_item = item[0]
    if int_mode:
        if int_mode == "tagged-all":
            return []
        if int_mode == "access":
            if current_item.get("access_vlan"):
                return [
                    {
                        "id": current_item["access_vlan"],
                        "name": vlan_mapping.get(
                            str(current_item["access_vlan"]), f"VLAN{str(current_item['access_vlan']).zfill(4)}"
                        ),
                    }
                ]
        if not isinstance(current_item["trunking_vlans"], list):
            trunk_vlans = [current_item["trunking_vlans"]]
        else:
            trunk_vlans = current_item["trunking_vlans"]
        return [
            {"id": vid, "name": vlan_mapping.get(str(vid), f"VLAN{str(vid).zfill(4)}")}
            for vid in list(chain.from_iterable([vlanconfig_to_list(vlan_stanza) for vlan_stanza in trunk_vlans]))
        ]
    return []


@library.filter
def parse_junos_ip_address(item):
    """Parse Junos IP and destination prefix.

    Example:
    >>> [{'prefix_length': [], 'ip_address': []}]
    >>> [{'prefix_length': ['10.65.229.106/31'], 'ip_address': ['10.65.229.106']}]
    >>> [{'prefix_length': ['10.65.133.0/29', '10.65.133.0/29'], 'ip_address': ['10.65.133.1', '10.65.133.3']}]
    >>> [{'prefix_length': None, 'ip_address': None}]
    """
    if isinstance(item, list) and len(item) > 0:
        if item[0]["prefix_length"] and item[0]["ip_address"]:
            return [
                {"prefix_length": item[0]["prefix_length"][0].split("/")[-1], "ip_address": item[0]["ip_address"][0]}
            ]
        if not item[0]["prefix_length"] and item[0]["ip_address"]:
            return [{"prefix_length": 32, "ip_address": item[0]["ip_address"][0]}]
    return []
