import json
from pathlib import Path

import click
import globus_compute_sdk
import globus_sdk

from entrypoint import endpoint_name as entry_point_endpoint_name
from entrypoint.compute_functions.entry_point_function import entry_point_function
from flows.auth import get_flow_client, get_group_client
from flows.backend_flow_adapters import get_flow_adapters
from flows.globus_flows import flow_builders
from flows.utils import bcolors, create_flow
from datasets import datasets


@click.command()
@click.option(
    "--reset-tokens",
    is_flag=True,
    default=False,
    help="Reset tokens and re-login",
)
@click.option(
    "--no-flow-overwrite",
    is_flag=True,
    default=False,
    help="Do not overwrite existing flows, instead create new ones",
)
@click.option(
    "--django-adapter-format",
    is_flag=True,
    default=False,
    help="Use the svelte-server adapter format (instead of Django)",
)
@click.option(
    "--globus-group",
    type=str,
    default="OpenCosmo",
    help="Name of the primary Globus Group (Flow Permissions)",
)
@click.argument(
    "adapter_output_folder",
    type=click.Path(
        dir_okay=True,
        file_okay=False,
    ),
)
def cli(
    reset_tokens: bool,
    no_flow_overwrite: bool,
    django_adapter_format: bool,
    globus_group: str,
    adapter_output_folder: str,
):
    # List of datasets and their group requirements
    requirement_groups = set()
    output_datasets = {}
    for dataset_name, dataset in datasets.items():
        if isinstance(dataset, dict):
            output_datasets.update(dataset)
        else:
            output_datasets[dataset_name] = dataset

    for dataset in output_datasets.values():
        if dataset.required_globus_groups is not None:
            requirement_groups.update(dataset.required_globus_groups)

    # Main Globus Group
    print()
    print("Getting Globus Group information")
    group_client = get_group_client()
    groups = group_client.get_my_groups()
    main_group = next(g for g in groups if g["name"] == globus_group)
    if main_group is None:
        raise ValueError(f"Group {globus_group} not found")
    main_group_id = main_group["id"]
    main_group_scope = f"urn:globus:groups:id:{main_group_id}"
    print(f"  - {globus_group:20s}: {main_group_id}")
    print(f"    {'Scope:':20s}: {main_group_scope}")

    # Substitution Groups
    substition_groups = {}
    for group_name in requirement_groups:
        group = next((g for g in groups if g["name"] == group_name), None)
        if group is None:
            raise ValueError(f"Group {group_name} not found")
        sub_group_id = group["id"]
        sub_group_scope = f"urn:globus:groups:id:{sub_group_id}"
        print(f"  - {group_name:20s}: {sub_group_id}")
        print(f"    {'Scope:':20s}: {sub_group_scope}")
        substition_groups[group_name] = sub_group_id
    dataset_group_requirements = {
        dataset_name: [
            substition_groups[group_name]
            for group_name in dataset.required_globus_groups
        ]
        for dataset_name, dataset in output_datasets.items()
        if dataset.required_globus_groups is not None
    }

    # Entry-point function
    compute_client = globus_compute_sdk.Client()

    # Entry-point endpoint
    entry_point_function_name = entry_point_function.slug
    print()
    print("Getting entrypoint endpoint:")
    endpoints = compute_client.get_endpoints()
    entry_point_endpoints = [
        endpoint
        for endpoint in endpoints
        if endpoint["name"] == entry_point_endpoint_name
    ]
    if len(entry_point_endpoints) == 0:
        print(
            f"{bcolors.FAIL}ERROR: Endpoint not registered: {entry_point_endpoint_name}"
            f"{bcolors.ENDC}"
        )
        return 1
    elif len(entry_point_endpoints) > 1:
        print(
            f"{bcolors.WARNING}Multiple endpoints found with name: {entry_point_endpoint_name}"
            f"{bcolors.ENDC}"
        )
        for i, endpoint in enumerate(entry_point_endpoints):
            print(f"  ({i}): {entry_point_endpoint_name:20s} {endpoint['uuid']}")
        endpoint_index = int(
            input(f"Select the endpoint to use (0-{len(entry_point_endpoints) - 1}): ")
        )
        endpoint = entry_point_endpoints[endpoint_index]
    else:
        endpoint = entry_point_endpoints[0]
    print(f"  - {endpoint['name']:20s}: {endpoint['uuid']}")

    # Entry-point function
    print()
    print("Getting entrypoint function:")
    entry_point_whitelist = compute_client.get_allowed_functions(endpoint["uuid"])
    if not entry_point_whitelist["restricted"]:
        print(f"{bcolors.FAIL}ERROR: Entry-point endpoint not restricted{bcolors.ENDC}")
        return 1
    entry_point_function_uuid = None
    for uuid in entry_point_whitelist["functions"]:
        function = compute_client.get_function(uuid)
        if function["function_name"] == entry_point_function_name:
            print(f"  - {entry_point_function_name:20s}: {uuid}")
            if entry_point_function_uuid is not None:
                print(
                    f"{bcolors.FAIL}ERROR: Multiple entry-point functions found on same endpoint"
                    f"{bcolors.ENDC}"
                )
                return 1
            entry_point_function_uuid = uuid
    if entry_point_function_uuid is None:
        print(
            f"{bcolors.FAIL}ERROR: Entry-point function not found: entry_point_function"
            f"{bcolors.ENDC}"
        )
        return 1

    # Flows
    print()
    print("Creating/updating flows:")
    flow_client = get_flow_client(reset_tokens=reset_tokens)
    registered_flows = []
    for flow_builder in flow_builders:
        flow_defn = flow_builder(
            setup_function_uuid=entry_point_function_uuid,
            setup_endpoint_uuid=endpoint["uuid"],
        )
        flow_id = create_flow(
            flow_client,
            flow_defn.name,
            flow_defn.flow_definition,
            flow_defn.input_schema,
            flow_defn.subtitle,
            flow_viewers=[main_group_scope],
            flow_starters=[main_group_scope],
            overwrite=not no_flow_overwrite,
        )
        flow_defn.globus_uuid = flow_id
        flow_scope = globus_sdk.SpecificFlowClient(flow_id).scopes.user
        print(f"  - {flow_defn.name:20s}: {flow_id}")
        print(f"    Scope: {flow_scope}")
        registered_flows.append(flow_defn)
    if not registered_flows:
        print(f"{bcolors.FAIL}ERROR: No flows registered{bcolors.ENDC}")
        return 1

    # Format flow adapter templates
    print()
    print("Formatting flow adapter templates:")
    adapter_substitutions = {}
    for flow in registered_flows:
        if flow.globus_uuid is None:  # Is this the best option?
            raise ValueError(f"Flow {flow.name} has no Globus UUID")
        adapter_substitutions[flow.slug] = flow.globus_uuid

    adapters = get_flow_adapters(adapter_substitutions, dataset_group_requirements)

    for adapter_name, adapter in adapters.items():
        flow = next(
            f for f in registered_flows if f.globus_uuid == adapter["flow_uuid"]
        )
        assert flow is not None
        adapter["frontend_settings"]["stages"] = [
            s.model_dump() for s in flow.flow_stages
        ]

    if not django_adapter_format:
        for adapter_name, adapter in adapters.items():
            adapter["adapter_slug"] = adapter.pop("flow_slug")
            adapter["adapter_name"] = adapter.pop("flow_name")
            adapter["adapter_description"] = adapter.pop("flow_description")
            adapter["preview_path"] = ""

    # Write flow adapter templates
    output_path = Path(adapter_output_folder)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    for adapter_name, adapter in adapters.items():
        with open(output_path / f"{adapter_name}.json", "w") as f:
            f.write(json.dumps(adapter, indent=2))
