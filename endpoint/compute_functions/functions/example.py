from ._compute_function import ComputeFunctionDefinition


def _exampletask(params: dict, run_id: str):
    import os
    import string
    import subprocess

    from pydantic import ValidationError

    from endpoint import output
    from endpoint.scripts.example_task.parameter_model import ExampleParameters

    # sanitize run_id
    allowed_chars = set(string.ascii_lowercase + string.digits + "-" + "_")
    if not set(run_id) <= allowed_chars:
        raise ValueError(f"Globus run ID {run_id} contains invalid characters")

    # change working directory
    # validate params
    try:
        parameters = ExampleParameters(**params)
    except ValidationError as e:
        return {
            "status": "FAILED",
            "message": f"Error during parameter validation:\n{e}",
        }

    working_directory = output.get_working_directory("example", run_id)
    os.chdir(working_directory)

    cmd = "example-task"
    args = parameters.to_cmd_args()
    args.extend(["--output", "example-task.hdf5", "--log-file", "run.log"])

    # run command via mpiexec
    if os.environ["HCP_SYSTEM"] == "POLARIS":
        nodefile = os.environ["PBS_NODEFILE"]
        nnodes = len(open(nodefile).readlines())
        nranks = nnodes * 32
        mpi_cmd = ["mpiexec", "-n", str(nranks), "--hostfile", nodefile]
    elif os.environ["HCP_SYSTEM"] == "PERLMUTTER":
        mpi_cmd = ["srun", "--cpu-bind=cores"]
    process = subprocess.run(
        mpi_cmd
        + [
            cmd,
            *args,
        ],
        capture_output=True,
        text=True,
    )

    files_to_link = {
        "preview": "preview.json",
        "results": "example-task.hdf5",
    }
    return output.handle_output("example", run_id, process, files_to_link)


exampletask = ComputeFunctionDefinition(
    slug="_exampletask",
    name="Example Task",
    systems=["polaris", "perlmutter"],
    function=_exampletask,
)
