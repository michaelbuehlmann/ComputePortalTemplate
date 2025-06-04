import logging  # TODO: maybe need a MPIFileHandler
import os

import click
from mpi4py import MPI

from endpoint.datasets import Dataset, datasets
from endpoint.utils.error_handler import init_mpi_error_handler

from .preview import create_preview_data


@click.command()
@click.option("--dataset", type=click.Choice(list(datasets.keys())), required=True)
@click.option("--name", type=str, required=True, help="Name for hello world")
@click.option("--option", is_flag=True, help="An example option")
@click.option("--output", type=str, required=True)
@click.option("--log-file", type=click.Path(writable=True, dir_okay=False))
def cli(
    dataset: str,
    name: str,
    option: bool,
    output: str,
    log_file: str | None = None,
) -> None:
    # Set up logging
    logging_config = {
        "format": "%(asctime)s %(levelname)8s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "level": "INFO",
    }
    if log_file is not None:
        logging_config["filename"] = log_file
    logging.basicConfig(**logging_config)  # type: ignore
    init_mpi_error_handler()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nranks = comm.Get_size()

    if rank == 0:
        logging.info("Starting example task with parameters:")
        logging.info(f"  dataset: {dataset}")
        logging.info(f"  name:     {name}")
        logging.info(f"  option:   {option}")
        logging.info(f"Running with {nranks} MPI ranks")
        logging.info(f"Working directory: {os.getcwd()}")

    dset: Dataset = datasets[dataset]

    if rank == 0:
        logging.info("Done")
        logging.info("Writing file")
        with open(output, "w") as f:
            f.write(f"Hello {name} from rank {rank} of {nranks}!\n")
            f.write(f"  Option is set: {option}\n")
            f.write(f"  Dataset: {dset.name}\n")

    if rank == 0:
        logging.info("Creating preview data")
        preview_data = create_preview_data(
            input_data={
                "dataset": dataset,
                "name": name,
                "option": option,
            },
            output_file=output,
        )
        with open("preview.json", "w") as f:
            f.write(preview_data.model_dump_json())
        logging.info("Done")

    if MPI is not None:
        comm.Barrier()


if __name__ == "__main__":
    cli()
