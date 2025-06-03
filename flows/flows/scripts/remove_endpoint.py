import click
import globus_compute_sdk


@click.command()
@click.argument(
    "endpoint_uuid",
    type=str,
)
def cli(endpoint_uuid: str):
    compute_client = globus_compute_sdk.Client()

    # Compute Endpoints
    print("Getting endpoints:")
    endpoints = compute_client.get_endpoints()
    endpoint = next(
        endpoint for endpoint in endpoints if endpoint["uuid"] == endpoint_uuid
    )
    status = compute_client.get_endpoint_status(endpoint["uuid"])
    print(f"Found endpoint {endpoint['name']}: {endpoint['uuid']} ({status['status']})")

    remove = input("Remove endpoint? (y/N): ")
    if remove.lower() == "y":
        print("Removing endpoint...")
        compute_client.delete_endpoint(endpoint["uuid"])
        print("Endpoint removed")
    else:
        print("Endpoint not removed")
