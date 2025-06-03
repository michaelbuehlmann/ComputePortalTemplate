import click
import globus_compute_sdk
from compute_functions import compute_functions

from entrypoint import endpoint_name
from entrypoint.compute_functions.entry_point_function import entry_point_function
from flows.backend_flow_adapters import get_flow_adapters
from flows.utils import bcolors


@click.command()
def cli():
    compute_client = globus_compute_sdk.Client()
    function_name = entry_point_function.slug

    # Compute Systems
    systems = set()
    for compute_function in compute_functions:
        systems.update(compute_function.systems)

    # Compute Endpoints
    print("Getting entrypoint endpoint:")
    endpoints = compute_client.get_endpoints()
    endpoints = [
        endpoint for endpoint in endpoints if endpoint["name"] == endpoint_name
    ]
    if len(endpoints) == 0:
        print(
            f"{bcolors.FAIL}ERROR: Endpoint not registered: {endpoint_name}"
            f"{bcolors.ENDC}"
        )
        return
    if len(endpoints) > 1:
        print(f"{bcolors.WARNING}WARNING: Multiple endpoints found:{bcolors.ENDC}")
        for i, endpoint in enumerate(endpoints):
            status = compute_client.get_endpoint_status(endpoint["uuid"])
            print(
                f" {i}: {endpoint['name']:20s}: {endpoint['uuid']} ({status['status']})"
            )
        endpoint_index = int(input(f"Select endpoint index (0-{len(endpoints) - 1}): "))
        endpoint = endpoints[endpoint_index]
    else:
        endpoint = endpoints[0]

    # Check if online
    status = compute_client.get_endpoint_status(endpoint["uuid"])
    print(f" - {endpoint_name:20s}: {endpoint['uuid']} ({status['status']})")
    if status["status"] != "online":
        print(
            f"{bcolors.FAIL}ERROR: Endpoint not online: {endpoint['uuid']} "
            f"{bcolors.ENDC}"
        )
        return

    # Get entrypoint function
    print("  Getting entrypoint function:")
    whitelist_response = compute_client.get_allowed_functions(endpoint["uuid"])
    if not whitelist_response["restricted"]:
        print(
            f"{bcolors.FAIL}ERROR: Endpoint {endpoint['name']} is not restricted"
            f"{bcolors.ENDC}"
        )
        return
    function_uuids = whitelist_response["functions"]
    if len(function_uuids) == 0:
        print(
            f"{bcolors.FAIL}ERROR: No functions found in whitelist of endpoint {endpoint['name']}"
            f"{bcolors.ENDC}"
        )
        return
    function = None
    for uuid in function_uuids:
        function = compute_client.get_function(uuid)
        if function["function_name"] == function_name:
            break
    if function is None:
        print(
            f"{bcolors.FAIL}ERROR: Function '{function_name}' not found in whitelist "
            f"of endpoint {endpoint['name']}{bcolors.ENDC}"
        )
        return
    print(f"   - {function_name:20s}: {function['function_uuid']}")
    print("  Done\n")

    adapters = get_flow_adapters({})
    for adapter_name, adapter in adapters.items():
        adapter_endpoint = adapter["flow_input"]["compute_endpoint_name"]
        adapter_function = adapter["flow_input"]["compute_function_name"]
        datasets = adapter["flow_input_schema"]["properties"]["dataset"]["enum"]

        print(f"  Testing adapter '{adapter_name}':")
        print(f"   - Endpoint: {adapter_endpoint}")
        print(f"   - Function: {adapter_function}")

        results = {}
        with globus_compute_sdk.Executor(
            endpoint_id=endpoint["uuid"], client=compute_client
        ) as executor:
            for dataset in datasets:
                results[dataset] = executor.submit_to_registered_function(
                    function_id=function["function_uuid"],
                    kwargs=dict(
                        endpoint_name=adapter_endpoint,
                        function_name=adapter_function,
                        params=dict(dataset=dataset),
                        run_id=0,
                    ),
                )
        for dataset in datasets:
            result = results[dataset].result()
            if result["status"] == "SUCCEEDED":
                print(bcolors.OKGREEN, end="")
            else:
                print(bcolors.FAIL, end="")
            print(
                f"   - Dataset: {dataset}:\n"
                f"     - Status:   {result['status']}\n"
                f"     - Message:  {result['message']}"
            )
            print(bcolors.ENDC, end="")
