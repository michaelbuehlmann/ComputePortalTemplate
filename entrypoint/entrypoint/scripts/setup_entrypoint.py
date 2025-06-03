from pathlib import Path

import click
import globus_compute_sdk
from globus_compute_sdk.serialize import DillCodeSource

from entrypoint import endpoint_name, repo_root
from entrypoint.compute_functions.entry_point_function import entry_point_function

from .auth import get_group_client


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


@click.command()
@click.option(
    "--reset-tokens",
    is_flag=True,
    default=False,
    help="Reset tokens and re-login",
)
@click.option(
    "--globus-group",
    type=str,
    default="OpenCosmo",
    help="Name of the Globus group to use for compute function registration",
)
@click.option(
    "--attach-endpoint",
    is_flag=True,
    help="Do not detach the endpoint process after starting / restarting from shell (for systemd)",
)
def cli(
    reset_tokens: bool,
    globus_group: str,
    attach_endpoint: bool,
):
    # Compute Functions
    print()
    print("Getting group information for compute function registration")
    group_client = get_group_client(reset_tokens=reset_tokens)
    groups = group_client.get_my_groups()
    group = next(g for g in groups if g["name"] == globus_group)
    if group is None:
        raise ValueError(f"Group {globus_group} not found")
    group_id = group["id"]
    group_scope = f"urn:globus:groups:id:{group_id}"
    print(f"  - {globus_group:20s}: {group_id}")
    print(f"    {'Scope:':20s}: {group_scope}")

    # Entry-point function
    print()
    print("Registering entry-point function:")
    code_serialization_strategy = DillCodeSource()
    # code_serialization_strategy = CombinedCode()
    compute_client = globus_compute_sdk.Client(
        code_serialization_strategy=code_serialization_strategy
    )
    function_id = compute_client.register_function(
        entry_point_function.function,
        function_name=entry_point_function.name,
        group=group_id,
    )
    entry_point_function.globus_uuid = function_id
    print(f"  - {entry_point_function.name:20s}: {function_id}")

    print(
        "Updating local endpoint config (entrypoint) with compute-function restrictions"
    )
    endpoint_config_path = Path.home() / ".globus_compute"

    config_path = repo_root / "config" / f"{endpoint_name}.yaml"
    output_path = endpoint_config_path / config_path.stem / "config.yaml"
    assert output_path.is_file()
    print(f"  replacing {output_path}...")
    with open(config_path, "r") as f:
        config = f.read()
    if attach_endpoint:
        config += "detach_endpoint: false"
    config += "allowed_functions:\n"
    config += f"  - {entry_point_function.globus_uuid}  # {entry_point_function.slug}\n"

    with open(output_path, "w") as f:
        f.write(config)

    print(f"{bcolors.WARNING}MAKE SURE TO RESTART THE ENDPOINTS!{bcolors.ENDC}")
