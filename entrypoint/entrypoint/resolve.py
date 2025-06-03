from datasets import datasets

from .client import client


def resolve_endpoint(endpoint_name: str) -> str:
    endpoints = client.get_endpoints()
    endpoints = [e for e in endpoints if e["name"] == endpoint_name]
    if len(endpoints) == 0:
        raise RuntimeError(f"Endpoint {endpoint_name} not found")
    endpoint = None
    for e in endpoints:
        status = client.get_endpoint_status(e["uuid"])
        if status["status"] == "online":
            endpoint = e
            break
    if endpoint is None:
        raise RuntimeError(f"Endpoint {endpoint_name} is not online")

    return endpoint["uuid"]


def resolve_function(function_name: str, endpoint_uuid: str, endpoint_name: str) -> str:
    whitelist = client.get_allowed_functions(endpoint_uuid)
    if not whitelist["restricted"]:
        raise RuntimeError(f"Whitelist for endpoint {endpoint_name} not found")
    function_uuids = whitelist["functions"]
    for uuid in function_uuids:
        function = client.get_function(uuid)
        if function["function_name"] == function_name:
            return uuid
    raise RuntimeError(
        f"Function {function_name} not found in whitelist of endpoint {endpoint_name}"
    )


def resolve(endpoint_format_string: str, function_name: str, dataset_name: str):
    system = None
    for key, ds in datasets.items():
        if isinstance(ds, dict):
            if key == dataset_name:
                dataset = ds
                system = next(iter(ds.values())).system
                break
        else:
            if ds.name == dataset_name:
                dataset = ds
                system = dataset.system

                break
    if system is None:
        return {
            "status": "FAILED",
            "message": f"Dataset {dataset_name} not found",
        }

    endpoint_name = endpoint_format_string.format(SYSTEM=system)

    try:
        endpoint_uuid = resolve_endpoint(endpoint_name)
        function_uuid = resolve_function(function_name, endpoint_uuid, endpoint_name)
    except RuntimeError as e:
        return {"status": "FAILED", "message": e.args[0]}
    return {
        "status": "SUCCEEDED",
        "message": None,
        "_private_compute_endpoint_uuid": endpoint_uuid,
        "_private_compute_function_uuid": function_uuid,
    }
