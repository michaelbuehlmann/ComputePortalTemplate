import os
import shutil
import subprocess
from functools import cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class OutputSettings(
    BaseSettings
):  # BaseSettings automatically pulls from the environment
    model_config = SettingsConfigDict(env_prefix="hcp_")
    result_collection_uuid: str
    result_collection_path: str
    result_collection_url: str
    working_base: Path = Path("${HOME}/hacc_compute_portal_workdir")
    result_base: Path = Path("${HOME}/hacc_compute_portal_results")


OUTPUT_CONFIG = OutputSettings()


@cache
def get_working_directory(compute_function: str, run_uuid: str) -> Path:
    """
    Get the working directory for a given compute function and run_uuid.
    """
    working_directory = OUTPUT_CONFIG.working_base / compute_function / run_uuid
    working_directory.mkdir(parents=True, exist_ok=True)
    return working_directory


def handle_output(
    compute_function: str,
    run_uuid: str,
    process: subprocess.CompletedProcess,
    files_to_link: dict[str, str],
    *args,
    **kwargs,
):
    """
    Main output handler for compute functions. This should be called once the run is
    completed. The function will handle output whether the run was successful or not.

    arguments:
    ----------
    compute_function: str - The name of the compute function that is calling this
        function. Along with the run_uuid, this is used to determine the working and
        outuput directories.
    run_uuid: str - The unique identifier for this run. This is used to determine
        working and output directories.
    process: subprocess.CompletedProcess - Compute functions call subprocess.run to
        execute the script that actually does the heavy lifting. Passing it in here
        allows us to access the output and error streams.
    files_to_link: dict[str, str] - A dictionary of files that will be moved to the
        output folders. Links to this files will be generated and returned, assuming the
        run was sucessful. Files are assumed to be in the working directory.
        Should be of the form:
        {"name": "filename.ext"}
        Which will result in the following entry in the output:
        {"name_url": "https://path/in/globus/filename.ext"}
        Which should be directly accessible to an authenticated user.
    """
    log_urls = write_logs(compute_function, run_uuid, process)
    if process.returncode:
        return handle_error(
            compute_function,
            run_uuid,
            process,
            log_urls,
            *args,
            **kwargs,
        )
    else:
        return handle_success(
            compute_function, run_uuid, files_to_link, log_urls, *args, **kwargs
        )


def write_logs(
    compute_function: str, run_uuid: str, process: subprocess.CompletedProcess
):
    logs_directory = OUTPUT_CONFIG.result_base / "logs" / compute_function / run_uuid
    working_directory = get_working_directory(compute_function, run_uuid)
    logs_directory.mkdir(parents=True, exist_ok=True, mode=0o755)
    # TODO Put logs somewhere special

    log_url = (
        OUTPUT_CONFIG.result_collection_url + f"/logs/{compute_function}/{run_uuid}"
    )

    log_urls = {}
    if process.stdout:
        with open(logs_directory / "stdout.txt", "w") as f:
            f.write(process.stdout)
        log_urls.update({"stdout_url": log_url + "/stdout.txt"})
    if process.stderr:
        with open(logs_directory / "stderr.txt", "w") as f:
            f.write(process.stderr)
        log_urls.update({"stderr_url": log_url + "/stderr.txt"})
    run_log = working_directory / "run.log"
    if run_log.exists():
        shutil.move(run_log, logs_directory / "run.log")
        log_urls.update({"run_log_url": log_url + "/run.log"})
    return log_urls


def handle_error(
    compute_function: str,
    run_uuid: str,
    process: subprocess.CompletedProcess,
    log_links: dict[str, str],
    *args,
    **kwargs,
):
    """
    Handle the case where the job failed. This process will reads error files from
    the individual MPI ranks.

    Additional links to log files can be provided in the `log_links` argument.
    """
    working_directory = get_working_directory(compute_function, run_uuid)
    print(f"ERRORS:\n{process.stderr}")
    errormessage = ""
    for errorfile in working_directory.glob("error_rank_*.txt"):
        with open(errorfile) as f:
            errormessage = f.read().strip()
        if errormessage:
            break
        else:
            errormessage = process.stderr.split("\n")[0]
    os.chdir(working_directory.parent)
    shutil.rmtree(working_directory)
    return {
        "status": "FAILED",
        "message": errormessage,
        **log_links,
    }


def handle_success(
    compute_function: str,
    run_uuid: str,
    files_to_link: dict[str, str],
    additional_links: Optional[dict[str, str]] = None,
    message: str = "",
    *args,
    **kwargs,
):
    """
    Handle the case where the job succeeded. This process will move the output files
    to the result directory. It will generate links to any files that are passed in
    the `files_to_link` argument. Additional links (currently used for logs) can be
    provided in the `additional_links` argument. These links will simply be returned
    as-is without modification.
    """
    working_directory = get_working_directory(compute_function, run_uuid)
    result_collection_directory = OUTPUT_CONFIG.result_base / compute_function
    result_directory = result_collection_directory / run_uuid
    result_directory.mkdir(parents=True, exist_ok=True, mode=0o755)
    os.chdir(result_directory)

    for file in files_to_link.values():
        if not (working_directory / file).exists():
            raise FileNotFoundError(
                f"File {file} not found in working directory {working_directory}"
            )
        shutil.copy(working_directory / file, result_directory)

    shutil.rmtree(working_directory)

    result = {
        "status": "SUCCEEDED",
        "message": message,
        "collection_uuid": OUTPUT_CONFIG.result_collection_uuid,
        "collection_path": f"{OUTPUT_CONFIG.result_collection_path}/{compute_function}/{run_uuid}",
    }
    for key, value in files_to_link.items():
        result[f"{key}_url"] = (
            OUTPUT_CONFIG.result_collection_url
            + f"/{compute_function}/{run_uuid}/{value}"
        )
    if additional_links:
        result = result | additional_links
    return result
