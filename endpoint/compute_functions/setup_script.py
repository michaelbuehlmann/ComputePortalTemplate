from pathlib import Path

import click
import globus_compute_sdk
from dotenv import load_dotenv
from globus_compute_sdk.serialize import DillCodeSource

from .auth import get_group_client
from .functions import compute_functions


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Load environment variables from .env file
load_dotenv()

# Path to root of this repository
endpoint_template_root = Path(__file__).parent.parent / "config"
default_globus_group = "OpenCosmo"


@click.command()
@click.option(
    "--reset-tokens",
    is_flag=True,
    default=False,
    help="Reset tokens and re-login",
)
@click.option(
    "--globus-group",
    default=default_globus_group,
    help="Globus Group name for compute function registration",
)
@click.argument(
    "system",
    type=click.Choice(["polaris", "perlmutter", "defiant"]),
)
def cli(reset_tokens: bool, globus_group: str, system: str):
    endpoint_template_dir = endpoint_template_root / system
    # Compute Endpoints
    compute_client = globus_compute_sdk.Client()
    endpoints = compute_client.get_endpoints()
    print()
    print("Registered endpoints:")
    for endpoint in endpoints:
        print(f" - {endpoint['name']}: {endpoint['uuid']}")
        print(f"   owner: {endpoint['owner']}")
        print(f"   display name: {endpoint['display_name']}")

    for config_path in endpoint_template_dir.glob("*.yaml"):
        if config_path.stem not in [endpoint["name"] for endpoint in endpoints]:
            print(f"Endpoint {config_path.stem} has not been registered with Globus")
            print("Please setup the endpoint and then run this script again")

    # Compute Functions
    print()
    print("Getting group information for compute function registration")
    group_client = get_group_client(reset_tokens=reset_tokens)
    groups = group_client.get_my_groups()
    group = next(g for g in groups if g["name"] == globus_group)
    if group is None:
        raise ValueError(f"Group {globus_group} not found")
    group_id = group["id"]
    print(f"  - {globus_group:20s}: {group_id}")

    print()
    print("Registering compute functions:")
    code_serialization_strategy = DillCodeSource()
    # code_serialization_strategy = CombinedCode()
    compute_client = globus_compute_sdk.Client(
        code_serialization_strategy=code_serialization_strategy
    )
    for compute_function in compute_functions:
        function_id = compute_client.register_function(
            compute_function.function,
            function_name=compute_function.slug,
            group=group_id,
        )
        compute_function.globus_uuid = function_id
        print(f"  - {compute_function.name:20s}: {function_id}")

    print("Updating local endpoint config with compute-function restrictions")
    endpoint_config_path = Path.home() / ".globus_compute"
    for config_path in endpoint_template_dir.glob("*.yaml"):
        output_path = endpoint_config_path / config_path.stem / "config.yaml"
        print(f"  replacing {output_path}...")
        assert output_path.is_file()
        with open(config_path, "r") as f:
            config = f.read()
        config += "allowed_functions:\n"
        for compute_function in compute_functions:
            config += f"  - {compute_function.globus_uuid}  # {compute_function.slug}\n"
        with open(output_path, "w") as f:
            f.write(config)
    print(f"{bcolors.WARNING}MAKE SURE TO RESTART THE ENDPOINTS!{bcolors.ENDC}")

    for config_path in endpoint_template_dir.glob("*.yaml"):
        print(f"  - globus-compute-endpoint restart {config_path.stem}")
