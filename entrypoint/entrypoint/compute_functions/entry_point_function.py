from ._compute_function import ComputeFunctionDefinition


def _entry_point_function(
    endpoint_name: str,
    function_name: str,
    params: dict,
    run_id: str,
):
    from entrypoint.resolve import resolve

    # Could / should check additional stuff here:
    # - validate parameters
    # - check if endpoint is online
    # - etc

    dataset_name = params.get("dataset", None)
    if dataset_name is None:
        return {"status": "FAILED", "message": "Dataset not provided"}
    result = resolve(endpoint_name, function_name, dataset_name)

    return result


entry_point_function = ComputeFunctionDefinition(
    slug="_entry_point_function",
    name="Flow Setup Function",
    function=_entry_point_function,
)
