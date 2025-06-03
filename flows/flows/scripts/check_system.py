import click
import globus_compute_sdk
from compute_functions import compute_functions

from flows.backend_flow_adapters import get_flow_adapters
from flows.utils import bcolors


@click.command()
def cli():
    compute_client = globus_compute_sdk.Client()

    # Compute Systems
    systems = set()
    for compute_function in compute_functions:
        systems.update(compute_function.systems)

    # Adapters
    adapters = get_flow_adapters({})

    # Target endpoints
    target_endpoints = set()
    for adapter_name, adapter in adapters.items():
        target_endpoints.update(
            {
                adapter["flow_input"]["compute_endpoint_name"].format(SYSTEM=s)
                for s in systems
            }
        )

    # Compute Endpoints
    print("Getting registered endpoints:")
    endpoints = compute_client.get_endpoints()
    endpoint_names = {endpoint["name"] for endpoint in endpoints}
    if not target_endpoints.issubset(endpoint_names):
        missing_endpoints = target_endpoints - endpoint_names
        for missing_endpoint in missing_endpoints:
            print(
                f"{bcolors.WARNING}WARNING: Endpoint not registered: {missing_endpoint}"
                f"{bcolors.ENDC}"
            )
    endpoints = [
        endpoint for endpoint in endpoints if endpoint["name"] in target_endpoints
    ]
    print("Done\n")

    # Check if online
    print("Checking status for endpoints:")
    for endpoint in endpoints:
        status = compute_client.get_endpoint_status(endpoint["uuid"])
        if status["status"] != "online":
            print(
                f"{bcolors.WARNING}WARNING: Endpoint not online: {endpoint['name']} "
                f"{bcolors.ENDC}"
                f"(status: {status['status']})",
            )
    print("Done\n")

    # Check whitelist
    print("Checking whitelist for endpoints:")
    function_names = {f.slug for f in compute_functions}
    for endpoint in endpoints:
        print(f" - {endpoint['name']}")
        whitelist_response = compute_client.get_allowed_functions(endpoint["uuid"])
        if not whitelist_response["restricted"]:
            print(
                f"{bcolors.WARNING}   WARNING: Endpoint {endpoint['name']} is not restricted!"
                f"{bcolors.ENDC}"
            )
            continue
        whitelist = whitelist_response["functions"]
        if len(whitelist) == 0:
            print(
                f"{bcolors.WARNING}Whitelist for endpoint {endpoint['name']} is empty"
                f"{bcolors.ENDC}"
            )
            continue
        whitelist_functions = set()
        for uuid in whitelist:
            fct = compute_client.get_function(uuid)
            whitelist_functions.add(fct["function_name"])
        for slug in function_names - whitelist_functions:
            print(
                f"{bcolors.WARNING}WARNING: Function not in whitelist: {slug} "
                f"{bcolors.ENDC}"
            )
        for slug in whitelist_functions - function_names:
            print(
                f"{bcolors.WARNING}WARNING: Foreign function in whitelist: {slug} "
                f"{bcolors.ENDC}"
            )
    print("Done\n")
