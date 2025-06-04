import numba
import numpy as np
import numpy.typing as npt


@numba.jit(nopython=True, parallel=True)
def _get_profile_indices(
    profile_fof_tag,
    profile_bin,
    sorted_target_fof_tag,
    out_profile_indices,
):
    for j in numba.prange(len(profile_fof_tag)):
        tag = profile_fof_tag[j]
        test_idx = np.searchsorted(sorted_target_fof_tag, tag)
        if sorted_target_fof_tag[test_idx] == tag:
            out_profile_indices[test_idx, profile_bin[j]] = j


def get_profilematrix(
    profiles: dict[str, np.ndarray],
    sorted_tags: npt.NDArray[np.int64],
    *,
    profile_halo_tag_field: str = "fof_halo_bin_tag",
    profile_bin_idx_field: str = "sod_halo_bin",
) -> dict[str, npt.NDArray[np.float32]]:
    """constructs an index matrix of shape `(nhalos, nbins)` for halo -> profile look-up

    Parameters
    ----------
    profiles:
        the profile data (e.g. by reading the sodhalopropertybins GenericIO files)

    sorted_tags:
        the halo tags (sorted ascending) for which to find profiles

    nbins:
        number of profile bins per halo

    Returns
    -------
    the i-th row of the returned index matrix contains the indices to the profile data
    corresponding to the halo_tag contained in `sorted_tags[i]`. The radial bins are
    sorted in ascending order, i.e. `output[k][i, j]` contains the j-th radial bin of
    the k-profile of the i-th halo.

    Note
    ----
    The function will trigger a RuntimeError if the profile of a requested halo
    could not be found or is incomplete.

    """
    # make sure it's sorted
    if not (
        np.all(np.diff(sorted_tags) > 0)
        and np.min(profiles[profile_bin_idx_field]) == 0
    ):
        raise RuntimeError("Error parsing halo profile data")

    nbins = np.max(profiles[profile_bin_idx_field]) + 1
    profile_indices = np.empty((len(sorted_tags), nbins), dtype=np.int64)
    profile_indices[:] = -1
    _get_profile_indices(
        profiles[profile_halo_tag_field],
        profiles[profile_bin_idx_field],
        sorted_tags,
        profile_indices,
    )
    if np.any(profile_indices == -1):
        print("DEBUG:", profile_indices, sorted_tags, nbins, flush=True)
        raise RuntimeError("Error parsing halo profile data")

    return {k: d[profile_indices] for k, d in profiles.items()}
