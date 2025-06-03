import click
from entrypoint.resolve import resolve


@click.command()
@click.argument("endpoint_format_string")
@click.argument("function_name")
@click.argument("dataset_name")
def cli(endpoint_format_string: str, function_name: str, dataset_name: str):
    result = resolve(endpoint_format_string, function_name, dataset_name)
    print(result)
