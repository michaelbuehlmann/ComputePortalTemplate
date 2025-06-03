from datetime import datetime
from pathlib import Path

import click
import globus_compute_sdk
from compute_functions import compute_functions

from entrypoint.resolve import resolve_endpoint, resolve_function
from flows.models import ComputeTestInput
from flows.utils import bcolors

# Compute Systems
systems = set()
for compute_function in compute_functions:
    systems.update(compute_function.systems)


@click.command()
@click.argument(
    "test_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def cli(
    test_file: Path,
):
    with open(test_file, "r") as f:
        test_input_raw = f.read()

    test_input = ComputeTestInput.model_validate_json(test_input_raw)
    endpoint_name = test_input.endpoint_name
    function_name = test_input.function_name
    function_params = test_input.params

    run_id = test_file.stem + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        endpoint_uuid = resolve_endpoint(endpoint_name)
        function_uuid = resolve_function(function_name, endpoint_uuid, endpoint_name)
    except RuntimeError as e:
        print(f"{bcolors.FAIL}Failed to resolve endpoint or function:{bcolors.ENDC}")
        print(f"  {e.args[0]}")
        return

    print(f"Running test {test_file.stem}:")
    print(f"  Endpoint: {endpoint_name} ({endpoint_uuid})")
    print(f"  Function: {function_name} ({function_uuid})")
    print(f"  Params:   {function_params}")

    # Run the function
    with globus_compute_sdk.Executor(endpoint_id=endpoint_uuid) as executor:
        result = executor.submit_to_registered_function(
            function_id=function_uuid,
            kwargs=dict(
                params=function_params,
                run_id=run_id,
            ),
        )
        print("Result:")
        print(result.result())
