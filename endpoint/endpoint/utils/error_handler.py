import logging
import sys
import traceback

from mpi4py import MPI

comm = MPI.COMM_WORLD


def _mpi_exception_handler(exc_type, exc_value, exc_traceback):
    rank = comm.Get_rank()
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error(
        f"Uncaught exception on rank {rank}",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    sys.stderr.write(f"Uncaught exception on rank {rank}\n")
    sys.stderr.write(
        "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )
    with open(f"error_rank_{rank}.txt", "w") as f:
        f.write("".join(traceback.format_exception_only(exc_type, exc_value)))
    comm.Abort(1)


def init_mpi_error_handler():
    sys.excepthook = _mpi_exception_handler
